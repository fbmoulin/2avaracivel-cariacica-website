"""
Optimized Flask Application for 2ª Vara Cível de Cariacica
Production-ready with enhanced performance, security, and maintainability
"""
import os
import time
import logging
from functools import wraps
from flask import Flask, g, request, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_compress import Compress
from flask_talisman import Talisman
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.contrib.cache import SimpleCache
from database import db, configure_database, create_all_tables, optimize_database_performance

# Configure optimized logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Initialize extensions
csrf = CSRFProtect()
compress = Compress()
cache = SimpleCache()

class PerformanceOptimizer:
    """Performance monitoring and optimization utilities"""
    
    def __init__(self):
        self.request_times = []
        self.slow_queries = []
        
    def record_request_time(self, duration):
        """Record request timing for monitoring"""
        self.request_times.append(duration)
        if len(self.request_times) > 1000:  # Keep last 1000 requests
            self.request_times.pop(0)
            
    def get_average_response_time(self):
        """Calculate average response time"""
        if not self.request_times:
            return 0
        return sum(self.request_times) / len(self.request_times)
    
    def is_slow_request(self, duration):
        """Check if request is considered slow"""
        return duration > 1.0  # 1 second threshold

performance_monitor = PerformanceOptimizer()

def cache_response(timeout=300):
    """Decorator for caching responses"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{request.endpoint}:{request.args}"
            cached_response = cache.get(cache_key)
            
            if cached_response is not None:
                return cached_response
                
            response = func(*args, **kwargs)
            cache.set(cache_key, response, timeout)
            return response
        return wrapper
    return decorator

def monitor_performance(func):
    """Decorator for monitoring request performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        response = func(*args, **kwargs)
        duration = time.time() - start_time
        
        performance_monitor.record_request_time(duration)
        
        if performance_monitor.is_slow_request(duration):
            logging.warning(f"Slow request detected: {request.endpoint} took {duration:.2f}s")
            
        return response
    return wrapper

