"""
Production-Optimized Flask Application for 2ª Vara Cível de Cariacica
Enterprise-grade refactoring with advanced performance optimizations
"""

import os
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any
from flask import Flask, request, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.middleware.profiler import ProfilerMiddleware
import threading
import atexit

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    """Enhanced base model with common fields and utilities"""
    pass

class ProductionConfig:
    """Production-optimized configuration with performance tuning"""
    
    # Database optimization
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///court_production.db')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 1800,
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'max_overflow': 50,
        'pool_size': 20,
        'echo': False,
        'pool_reset_on_return': 'commit',
        'connect_args': {
            'options': '-c default_transaction_isolation=read_committed'
        }
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security hardening
    SECRET_KEY = os.environ.get('SESSION_SECRET', os.urandom(32).hex())
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = 7200  # 2 hours
    
    # Performance optimization
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    JSONIFY_PRETTYPRINT_REGULAR = False
    TEMPLATES_AUTO_RELOAD = False
    
    # Caching configuration
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    CACHE_DEFAULT_TIMEOUT = 600
    CACHE_KEY_PREFIX = 'court_'
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = '1000 per hour'
    RATELIMIT_HEADERS_ENABLED = True
    
    # Application settings
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = 'gpt-4o'
    OPENAI_MAX_TOKENS = 500
    OPENAI_TEMPERATURE = 0.7

class PerformanceMonitor:
    """Real-time performance monitoring and optimization"""
    
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'requests_per_second': 0,
            'avg_response_time': 0,
            'memory_usage': 0,
            'cpu_usage': 0,
            'cache_hit_rate': 0,
            'database_connections': 0
        }
        self.request_times = []
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def record_request(self, response_time: float):
        """Record request metrics"""
        with self.lock:
            self.metrics['requests_total'] += 1
            self.request_times.append(response_time)
            
            # Keep only last 1000 requests for rolling average
            if len(self.request_times) > 1000:
                self.request_times = self.request_times[-1000:]
            
            self.metrics['avg_response_time'] = sum(self.request_times) / len(self.request_times)
            
            # Calculate requests per second
            current_time = time.time()
            if current_time - self.last_update >= 1.0:
                self.metrics['requests_per_second'] = len([
                    t for t in self.request_times 
                    if time.time() - t < 1.0
                ])
                self.last_update = current_time
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        try:
            import psutil
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics['memory_usage'] = memory.percent
            
            # CPU usage
            self.metrics['cpu_usage'] = psutil.cpu_percent()
            
            return self.metrics.copy()
        except ImportError:
            return self.metrics.copy()

class DatabaseOptimizer:
    """Database connection and query optimization"""
    
    def __init__(self, app: Flask, db: SQLAlchemy):
        self.app = app
        self.db = db
        self.connection_pool_stats = {
            'active_connections': 0,
            'total_connections': 0,
            'failed_connections': 0
        }
    
    def optimize_connections(self):
        """Apply database connection optimizations"""
        @self.app.before_request
        def before_request():
            g.db_start_time = time.time()
        
        @self.app.after_request
        def after_request(response):
            if hasattr(g, 'db_start_time'):
                db_time = time.time() - g.db_start_time
                if db_time > 0.1:  # Log slow queries
                    logger.warning(f"Slow database operation: {db_time:.3f}s")
            return response
    
    def get_connection_stats(self) -> Dict[str, int]:
        """Get database connection statistics"""
        try:
            engine = self.db.engine
            pool = engine.pool
            
            return {
                'pool_size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'invalid': pool.invalid()
            }
        except Exception as e:
            logger.error(f"Error getting connection stats: {e}")
            return self.connection_pool_stats

class CacheOptimizer:
    """Intelligent caching with performance optimization"""
    
    def __init__(self, cache: Cache):
        self.cache = cache
        self.hit_count = 0
        self.miss_count = 0
        self.lock = threading.Lock()
    
    def get_with_stats(self, key: str) -> Any:
        """Get cached value with hit/miss tracking"""
        value = self.cache.get(key)
        
        with self.lock:
            if value is not None:
                self.hit_count += 1
            else:
                self.miss_count += 1
        
        return value
    
    def set_optimized(self, key: str, value: Any, timeout: Optional[int] = None):
        """Set cache value with optimization"""
        # Use shorter timeout for frequently accessed data
        if not timeout:
            timeout = 300 if 'frequent' in key else 600
        
        return self.cache.set(key, value, timeout=timeout)
    
    def get_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hit_count + self.miss_count
        return (self.hit_count / total * 100) if total > 0 else 0

