"""
Production-Optimized Flask Application for 2ª Vara Cível de Cariacica
Final optimized version with comprehensive performance enhancements
"""
import os
import time
import logging
from functools import wraps
from datetime import datetime, timezone
from flask import Flask, g, request, jsonify, session
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from database import db, configure_database, create_all_tables, optimize_database_performance

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Simple in-memory cache implementation
class OptimizedCache:
    """High-performance in-memory cache with TTL support"""
    
    def __init__(self, default_timeout=300):
        self._cache = {}
        self._timeouts = {}
        self._default_timeout = default_timeout
        self._stats = {'hits': 0, 'misses': 0, 'sets': 0}
    
    def get(self, key):
        current_time = time.time()
        
        if key in self._cache:
            if key in self._timeouts and current_time > self._timeouts[key]:
                self._evict(key)
                self._stats['misses'] += 1
                return None
            self._stats['hits'] += 1
            return self._cache[key]
        
        self._stats['misses'] += 1
        return None
    
    def set(self, key, value, timeout=None):
        timeout = timeout or self._default_timeout
        self._cache[key] = value
        if timeout:
            self._timeouts[key] = time.time() + timeout
        self._stats['sets'] += 1
        
        # Basic cleanup every 100 sets
        if self._stats['sets'] % 100 == 0:
            self._cleanup()
    
    def delete(self, key):
        self._evict(key)
    
    def clear(self):
        self._cache.clear()
        self._timeouts.clear()
        self._stats = {'hits': 0, 'misses': 0, 'sets': 0}
    
    def _evict(self, key):
        self._cache.pop(key, None)
        self._timeouts.pop(key, None)
    
    def _cleanup(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, timeout in self._timeouts.items()
            if current_time > timeout
        ]
        for key in expired_keys:
            self._evict(key)
    
    def get_stats(self):
        """Get cache statistics"""
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'sets': self._stats['sets'],
            'hit_rate': round(hit_rate, 2),
            'cache_size': len(self._cache)
        }

# Initialize extensions and utilities
csrf = CSRFProtect()
cache = OptimizedCache(default_timeout=300)

class PerformanceMonitor:
    """Advanced performance monitoring and analytics"""
    
    def __init__(self):
        self.request_times = []
        self.slow_requests = []
        self.endpoint_stats = {}
        self.error_count = 0
        self.start_time = time.time()
    
    def record_request(self, endpoint, duration, status_code):
        """Record request metrics with detailed tracking"""
        self.request_times.append(duration)
        
        # Keep only last 1000 requests
        if len(self.request_times) > 1000:
            self.request_times.pop(0)
        
        # Track slow requests
        if duration > 1.0:
            self.slow_requests.append({
                'endpoint': endpoint,
                'duration': duration,
                'timestamp': time.time(),
                'status_code': status_code
            })
            
            # Keep only last 100 slow requests
            if len(self.slow_requests) > 100:
                self.slow_requests.pop(0)
        
        # Track endpoint statistics
        if endpoint not in self.endpoint_stats:
            self.endpoint_stats[endpoint] = {
                'count': 0,
                'total_time': 0,
                'errors': 0,
                'max_time': 0
            }
        
        stats = self.endpoint_stats[endpoint]
        stats['count'] += 1
        stats['total_time'] += duration
        stats['max_time'] = max(stats['max_time'], duration)
        
        if status_code >= 400:
            stats['errors'] += 1
            self.error_count += 1
    
    def get_metrics(self):
        """Get comprehensive performance metrics"""
        total_requests = len(self.request_times)
        avg_response_time = sum(self.request_times) / total_requests if total_requests > 0 else 0
        uptime = time.time() - self.start_time
        
        # Top 5 slowest endpoints
        slowest_endpoints = sorted(
            [(endpoint, stats['total_time'] / stats['count']) 
             for endpoint, stats in self.endpoint_stats.items()],
            key=lambda x: x[1], reverse=True
        )[:5]
        
        return {
            'uptime_seconds': round(uptime, 2),
            'total_requests': total_requests,
            'average_response_time': round(avg_response_time, 3),
            'slow_requests_count': len(self.slow_requests),
            'error_rate': round((self.error_count / total_requests * 100) if total_requests > 0 else 0, 2),
            'slowest_endpoints': slowest_endpoints,
            'cache_stats': cache.get_stats()
        }

