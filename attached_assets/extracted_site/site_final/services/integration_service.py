"""
Integration service for robust system stability and workflow management
Provides centralized integration handling, circuit breaker patterns, and resilience
"""
import logging
import time
import functools
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import threading
import queue
import json


class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    DOWN = "down"


@dataclass
class CircuitBreakerState:
    """Circuit breaker state tracking"""
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    status: ServiceStatus = ServiceStatus.HEALTHY
    consecutive_successes: int = 0
    
    
class CircuitBreaker:
    """Circuit breaker pattern implementation for service resilience"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, success_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.state = CircuitBreakerState()
        self._lock = threading.Lock()
        
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self._lock:
            if self._should_attempt_call():
                try:
                    result = func(*args, **kwargs)
                    self._on_success()
                    return result
                except Exception as e:
                    self._on_failure()
                    raise e
            else:
                raise Exception(f"Circuit breaker open - service unavailable")
    
    def _should_attempt_call(self) -> bool:
        """Determine if call should be attempted based on circuit state"""
        if self.state.status == ServiceStatus.HEALTHY:
            return True
        
        if self.state.status == ServiceStatus.DOWN:
            # Check if enough time has passed to try recovery
            if (self.state.last_failure_time and 
                datetime.now() - self.state.last_failure_time > timedelta(seconds=self.recovery_timeout)):
                self.state.status = ServiceStatus.DEGRADED
                return True
            return False
        
        # DEGRADED or FAILING status - allow attempts but with caution
        return True
    
    def _on_success(self):
        """Handle successful call"""
        if self.state.status == ServiceStatus.DEGRADED:
            self.state.consecutive_successes += 1
            if self.state.consecutive_successes >= self.success_threshold:
                self.state.status = ServiceStatus.HEALTHY
                self.state.failure_count = 0
                self.state.consecutive_successes = 0
        else:
            self.state.consecutive_successes += 1
            if self.state.failure_count > 0:
                self.state.failure_count = max(0, self.state.failure_count - 1)
    
    def _on_failure(self):
        """Handle failed call"""
        self.state.failure_count += 1
        self.state.consecutive_successes = 0
        self.state.last_failure_time = datetime.now()
        
        if self.state.failure_count >= self.failure_threshold:
            self.state.status = ServiceStatus.DOWN
        elif self.state.failure_count >= self.failure_threshold // 2:
            self.state.status = ServiceStatus.FAILING
        else:
            self.state.status = ServiceStatus.DEGRADED


class RetryManager:
    """Intelligent retry mechanism with exponential backoff"""
    
    @staticmethod
    def with_retry(max_attempts: int = 3, backoff_factor: float = 1.5, 
                   initial_delay: float = 1.0, max_delay: float = 30.0):
        """Decorator for automatic retry with exponential backoff"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                delay = initial_delay
                
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            time.sleep(min(delay, max_delay))
                            delay *= backoff_factor
                            logging.warning(f"Retry attempt {attempt + 1} for {func.__name__}: {str(e)}")
                        else:
                            logging.error(f"All retry attempts failed for {func.__name__}: {str(e)}")
                
                raise last_exception
            return wrapper
        return decorator


