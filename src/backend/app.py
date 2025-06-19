"""
Backend Application Entry Point
2ª Vara Cível de Cariacica - Modular Architecture
"""
import os
from flask import Flask
from flask_cors import CORS
from src.backend.core.config import get_config
from src.backend.core.database import init_database
from src.backend.core.extensions import init_extensions
from src.backend.api import register_api_blueprints
from src.backend.core.middleware import setup_middleware
from src.backend.core.error_handlers import setup_error_handlers


def create_app(config_name=None):
    """Application factory with modular architecture"""
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Enable CORS for frontend communication
    CORS(app, origins=['http://localhost:3000', 'http://localhost:5000'])
    
    # Initialize extensions
    init_extensions(app)
    
    # Initialize database
    init_database(app)
    
    # Setup middleware
    setup_middleware(app)
    
    # Setup error handlers
    setup_error_handlers(app)
    
    # Register API blueprints
    register_api_blueprints(app)
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)