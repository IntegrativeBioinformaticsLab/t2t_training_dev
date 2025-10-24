#!/usr/bin/env python3
"""
Test script to verify all components work
"""

import os
import sys

print("=" * 60)
print("Text2Trait System Test")
print("=" * 60)

# Test 1: Database
print("\n1. Testing database...")
try:
    from t2t_store import init_db, fetch_entity_dropdown_options, fetch_relation_dropdown_options
    db_path = 't2t.db'

    if not os.path.exists(db_path):
        print(f"   Creating database: {db_path}")
        init_db(db_path)

    entities = fetch_entity_dropdown_options(db_path)
    relations = fetch_relation_dropdown_options(db_path)

    print(f"   ✓ Entity types: {len(entities)} ({', '.join(entities[:3])}...)")
    print(f"   ✓ Relation types: {len(relations)} ({', '.join(relations[:3])}...)")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Test 2: Backend imports
print("\n2. Testing backend imports...")
try:
    import t2t_training_be
    print("   ✓ Main backend imports")
except Exception as e:
    print(f"   ✗ Error: {e}")

try:
    import t2t_admin_be
    print("   ✓ Admin backend imports")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Frontend imports
print("\n3. Testing frontend imports...")
try:
    import t2t_training_fe
    print("   ✓ Main frontend imports")
except Exception as e:
    print(f"   ✗ Error: {e}")

try:
    import t2t_admin_fe
    print("   ✓ Admin frontend imports")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Check Flask apps
print("\n4. Checking Flask configuration...")
try:
    from t2t_training_be import app as main_app
    print(f"   ✓ Main backend app configured")
    print(f"     Routes: {len(main_app.url_map._rules)} endpoints")
except Exception as e:
    print(f"   ✗ Error: {e}")

try:
    from t2t_admin_be import app as admin_app
    print(f"   ✓ Admin backend app configured")
    print(f"     Routes: {len(admin_app.url_map._rules)} endpoints")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 5: Datetime fixes
print("\n5. Testing datetime handling...")
try:
    from datetime import datetime, timezone, timedelta
    expires = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    expires_dt = datetime.fromisoformat(expires)
    now = datetime.now(timezone.utc)
    is_expired = expires_dt < now
    print(f"   ✓ Timezone-aware datetime: {not is_expired}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("System test complete!")
print("=" * 60)
print("\nTo start the application:")
print("  ./start_all.sh")
print("\nAccess points:")
print("  - Annotation: http://localhost:8050")
print("  - Admin Panel: http://localhost:8051")
