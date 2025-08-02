#!/bin/bash
# Kill any existing Python processes on port 5000
lsof -ti:5000 | xargs kill -9 2>/dev/null || true

# Start the Flask server
export FLASK_APP=app.py
export FLASK_ENV=development
export DATABASE_URL=$DATABASE_URL

echo "Starting Flask server..."
python -m flask run --host=0.0.0.0 --port=5000