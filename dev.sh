#!/bin/bash

# Development runner script

echo "Starting MediaMaster development server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run ./setup-dev.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Using default configuration."
fi

# Set Flask environment variables
export FLASK_APP=run.py
export FLASK_ENV=development
export DATABASE_URL="sqlite://$(pwd)/instance/mediamaster.db"

# Start the development server
echo "Starting server at http://127.0.0.1:8000"
echo "Press Ctrl+C to stop the server"
python run.py
