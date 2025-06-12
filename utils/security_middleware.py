"""
Enhanced Security Middleware for 2ª Vara Cível de Cariacica
Implements comprehensive security headers, input validation, and threat detection
"""

from flask import request, g, current_app, abort, jsonify
from functools import wraps
import re
import time
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    def __init__(self, app=None):
        self.app = app
        self.rate_limits = defaultdict(list)
        self.blocked_ips = set()
        self.suspicious_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'expression\s*\(',
            r'url\s*\(',
            r'import\s+\(',
            r'document\.',
            r'window\.',
            r'eval\s*\(',
            r'setTimeout\s*\(',
            r'setInterval\s*\(',
            r'function\s*\(',
            r'=\s*new\s+',
            r'vbscript:',
            r'data:text/html',
            r'<?php',
            r'<\?=',
            r'<%.*?%>',
            r'\{.*?\}',
            r'union\s+select',
            r'drop\s+table',
            r'insert\s+into',
            r'delete\s+from',
            r'update\s+.*set',
            r'exec\s*\(',
            r'sp_executesql'
        ]
        
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize security middleware with Flask app"""
        self.app = app
        
        # Register before request handler
        app.before_request(self.before_request)
        
        # Register after request handler
        app.after_request(self.after_request)
        
        # Register error handlers
        app.errorhandler(429)(self.rate_limit_handler)
        app.errorhandler(403)(self.forbidden_handler)

    def before_request(self):
        """Execute security checks before each request"""
        try:
            # Get client IP
            client_ip = self.get_client_ip()
            g.client_ip = client_ip
            
            # Check if IP is blocked
            if client_ip in self.blocked_ips:
                logger.warning(f"Blocked IP attempted access: {client_ip}")
                abort(403)
            
            # Rate limiting
            if not self.check_rate_limit(client_ip):
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                abort(429)
            
            # Input validation
            if not self.validate_request():
                logger.warning(f"Malicious input detected from IP: {client_ip}")
                self.block_ip(client_ip)
                abort(403)
            
            # Security headers preparation
            g.security_headers = current_app.config.get('SECURITY_HEADERS', {})
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")

    def after_request(self, response):
        """Add security headers after request processing"""
        try:
            # Add security headers
            security_headers = getattr(g, 'security_headers', {})
            for header, value in security_headers.items():
                response.headers[header] = value
            
            # Add CSP header for content security
            csp_policy = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
            response.headers['Content-Security-Policy'] = csp_policy
            
            # Add cache control for sensitive pages
            if request.endpoint in ['admin.dashboard', 'admin.logs']:
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
            
            return response
            
        except Exception as e:
            logger.error(f"Error adding security headers: {e}")
            return response

    def get_client_ip(self):
        """Get the real client IP address"""
        # Check for forwarded headers
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr

    def check_rate_limit(self, client_ip, limit=100, window=3600):
        """Check if client IP exceeds rate limit"""
        now = time.time()
        
        # Clean old entries
        self.rate_limits[client_ip] = [
            timestamp for timestamp in self.rate_limits[client_ip]
            if now - timestamp < window
        ]
        
        # Check current rate
        if len(self.rate_limits[client_ip]) >= limit:
            return False
        
        # Add current request
        self.rate_limits[client_ip].append(now)
        return True

    def validate_request(self):
        """Validate request for malicious content"""
        try:
            # Check all input sources
            inputs_to_check = []
            
            # Form data
            if request.form:
                inputs_to_check.extend(request.form.values())
            
            # Query parameters
            if request.args:
                inputs_to_check.extend(request.args.values())
            
            # JSON data
            if request.is_json and request.get_json():
                json_data = request.get_json()
                if isinstance(json_data, dict):
                    inputs_to_check.extend(self.extract_values_from_dict(json_data))
            
            # Headers (check user-agent and referer)
            headers_to_check = ['User-Agent', 'Referer']
            for header in headers_to_check:
                if request.headers.get(header):
                    inputs_to_check.append(request.headers.get(header))
            
            # Validate each input
            for input_value in inputs_to_check:
                if not self.is_safe_input(str(input_value)):
                    logger.warning(f"Suspicious input detected: {input_value[:100]}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error in request validation: {e}")
            return False

    def extract_values_from_dict(self, data, values=None):
        """Recursively extract all values from nested dictionary"""
        if values is None:
            values = []
        
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, (dict, list)):
                    self.extract_values_from_dict(value, values)
                else:
                    values.append(str(value))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self.extract_values_from_dict(item, values)
                else:
                    values.append(str(item))
        
        return values

    def is_safe_input(self, input_value):
        """Check if input contains suspicious patterns"""
        if not input_value:
            return True
        
        # Normalize input for checking
        normalized = input_value.lower().replace(' ', '').replace('\t', '').replace('\n', '')
        
        # Check against suspicious patterns
        for pattern in self.suspicious_patterns:
            if re.search(pattern, normalized, re.IGNORECASE):
                return False
        
        # Check for excessively long inputs (potential buffer overflow)
        if len(input_value) > 10000:
            return False
        
        # Check for repeated characters (potential DoS)
        if len(set(input_value)) < len(input_value) / 10 and len(input_value) > 100:
            return False
        
        return True

    def block_ip(self, client_ip, duration=3600):
        """Block an IP address for specified duration"""
        # Don't block localhost/testing IPs
        if client_ip in ['127.0.0.1', 'localhost', '::1']:
            logger.debug(f"Not blocking localhost IP: {client_ip}")
            return
            
        self.blocked_ips.add(client_ip)
        logger.warning(f"IP blocked: {client_ip}")
        
        # Schedule unblocking (in a real application, use a proper job queue)
        # For now, we'll rely on application restart to clear blocks

    def rate_limit_handler(self, e):
        """Handle rate limit exceeded"""
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429

    def forbidden_handler(self, e):
        """Handle forbidden access"""
        return jsonify({
            'error': 'Access forbidden',
            'message': 'Your request has been blocked due to security policy.'
        }), 403


def require_csrf_token(f):
    """Decorator to require CSRF token for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            token = request.form.get('csrf_token') or request.headers.get('X-CSRFToken')
            if not token:
                logger.warning(f"Missing CSRF token from {g.get('client_ip', 'unknown')}")
                abort(403)
        return f(*args, **kwargs)
    return decorated_function


