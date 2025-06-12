"""
Request middleware for performance monitoring, security, and stability
Implements comprehensive request lifecycle management
"""
import time
import logging
import json
from datetime import datetime
from flask import request, g, current_app
from functools import wraps
from services.integration_service import integration_service
import uuid


class RequestMiddleware:
    """Middleware for request processing and monitoring"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown_request)
        
        # Register error handlers
        app.errorhandler(429)(self.handle_rate_limit)
        app.errorhandler(500)(self.handle_server_error)
    
    def before_request(self):
        """Execute before each request"""
        # Generate unique request ID
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()
        
        # Log request start
        current_app.logger.info(
            f"REQUEST_START {g.request_id} {request.method} {request.path} "
            f"from {request.remote_addr}"
        )
        
        # Security headers validation
        self._validate_security_headers()
        
        # Request size validation
        if request.content_length and request.content_length > current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024):
            current_app.logger.warning(f"Large request detected: {request.content_length} bytes")
    
    def after_request(self, response):
        """Execute after each request"""
        if hasattr(g, 'start_time'):
            duration = (time.time() - g.start_time) * 1000  # Convert to milliseconds
            
            # Record metrics
            integration_service.health_monitor.record_request(
                success=(200 <= response.status_code < 400),
                response_time=duration
            )
            
            # Add performance headers
            response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
            response.headers['X-Response-Time'] = f"{duration:.2f}ms"
            
            # Log request completion
            current_app.logger.info(
                f"REQUEST_END {getattr(g, 'request_id', 'unknown')} "
                f"{response.status_code} {duration:.2f}ms"
            )
            
            # Warn on slow requests
            if duration > 2000:  # 2 seconds
                current_app.logger.warning(
                    f"SLOW_REQUEST {getattr(g, 'request_id', 'unknown')} "
                    f"{request.path} took {duration:.2f}ms"
                )
        
        # Security headers
        self._add_security_headers(response)
        
        return response
    
    def teardown_request(self, exception):
        """Clean up after request"""
        if exception:
            current_app.logger.error(
                f"REQUEST_EXCEPTION {getattr(g, 'request_id', 'unknown')} "
                f"{type(exception).__name__}: {str(exception)}"
            )
    
    def _validate_security_headers(self):
        """Validate security-related request headers"""
        # Check for suspicious headers
        suspicious_headers = ['x-forwarded-host', 'x-original-url', 'x-rewrite-url']
        for header in suspicious_headers:
            if header in request.headers:
                current_app.logger.warning(
                    f"Suspicious header detected: {header} = {request.headers[header]}"
                )
    
    def _add_security_headers(self, response):
        """Add security headers to response"""
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; img-src 'self' data: https:; font-src 'self' cdn.jsdelivr.net;",
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response
    
    def handle_rate_limit(self, error):
        """Handle rate limit exceeded errors"""
        current_app.logger.warning(
            f"RATE_LIMIT_EXCEEDED {getattr(g, 'request_id', 'unknown')} "
            f"{request.remote_addr} {request.path}"
        )
        return {
            'error': 'Taxa de requisições excedida',
            'message': 'Aguarde alguns momentos antes de tentar novamente',
            'retry_after': getattr(error, 'retry_after', 60)
        }, 429
    
    def handle_server_error(self, error):
        """Handle internal server errors"""
        current_app.logger.error(
            f"SERVER_ERROR {getattr(g, 'request_id', 'unknown')} "
            f"{type(error).__name__}: {str(error)}"
        )
        return {
            'error': 'Erro interno do servidor',
            'message': 'Ocorreu um erro interno. Tente novamente mais tarde.',
            'request_id': getattr(g, 'request_id', 'unknown')
        }, 500


def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            
            if duration > 1000:  # Log functions taking more than 1 second
                current_app.logger.warning(
                    f"SLOW_FUNCTION {func.__name__} took {duration:.2f}ms"
                )
            
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            current_app.logger.error(
                f"FUNCTION_ERROR {func.__name__} failed after {duration:.2f}ms: {str(e)}"
            )
            raise
    return wrapper


def validate_request_data(required_fields=None, optional_fields=None):
    """Decorator to validate request data"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data or not data[field]]
                if missing_fields:
                    return {
                        'error': 'Campos obrigatórios ausentes',
                        'missing_fields': missing_fields
                    }, 400
            
            # Add validated data to kwargs
            kwargs['validated_data'] = data
            return func(*args, **kwargs)
        return wrapper
    return decorator


def cache_response(timeout=300, key_prefix='view'):
    """Decorator for response caching"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{request.path}:{request.query_string.decode()}"
            
            # Try to get from cache
            try:
                from app_factory import cache
                cached_response = cache.get(cache_key)
                if cached_response:
                    current_app.logger.debug(f"Cache hit for {cache_key}")
                    return cached_response
            except Exception as e:
                current_app.logger.warning(f"Cache get failed: {e}")
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            try:
                from app_factory import cache
                cache.set(cache_key, result, timeout=timeout)
                current_app.logger.debug(f"Cached response for {cache_key}")
            except Exception as e:
                current_app.logger.warning(f"Cache set failed: {e}")
            
            return result
        return wrapper
    return decorator