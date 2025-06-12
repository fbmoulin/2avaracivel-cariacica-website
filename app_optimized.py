"""
Optimized Flask application for 2ª Vara Cível de Cariacica
Production-ready with advanced performance optimizations and clean architecture
"""
import os
import logging
from typing import Optional
from flask import Flask, g, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
import time

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

class Base(DeclarativeBase):
    """Enhanced base class with common fields"""
    pass

# Global database instance
db = SQLAlchemy(model_class=Base)


class ApplicationConfig:
    """Centralized configuration management with environment-based overrides"""
    
    # Database Configuration
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///court_site.db")
    DATABASE_ENGINE_OPTIONS = {
        "pool_recycle": 1800,
        "pool_pre_ping": True,
        "pool_timeout": 45,
        "max_overflow": 30,
        "pool_size": 15,
        "echo": False,
        "pool_reset_on_return": "commit"
    }
    
    # Security Configuration
    SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Performance Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    SEND_FILE_MAX_AGE_DEFAULT = 43200  # 12 hours
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # Application Configuration
    INTEGRATION_TIMEOUT = 30
    CIRCUIT_BREAKER_ENABLED = True
    MONITORING_ENABLED = True
    CACHE_TIMEOUT = 600
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = "gpt-4o"
    OPENAI_MAX_TOKENS = 500
    OPENAI_TEMPERATURE = 0.7
    
    @classmethod
    def get_environment(cls) -> str:
        """Get current environment"""
        return os.environ.get('FLASK_ENV', 'production')
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production"""
        return cls.get_environment() == 'production'


class PerformanceMiddleware:
    """Lightweight performance monitoring middleware"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize performance middleware"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown_request)
    
    def before_request(self):
        """Track request start time"""
        g.start_time = time.time()
        g.request_id = self.generate_request_id()
    
    def after_request(self, response):
        """Log request performance"""
        if hasattr(g, 'start_time'):
            duration = (time.time() - g.start_time) * 1000
            if duration > 1000:  # Only log slow requests
                logging.warning(f"Slow request {g.request_id}: {duration:.2f}ms - {request.method} {request.path}")
        return response
    
    def teardown_request(self, exception):
        """Clean up request context"""
        if exception:
            logging.error(f"Request {getattr(g, 'request_id', 'unknown')} failed: {exception}")
    
    @staticmethod
    def generate_request_id() -> str:
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())[:8]


def create_optimized_app(config_override: Optional[dict] = None) -> Flask:
    """
    Create optimized Flask application with enhanced configuration
    
    Args:
        config_override: Optional configuration overrides
    
    Returns:
        Configured Flask application
    """
    app = Flask(__name__, static_folder='static', template_folder='templates')
    
    # Apply base configuration
    app.config.from_object(ApplicationConfig)
    
    # Apply any overrides
    if config_override:
        app.config.update(config_override)
    
    # Configure proxy handling
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1, x_prefix=1)
    
    # Set secret key
    app.secret_key = app.config['SECRET_KEY']
    
    # Configure database
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config['DATABASE_URL']
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = app.config['DATABASE_ENGINE_OPTIONS']
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize performance monitoring
    PerformanceMiddleware(app)
    
    # Register optimized error handlers
    register_error_handlers(app)
    
    # Initialize services conditionally
    initialize_services(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Create database tables
    with app.app_context():
        import models
        db.create_all()
    
    logging.info(f"Application initialized in {app.config.get('FLASK_ENV', 'production')} mode")
    return app


def register_error_handlers(app: Flask):
    """Register optimized error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        from flask import jsonify
        return jsonify(error="Rate limit exceeded"), 429


def initialize_services(app: Flask):
    """Initialize application services with error handling"""
    
    # Initialize request middleware
    try:
        from utils.request_middleware import RequestMiddleware
        RequestMiddleware(app)
        logging.info("Request middleware initialized")
    except ImportError as e:
        logging.warning(f"Request middleware not available: {e}")
    
    # Initialize integration service
    try:
        from services.integration_service import setup_integration_services
        setup_integration_services()
        logging.info("Integration services initialized")
    except ImportError as e:
        logging.warning(f"Integration services not available: {e}")
    
    # Initialize cache service
    try:
        from services.cache_service_optimized import cache_service
        # Cache service is auto-initialized
        logging.info("Cache service initialized")
    except ImportError as e:
        logging.warning(f"Cache service not available: {e}")
    
    # Initialize monitoring
    if app.config.get('MONITORING_ENABLED'):
        try:
            from error_monitor import setup_flask_error_handlers
            from performance_monitor import setup_performance_monitoring
            setup_flask_error_handlers(app)
            setup_performance_monitoring(app)
            logging.info("Monitoring services initialized")
        except ImportError as e:
            logging.warning(f"Monitoring services not available: {e}")


def register_blueprints(app: Flask):
    """Register application blueprints with error handling"""
    
    # Register main blueprints
    try:
        from routes_optimized_v2 import main_bp, services_bp, chatbot_bp
        app.register_blueprint(main_bp)
        app.register_blueprint(services_bp)
        app.register_blueprint(chatbot_bp)
        logging.info("Main blueprints registered")
    except ImportError as e:
        logging.error(f"Failed to register main blueprints: {e}")
        # Fallback to original routes
        try:
            from routes import main_bp, services_bp, chatbot_bp
            app.register_blueprint(main_bp)
            app.register_blueprint(services_bp)
            app.register_blueprint(chatbot_bp)
            logging.info("Fallback blueprints registered")
        except ImportError as e2:
            logging.error(f"Failed to register fallback blueprints: {e2}")
    
    # Register admin blueprint
    try:
        from routes_admin import admin_bp
        app.register_blueprint(admin_bp)
        logging.info("Admin blueprint registered")
    except ImportError as e:
        logging.warning(f"Admin blueprint not available: {e}")


# Create the optimized application instance
app = create_optimized_app()


if __name__ == '__main__':
    # Development server configuration
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=not ApplicationConfig.is_production(),
        threaded=True
    )