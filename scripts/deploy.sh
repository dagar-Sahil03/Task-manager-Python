#!/bin/bash

# Deployment script for Task Tracker application
# This script starts the application using Gunicorn

set -e  # Exit on error

echo "========================================="
echo "Task Tracker - Deployment Script"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if Gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "Error: Gunicorn is not installed. Installing..."
    pip install gunicorn
fi

# Load environment variables
if [ -f ".env" ]; then
    echo "Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Warning: .env file not found. Using default values."
fi

# Check if database exists
if [ ! -f "${DATABASE_PATH:-database/tasks.db}" ]; then
    echo "Initializing database..."
    python3 -c "from models import TaskModel; TaskModel()"
    echo "✓ Database initialized"
fi

# Create logs directory if it doesn't exist
mkdir -p logs 2>/dev/null || true

# Start Gunicorn
echo ""
echo "Starting Gunicorn server..."
echo ""

# Use gunicorn_config.py if it exists, otherwise use defaults
if [ -f "gunicorn_config.py" ]; then
    gunicorn -c gunicorn_config.py wsgi:app
else
    # Default configuration
    gunicorn \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --timeout 30 \
        --access-logfile - \
        --error-logfile - \
        wsgi:app
fi

