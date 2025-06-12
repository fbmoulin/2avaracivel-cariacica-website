"""
Application factory for 2ª Vara Cível de Cariacica
Refactored for scalability and maintainability
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from config import get_config
from services.integration_service import setup_integration_services, integration_service
from utils.request_middleware import RequestMiddleware
from utils.workflow_optimizer import start_workflow_engine
from utils.error_logger import setup_error_logging


class Base(DeclarativeBase):
    pass


# Initialize extensions
db = SQLAlchemy(model_class=Base)
cache = Cache()
limiter = Limiter(
    get_remote_address,
    default_limits=["1000 per hour"]
)


def create_app(config_name=None):
    """Application factory pattern for better scalability"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Initialize extensions
    from models import db
    db.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    
    # Initialize scheduler service for automated reports
    try:
        from services.scheduler_service import scheduler_service
        scheduler_service.start()
        app.logger.info("Automated email reporting service started")
    except Exception as e:
        app.logger.error(f"Failed to start scheduler service: {e}")
    
    # Configure proxy handling for production
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup error handlers
    setup_error_handlers(app)
    
    # Create database tables
    with app.app_context():
        import models
        db.create_all()
    
    # Setup monitoring
    setup_monitoring(app)
    
    # Initialize integration services
    setup_integration_services()
    
    # Setup enhanced error logging
    setup_error_logging(app)
    
    # Setup request middleware
    request_middleware = RequestMiddleware()
    request_middleware.init_app(app)
    
    # Start workflow engine
    start_workflow_engine()
    
    # Setup graceful shutdown handler
    import atexit
    atexit.register(integration_service.graceful_shutdown)
    atexit.register(stop_workflow_engine)
    
    return app


def setup_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        # File logging for production
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/court_app.log',
            maxBytes=app.config.get('LOG_MAX_SIZE', 10240000),
            backupCount=app.config.get('LOG_BACKUP_COUNT', 10)
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
        app.logger.info('Court application startup')


def register_blueprints(app):
    """Register application blueprints"""
    try:
        from routes_optimized import main_bp, services_bp, chatbot_bp, admin_bp
        from routes_error_monitoring import error_bp
        from routes_async_simple import async_simple_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(services_bp)
        app.register_blueprint(chatbot_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(error_bp)
        app.register_blueprint(async_simple_bp)
        
        app.logger.info("All blueprints registered successfully")
    except ImportError as e:
        app.logger.error(f"Blueprint import error: {e}")
        # Fallback to original routes if optimized not available
        from routes import main_bp, services_bp, chatbot_bp
        from routes_error_monitoring import error_bp
        from routes_async_simple import async_simple_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(services_bp)
        app.register_blueprint(chatbot_bp)
        app.register_blueprint(error_bp)
        app.register_blueprint(async_simple_bp)


def setup_error_handlers(app):
    """Setup centralized error handling"""
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f'404 error: {error}')
        try:
            return render_template('errors/404.html'), 404
        except:
            return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'500 error: {error}')
        db.session.rollback()
        try:
            return render_template('errors/500.html'), 500
        except:
            return render_template('500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f'403 error: {error}')
        try:
            return render_template('errors/403.html'), 403
        except:
            return "403 - Forbidden", 403
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        app.logger.warning(f'Rate limit exceeded: {e}')
        try:
            return render_template('errors/429.html'), 429
        except:
            return "429 - Too Many Requests", 429


def setup_monitoring(app):
    """Setup comprehensive application monitoring with auto-recovery"""
    try:
        from error_monitor import setup_flask_error_handlers, start_monitoring
        setup_flask_error_handlers(app)
        start_monitoring()
    except ImportError:
        app.logger.warning('Error monitoring not available')
    
    # Initialize robust integration monitoring
    try:
        from services.robust_integration_monitor import integration_monitor
        integration_monitor.start_monitoring(check_interval=30)
        app.logger.info('Robust integration monitoring started')
    except Exception as e:
        app.logger.warning(f'Robust integration monitoring failed to start: {e}')
    
    # Enhanced health check endpoint
    @app.route('/health')
    def health_check():
        """Comprehensive health check endpoint"""
        from datetime import datetime
        try:
            from services.robust_integration_monitor import integration_monitor
            health_report = integration_monitor.get_system_health_report()
            return health_report
        except Exception as e:
            app.logger.error(f'Health check failed: {e}')
            return {
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }


# For backwards compatibility
app = create_app()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='development',
                       help='Configuration to use (development, production, testing)')
    args = parser.parse_args()
    
    app = create_app(args.config)
    app.run(host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', False))