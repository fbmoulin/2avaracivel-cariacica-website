#!/usr/bin/env python3
"""
Simple server startup script for testing
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    print("Starting Flask server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
except Exception as e:
    print(f"Failed to start server: {e}")
    import traceback
    traceback.print_exc()