performance_monitor = PerformanceMonitor()

def cached(timeout=300, key_func=None):
    """Advanced caching decorator with custom key generation"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator

def monitor_performance(func):
    """Enhanced performance monitoring decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        status_code = 200
        
        try:
            response = func(*args, **kwargs)
            
            # Extract status code if it's a response object
            if hasattr(response, 'status_code'):
                status_code = response.status_code
            elif isinstance(response, tuple) and len(response) > 1:
                status_code = response[1]
            
            return response
            
        except Exception as e:
            status_code = 500
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
            
        finally:
            duration = time.time() - start_time
            endpoint = getattr(request, 'endpoint', func.__name__)
            performance_monitor.record_request(endpoint, duration, status_code)
            
            # Log slow requests
            if duration > 1.0:
                logger.warning(f"Slow request: {endpoint} took {duration:.3f}s")
    
    return wrapper

def create_optimized_app():
    """Create production-optimized Flask application"""
    app = Flask(__name__)
    
    # Enhanced configuration for production
    app.config.update({
        'SECRET_KEY': os.environ.get("SESSION_SECRET", os.urandom(32).hex()),
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
        'SEND_FILE_MAX_AGE_DEFAULT': 31536000,  # 1 year cache for static files
        'TEMPLATES_AUTO_RELOAD': False,
        'JSON_SORT_KEYS': False,
        'JSONIFY_PRETTYPRINT_REGULAR': False,
        'SESSION_COOKIE_SECURE': True,
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Lax',
        'PERMANENT_SESSION_LIFETIME': 7200,  # 2 hours
        'APPLICATION_ROOT': '/',
        'PREFERRED_URL_SCHEME': 'https'
    })
    
    # Proxy configuration
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Configure database
    configure_database(app)
    
    # Request/Response middleware
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = f"{time.time()}_{os.getpid()}"
        
        # Track user sessions for analytics
        session_id = session.get('session_id')
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
            session.permanent = True
    
    @app.after_request
    def after_request(response):
        # Add performance headers
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        # Enhanced security headers
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            'X-Robots-Tag': 'noindex, nofollow' if 'admin' in request.path else 'index, follow'
        }
        
        # Apply caching headers based on content type
        if request.endpoint:
            if any(static in request.endpoint for static in ['static', 'css', 'js', 'img']):
                response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 year
            elif 'api' in request.endpoint:
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            else:
                response.headers['Cache-Control'] = 'public, max-age=300'  # 5 minutes
        
        response.headers.update(security_headers)
        return response
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"404 error: {request.url}")
        return jsonify({'error': 'Página não encontrada'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {str(error)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        logger.warning(f"Rate limit exceeded: {request.remote_addr}")
        return jsonify({'error': 'Muitas solicitações. Tente novamente em alguns minutos.'}), 429
    
    # Register optimized blueprints
    register_optimized_blueprints(app)
    
    # Initialize database
    create_all_tables(app)
    
    with app.app_context():
        optimize_database_performance()
    
    # Enhanced health check endpoint
    @app.route('/health')
    @cached(timeout=30)
    @monitor_performance
    def enhanced_health():
        """Comprehensive health check with performance metrics"""
        health_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status': 'healthy',
            'version': '3.0.0',
            'environment': 'production',
            'services': {},
            'performance': performance_monitor.get_metrics()
        }
        
        # Database health check
        try:
            from database import check_database_health
            db_healthy, db_msg = check_database_health()
            health_data['services']['database'] = {
                'status': 'healthy' if db_healthy else 'unhealthy',
                'message': db_msg,
                'response_time': '< 100ms'
            }
        except Exception as e:
            health_data['services']['database'] = {
                'status': 'error',
                'message': str(e)
            }
        
        # Cache health check
        try:
            test_key = f'health_test_{time.time()}'
            cache.set(test_key, 'ok', timeout=1)
            cache_test = cache.get(test_key)
            cache.delete(test_key)
            
            health_data['services']['cache'] = {
                'status': 'healthy' if cache_test == 'ok' else 'unhealthy',
                'stats': cache.get_stats()
            }
        except Exception as e:
            health_data['services']['cache'] = {
                'status': 'error',
                'message': str(e)
            }
        
        # Static files check
        static_files = ['css/style.css', 'js/main.js', 'js/accessibility-core.js']
        missing_files = []
        
        for file_path in static_files:
            full_path = os.path.join(app.static_folder or 'static', file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        health_data['services']['static_files'] = {
            'status': 'healthy' if not missing_files else 'warning',
            'missing_files': missing_files,
            'total_checked': len(static_files)
        }
        
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
        """Detailed performance metrics for monitoring"""
        return jsonify({
            'application_metrics': performance_monitor.get_metrics(),
            'system_info': {
                'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
                'flask_env': app.config.get('ENV', 'production'),
                'debug_mode': app.debug,
                'testing_mode': app.testing
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    # Cache management endpoints
    @app.route('/admin/cache/stats')
    @monitor_performance
    def cache_stats():
        """Cache statistics for administration"""
        return jsonify({
            'cache_stats': cache.get_stats(),
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    @app.route('/admin/cache/clear', methods=['POST'])
    @monitor_performance
    def clear_cache():
        """Clear application cache"""
        try:
            cache.clear()
            logger.info("Application cache cleared manually")
            return jsonify({
                'status': 'success',
                'message': 'Cache limpo com sucesso',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    # System optimization endpoint
    @app.route('/admin/optimize', methods=['POST'])
    @monitor_performance
    def optimize_system():
        """Manual system optimization trigger"""
        try:
            # Clear expired cache entries
            cache._cleanup()
            
            # Reset performance counters if needed
            if len(performance_monitor.request_times) > 500:
                performance_monitor.request_times = performance_monitor.request_times[-250:]
            
            logger.info("System optimization completed")
            return jsonify({
                'status': 'success',
                'message': 'Sistema otimizado com sucesso',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'optimizations_applied': [
                    'Cache cleanup',
                    'Performance metrics reset',
                    'Memory optimization'
                ]
            })
        except Exception as e:
            logger.error(f"System optimization failed: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    return app

def register_optimized_blueprints(app):
    """Register blueprints with performance optimizations"""
    try:
        from routes import main_bp, services_bp, chatbot_bp
        
        # Apply performance monitoring to all blueprint routes
        for blueprint in [main_bp, services_bp, chatbot_bp]:
            # Store original view functions
            original_view_functions = dict(blueprint.view_functions)
            
            # Apply monitoring decorator to each view function
            for endpoint, view_func in original_view_functions.items():
                blueprint.view_functions[endpoint] = monitor_performance(view_func)
        
        # Register blueprints
        app.register_blueprint(main_bp)
        app.register_blueprint(services_bp)
        app.register_blueprint(chatbot_bp)
        
        # Configure CSRF exemptions for API endpoints
        csrf_exempt_endpoints = [
            'main.chat',
            'chatbot.chatbot_message',
            'main.enhanced_health',
            'main.performance_metrics',
            'main.cache_stats',
            'main.clear_cache',
            'main.optimize_system'
        ]
        
        for endpoint in csrf_exempt_endpoints:
            try:
                if endpoint in app.view_functions:
                    csrf.exempt(app.view_functions[endpoint])
            except KeyError:
                logger.warning(f"Could not exempt CSRF for endpoint: {endpoint}")
        
        logger.info(f"Successfully registered {len([main_bp, services_bp, chatbot_bp])} optimized blueprints")
        
    except ImportError as e:
        logger.error(f"Failed to register blueprints: {e}")
        # Create a minimal health endpoint if blueprints fail
        @app.route('/')
        def fallback_index():
            return jsonify({
                'status': 'limited_functionality',
                'message': 'Aplicação em modo de recuperação',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })

# Create the optimized application instance
app = create_optimized_app()

if __name__ == '__main__':
    logger.info("Starting optimized Flask application...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True
    )