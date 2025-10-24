#!/usr/bin/env python3
"""
Admin Account Creation Script (Standalone - SQLite only)

Generates a secure random password and creates an admin account in SQLite.
The password is displayed once and should be saved securely.
"""

import os
import sys
import secrets
import string
import bcrypt
import uuid
import sqlite3
from datetime import datetime, timezone
from t2t_store import get_conn

DB_PATH = os.getenv("T2T_DB", "t2t.db")

def generate_secure_password(length=20):
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"

    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*()-_=+")
    ]

    password += [secrets.choice(alphabet) for _ in range(length - 4)]

    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)

    return ''.join(password_list)

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_admin_user(email: str, display_name: str = None):
    """Create a new admin user with a secure generated password."""

    try:
        conn = get_conn(DB_PATH)
        cur = conn.cursor()

        # Check if admin already exists
        cur.execute("SELECT email FROM admin_users WHERE email = ?", (email,))
        if cur.fetchone():
            print(f"❌ Admin user with email {email} already exists!")
            print("Use the --reset flag if you need to update the password.")
            conn.close()
            return None

        # Generate secure password
        password = generate_secure_password(24)
        password_hash = hash_password(password)

        # Create admin user
        admin_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        cur.execute("""
            INSERT INTO admin_users (id, email, password_hash, display_name, is_active, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
        """, (admin_id, email, password_hash, display_name or email.split('@')[0], created_at))

        conn.close()

        print("=" * 70)
        print("✓ Admin Account Created Successfully!")
        print("=" * 70)
        print()
        print(f"  Email:        {email}")
        print(f"  Display Name: {display_name or email.split('@')[0]}")
        print(f"  Password:     {password}")
        print()
        print("=" * 70)
        print("⚠️  IMPORTANT: Save this password securely!")
        print("=" * 70)
        print()
        print("This password will NOT be shown again.")
        print("The password is hashed in the database and cannot be retrieved.")
        print()
        print("If you lose this password, you will need to run:")
        print(f"  python3 create_admin_standalone.py --reset {email}")
        print()

        # Save to secure file
        password_file = f".admin_password_{email.replace('@', '_at_').replace('.', '_')}.txt"
        try:
            with open(password_file, 'w') as f:
                f.write(f"Admin Account Credentials\n")
                f.write(f"========================\n")
                f.write(f"Email: {email}\n")
                f.write(f"Password: {password}\n")
                f.write(f"Created: {datetime.now().isoformat()}\n")

            os.chmod(password_file, 0o600)

            print(f"Password also saved to: {password_file}")
            print("(This file is readable only by you)")
            print()
        except Exception as e:
            print(f"Warning: Could not save password to file: {e}")

        return {"email": email, "password": password}

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        return None

def reset_admin_password(email: str):
    """Reset an admin user's password."""

    try:
        conn = get_conn(DB_PATH)
        cur = conn.cursor()

        # Check if admin exists
        cur.execute("SELECT id FROM admin_users WHERE email = ?", (email,))
        row = cur.fetchone()

        if not row:
            print(f"❌ Admin user with email {email} not found!")
            conn.close()
            return None

        # Generate new password
        password = generate_secure_password(24)
        password_hash = hash_password(password)

        # Update password
        cur.execute("UPDATE admin_users SET password_hash = ? WHERE email = ?",
                   (password_hash, email))

        conn.close()

        print("=" * 70)
        print("✓ Admin Password Reset Successfully!")
        print("=" * 70)
        print()
        print(f"  Email:        {email}")
        print(f"  New Password: {password}")
        print()
        print("=" * 70)
        print("⚠️  IMPORTANT: Save this password securely!")
        print("=" * 70)
        print()
        return {"email": email, "password": password}

    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        return None

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create or reset admin users (SQLite version)")
    parser.add_argument("email", help="Admin email address")
    parser.add_argument("--name", help="Display name for the admin", default=None)
    parser.add_argument("--reset", action="store_true", help="Reset password for existing admin")

    args = parser.parse_args()

    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        print("Run the setup script first: ./setup.sh")
        sys.exit(1)

    if args.reset:
        reset_admin_password(args.email)
    else:
        create_admin_user(args.email, args.name)
