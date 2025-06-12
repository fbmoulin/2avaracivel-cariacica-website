import os
import logging
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from database import db, configure_database, create_all_tables, optimize_database_performance

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

csrf = CSRFProtect()

def create_app():
    # Create the Flask application
    app = Flask(__name__)
    
    # Set secret key from environment variable or use default for development
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    
    # Proxy fix for deployment behind reverse proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Configure database with optimized settings
    configure_database(app)
    
    # Additional configuration for robust integration
    app.config.update({
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,
        'INTEGRATION_TIMEOUT': 30,
        'CIRCUIT_BREAKER_ENABLED': True,
        'MONITORING_ENABLED': True,
        'CACHE_TIMEOUT': 300
    })
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Exempt specific APIs from CSRF protection
    csrf.exempt('chatbot.chatbot_message')
    csrf.exempt('admin.performance_metrics')
    
    # Initialize middleware and monitoring
    try:
        from utils.request_middleware import RequestMiddleware
        RequestMiddleware(app)
        logging.info("Request middleware initialized")
    except ImportError:
        logging.warning("Request middleware not available")
    
    try:
        from services.integration_service import integration_service
        if hasattr(integration_service, 'initialize'):
            integration_service.initialize()
        logging.info("Integration service initialized")
    except (ImportError, AttributeError):
        logging.warning("Integration service not available")
    
    # Register blueprints
    from routes import main_bp, services_bp, chatbot_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(chatbot_bp)
    
    # Register admin blueprint if available
    try:
        from routes_admin import admin_bp
        app.register_blueprint(admin_bp)
        logging.info("Admin dashboard registered")
    except ImportError:
        logging.warning("Admin dashboard not available")
    
    # Create database tables with optimized approach
    create_all_tables(app)
    
    # Apply database performance optimizations
    with app.app_context():
        optimize_database_performance()
    
    # Setup enhanced error monitoring and performance tracking
    try:
        from services.error_handler import setup_integration_monitoring, error_collector
        from error_monitor import setup_flask_error_handlers, start_monitoring
        from performance_monitor import setup_performance_monitoring
        
        setup_flask_error_handlers(app)
        setup_performance_monitoring(app)
        setup_integration_monitoring()
        start_monitoring()
        
        logging.info("Enhanced error monitoring and performance tracking initialized")
    except ImportError:
        logging.warning("Monitoring services not fully available")
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
