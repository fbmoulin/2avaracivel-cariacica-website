"""
Optimized Flask Application Factory
Enhanced with performance monitoring, advanced caching, and production-ready configurations
"""
import os
import logging
from datetime import timedelta
from flask import Flask, request, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import time
import psutil
from functools import wraps

# Configure logging with structured format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Performance monitoring decorator
def monitor_performance(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        g.start_time = start_time
        
        try:
            result = f(*args, **kwargs)
            duration = time.time() - start_time
            
            # Log slow requests
            if duration > 1.0:
                logger.warning(f"Slow request: {request.endpoint} took {duration:.2f}s")
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Request failed: {request.endpoint} in {duration:.2f}s - {str(e)}")
            raise
    
    return decorated_function

def create_optimized_app():
    """Create optimized Flask application with enhanced features"""
    app = Flask(__name__)
    
    # Enhanced configuration
    app.config.update({
        'SECRET_KEY': os.environ.get('SESSION_SECRET'),
        'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL'),
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'pool_recycle': 1800,
            'pool_pre_ping': True,
            'pool_timeout': 30,
            'max_overflow': 30,
            'pool_size': 15,
            'pool_reset_on_return': 'commit',
            'echo': False
        },
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        
        # Enhanced caching configuration
        'CACHE_TYPE': 'simple',
        'CACHE_DEFAULT_TIMEOUT': 300,
        'CACHE_THRESHOLD': 1000,
        
        # Rate limiting
        'RATELIMIT_STORAGE_URL': 'memory://',
        'RATELIMIT_DEFAULT': '1000 per hour',
        
        # Session configuration
        'PERMANENT_SESSION_LIFETIME': timedelta(hours=2),
        'SESSION_COOKIE_SECURE': True,
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Lax',
        
        # Performance settings
        'JSON_SORT_KEYS': False,
        'JSONIFY_PRETTYPRINT_REGULAR': False,
        'SEND_FILE_MAX_AGE_DEFAULT': 31536000,  # 1 year cache
        
        # Content security
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
    })
    
    # Initialize extensions
    cache = Cache(app)
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["1000 per hour"]
    )
    limiter.init_app(app)
    
    # Initialize database
    from database import configure_database, create_all_tables
    configure_database(app)
    
    with app.app_context():
        create_all_tables(app)
    
    # Register optimized blueprints
    try:
        from optimized_routes import create_optimized_blueprints
        blueprints = create_optimized_blueprints(cache, limiter)
    except ImportError:
        # Fallback to original routes if optimized not available
        from routes import main_bp, services_bp, chatbot_bp
        blueprints = [main_bp, services_bp, chatbot_bp]
    
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
    
    logger.info("Optimized blueprints registered successfully")
    
    # Enhanced security headers
    @app.after_request
    def add_security_headers(response):
        response.headers.update({
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; img-src 'self' data: https:; font-src 'self' cdn.jsdelivr.net;"
        })
        return response
    
    # Performance monitoring middleware
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        return response
    
    # Health check endpoint
    @app.route('/health')
    @cache.cached(timeout=60)
    def health_check():
        """Optimized health check with system metrics"""
        try:
            from database import check_database_health
            
            # System metrics
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Database health
            db_healthy, db_message = check_database_health()
            
            health_data = {
                'status': 'healthy' if db_healthy else 'degraded',
                'timestamp': time.time(),
                'database': {
                    'status': 'healthy' if db_healthy else 'error',
                    'message': db_message
                },
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': round(memory.available / (1024**3), 2)
                },
                'cache': {
                    'status': 'healthy',
                    'type': app.config['CACHE_TYPE']
                }
            }
            
            status_code = 200 if db_healthy else 503
            return health_data, status_code
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'error',
                'timestamp': time.time(),
                'error': str(e)
            }, 500
    
    # Performance metrics endpoint
    @app.route('/metrics')
    @limiter.limit("10 per minute")
    def metrics():
        """System performance metrics"""
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Process info
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return {
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_total_gb': round(memory.total / (1024**3), 2),
                    'memory_used_gb': round(memory.used / (1024**3), 2),
                    'memory_percent': memory.percent
                },
                'process': {
                    'memory_rss_mb': round(process_memory.rss / (1024**2), 2),
                    'memory_vms_mb': round(process_memory.vms / (1024**2), 2),
                    'cpu_percent': process.cpu_percent()
                },
                'cache': {
                    'type': app.config['CACHE_TYPE'],
                    'timeout': app.config['CACHE_DEFAULT_TIMEOUT']
                }
            }
            
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return {'error': str(e)}, 500
    
    logger.info("Optimized Flask application created successfully")
    return app

if __name__ == '__main__':
    app = create_optimized_app()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)