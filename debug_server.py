#!/usr/bin/env python3
"""
Debug server test for 2ª Vara Cível de Cariacica
Tests basic Flask functionality and identifies startup issues
"""

import os
import sys
from flask import Flask, render_template

def create_debug_app():
    """Create minimal Flask app for debugging"""
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "debug-key")
    
    @app.route('/')
    def index():
        return """
        <html>
        <head><title>2ª Vara Cível - Debug</title></head>
        <body>
        <h1>Debug Test - Server Working</h1>
        <p>Location text should be visible with proper contrast.</p>
        <div style="background: white; color: #333; padding: 20px; border: 2px solid #ccc;">
            <h3 style="color: #2c5aa0;">Location Information</h3>
            <p><strong>2ª Vara Cível de Cariacica</strong><br>
            Rua Expedito Garcia, s/n<br>
            Centro, Cariacica - ES</p>
        </div>
        <button id="accessibility-toggle" style="position: fixed; bottom: 80px; right: 20px; background: #2c5aa0; color: white; padding: 12px 20px; border: none; border-radius: 25px;">
            Acessibilidade
        </button>
        </body>
        </html>
        """
    
    @app.route('/health')
    def health():
        return {'status': 'ok', 'message': 'Debug server running'}
    
    return app

if __name__ == '__main__':
    app = create_debug_app()
    print("Starting debug server on port 5000...")
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)