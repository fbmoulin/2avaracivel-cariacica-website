"""
Health Check API - Modular Backend
System health monitoring and diagnostics
"""
from flask import Blueprint, jsonify, current_app
from src.backend.core.database import check_database_health
from src.backend.core.extensions import cache
import logging
import time
import psutil

logger = logging.getLogger(__name__)
health_api = Blueprint('health', __name__)


@health_api.route('/', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'court-backend',
        'timestamp': time.time()
    })


@health_api.route('/detailed', methods=['GET'])
def detailed_health():
    """Detailed health check with system metrics"""
    try:
        # Database health
        db_healthy = check_database_health()
        
        # Cache health
        cache_healthy = True
        try:
            cache.set('health_check', 'ok', timeout=1)
            cache_healthy = cache.get('health_check') == 'ok'
        except Exception:
            cache_healthy = False
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status = {
            'status': 'healthy' if db_healthy and cache_healthy else 'degraded',
            'service': 'court-backend',
            'timestamp': time.time(),
            'components': {
                'database': 'healthy' if db_healthy else 'unhealthy',
                'cache': 'healthy' if cache_healthy else 'unhealthy',
            },
            'system_metrics': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2)
            },
            'version': current_app.config.get('API_VERSION', 'v1')
        }
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 503


@health_api.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus-style metrics endpoint"""
    try:
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        metrics_text = f"""# HELP court_backend_cpu_percent CPU usage percentage
# TYPE court_backend_cpu_percent gauge
court_backend_cpu_percent {cpu_percent}

# HELP court_backend_memory_percent Memory usage percentage
# TYPE court_backend_memory_percent gauge
court_backend_memory_percent {memory.percent}

# HELP court_backend_database_status Database connection status
# TYPE court_backend_database_status gauge
court_backend_database_status {1 if check_database_health() else 0}
"""
        
        return metrics_text, 200, {'Content-Type': 'text/plain'}
        
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        return f"# Error collecting metrics: {e}", 500, {'Content-Type': 'text/plain'}