#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Standalone Admin backend (SQLite-only version - no Supabase required)
Handles authentication, project management, and PDF fetching.
"""

import os
import json
import requests
import sqlite3
import secrets
import bcrypt
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
from functools import wraps

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from t2t_store import get_conn, generate_doi_hash, decode_doi_hash

# -----------------------------
# Config
# -----------------------------
DB_PATH = os.getenv("T2T_DB", "t2t.db")
PDF_STORAGE_PATH = os.getenv("T2T_PDF_STORAGE", "pdfs")
ADMIN_PORT = int(os.getenv("T2T_ADMIN_PORT", "5002"))
SKIP_AUTH = os.getenv("T2T_SKIP_AUTH", "false").lower() == "true"

# External APIs
CROSSREF_API = "https://api.crossref.org/works/"
DOI2PDF_API = "https://doi2pdf.p.rapidapi.com/doi2pdf"
UNPAYWALL_EMAIL = os.getenv("UNPAYWALL_EMAIL", "your.email@example.com")

app = Flask(__name__)
CORS(app)

# -----------------------------
# Helper Functions
# -----------------------------

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False

def generate_session_token() -> str:
    """Generate a secure random session token."""
    return secrets.token_urlsafe(32)

def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())

def create_session(admin_id: str, ip_address: str = None, user_agent: str = None) -> Optional[str]:
    """Create a new session for an admin user."""
    try:
        conn = get_conn(DB_PATH)
        cur = conn.cursor()

        session_id = generate_uuid()
        session_token = generate_session_token()
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
        created_at = datetime.now(timezone.utc).isoformat()

        cur.execute("""
            INSERT INTO admin_sessions (id, admin_id, session_token, expires_at, created_at, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session_id, admin_id, session_token, expires_at, created_at, ip_address, user_agent))

        conn.commit()
        conn.close()
        return session_token
    except Exception as e:
        print(f"Error creating session: {e}")
        return None