def create_optimized_app():
    """Create optimized Flask application with enhanced features"""
    app = Flask(__name__)
    
    # Enhanced configuration
    app.config.update({
        'SECRET_KEY': os.environ.get("SESSION_SECRET"),
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
        'SEND_FILE_MAX_AGE_DEFAULT': 31536000,  # 1 year cache for static files
        'TEMPLATES_AUTO_RELOAD': False,  # Disable in production
        'JSON_SORT_KEYS': False,  # Improve JSON performance
        'JSONIFY_PRETTYPRINT_REGULAR': False,  # Reduce response size
    })
    
    # Proxy configuration for deployment
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize extensions
    csrf.init_app(app)
    compress.init_app(app)
    
    # Enhanced security with Talisman
    csp = {
        'default-src': "'self'",
        'script-src': [
            "'self'",
            "'unsafe-inline'",  # Required for inline scripts
            "https://cdnjs.cloudflare.com",
            "https://cdn.jsdelivr.net",
            "https://code.jquery.com"
        ],
        'style-src': [
            "'self'",
            "'unsafe-inline'",  # Required for inline styles
            "https://cdnjs.cloudflare.com",
            "https://fonts.googleapis.com"
        ],
        'font-src': [
            "'self'",
            "https://fonts.gstatic.com",
            "https://cdnjs.cloudflare.com"
        ],
        'img-src': [
            "'self'",
            "data:",
            "https:"
        ],
        'connect-src': "'self'"
    }
    
    Talisman(app, content_security_policy=csp)
    
    # Configure database
    configure_database(app)
    
    # Performance monitoring middleware
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = f"{time.time()}_{os.getpid()}"
        
    @app.after_request
    def after_request(response):
        # Add custom performance headers
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
            
        # Enhanced security headers
        response.headers.update({
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            'Cache-Control': 'no-cache, no-store, must-revalidate' if request.endpoint and 'api' in request.endpoint else 'public, max-age=300'
        })
        
        return response
    
    # Register optimized blueprints
    register_optimized_blueprints(app)
    
    # Database initialization
    create_all_tables(app)
    
    with app.app_context():
        optimize_database_performance()
    
    # Enhanced health check endpoint
    @app.route('/health')
    @cache_response(timeout=30)  # Cache health check for 30 seconds
    def enhanced_health():
        start_time = time.time()
        
        health_data = {
            'timestamp': time.time(),
            'status': 'healthy',
            'version': '2.0.0',
            'environment': 'production',
            'performance': {
                'average_response_time': performance_monitor.get_average_response_time(),
                'recent_requests': len(performance_monitor.request_times)
            },
            'services': {}
        }
        
        # Database health check
        try:
            from database import check_database_health
            db_healthy, db_msg = check_database_health()
            health_data['services']['database'] = {
                'status': 'healthy' if db_healthy else 'unhealthy',
                'message': db_msg
            }
        except Exception as e:
            health_data['services']['database'] = {
                'status': 'error',
                'message': str(e)
            }
        
        # Cache health check
        try:
            cache.set('health_test', 'ok', timeout=1)
            cache_test = cache.get('health_test')
            health_data['services']['cache'] = {
                'status': 'healthy' if cache_test == 'ok' else 'unhealthy',
                'type': 'memory'
            }
        except Exception as e:
            health_data['services']['cache'] = {
                'status': 'error',
                'message': str(e)
            }
        
        # Static files check
        try:
            static_files = [
                'css/style.css',
                'js/main.js',
                'js/accessibility-core.js'
            ]
            missing_files = []
            for file_path in static_files:
                full_path = os.path.join(app.static_folder, file_path)
                if not os.path.exists(full_path):
                    missing_files.append(file_path)
            
            health_data['services']['static_files'] = {
                'status': 'healthy' if not missing_files else 'warning',
                'missing_files': missing_files
            }
        except Exception as e:
            health_data['services']['static_files'] = {
                'status': 'error',
                'message': str(e)
            }
        
        health_data['check_duration'] = time.time() - start_time
        
        # Determine overall status
        service_statuses = [service.get('status') for service in health_data['services'].values()]
        if 'error' in service_statuses or 'unhealthy' in service_statuses:
            health_data['status'] = 'unhealthy'
        elif 'warning' in service_statuses:
            health_data['status'] = 'warning'
        
        return jsonify(health_data)
    
    # Performance metrics endpoint
    @app.route('/metrics')
    @monitor_performance
    def performance_metrics():
        """Endpoint for monitoring application performance"""
        return jsonify({
            'performance': {
                'average_response_time': performance_monitor.get_average_response_time(),
                'total_requests': len(performance_monitor.request_times),
                'slow_requests': len([t for t in performance_monitor.request_times if t > 1.0])
            },
            'system': {
                'timestamp': time.time(),
                'uptime': time.time() - app.config.get('START_TIME', time.time())
            }
        })
    
    # Cache management endpoint
    @app.route('/admin/cache/clear', methods=['POST'])
    def clear_cache():
        """Clear application cache"""
        try:
            cache.clear()
            return jsonify({'status': 'success', 'message': 'Cache cleared successfully'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    # Store start time for uptime calculation
    app.config['START_TIME'] = time.time()
    
    return app

def register_optimized_blueprints(app):
    """Register blueprints with optimizations"""
    try:
        from routes import main_bp, services_bp, chatbot_bp
        
        # Apply performance monitoring to all routes
        for blueprint in [main_bp, services_bp, chatbot_bp]:
            for endpoint, view_func in blueprint.view_functions.items():
                blueprint.view_functions[endpoint] = monitor_performance(view_func)
        
        app.register_blueprint(main_bp)
        app.register_blueprint(services_bp)
        app.register_blueprint(chatbot_bp)
        
        # Exempt API endpoints from CSRF protection
        csrf_exempt_endpoints = [
            'main.chat',
            'chatbot.chatbot_message',
            'main.enhanced_health',
            'main.performance_metrics'
        ]
        
        for endpoint in csrf_exempt_endpoints:
            try:
                csrf.exempt(app.view_functions[endpoint])
            except KeyError:
                logging.warning(f"Could not exempt CSRF for endpoint: {endpoint}")
        
        logging.info("Optimized blueprints registered successfully")
        
    except ImportError as e:
        logging.error(f"Failed to register blueprints: {e}")

# Create the optimized app instance
app = create_optimized_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)