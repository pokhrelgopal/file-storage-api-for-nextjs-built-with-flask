#!/usr/bin/env fish

# Development runner script for Fish shell

echo "Starting MediaMaster development server..."

# Check if virtual environment exists
if not test -d "venv"
    echo "Virtual environment not found. Please run ./setup-dev.fish first"
    exit 1
end

# Activate virtual environment
source venv/bin/activate.fish

# Check if .env file exists
if not test -f ".env"
    echo "Warning: .env file not found. Using default configuration."
end

# Set Flask environment variables
set -x FLASK_APP run.py
set -x FLASK_ENV development
set -x DATABASE_URL "sqlite:///"(pwd)"/instance/mediamaster.db"

# Start the development server
echo "Starting server at http://127.0.0.1:8000"
echo "Press Ctrl+C to stop the server"
python run.py
