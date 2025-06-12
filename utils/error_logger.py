"""
Enhanced Error Logging System
2ª Vara Cível de Cariacica - Comprehensive error tracking and monitoring
"""

import os
import json
import logging
import traceback
from datetime import datetime, timedelta
from flask import request, g, session
from werkzeug.exceptions import HTTPException
import threading
import time
from typing import Dict, List, Optional, Any

class ErrorLogger:
    """Enhanced error logging with structured data and real-time monitoring"""
    
    def __init__(self, app=None):
        self.app = app
        self.error_count = 0
        self.errors_today = []
        self.critical_errors = []
        self.max_log_entries = 5000
        self.alert_threshold = 50
        self.lock = threading.Lock()
        
        # Configure structured logging
        self.setup_logging()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize error logging with Flask app"""
        self.app = app
        
        # Setup error handlers
        app.errorhandler(404)(self.handle_not_found)
        app.errorhandler(500)(self.handle_internal_error)
        app.errorhandler(403)(self.handle_forbidden)
        app.errorhandler(400)(self.handle_bad_request)
        app.errorhandler(Exception)(self.handle_exception)
        
        # Setup request logging
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)
    
    def setup_logging(self):
        """Configure advanced logging system"""
        # Main error logger
        self.logger = logging.getLogger('error_system')
        self.logger.setLevel(logging.DEBUG)
        
        # File handlers
        error_handler = logging.FileHandler('app_errors.log')
        error_handler.setLevel(logging.ERROR)
        
        debug_handler = logging.FileHandler('app_debug.log')
        debug_handler.setLevel(logging.DEBUG)
        
        critical_handler = logging.FileHandler('critical_errors.log')
        critical_handler.setLevel(logging.CRITICAL)
        
        # JSON formatter for structured logging
        json_formatter = JsonFormatter()
        
        # Standard formatter for readable logs
        standard_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        error_handler.setFormatter(json_formatter)
        debug_handler.setFormatter(standard_formatter)
        critical_handler.setFormatter(json_formatter)
        
        self.logger.addHandler(error_handler)
        self.logger.addHandler(debug_handler)
        self.logger.addHandler(critical_handler)
    
    def log_error(self, error: Exception, context: Dict = None, level: str = 'ERROR'):
        """Log error with comprehensive context"""
        with self.lock:
            error_data = self._build_error_data(error, context)
            
            # Log to appropriate level
            if level == 'CRITICAL':
                self.logger.critical(json.dumps(error_data))
                self.critical_errors.append(error_data)
            elif level == 'ERROR':
                self.logger.error(json.dumps(error_data))
            elif level == 'WARNING':
                self.logger.warning(json.dumps(error_data))
            else:
                self.logger.info(json.dumps(error_data))
            
            # Add to memory storage
            self.errors_today.append(error_data)
            self.error_count += 1
            
            # Maintain log size
            if len(self.errors_today) > self.max_log_entries:
                self.errors_today = self.errors_today[-self.max_log_entries:]
            
            # Check alert threshold
            if self.error_count % self.alert_threshold == 0:
                self._trigger_alert(error_data)
    
    def _build_error_data(self, error: Exception, context: Dict = None) -> Dict:
        """Build comprehensive error data structure"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_id': f"ERR_{int(time.time())}_{self.error_count}",
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'severity': self._determine_severity(error),
            'context': context or {}
        }
        
        # Add request context if available
        try:
            if request:
                error_data['request'] = {
                    'method': request.method,
                    'url': request.url,
                    'path': request.path,
                    'remote_addr': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', ''),
                    'referrer': request.referrer,
                    'form_data': self._sanitize_form_data(request.form),
                    'args': dict(request.args),
                    'headers': dict(request.headers)
                }
                
                # Add session info if available
                if session:
                    error_data['session'] = {
                        'session_id': session.get('_id', 'anonymous'),
                        'user_info': session.get('user', 'not_logged_in')
                    }
        except:
            error_data['request'] = {'error': 'Unable to capture request context'}
        
        return error_data
    
    def _sanitize_form_data(self, form_data) -> Dict:
        """Sanitize form data to remove sensitive information"""
        sensitive_fields = ['password', 'token', 'csrf_token', 'secret']
        sanitized = {}
        
        for key, value in form_data.items():
            if any(field in key.lower() for field in sensitive_fields):
                sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = str(value)[:200] if len(str(value)) > 200 else str(value)
        
        return sanitized
    
    def _determine_severity(self, error: Exception) -> str:
        """Determine error severity level"""
        if isinstance(error, (MemoryError, SystemExit, KeyboardInterrupt)):
            return 'CRITICAL'
        elif isinstance(error, (ConnectionError, TimeoutError, OSError)):
            return 'HIGH'
        elif isinstance(error, (ValueError, TypeError, AttributeError)):
            return 'MEDIUM'
        elif isinstance(error, HTTPException):
            if error.code >= 500:
                return 'HIGH'
            elif error.code >= 400:
                return 'MEDIUM'
            else:
                return 'LOW'
        else:
            return 'MEDIUM'
    
    def _trigger_alert(self, error_data: Dict):
        """Trigger alert when error threshold is reached"""
        alert_data = {
            'alert_time': datetime.now().isoformat(),
            'error_count': self.error_count,
            'recent_error': error_data,
            'critical_errors_count': len(self.critical_errors)
        }
        
        self.logger.critical(f"ALERT_TRIGGERED: {json.dumps(alert_data)}")
        
        # Save alert to separate file
        with open('error_alerts.log', 'a') as f:
            f.write(f"{json.dumps(alert_data)}\n")
    
    # Flask error handlers
    def handle_not_found(self, error):
        """Handle 404 errors"""
        self.log_error(error, {'error_type': '404_not_found'}, 'WARNING')
        return f"Página não encontrada: {request.path}", 404
    
    def handle_internal_error(self, error):
        """Handle 500 errors"""
        self.log_error(error, {'error_type': '500_internal_error'}, 'CRITICAL')
        return "Erro interno do servidor. Nossa equipe foi notificada.", 500
    
    def handle_forbidden(self, error):
        """Handle 403 errors"""
        self.log_error(error, {'error_type': '403_forbidden'}, 'WARNING')
        return "Acesso negado.", 403
    
    def handle_bad_request(self, error):
        """Handle 400 errors"""
        self.log_error(error, {'error_type': '400_bad_request'}, 'WARNING')
        return "Requisição inválida.", 400
    
    def handle_exception(self, error):
        """Handle all other exceptions"""
        self.log_error(error, {'error_type': 'unhandled_exception'}, 'ERROR')
        return "Ocorreu um erro inesperado. Nossa equipe foi notificada.", 500
    
    # Request lifecycle logging
    def before_request(self):
        """Log before each request"""
        g.start_time = time.time()
        g.request_id = f"REQ_{int(time.time())}_{threading.current_thread().ident}"
        
        # Log request start for debugging
        self.logger.debug(f"REQUEST_START {g.request_id} {request.method} {request.path}")
    
    def after_request(self, response):
        """Log after each request"""
        if hasattr(g, 'start_time'):
            duration = (time.time() - g.start_time) * 1000  # Convert to ms
            
            # Log response info
            self.logger.debug(
                f"REQUEST_END {getattr(g, 'request_id', 'unknown')} "
                f"{response.status_code} {duration:.2f}ms"
            )
            
            # Log slow requests as warnings
            if duration > 5000:  # 5 seconds
                self.log_error(
                    Exception(f"Slow request: {duration:.2f}ms"),
                    {'duration_ms': duration, 'status_code': response.status_code},
                    'WARNING'
                )
        
        return response
    
    def teardown_request(self, exception):
        """Handle request teardown"""
        if exception:
            self.log_error(
                exception,
                {'error_type': 'request_teardown_error'},
                'ERROR'
            )
    
    # Analysis and reporting methods
    def get_error_summary(self, hours: int = 24) -> Dict:
        """Get error summary for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_errors = [
            error for error in self.errors_today
            if datetime.fromisoformat(error['timestamp']) > cutoff_time
        ]
        
        # Count by type
        error_types = {}
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        
        for error in recent_errors:
            error_type = error['error_type']
            severity = error.get('severity', 'MEDIUM')
            
            error_types[error_type] = error_types.get(error_type, 0) + 1
            severity_counts[severity] += 1
        
        return {
            'period_hours': hours,
            'total_errors': len(recent_errors),
            'error_types': error_types,
            'severity_breakdown': severity_counts,
            'critical_errors': len(self.critical_errors),
            'most_common_error': max(error_types.keys(), key=error_types.get) if error_types else None,
            'error_rate_per_hour': len(recent_errors) / hours if hours > 0 else 0
        }
    
    def export_errors(self, filename: str = None, hours: int = 24) -> str:
        """Export errors to JSON file"""
        if not filename:
            filename = f"error_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_errors = [
            error for error in self.errors_today
            if datetime.fromisoformat(error['timestamp']) > cutoff_time
        ]
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'period_hours': hours,
            'total_errors': len(recent_errors),
            'errors': recent_errors,
            'summary': self.get_error_summary(hours)
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filename

class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_obj = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_obj)

# Global error logger instance
error_logger = ErrorLogger()

def setup_error_logging(app):
    """Setup error logging for Flask app"""
    error_logger.init_app(app)
    return error_logger