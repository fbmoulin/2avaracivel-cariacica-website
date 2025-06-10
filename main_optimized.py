"""
Optimized main application entry point
Production-ready with scaling optimizations
"""
import os
import sys
from datetime import datetime
from flask import render_template
from app_factory import create_app, db

# Import optimized routes
from routes_optimized import main_bp, services_bp, chatbot_bp, admin_bp

def create_production_app():
    """Create optimized application instance"""
    app = create_app()
    
    # Clear any existing blueprints and register optimized ones
    app.blueprints.clear()
    app.register_blueprint(main_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(admin_bp)
    
    # Add missing imports to app factory
    with app.app_context():
        from flask import render_template
        app_factory.render_template = render_template
    
    return app

# Create the optimized app instance
app = create_production_app()

if __name__ == '__main__':
    # Development server with optimizations
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config.get('DEBUG', False),
        threaded=True
    )