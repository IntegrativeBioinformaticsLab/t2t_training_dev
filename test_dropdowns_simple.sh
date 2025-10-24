#!/bin/bash

# Simple script to test if dropdowns will work

echo "=========================================="
echo "Dropdown Test"
echo "=========================================="

echo ""
echo "1. Checking database file..."
if [ ! -f "t2t.db" ]; then
    echo "   ✗ ERROR: t2t.db not found!"
    exit 1
fi

DB_TYPE=$(file t2t.db | grep -o "SQLite")
if [ -z "$DB_TYPE" ]; then
    echo "   ✗ ERROR: t2t.db is not a SQLite database!"
    echo "   File type: $(file t2t.db)"
    exit 1
else
    echo "   ✓ Database file exists and is SQLite"
fi

echo ""
echo "2. Checking entity types in database..."
ENTITY_COUNT=$(sqlite3 t2t.db "SELECT COUNT(*) FROM entity_types;" 2>&1)
if [ $? -ne 0 ]; then
    echo "   ✗ ERROR: Cannot query entity_types table"
    echo "   $ENTITY_COUNT"
    exit 1
elif [ "$ENTITY_COUNT" -eq 0 ]; then
    echo "   ✗ ERROR: No entity types in database!"
    exit 1
else
    echo "   ✓ Found $ENTITY_COUNT entity types"
    sqlite3 t2t.db "SELECT '     - ' || name FROM entity_types ORDER BY name;"
fi

echo ""
echo "3. Checking relation types in database..."
RELATION_COUNT=$(sqlite3 t2t.db "SELECT COUNT(*) FROM relation_types;" 2>&1)
if [ $? -ne 0 ]; then
    echo "   ✗ ERROR: Cannot query relation_types table"
    echo "   $RELATION_COUNT"
    exit 1
elif [ "$RELATION_COUNT" -eq 0 ]; then
    echo "   ✗ ERROR: No relation types in database!"
    exit 1
else
    echo "   ✓ Found $RELATION_COUNT relation types"
    sqlite3 t2t.db "SELECT '     - ' || name FROM relation_types ORDER BY name LIMIT 5;"
    echo "     ... and more"
fi

echo ""
echo "4. Checking configuration..."
if [ -f ".env" ]; then
    echo "   ✓ .env file exists"

    SKIP_AUTH=$(grep "^T2T_SKIP_AUTH=" .env | cut -d= -f2)
    if [ "$SKIP_AUTH" == "true" ]; then
        echo "   ✓ Skip auth enabled (good for debugging)"
    else
        echo "   ⚠ Skip auth disabled (you'll need to login)"
    fi

    HOST=$(grep "^T2T_HOST=" .env | cut -d= -f2)
    echo "   Host binding: $HOST"

else
    echo "   ⚠ .env file not found (using defaults)"
fi

echo ""
echo "=========================================="
echo "✓ All checks passed!"
echo "=========================================="
echo ""
echo "Dropdowns should work when you:"
echo "  1. Start services: ./start_all.sh"
echo "  2. Open browser: http://localhost:8050"
echo "  3. Enter email and check dropdowns"
echo ""
echo "If dropdowns don't appear:"
echo "  - Check browser console (F12) for errors"
echo "  - Check backend terminal for /api/choices requests"
echo "  - Make sure backend port 5001 is running"
echo ""