def sanitize_input(input_value, max_length=1000):
    """Sanitize user input"""
    if not input_value:
        return input_value
    
    # Convert to string and limit length
    sanitized = str(input_value)[:max_length]
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', sanitized)
    
    # Normalize whitespace
    sanitized = ' '.join(sanitized.split())
    
    return sanitized


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validate Brazilian phone number"""
    # Remove non-digits
    phone_digits = re.sub(r'\D', '', phone)
    
    # Check if it's a valid Brazilian phone number
    if len(phone_digits) in [10, 11] and phone_digits.startswith(('11', '12', '13', '14', '15', '16', '17', '18', '19', '21', '22', '24', '27', '28', '31', '32', '33', '34', '35', '37', '38', '41', '42', '43', '44', '45', '46', '47', '48', '49', '51', '53', '54', '55', '61', '62', '63', '64', '65', '66', '67', '68', '69', '71', '73', '74', '75', '77', '79', '81', '82', '83', '84', '85', '86', '87', '88', '89', '91', '92', '93', '94', '95', '96', '97', '98', '99')):
        return True
    
    return False


def log_security_event(event_type, details, client_ip=None):
    """Log security events for monitoring"""
    if not client_ip:
        client_ip = getattr(g, 'client_ip', 'unknown')
    
    security_log = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'client_ip': client_ip,
        'details': details,
        'user_agent': request.headers.get('User-Agent', 'unknown'),
        'endpoint': request.endpoint or 'unknown'
    }
    
    logger.warning(f"SECURITY_EVENT: {json.dumps(security_log)}")