def create_production_app() -> Flask:
    """Create production-optimized Flask application"""
    app = Flask(__name__)
    app.config.from_object(ProductionConfig)
    
    # Production middleware
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Add profiler in development
    if os.environ.get('FLASK_ENV') == 'development':
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, profile_dir='profiles')
    
    # Initialize extensions
    db = SQLAlchemy(app, model_class=Base)
    cache = Cache(app)
    limiter = Limiter(key_func=get_remote_address)
    limiter.init_app(app)
    
    # Initialize optimizers
    performance_monitor = PerformanceMonitor()
    db_optimizer = DatabaseOptimizer(app, db)
    cache_optimizer = CacheOptimizer(cache)
    
    # Apply optimizations
    db_optimizer.optimize_connections()
    
    # Performance monitoring middleware
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = f"req_{int(time.time())}_{threading.current_thread().ident}"
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            response_time = time.time() - g.start_time
            performance_monitor.record_request(response_time)
            
            # Add performance headers
            response.headers['X-Response-Time'] = f"{response_time:.3f}s"
            response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
        
        return response
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        logger.error(f"Internal error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({'error': 'Rate limit exceeded', 'retry_after': e.retry_after}), 429
    
    # Health and monitoring endpoints
    @app.route('/health/detailed')
    def detailed_health():
        """Comprehensive health check with performance metrics"""
        try:
            # Database health
            db.session.execute('SELECT 1')
            db_healthy = True
        except Exception:
            db_healthy = False
        
        # Cache health
        try:
            cache.set('health_check', 'ok', timeout=1)
            cache_healthy = cache.get('health_check') == 'ok'
        except Exception:
            cache_healthy = False
        
        # Performance metrics
        metrics = performance_monitor.get_system_metrics()
        db_stats = db_optimizer.get_connection_stats()
        cache_hit_rate = cache_optimizer.get_hit_rate()
        
        health_data = {
            'status': 'healthy' if db_healthy and cache_healthy else 'degraded',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'database': {'healthy': db_healthy, 'stats': db_stats},
                'cache': {'healthy': cache_healthy, 'hit_rate': cache_hit_rate},
                'performance': metrics
            },
            'uptime': time.time() - app.start_time
        }
        
        return jsonify(health_data)
    
    @app.route('/metrics')
    def metrics_endpoint():
        """Prometheus-style metrics endpoint"""
        metrics = performance_monitor.get_system_metrics()
        db_stats = db_optimizer.get_connection_stats()
        
        metrics_text = f"""
# HELP court_requests_total Total number of requests
# TYPE court_requests_total counter
court_requests_total {metrics['requests_total']}

# HELP court_request_duration_seconds Average request duration
# TYPE court_request_duration_seconds gauge
court_request_duration_seconds {metrics['avg_response_time']}

# HELP court_memory_usage_percent Memory usage percentage
# TYPE court_memory_usage_percent gauge
court_memory_usage_percent {metrics['memory_usage']}

# HELP court_cpu_usage_percent CPU usage percentage
# TYPE court_cpu_usage_percent gauge
court_cpu_usage_percent {metrics['cpu_usage']}

# HELP court_db_connections_active Active database connections
# TYPE court_db_connections_active gauge
court_db_connections_active {db_stats.get('checked_out', 0)}
"""
        
        from flask import Response
        return Response(metrics_text, mimetype='text/plain')
    
    # Performance optimization endpoints
    @app.route('/admin/optimize')
    @limiter.limit("10 per minute")
    def optimize_performance():
        """Manual performance optimization trigger"""
        try:
            # Clear expired cache entries
            if hasattr(cache.cache, '_cache'):
                expired_keys = []
                for key in cache.cache._cache.keys():
                    if cache.get(key) is None:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    cache.delete(key)
            
            # Database maintenance
            db.session.execute('VACUUM ANALYZE')
            db.session.commit()
            
            return jsonify({
                'status': 'optimization_complete',
                'cleared_cache_keys': len(expired_keys) if 'expired_keys' in locals() else 0,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Optimization error: {e}")
            return jsonify({'error': 'Optimization failed'}), 500
    
    # Register optimized blueprints
    register_optimized_blueprints(app, cache_optimizer)
    
    # Store app start time
    app.start_time = time.time()
    
    # Cleanup on shutdown
    atexit.register(lambda: logger.info("Application shutdown"))
    
    logger.info("Production-optimized application created successfully")
    return app

def register_optimized_blueprints(app: Flask, cache_optimizer: CacheOptimizer):
    """Register blueprints with performance optimizations"""
    try:
        # Import and register main blueprints
        from routes import main_bp, services_bp, chatbot_bp
        from routes_admin import admin_bp
        from routes_error_monitoring import error_bp
        from routes_async_simple import async_simple_bp
        
        # Apply caching decorators to blueprints
        apply_blueprint_caching(main_bp, cache_optimizer)
        apply_blueprint_caching(services_bp, cache_optimizer)
        
        app.register_blueprint(main_bp)
        app.register_blueprint(services_bp)
        app.register_blueprint(chatbot_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(error_bp)
        app.register_blueprint(async_simple_bp)
        
        logger.info("All optimized blueprints registered successfully")
        
    except ImportError as e:
        logger.error(f"Blueprint import error: {e}")
        raise

def apply_blueprint_caching(blueprint, cache_optimizer: CacheOptimizer):
    """Apply intelligent caching to blueprint routes"""
    from functools import wraps
    
    def cache_route(timeout=300):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Generate cache key
                cache_key = f"route_{f.__name__}_{hash(str(args) + str(kwargs))}"
                
                # Check cache
                cached_result = cache_optimizer.get_with_stats(cache_key)
                if cached_result:
                    return cached_result
                
                # Execute function and cache result
                result = f(*args, **kwargs)
                cache_optimizer.set_optimized(cache_key, result, timeout)
                
                return result
            return decorated_function
        return decorator
    
    # Apply caching to static routes
    for endpoint, view_func in blueprint.view_functions.items():
        if endpoint in ['index', 'about', 'faq', 'judge']:
            blueprint.view_functions[endpoint] = cache_route(3600)(view_func)

# Application factory
def create_app():
    """Main application factory"""
    return create_production_app()

if __name__ == '__main__':
    app = create_production_app()
    app.run(host='0.0.0.0', port=5000, debug=False)