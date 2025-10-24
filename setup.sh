#!/bin/bash

# Setup script for Text2Trait annotation system
# Installs dependencies and prepares the environment

set -e

echo "Setting up Text2Trait annotation system..."
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Error: Python 3 is required"; exit 1; }

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p pdfs
mkdir -p logs

# Initialize database
echo ""
echo "Initializing database..."
python3 -c "from t2t_store import init_db; import os; init_db(os.environ.get('T2T_DB', 't2t.db'))"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo ""
echo "1. Create your first admin account:"
echo "   python3 create_admin.py your@email.com --name 'Your Name'"
echo "   IMPORTANT: Save the generated password!"
echo ""
echo "2. Start all services:"
echo "   ./start_all.sh"
echo ""
echo "3. Access the applications:"
echo "   - Annotation Interface: http://localhost:8050"
echo "   - Admin Panel: http://localhost:8051"
echo ""
echo "For testing without admin features:"
echo "   ./start_simple.sh"
echo ""
echo "See README.md for detailed usage instructions."
echo ""
