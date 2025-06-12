"""
Comprehensive error handling and integration monitoring service
Provides centralized error tracking, circuit breaker patterns, and performance monitoring
"""
import logging
import time
import json
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional
import threading

class CircuitBreaker:
    """Circuit breaker pattern for external service calls"""
    
    def __init__(self, failure_threshold=5, recovery_timeout=60, expected_exception=Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.Lock()

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self._lock:
                if self.state == 'OPEN':
                    if self._should_attempt_reset():
                        self.state = 'HALF_OPEN'
                    else:
                        raise Exception(f"Circuit breaker is OPEN for {func.__name__}")

                try:
                    result = func(*args, **kwargs)
                    self._on_success()
                    return result
                except self.expected_exception as e:
                    self._on_failure()
                    raise e

        return wrapper

    def _should_attempt_reset(self):
        return (self.last_failure_time and 
                time.time() - self.last_failure_time >= self.recovery_timeout)

    def _on_success(self):
        self.failure_count = 0
        self.state = 'CLOSED'

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'

class IntegrationMonitor:
    """Monitor and manage service integrations"""
    
    def __init__(self):
        self.services = {}
        self.health_checks = {}
        self.performance_metrics = {}
        self._lock = threading.Lock()

    def register_service(self, name: str, health_check_func: callable, circuit_breaker: CircuitBreaker = None):
        """Register a service for monitoring"""
        with self._lock:
            self.services[name] = {
                'health_check': health_check_func,
                'circuit_breaker': circuit_breaker,
                'last_check': None,
                'status': 'unknown',
                'error_count': 0,
                'total_calls': 0
            }

    def check_service_health(self, name: str) -> Dict[str, Any]:
        """Check health of a specific service"""
        if name not in self.services:
            return {'status': 'unknown', 'error': 'Service not registered'}

        service = self.services[name]
        try:
            start_time = time.time()
            service['health_check']()
            response_time = time.time() - start_time
            
            with self._lock:
                service['last_check'] = datetime.utcnow()
                service['status'] = 'healthy'
                service['total_calls'] += 1
                
                # Track performance
                if name not in self.performance_metrics:
                    self.performance_metrics[name] = []
                self.performance_metrics[name].append({
                    'timestamp': datetime.utcnow(),
                    'response_time': response_time,
                    'status': 'success'
                })
                
                # Keep only last 100 metrics
                self.performance_metrics[name] = self.performance_metrics[name][-100:]

            return {
                'status': 'healthy',
                'response_time': response_time,
                'last_check': service['last_check']
            }

        except Exception as e:
            with self._lock:
                service['error_count'] += 1
                service['status'] = 'unhealthy'
                service['last_check'] = datetime.utcnow()
                
                if name not in self.performance_metrics:
                    self.performance_metrics[name] = []
                self.performance_metrics[name].append({
                    'timestamp': datetime.utcnow(),
                    'response_time': None,
                    'status': 'error',
                    'error': str(e)
                })

            logging.error(f"Health check failed for {name}: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': service['last_check']
            }

    def get_all_service_health(self) -> Dict[str, Any]:
        """Get health status of all registered services"""
        health_report = {}
        for name in self.services:
            health_report[name] = self.check_service_health(name)
        return health_report

    def get_performance_metrics(self, name: str = None) -> Dict[str, Any]:
        """Get performance metrics for services"""
        if name:
            return self.performance_metrics.get(name, [])
        return self.performance_metrics

class ErrorCollector:
    """Collect and analyze application errors"""
    
    def __init__(self, max_errors=1000):
        self.errors = []
        self.max_errors = max_errors
        self._lock = threading.Lock()

    def record_error(self, error: Exception, context: Dict[str, Any] = None):
        """Record an error with context"""
        error_data = {
            'timestamp': datetime.utcnow(),
            'type': type(error).__name__,
            'message': str(error),
            'context': context or {},
            'traceback': str(error.__traceback__) if error.__traceback__ else None
        }

        with self._lock:
            self.errors.append(error_data)
            if len(self.errors) > self.max_errors:
                self.errors = self.errors[-self.max_errors:]

        logging.error(f"Error recorded: {error_data}")

    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_errors = [e for e in self.errors if e['timestamp'] > cutoff_time]

        error_types = {}
        for error in recent_errors:
            error_type = error['type']
            if error_type not in error_types:
                error_types[error_type] = 0
            error_types[error_type] += 1

        return {
            'total_errors': len(recent_errors),
            'error_types': error_types,
            'last_error': recent_errors[-1] if recent_errors else None,
            'timeframe_hours': hours
        }

    def clear_old_errors(self, hours: int = 168):  # 7 days default
        """Clear errors older than specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        with self._lock:
            self.errors = [e for e in self.errors if e['timestamp'] > cutoff_time]

# Global instances
integration_monitor = IntegrationMonitor()
error_collector = ErrorCollector()

def setup_integration_monitoring():
    """Setup monitoring for all integrated services"""
    
    # Database health check
    def database_health():
        from database import db, get_database_stats
        stats = get_database_stats()
        if stats.get('status') != 'healthy':
            raise Exception(f"Database unhealthy: {stats}")
    
    # OpenAI health check
    def openai_health():
        try:
            import openai
            import os
            if not os.environ.get('OPENAI_API_KEY'):
                raise Exception("OpenAI API key not configured")
        except ImportError:
            raise Exception("OpenAI library not available")
    
    # Cache service health check
    def cache_health():
        try:
            from services.cache_service import cache_service
            cache_service.get_stats()
        except ImportError:
            raise Exception("Cache service not available")
    
    # Register services with circuit breakers
    integration_monitor.register_service(
        'database', 
        database_health, 
        CircuitBreaker(failure_threshold=3, recovery_timeout=30)
    )
    
    integration_monitor.register_service(
        'openai', 
        openai_health, 
        CircuitBreaker(failure_threshold=5, recovery_timeout=60)
    )
    
    integration_monitor.register_service(
        'cache', 
        cache_health, 
        CircuitBreaker(failure_threshold=2, recovery_timeout=20)
    )
    
    logging.info("Integration monitoring setup completed")

def get_system_health_report() -> Dict[str, Any]:
    """Generate comprehensive system health report"""
    return {
        'timestamp': datetime.utcnow(),
        'services': integration_monitor.get_all_service_health(),
        'errors': error_collector.get_error_summary(24),
        'performance': integration_monitor.get_performance_metrics()
    }