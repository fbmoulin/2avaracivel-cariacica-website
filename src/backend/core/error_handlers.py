"""
Error Handlers - Modular Backend
Centralized error handling and logging
"""
from flask import jsonify, request, current_app
import logging
import traceback

logger = logging.getLogger(__name__)


def setup_error_handlers(app):
    """Setup application error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle bad request errors"""
        logger.warning(f"Bad request: {request.url} - {error}")
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid request data',
            'status_code': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle unauthorized access"""
        logger.warning(f"Unauthorized access: {request.url}")
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required',
            'status_code': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle forbidden access"""
        logger.warning(f"Forbidden access: {request.url}")
        return jsonify({
            'error': 'Forbidden',
            'message': 'Access denied',
            'status_code': 403
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle not found errors"""
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Not Found',
                'message': 'Resource not found',
                'status_code': 404
            }), 404
        # For non-API routes, could redirect to frontend
        return jsonify({
            'error': 'Not Found',
            'message': 'Page not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        """Handle rate limit exceeded"""
        logger.warning(f"Rate limit exceeded: {request.remote_addr}")
        return jsonify({
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests. Please try again later.',
            'status_code': 429
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle internal server errors"""
        logger.error(f"Internal error: {error}")
        logger.error(traceback.format_exc())
        
        if current_app.debug:
            return jsonify({
                'error': 'Internal Server Error',
                'message': str(error),
                'traceback': traceback.format_exc(),
                'status_code': 500
            }), 500
        
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle unexpected exceptions"""
        logger.error(f"Unhandled exception: {error}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'error': 'Unexpected Error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500