"""
Middleware Configuration - Modular Backend
Request/response middleware for security and performance
"""
from flask import request, g
import time
import logging

logger = logging.getLogger(__name__)


def setup_middleware(app):
    """Setup application middleware"""
    
    @app.before_request
    def before_request():
        """Pre-request processing"""
        g.start_time = time.time()
        
        # Security headers
        if request.endpoint and not request.endpoint.startswith('static'):
            # Add request ID for tracking
            g.request_id = request.headers.get('X-Request-ID', 
                                             f"{int(time.time() * 1000)}")
    
    @app.after_request
    def after_request(response):
        """Post-request processing"""
        # Add security headers
        security_headers = app.config.get('SECURITY_HEADERS', {})
        for header, value in security_headers.items():
            response.headers[header] = value
        
        # Add CORS headers
        if request.origin:
            response.headers['Access-Control-Allow-Origin'] = request.origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        # Performance logging
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            if duration > 1.0:  # Log slow requests
                logger.warning(f"Slow request: {request.endpoint} took {duration:.2f}s")
        
        return response
    
    @app.teardown_appcontext
    def close_db(error):
        """Close database connections"""
        if error:
            logger.error(f"Request error: {error}")