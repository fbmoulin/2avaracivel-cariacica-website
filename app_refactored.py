"""
Refactored Flask Application for 2ª Vara Cível de Cariacica
Optimized for performance, security, and maintainability
"""
import os
import logging
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from database import configure_database, create_all_tables, optimize_database_performance

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize CSRF protection
csrf = CSRFProtect()

def create_app(config_name='production'):
    """
    Application factory pattern for creating Flask app instances
    
    Args:
        config_name: Configuration environment (production, development, testing)
    
    Returns:
        Configured Flask application instance
    """
    # Create Flask application
    app = Flask(__name__)
    
    # Load configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    
    # Security configuration
    app.config.update({
        'SESSION_COOKIE_SECURE': True,
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Lax',
        'PERMANENT_SESSION_LIFETIME': 3600,  # 1 hour
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max file size
        'CACHE_TIMEOUT': 300,  # 5 minutes default cache
        'WTF_CSRF_TIME_LIMIT': None,  # CSRF tokens don't expire
        'WTF_CSRF_SSL_STRICT': False  # Allow HTTP in development
    })
    
    # Configure proxy fix for deployment behind reverse proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize database with optimized settings
    configure_database(app)
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Configure security headers
    configure_security_headers(app)
    
    # Create database tables
    create_all_tables(app)
    
    # Apply database optimizations
    with app.app_context():
        optimize_database_performance()
    
    # Register health check endpoint
    register_health_endpoint(app)
    
    logger.info(f"Application initialized in {config_name} mode")
    
    return app

def register_error_handlers(app):
    """Register error handlers for common HTTP errors"""
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Access forbidden'}, 403

def register_blueprints(app):
    """Register application blueprints with error handling"""
    try:
        from routes import main_bp, services_bp, chatbot_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(services_bp)
        app.register_blueprint(chatbot_bp)
        
        # Exempt chatbot endpoints from CSRF protection
        csrf_exempt_endpoints = [
            'main.chat',
            'chatbot.chatbot_message'
        ]
        
        for endpoint in csrf_exempt_endpoints:
            try:
                csrf.exempt(app.view_functions[endpoint])
                logger.info(f"CSRF exempted for endpoint: {endpoint}")
            except KeyError:
                logger.warning(f"Could not exempt CSRF for endpoint: {endpoint}")
        
        logger.info("Blueprints registered successfully")
        
    except ImportError as e:
        logger.error(f"Failed to register blueprints: {e}")
        raise

def configure_security_headers(app):
    """Configure comprehensive security headers"""
    
    @app.after_request
    def add_security_headers(response):
        # Core security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.openai.com"
        )
        response.headers['Content-Security-Policy'] = csp
        
        # Additional security headers
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'
        
        return response

def register_health_endpoint(app):
    """Register health check endpoint with comprehensive status checks"""
    
    @app.route('/health')
    def health():
        import time
        from services.health_monitor import HealthMonitor
        
        monitor = HealthMonitor()
        health_report = monitor.get_comprehensive_health_report()
        
        return health_report

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Production configuration
    if os.environ.get('FLASK_ENV') == 'production':
        logger.info("Starting in production mode")
        # In production, use gunicorn instead
    else:
        # Development mode
        logger.info("Starting in development mode")
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Disable reloader to prevent issues
        )