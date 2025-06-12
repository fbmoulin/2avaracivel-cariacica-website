#!/usr/bin/env python3
"""
Error monitoring system for 2ª Vara Cível de Cariacica website
Real-time error tracking and logging with alerts
"""

import os
import sys
import json
import logging
import traceback
from datetime import datetime, timedelta
from werkzeug.exceptions import HTTPException
from flask import request, session
import threading
import time

# Configure error logging
error_logger = logging.getLogger('error_monitor')
error_handler = logging.FileHandler('errors.log')
error_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
error_handler.setFormatter(error_formatter)
error_logger.addHandler(error_handler)
error_logger.setLevel(logging.ERROR)

class ErrorMonitor:
    def __init__(self):
        self.error_count = 0
        self.error_log = []
        self.max_log_size = 1000
        self.alert_threshold = 10
        self.monitoring = True
        
    def log_error(self, error, context=None):
        """Log an error with context information"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        # Add request context if available
        try:
            if request:
                error_data['context'].update({
                    'url': request.url,
                    'method': request.method,
                    'user_agent': request.headers.get('User-Agent'),
                    'ip_address': request.remote_addr,
                    'referrer': request.headers.get('Referer')
                })
        except:
            pass
        
        # Add to memory log
        self.error_log.append(error_data)
        if len(self.error_log) > self.max_log_size:
            self.error_log.pop(0)
        
        # Log to file
        error_logger.error(f"{error_data['error_type']}: {error_data['error_message']}")
        
        # Increment counter
        self.error_count += 1
        
        # Check if alert needed
        if self.error_count % self.alert_threshold == 0:
            self.trigger_alert()
    
    def log_database_error(self, error, query=None):
        """Log database-specific errors"""
        context = {'component': 'database'}
        if query:
            context['query'] = str(query)
        
        self.log_error(error, context)
    
    def log_api_error(self, error, endpoint=None, response_code=None):
        """Log API-specific errors"""
        context = {
            'component': 'api',
            'endpoint': endpoint,
            'response_code': response_code
        }
        
        self.log_error(error, context)
    
    def log_chatbot_error(self, error, user_message=None):
        """Log chatbot-specific errors"""
        context = {
            'component': 'chatbot',
            'user_message': user_message
        }
        
        self.log_error(error, context)
    
    def get_error_stats(self, hours=24):
        """Get error statistics for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_errors = [
            error for error in self.error_log
            if datetime.fromisoformat(error['timestamp']) > cutoff_time
        ]
        
        # Count by error type
        error_types = {}
        for error in recent_errors:
            error_type = error['error_type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Count by component
        components = {}
        for error in recent_errors:
            component = error.get('context', {}).get('component', 'unknown')
            components[component] = components.get(component, 0) + 1
        
        return {
            'total_errors': len(recent_errors),
            'error_types': error_types,
            'components': components,
            'recent_errors': recent_errors[-10:]  # Last 10 errors
        }
    
    def trigger_alert(self):
        """Trigger alert when error threshold is reached"""
        alert_message = f"Error threshold reached: {self.error_count} total errors"
        error_logger.critical(alert_message)
        
        # Save alert to file
        with open('error_alerts.log', 'a') as f:
            f.write(f"{datetime.now().isoformat()}: {alert_message}\n")
    
    def export_errors_json(self, filename='error_export.json'):
        """Export errors to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.error_log, f, indent=2, default=str)
    
    def clear_old_errors(self, days=7):
        """Clear errors older than specified days"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        self.error_log = [
            error for error in self.error_log
            if datetime.fromisoformat(error['timestamp']) > cutoff_time
        ]

# Global error monitor instance
error_monitor = ErrorMonitor()

def setup_flask_error_handlers(app):
    """Setup Flask error handlers"""
    
    @app.errorhandler(404)
    def handle_404(error):
        error_monitor.log_error(error, {'error_code': 404})
        try:
            from flask import render_template
            return render_template('404.html'), 404
        except:
            return "404 - Page Not Found", 404
    
    @app.errorhandler(500)
    def handle_500(error):
        error_monitor.log_error(error, {'error_code': 500})
        try:
            from flask import render_template
            return render_template('500.html'), 500
        except:
            return "500 - Internal Server Error", 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        if isinstance(error, HTTPException):
            error_monitor.log_error(error, {'error_code': error.code})
            return error
        
        error_monitor.log_error(error, {'error_code': 500})
        try:
            from flask import render_template
            return render_template('500.html'), 500
        except:
            return "500 - Internal Server Error", 500

def monitor_performance():
    """Monitor application performance metrics"""
    while error_monitor.monitoring:
        try:
            # Check memory usage, CPU, etc.
            import psutil
            process = psutil.Process()
            
            memory_percent = process.memory_percent()
            cpu_percent = process.cpu_percent()
            
            if memory_percent > 80:
                error_monitor.log_error(
                    Exception(f"High memory usage: {memory_percent}%"),
                    {'component': 'performance', 'metric': 'memory'}
                )
            
            if cpu_percent > 80:
                error_monitor.log_error(
                    Exception(f"High CPU usage: {cpu_percent}%"),
                    {'component': 'performance', 'metric': 'cpu'}
                )
        
        except ImportError:
            # psutil not available
            pass
        except Exception as e:
            error_monitor.log_error(e, {'component': 'performance_monitor'})
        
        time.sleep(60)  # Check every minute

def start_monitoring():
    """Start background monitoring"""
    monitor_thread = threading.Thread(target=monitor_performance, daemon=True)
    monitor_thread.start()

def generate_error_report():
    """Generate comprehensive error report"""
    stats = error_monitor.get_error_stats()
    
    report = f"""
ERROR MONITORING REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
==================================================

SUMMARY (Last 24 hours):
- Total Errors: {stats['total_errors']}
- Error Types: {len(stats['error_types'])}
- Components Affected: {len(stats['components'])}

ERROR BREAKDOWN BY TYPE:
"""
    
    for error_type, count in sorted(stats['error_types'].items(), key=lambda x: x[1], reverse=True):
        report += f"- {error_type}: {count}\n"
    
    report += "\nERROR BREAKDOWN BY COMPONENT:\n"
    for component, count in sorted(stats['components'].items(), key=lambda x: x[1], reverse=True):
        report += f"- {component}: {count}\n"
    
    report += "\nRECENT ERRORS:\n"
    for error in stats['recent_errors']:
        timestamp = error['timestamp'][:19]  # Remove microseconds
        report += f"[{timestamp}] {error['error_type']}: {error['error_message']}\n"
    
    return report

if __name__ == "__main__":
    # Generate and display current error report
    report = generate_error_report()
    print(report)
    
    # Save report to file
    with open('error_report.txt', 'w') as f:
        f.write(report)
    
    print("\nError report saved to error_report.txt")
    print(f"Total errors logged: {error_monitor.error_count}")