class HealthMonitor:
    """System health monitoring and metrics collection"""
    
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_failed': 0,
            'response_times': [],
            'error_rates': [],
            'last_health_check': None
        }
        self._lock = threading.Lock()
    
    def record_request(self, success: bool, response_time: float):
        """Record request metrics"""
        with self._lock:
            self.metrics['requests_total'] += 1
            if success:
                self.metrics['requests_success'] += 1
            else:
                self.metrics['requests_failed'] += 1
            
            self.metrics['response_times'].append(response_time)
            
            # Keep only last 1000 response times
            if len(self.metrics['response_times']) > 1000:
                self.metrics['response_times'] = self.metrics['response_times'][-1000:]
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get current health metrics"""
        with self._lock:
            total_requests = self.metrics['requests_total']
            if total_requests == 0:
                return {
                    'status': 'healthy',
                    'error_rate': 0.0,
                    'avg_response_time': 0.0,
                    'total_requests': 0
                }
            
            error_rate = (self.metrics['requests_failed'] / total_requests) * 100
            avg_response_time = sum(self.metrics['response_times']) / len(self.metrics['response_times']) if self.metrics['response_times'] else 0
            
            # Determine health status
            status = 'healthy'
            if error_rate > 10:
                status = 'failing'
            elif error_rate > 5:
                status = 'degraded'
            elif avg_response_time > 2000:  # 2 seconds
                status = 'degraded'
            
            return {
                'status': status,
                'error_rate': round(error_rate, 2),
                'avg_response_time': round(avg_response_time, 2),
                'total_requests': total_requests,
                'success_requests': self.metrics['requests_success'],
                'failed_requests': self.metrics['requests_failed']
            }


class IntegrationService:
    """Main integration service for system stability and coordination"""
    
    def __init__(self):
        self.circuit_breakers = {}
        self.health_monitor = HealthMonitor()
        self.retry_manager = RetryManager()
        self._service_registry = {}
        self._event_queue = queue.Queue()
        self._logger = logging.getLogger(__name__)
        self._initialized = False
    
    def initialize(self):
        """Initialize the integration service with default configurations"""
        if self._initialized:
            return
        
        # Register core services
        self.register_service('openai', {
            'failure_threshold': 3,
            'recovery_timeout': 30,
            'success_threshold': 2,
            'timeout': 25
        })
        
        self.register_service('database', {
            'failure_threshold': 5,
            'recovery_timeout': 60,
            'success_threshold': 3,
            'timeout': 10
        })
        
        self.register_service('cache', {
            'failure_threshold': 2,
            'recovery_timeout': 15,
            'success_threshold': 1,
            'timeout': 5
        })
        
        self._initialized = True
        self._logger.info("Integration service initialized with core services")
        
    def register_service(self, name: str, service_config: Dict[str, Any]):
        """Register a service with the integration layer"""
        self._service_registry[name] = {
            'config': service_config,
            'circuit_breaker': CircuitBreaker(
                failure_threshold=service_config.get('failure_threshold', 5),
                recovery_timeout=service_config.get('recovery_timeout', 60),
                success_threshold=service_config.get('success_threshold', 3)
            ),
            'last_health_check': None,
            'status': ServiceStatus.HEALTHY
        }
        self._logger.info(f"Registered service: {name}")
    
    def call_service(self, service_name: str, func: Callable, *args, **kwargs):
        """Call a service through the integration layer with resilience patterns"""
        if service_name not in self._service_registry:
            raise ValueError(f"Service {service_name} not registered")
        
        service = self._service_registry[service_name]
        circuit_breaker = service['circuit_breaker']
        
        start_time = time.time()
        try:
            result = circuit_breaker.call(func, *args, **kwargs)
            response_time = (time.time() - start_time) * 1000
            self.health_monitor.record_request(True, response_time)
            return result
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.health_monitor.record_request(False, response_time)
            self._logger.error(f"Service call failed for {service_name}: {str(e)}")
            raise e
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get status of a specific service"""
        if service_name not in self._service_registry:
            return {'status': 'unknown', 'error': 'Service not registered'}
        
        service = self._service_registry[service_name]
        circuit_breaker = service['circuit_breaker']
        
        return {
            'status': circuit_breaker.state.status.value,
            'failure_count': circuit_breaker.state.failure_count,
            'consecutive_successes': circuit_breaker.state.consecutive_successes,
            'last_failure': circuit_breaker.state.last_failure_time.isoformat() if circuit_breaker.state.last_failure_time else None
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        health_metrics = self.health_monitor.get_health_metrics()
        service_statuses = {}
        
        for service_name in self._service_registry:
            service_statuses[service_name] = self.get_service_status(service_name)
        
        # Determine overall system status
        overall_status = 'healthy'
        failing_services = sum(1 for status in service_statuses.values() 
                             if status.get('status') in ['failing', 'down'])
        
        if failing_services > 0:
            if failing_services >= len(self._service_registry) / 2:
                overall_status = 'failing'
            else:
                overall_status = 'degraded'
        
        return {
            'overall_status': overall_status,
            'health_metrics': health_metrics,
            'services': service_statuses,
            'timestamp': datetime.now().isoformat()
        }
    
    def perform_health_check(self, service_name: str = None):
        """Perform health checks on services"""
        if service_name:
            services_to_check = [service_name] if service_name in self._service_registry else []
        else:
            services_to_check = list(self._service_registry.keys())
        
        results = {}
        for service in services_to_check:
            try:
                # Perform basic connectivity test
                service_config = self._service_registry[service]['config']
                health_check_func = service_config.get('health_check_func')
                
                if health_check_func:
                    health_check_func()
                    results[service] = 'healthy'
                else:
                    results[service] = 'no_health_check'
                    
            except Exception as e:
                results[service] = f'unhealthy: {str(e)}'
                self._logger.warning(f"Health check failed for {service}: {str(e)}")
        
        return results
    
    def graceful_shutdown(self):
        """Perform graceful shutdown of integration services"""
        self._logger.info("Starting graceful shutdown of integration services")
        
        # Save current metrics and state
        shutdown_report = {
            'timestamp': datetime.now().isoformat(),
            'final_health': self.get_system_health(),
            'uptime_metrics': self.health_monitor.get_health_metrics()
        }
        
        try:
            with open('shutdown_report.json', 'w') as f:
                json.dump(shutdown_report, f, indent=2)
        except Exception as e:
            self._logger.error(f"Failed to save shutdown report: {str(e)}")
        
        self._logger.info("Integration service shutdown complete")


# Global integration service instance
integration_service = IntegrationService()


def with_integration(service_name: str):
    """Decorator to wrap functions with integration service patterns"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return integration_service.call_service(service_name, func, *args, **kwargs)
        return wrapper
    return decorator


def setup_integration_services():
    """Setup and configure integration services"""
    # Register core services
    integration_service.register_service('database', {
        'failure_threshold': 3,
        'recovery_timeout': 30,
        'success_threshold': 2
    })
    
    integration_service.register_service('openai', {
        'failure_threshold': 5,
        'recovery_timeout': 60,
        'success_threshold': 3
    })
    
    integration_service.register_service('cache', {
        'failure_threshold': 10,
        'recovery_timeout': 10,
        'success_threshold': 2
    })
    
    integration_service.register_service('external_api', {
        'failure_threshold': 3,
        'recovery_timeout': 120,
        'success_threshold': 2
    })
    
    logging.info("Integration services configured successfully")