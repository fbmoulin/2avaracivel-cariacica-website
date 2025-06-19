"""
API Blueprint Registration - Modular Backend
Centralized API route management
"""
from flask import Blueprint
from src.backend.api.contact import contact_api
from src.backend.api.process import process_api
from src.backend.api.chatbot import chatbot_api
from src.backend.api.scheduling import scheduling_api
from src.backend.api.health import health_api


def register_api_blueprints(app):
    """Register all API blueprints with the Flask app"""
    
    # Create main API blueprint
    api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
    
    # Register sub-blueprints
    api_v1.register_blueprint(contact_api, url_prefix='/contact')
    api_v1.register_blueprint(process_api, url_prefix='/process')
    api_v1.register_blueprint(chatbot_api, url_prefix='/chatbot')
    api_v1.register_blueprint(scheduling_api, url_prefix='/scheduling')
    api_v1.register_blueprint(health_api, url_prefix='/health')
    
    # Register main API blueprint with app
    app.register_blueprint(api_v1)
    
    # Health check endpoint at root level
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'court-backend'}