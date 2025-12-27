#!/bin/bash

# Setup script for Task Tracker application on Linux
# This script sets up the environment, installs dependencies, and prepares the application

set -e  # Exit on error

echo "========================================="
echo "Task Tracker - Setup Script"
echo "========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python version: $(python3 --version)"

# Check Python version (3.8+)
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "Error: Python 3.8 or higher is required."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "Error: requirements.txt not found!"
    exit 1
fi

# Create database directory if it doesn't exist
if [ ! -d "database" ]; then
    echo ""
    echo "Creating database directory..."
    mkdir -p database
    echo "✓ Database directory created"
fi

# Set up environment variables
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cat > .env << EOF
# Flask Configuration
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
FLASK_ENV=production
FLASK_DEBUG=False

# Database Configuration
DATABASE_PATH=database/tasks.db

# Gunicorn Configuration (optional)
GUNICORN_BIND=0.0.0.0:8000
GUNICORN_WORKERS=4
GUNICORN_LOG_LEVEL=info
EOF
    echo "✓ .env file created with default values"
    echo "  Please review and update .env file if needed"
else
    echo "✓ .env file already exists"
fi

# Initialize database
echo ""
echo "Initializing database..."
python3 -c "from models import TaskModel; TaskModel()"
echo "✓ Database initialized"

# Make scripts executable
echo ""
echo "Setting executable permissions on scripts..."
chmod +x scripts/*.sh 2>/dev/null || true
echo "✓ Scripts made executable"

echo ""
echo "========================================="
echo "Setup completed successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. (Optional) Seed database: python3 seed_data.py"
echo "3. Run development server: python3 app.py"
echo "   OR"
echo "3. Deploy with Gunicorn: ./scripts/deploy.sh"
echo ""

