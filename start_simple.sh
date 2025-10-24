#!/bin/bash

# Start only the basic annotation system (no admin panel, no project management)
# Simple mode - annotation interface only (no admin panel)
# Usage: ./start_simple.sh

set -e

echo "Starting Simple Annotation System (SQLite only)..."
echo ""

# Detect Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "Error: Python not found!"
    exit 1
fi

echo "Using Python: $PYTHON_CMD"

# Load environment variables
if [ -f .env ]; then
    echo "Loading .env file..."
    set -a
    source .env
    set +a
    echo "✓ Environment loaded"
else
    echo "Warning: .env file not found!"
fi

echo ""
echo "Starting services..."
echo ""

# Start main backend (SQLite only)
echo "Starting main backend (port $T2T_BACKEND_PORT)..."
$PYTHON_CMD t2t_training_be.py &
MAIN_BE_PID=$!
echo "  Backend PID: $MAIN_BE_PID"

sleep 3

# Check if backend is running
if ps -p $MAIN_BE_PID > /dev/null; then
    echo "  ✓ Backend started successfully"
else
    echo "  ✗ Backend failed to start"
    exit 1
fi

# Start main frontend
echo ""
echo "Starting main frontend (port $T2T_FRONTEND_PORT)..."
$PYTHON_CMD t2t_training_fe.py &
MAIN_FE_PID=$!
echo "  Frontend PID: $MAIN_FE_PID"

sleep 3

# Check if frontend is running
if ps -p $MAIN_FE_PID > /dev/null; then
    echo "  ✓ Frontend started successfully"
else
    echo "  ✗ Frontend failed to start"
    kill $MAIN_BE_PID 2>/dev/null
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Simple annotation system running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Annotation Interface: http://localhost:$T2T_FRONTEND_PORT"
echo ""
echo "  Backend PID:          $MAIN_BE_PID"
echo "  Frontend PID:         $MAIN_FE_PID"
echo ""
echo "Features available:"
echo "  ✓ Manual DOI entry"
echo "  ✓ Sentence and tuple annotation"
echo "  ✓ Browse saved annotations"
echo ""
echo "Features NOT available (require admin panel):"
echo "  ✗ Project management"
echo "  ✗ PDF batch fetching"
echo "  ✗ Project/paper dropdowns"
echo ""
echo "Press Ctrl+C to stop services"
echo ""

# Wait for Ctrl+C
trap "echo 'Stopping services...'; kill $MAIN_BE_PID $MAIN_FE_PID 2>/dev/null; exit 0" INT TERM

# Wait for processes
wait