def verify_session(session_token: str) -> Optional[Dict]:
    """Verify a session token and return admin info if valid."""
    try:
        conn = get_conn(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            SELECT s.*, a.email, a.display_name, a.is_active
            FROM admin_sessions s
            JOIN admin_users a ON s.admin_id = a.id
            WHERE s.session_token = ?
        """, (session_token,))

        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        # Parse row
        session_id, admin_id, token, expires_at, created_at, ip, ua, email, display_name, is_active = row

        # Check if expired
        expires = datetime.fromisoformat(expires_at)
        if expires < datetime.now(timezone.utc):
            # Delete expired session
            conn = get_conn(DB_PATH)
            conn.execute("DELETE FROM admin_sessions WHERE session_token = ?", (session_token,))
            conn.commit()
            conn.close()
            return None

        # Check if active
        if not is_active:
            return None

        return {
            "id": admin_id,
            "email": email,
            "display_name": display_name
        }
    except Exception as e:
        print(f"Error verifying session: {e}")
        return None

def delete_session(session_token: str):
    """Delete a session (logout)."""
    try:
        conn = get_conn(DB_PATH)
        conn.execute("DELETE FROM admin_sessions WHERE session_token = ?", (session_token,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error deleting session: {e}")

# -----------------------------
# Authentication Decorator
# -----------------------------

def session_required(f):
    """Decorator to require valid session authentication."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Skip auth in development mode
        if SKIP_AUTH:
            request.admin = {
                "id": "dev-admin",
                "email": "dev@localhost",
                "display_name": "Development Admin"
            }
            return f(*args, **kwargs)

        session_token = request.headers.get("Authorization")

        if session_token and session_token.startswith("Bearer "):
            session_token = session_token[7:]
        else:
            try:
                payload = request.get_json(force=True, silent=True)
                session_token = payload.get("session_token") if payload else None
            except Exception:
                pass

        if not session_token:
            return jsonify({"error": "Authentication required", "code": "NO_SESSION"}), 401

        admin = verify_session(session_token)
        if not admin:
            return jsonify({"error": "Invalid or expired session", "code": "INVALID_SESSION"}), 401

        request.admin = admin
        return f(*args, **kwargs)

    return wrapper

# -----------------------------
# Authentication Endpoints
# -----------------------------

@app.post("/api/admin/login")
def admin_login():
    """Admin login endpoint."""
    try:
        payload = request.get_json(force=True, silent=False)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    email = (payload.get("email") or "").strip()
    password = payload.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    try:
        conn = get_conn(DB_PATH)
        cur = conn.cursor()

        cur.execute("SELECT * FROM admin_users WHERE email = ?", (email,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return jsonify({"error": "Invalid credentials"}), 401

        admin_id, email, password_hash, display_name, is_active, created_at, last_login_at = row

        if not is_active:
            return jsonify({"error": "Account is disabled"}), 403

        if not verify_password(password, password_hash):
            return jsonify({"error": "Invalid credentials"}), 401

        ip_address = request.remote_addr
        user_agent = request.headers.get("User-Agent", "")

        session_token = create_session(admin_id, ip_address, user_agent)

        if not session_token:
            return jsonify({"error": "Failed to create session"}), 500

        # Update last login
        conn = get_conn(DB_PATH)
        conn.execute("UPDATE admin_users SET last_login_at = ? WHERE id = ?",
                    (datetime.now(timezone.utc).isoformat(), admin_id))
        conn.commit()
        conn.close()

        return jsonify({
            "session_token": session_token,
            "admin": {
                "id": admin_id,
                "email": email,
                "display_name": display_name
            }
        })

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": "Login failed"}), 500

@app.post("/api/admin/logout")
@session_required
def admin_logout():
    """Logout endpoint."""
    session_token = request.headers.get("Authorization", "").replace("Bearer ", "")

    if not session_token:
        try:
            payload = request.get_json(force=True, silent=True)
            session_token = payload.get("session_token") if payload else None
        except Exception:
            pass

    if session_token:
        delete_session(session_token)

    return jsonify({"message": "Logged out successfully"})

@app.get("/api/admin/verify")
@session_required
def verify_admin_session():
    """Verify session validity."""
    return jsonify({
        "valid": True,
        "admin": {
            "id": request.admin["id"],
            "email": request.admin["email"],
            "display_name": request.admin.get("display_name")
        }
    })

# -----------------------------
# Project Management Endpoints
# -----------------------------

@app.get("/api/admin/projects")
def list_projects():
    """List all projects."""
    try:
        conn = get_conn(DB_PATH)
        cur = conn.cursor()

        cur.execute("SELECT * FROM projects ORDER BY created_at DESC")
        rows = cur.fetchall()
        conn.close()

        projects = []
        for row in rows:
            projects.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "created_by": row[3],
                "created_at": row[4]
            })

        return jsonify(projects)
    except Exception as e:
        return jsonify({"error": f"Failed to list projects: {e}"}), 500

@app.post("/api/admin/projects")
@session_required
def create_project():
    """Create a new project."""
    payload = request.get_json()
    name = payload.get("name", "").strip()
    description = payload.get("description", "").strip()

    if not name:
        return jsonify({"error": "Project name is required"}), 400

    try:
        conn = get_conn(DB_PATH)
        cur = conn.cursor()

        project_id = generate_uuid()
        created_at = datetime.now(timezone.utc).isoformat()

        cur.execute("""
            INSERT INTO projects (id, name, description, created_by, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (project_id, name, description, request.admin["email"], created_at))

        conn.commit()
        conn.close()

        return jsonify({
            "id": project_id,
            "name": name,
            "description": description,
            "created_by": request.admin["email"],
            "created_at": created_at
        })
    except Exception as e:
        return jsonify({"error": f"Failed to create project: {e}"}), 500

@app.get("/api/admin/projects/<project_id>/papers")
def list_project_papers(project_id: str):
    """List all papers in a project."""
    try:
        conn = get_conn(DB_PATH)
        cur = conn.cursor()

        cur.execute("SELECT * FROM project_papers WHERE project_id = ? ORDER BY created_at DESC", (project_id,))
        rows = cur.fetchall()
        conn.close()

        papers = []
        for row in rows:
            papers.append({
                "id": row[0],
                "project_id": row[1],
                "doi": row[2],
                "doi_hash": row[3],
                "title": row[4],
                "authors": row[5],
                "year": row[6],
                "pdf_path": row[7],
                "pdf_status": row[8],
                "pdf_error": row[9],
                "created_at": row[10]
            })

        return jsonify(papers)
    except Exception as e:
        return jsonify({"error": f"Failed to list papers: {e}"}), 500

@app.post("/api/admin/projects/<project_id>/papers")
@session_required
def add_paper_to_project(project_id: str):
    """Add a paper to a project."""
    payload = request.get_json()
    doi = payload.get("doi", "").strip()

    if not doi:
        return jsonify({"error": "DOI is required"}), 400

    try:
        conn = get_conn(DB_PATH)
        cur = conn.cursor()

        paper_id = generate_uuid()
        doi_hash = generate_doi_hash(doi)
        created_at = datetime.now(timezone.utc).isoformat()

        cur.execute("""
            INSERT INTO project_papers (id, project_id, doi, doi_hash, pdf_status, created_at)
            VALUES (?, ?, ?, ?, 'pending', ?)
        """, (paper_id, project_id, doi, doi_hash, created_at))

        conn.commit()
        conn.close()

        return jsonify({
            "id": paper_id,
            "project_id": project_id,
            "doi": doi,
            "doi_hash": doi_hash,
            "pdf_status": "pending",
            "created_at": created_at
        })
    except Exception as e:
        return jsonify({"error": f"Failed to add paper: {e}"}), 500

@app.post("/api/admin/projects/<project_id>/fetch")
@session_required
def fetch_project_pdfs(project_id: str):
    """Fetch PDFs for all papers in a project."""
    return jsonify({"message": "PDF fetching not yet implemented", "project_id": project_id})

@app.get("/api/admin/tuples")
def list_tuples():
    """List all tuples."""
    try:
        limit = request.args.get("limit", 100, type=int)

        conn = get_conn(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            SELECT t.*, s.text as sentence_text
            FROM tuples t
            LEFT JOIN sentences s ON t.sentence_id = s.id
            ORDER BY t.created_at DESC
            LIMIT ?
        """, (limit,))

        rows = cur.fetchall()
        conn.close()

        tuples = []
        for row in rows:
            tuples.append({
                "id": row[0],
                "sentence_id": row[1],
                "source_entity_name": row[2],
                "source_entity_attr": row[3],
                "relation_type": row[4],
                "sink_entity_name": row[5],
                "sink_entity_attr": row[6],
                "contributor_email": row[7],
                "created_at": row[8],
                "sentence_text": row[9] if len(row) > 9 else None
            })

        return jsonify(tuples)
    except Exception as e:
        return jsonify({"error": f"Failed to list tuples: {e}"}), 500

if __name__ == "__main__":
    Path(PDF_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    print(f"Starting standalone admin backend on port {ADMIN_PORT}...")
    print(f"Database: {DB_PATH}")
    print(f"PDF Storage: {PDF_STORAGE_PATH}")
    app.run(host="0.0.0.0", port=ADMIN_PORT, debug=True)
