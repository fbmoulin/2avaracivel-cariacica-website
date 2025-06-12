"""
Production-Optimized Main Entry Point
2ª Vara Cível de Cariacica - Enterprise deployment with advanced optimizations
"""

import os
import sys
import logging
import signal
import atexit
from typing import Optional
import multiprocessing
from gunicorn.app.base import BaseApplication

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('court_production.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ProductionGunicornApp(BaseApplication):
    """Optimized Gunicorn application for production deployment"""
    
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()
    
    def load_config(self):
        """Load optimized Gunicorn configuration"""
        # Performance optimizations
        config = {
            'bind': '0.0.0.0:5000',
            'workers': min(multiprocessing.cpu_count() * 2 + 1, 8),
            'worker_class': 'sync',
            'worker_connections': 1000,
            'max_requests': 10000,
            'max_requests_jitter': 1000,
            'timeout': 30,
            'keepalive': 2,
            'preload_app': True,
            
            # Memory management
            'worker_tmp_dir': '/dev/shm',
            'tmp_upload_dir': '/tmp',
            
            # Logging
            'accesslog': 'access.log',
            'errorlog': 'error.log',
            'access_log_format': '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s',
            
            # Security
            'limit_request_line': 4096,
            'limit_request_fields': 100,
            'limit_request_field_size': 8190,
        }
        
        # Override with environment variables
        for key, value in config.items():
            self.cfg.set(key.lower(), value)
    
    def load(self):
        """Load the Flask application"""
        return self.application

def create_optimized_application():
    """Create production-optimized Flask application"""
    try:
        # Import optimized application
        from app_production import create_production_app
        app = create_production_app()
        
        # Initialize performance optimization
        from services.performance_optimizer import performance_manager
        from services.optimized_database import initialize_optimized_database
        
        # Setup database optimization
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            initialize_optimized_database(database_url)
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            performance_manager.profiler.monitoring_active = False
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Cleanup function
        def cleanup():
            logger.info("Application cleanup completed")
        
        atexit.register(cleanup)
        
        logger.info("Production-optimized application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        # Fallback to standard application
        from app_factory import create_app
        return create_app()

def run_development_server():
    """Run development server with optimization monitoring"""
    app = create_optimized_application()
    
    # Enable development optimizations
    os.environ['FLASK_ENV'] = 'development'
    
    logger.info("Starting development server with performance monitoring...")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

def run_production_server():
    """Run production server with Gunicorn"""
    app = create_optimized_application()
    
    # Production configuration
    options = {
        'bind': '0.0.0.0:5000',
        'workers': min(multiprocessing.cpu_count() * 2 + 1, 8),
        'worker_class': 'sync',
        'timeout': 30,
        'keepalive': 2,
        'max_requests': 10000,
        'preload_app': True,
    }
    
    logger.info(f"Starting production server with {options['workers']} workers...")
    ProductionGunicornApp(app, options).run()

def main():
    """Main entry point with environment detection"""
    environment = os.environ.get('FLASK_ENV', 'production')
    
    if environment == 'development':
        run_development_server()
    else:
        run_production_server()

if __name__ == '__main__':
    main()