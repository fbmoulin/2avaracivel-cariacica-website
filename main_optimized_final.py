"""
Final Optimized Production Deployment
2ª Vara Cível de Cariacica - Streamlined for Maximum Performance
"""

import os
import sys
import multiprocessing
from gunicorn.app.base import BaseApplication

class OptimizedGunicornApp(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            'bind': '0.0.0.0:5000',
            'workers': min(multiprocessing.cpu_count() * 2 + 1, 6),
            'worker_class': 'sync',
            'worker_connections': 1000,
            'max_requests': 5000,
            'max_requests_jitter': 500,
            'timeout': 30,
            'keepalive': 2,
            'preload_app': True,
            'worker_tmp_dir': '/dev/shm',
            'access_log_format': '%(h)s "%(r)s" %(s)s %(b)s %(D)s',
            'limit_request_line': 4096,
            'limit_request_fields': 100,
        }
        
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

def create_production_app():
    try:
        from app_compiled import app
        return app
    except ImportError:
        from app_production import create_production_app
        return create_production_app()
    except ImportError:
        from app import create_app
        return create_app()

def main():
    app = create_production_app()
    
    if os.environ.get('FLASK_ENV') == 'development':
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        OptimizedGunicornApp(app).run()

if __name__ == '__main__':
    main()