#!/usr/bin/env python3
"""
Debug script to verify dropdowns work end-to-end
"""

import os
import sys
import json

print("=" * 60)
print("Dropdown Debug Script")
print("=" * 60)

# Test 1: Database functions
print("\n1. Testing database dropdown functions...")
try:
    from t2t_store import fetch_entity_dropdown_options, fetch_relation_dropdown_options

    db_path = os.getenv("T2T_DB", "t2t.db")

    entities = fetch_entity_dropdown_options(db_path)
    relations = fetch_relation_dropdown_options(db_path)

    print(f"   Entity types ({len(entities)}):")
    for e in entities:
        print(f"     - {e}")

    print(f"\n   Relation types ({len(relations)}):")
    for r in relations:
        print(f"     - {r}")

    if len(entities) == 0 or len(relations) == 0:
        print("\n   ✗ ERROR: Dropdowns are empty!")
        print("   Run: python3 -c \"from t2t_store import init_db; init_db('t2t.db')\"")
        sys.exit(1)
    else:
        print("\n   ✓ Database dropdown functions work")

except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Backend API endpoint simulation
print("\n2. Testing backend API response...")
try:
    from t2t_training_be import app

    with app.test_client() as client:
        response = client.get('/api/choices')

        if response.status_code == 200:
            data = response.get_json()
            print(f"   ✓ API returns: {response.status_code}")
            print(f"   Entity types: {len(data.get('entity_types', []))}")
            print(f"   Relation types: {len(data.get('relation_types', []))}")

            if len(data.get('entity_types', [])) == 0:
                print("\n   ✗ ERROR: API returns empty entity_types")
                sys.exit(1)
            if len(data.get('relation_types', [])) == 0:
                print("\n   ✗ ERROR: API returns empty relation_types")
                sys.exit(1)
        else:
            print(f"   ✗ API error: {response.status_code}")
            print(f"   Response: {response.get_data(as_text=True)}")
            sys.exit(1)

except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Check frontend configuration
print("\n3. Checking frontend configuration...")
try:
    import t2t_training_fe

    api_base = os.getenv("T2T_API_BASE", "http://127.0.0.1:5001")
    api_choices = f"{api_base}/api/choices"

    print(f"   API_BASE: {api_base}")
    print(f"   API_CHOICES: {api_choices}")
    print("   ✓ Frontend configuration loaded")

except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("All checks passed!")
print("=" * 60)
print("\nDropdowns should work if:")
print("  1. Backend is running: python3 t2t_training_be.py")
print("  2. Frontend is running: python3 t2t_training_fe.py")
print("  3. Access: http://localhost:8050")
print("\nIf dropdowns still don't show:")
print("  - Check browser console for errors")
print("  - Check backend logs for /api/choices requests")
print("  - Verify no CORS errors in browser")
