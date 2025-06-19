"""
Robust Integration Service for Enhanced System Stability
Provides advanced circuit breaker patterns, retry mechanisms, and health monitoring
"""
import logging
import time
import asyncio
import threading
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from functools import wraps
import json
import os


class ServiceState(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    CIRCUIT_OPEN = "circuit_open"
    RECOVERING = "recovering"


@dataclass
class ServiceMetrics:
    """Comprehensive service metrics tracking"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    average_response_time: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    uptime_percentage: float = 100.0
    
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_calls == 0:
            return 100.0
        return (self.successful_calls / self.total_calls) * 100.0


@dataclass
class CircuitBreakerConfig:
    """Advanced circuit breaker configuration"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    success_threshold: int = 3
    timeout: int = 30
    half_open_max_calls: int = 3
    monitoring_window: int = 300  # 5 minutes
    exponential_backoff: bool = True
    max_backoff: int = 300


class AdvancedCircuitBreaker:
    """Enhanced circuit breaker with exponential backoff and monitoring"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = ServiceState.HEALTHY
        self.metrics = ServiceMetrics()
        self.last_state_change = datetime.now()
        self.backoff_factor = 1
        self._lock = threading.Lock()
        self._recent_calls = []
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self._lock:
            if self.state == ServiceState.CIRCUIT_OPEN:
                if self._should_attempt_reset():
                    self.state = ServiceState.RECOVERING
                    self.last_state_change = datetime.now()
                else:
                    raise Exception(f"Circuit breaker open - service unavailable")
            
            elif self.state == ServiceState.RECOVERING:
                if self.metrics.consecutive_successes >= self.config.success_threshold:
                    self._reset_circuit()
                elif len([c for c in self._recent_calls if c['timestamp'] > datetime.now() - timedelta(seconds=60)]) >= self.config.half_open_max_calls:
                    raise Exception(f"Circuit breaker recovering - limited calls allowed")
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            self._record_success(time.time() - start_time)
            return result
        except Exception as e:
            self._record_failure(time.time() - start_time)
            raise e
    
    def _record_success(self, response_time: float):
        """Record successful call"""
        with self._lock:
            self.metrics.total_calls += 1
            self.metrics.successful_calls += 1
            self.metrics.consecutive_successes += 1
            self.metrics.consecutive_failures = 0
            self.metrics.last_success = datetime.now()
            self._update_response_time(response_time)
            self._add_recent_call(True, response_time)
            
            if self.state == ServiceState.RECOVERING and self.metrics.consecutive_successes >= self.config.success_threshold:
                self._reset_circuit()
    
    def _record_failure(self, response_time: float):
        """Record failed call"""
        with self._lock:
            self.metrics.total_calls += 1
            self.metrics.failed_calls += 1
            self.metrics.consecutive_failures += 1
            self.metrics.consecutive_successes = 0
            self.metrics.last_failure = datetime.now()
            self._update_response_time(response_time)
            self._add_recent_call(False, response_time)
            
            if self.metrics.consecutive_failures >= self.config.failure_threshold:
                self._open_circuit()
    
    def _should_attempt_reset(self) -> bool:
        """Determine if circuit should attempt reset"""
        if self.config.exponential_backoff:
            backoff_time = min(self.config.recovery_timeout * self.backoff_factor, self.config.max_backoff)
        else:
            backoff_time = self.config.recovery_timeout
            
        return datetime.now() >= self.last_state_change + timedelta(seconds=backoff_time)
    
    def _open_circuit(self):
        """Open circuit breaker"""
        self.state = ServiceState.CIRCUIT_OPEN
        self.last_state_change = datetime.now()
        if self.config.exponential_backoff:
            self.backoff_factor = min(self.backoff_factor * 2, 10)
    
    def _reset_circuit(self):
        """Reset circuit breaker to healthy state"""
        self.state = ServiceState.HEALTHY
        self.last_state_change = datetime.now()
        self.backoff_factor = 1
        self.metrics.consecutive_failures = 0
    
    def _update_response_time(self, response_time: float):
        """Update average response time"""
        if self.metrics.average_response_time == 0:
            self.metrics.average_response_time = response_time
        else:
            # Exponential moving average
            self.metrics.average_response_time = (self.metrics.average_response_time * 0.9) + (response_time * 0.1)
    
    def _add_recent_call(self, success: bool, response_time: float):
        """Add call to recent calls tracking"""
        call_record = {
            'timestamp': datetime.now(),
            'success': success,
            'response_time': response_time
        }
        self._recent_calls.append(call_record)
        
        # Keep only recent calls within monitoring window
        cutoff_time = datetime.now() - timedelta(seconds=self.config.monitoring_window)
        self._recent_calls = [c for c in self._recent_calls if c['timestamp'] > cutoff_time]
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive circuit breaker status"""
        return {
            'state': self.state.value,
            'metrics': {
                'total_calls': self.metrics.total_calls,
                'success_rate': self.metrics.success_rate(),
                'average_response_time': round(self.metrics.average_response_time, 3),
                'consecutive_failures': self.metrics.consecutive_failures,
                'consecutive_successes': self.metrics.consecutive_successes,
                'last_success': self.metrics.last_success.isoformat() if self.metrics.last_success else None,
                'last_failure': self.metrics.last_failure.isoformat() if self.metrics.last_failure else None
            },
            'config': {
                'failure_threshold': self.config.failure_threshold,
                'recovery_timeout': self.config.recovery_timeout,
                'success_threshold': self.config.success_threshold
            },
            'backoff_factor': self.backoff_factor
        }


class RobustIntegrationManager:
    """Advanced integration manager with comprehensive reliability features"""
    
    def __init__(self):
        self.services: Dict[str, AdvancedCircuitBreaker] = {}
        self.health_monitor = HealthMonitor()
        self.logger = logging.getLogger(__name__)
        self._initialized = False
        self._global_metrics = {
            'total_service_calls': 0,
            'total_service_failures': 0,
            'service_availability': {}
        }
    
    def initialize(self):
        """Initialize robust integration manager"""
        if self._initialized:
            return
        
        # Configure core services with optimized settings
        self.register_service('database', CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=30,
            success_threshold=3,
            timeout=10,
            exponential_backoff=True
        ))
        
        self.register_service('openai', CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=60,
            success_threshold=2,
            timeout=25,
            exponential_backoff=True
        ))
        
        self.register_service('cache', CircuitBreakerConfig(
            failure_threshold=10,
            recovery_timeout=15,
            success_threshold=2,
            timeout=5,
            exponential_backoff=False
        ))
        
        self.register_service('external_api', CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=120,
            success_threshold=2,
            timeout=30,
            exponential_backoff=True
        ))
        
        self._initialized = True
        self.logger.info("Robust integration manager initialized with enhanced reliability features")
    
    def register_service(self, name: str, config: CircuitBreakerConfig):
        """Register service with advanced circuit breaker"""
        self.services[name] = AdvancedCircuitBreaker(config)
        self.logger.info(f"Registered service '{name}' with robust circuit breaker")
    
    def call_service(self, service_name: str, func: Callable, *args, **kwargs) -> Any:
        """Call service with comprehensive protection"""
        if service_name not in self.services:
            self.logger.warning(f"Service '{service_name}' not registered, calling directly")
            return func(*args, **kwargs)
        
        circuit_breaker = self.services[service_name]
        self._global_metrics['total_service_calls'] += 1
        
        try:
            result = circuit_breaker.call(func, *args, **kwargs)
            self._update_availability_metrics(service_name, True)
            return result
        except Exception as e:
            self._global_metrics['total_service_failures'] += 1
            self._update_availability_metrics(service_name, False)
            self.logger.error(f"Service '{service_name}' call failed: {str(e)}")
            raise e
    
    def _update_availability_metrics(self, service_name: str, success: bool):
        """Update service availability metrics"""
        if service_name not in self._global_metrics['service_availability']:
            self._global_metrics['service_availability'][service_name] = {
                'total_calls': 0,
                'successful_calls': 0
            }
        
        metrics = self._global_metrics['service_availability'][service_name]
        metrics['total_calls'] += 1
        if success:
            metrics['successful_calls'] += 1
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get detailed service status"""
        if service_name not in self.services:
            return {'error': f"Service '{service_name}' not registered"}
        
        return self.services[service_name].get_status()
    
    def get_overall_status(self) -> Dict[str, Any]:
        """Get comprehensive system integration status"""
        service_statuses = {}
        healthy_services = 0
        total_services = len(self.services)
        
        for service_name, circuit_breaker in self.services.items():
            status = circuit_breaker.get_status()
            service_statuses[service_name] = status
            
            if status['state'] in ['healthy', 'recovering']:
                healthy_services += 1
        
        overall_health = (healthy_services / total_services * 100) if total_services > 0 else 0
        
        return {
            'overall_health_percentage': round(overall_health, 2),
            'healthy_services': healthy_services,
            'total_services': total_services,
            'global_metrics': self._global_metrics,
            'service_details': service_statuses,
            'timestamp': datetime.now().isoformat()
        }
    
    def force_reset_circuit(self, service_name: str) -> bool:
        """Manually reset circuit breaker for a service"""
        if service_name not in self.services:
            return False
        
        circuit_breaker = self.services[service_name]
        circuit_breaker._reset_circuit()
        self.logger.info(f"Manually reset circuit breaker for service '{service_name}'")
        return True
    
    def get_service_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for improving service reliability"""
        recommendations = []
        
        for service_name, circuit_breaker in self.services.items():
            status = circuit_breaker.get_status()
            success_rate = status['metrics']['success_rate']
            avg_response_time = status['metrics']['average_response_time']
            
            if success_rate < 95:
                recommendations.append({
                    'service': service_name,
                    'type': 'reliability',
                    'message': f"Success rate ({success_rate:.1f}%) below optimal threshold",
                    'suggestion': 'Consider reviewing service configuration or dependencies'
                })
            
            if avg_response_time > 5:
                recommendations.append({
                    'service': service_name,
                    'type': 'performance',
                    'message': f"Average response time ({avg_response_time:.2f}s) is high",
                    'suggestion': 'Consider optimizing service calls or increasing timeout'
                })
            
            if status['state'] == 'circuit_open':
                recommendations.append({
                    'service': service_name,
                    'type': 'critical',
                    'message': 'Circuit breaker is open - service unavailable',
                    'suggestion': 'Investigate underlying service issues immediately'
                })
        
        return recommendations


class HealthMonitor:
    """Advanced health monitoring with predictive capabilities"""
    
    def __init__(self):
        self.health_history = {}
        self.logger = logging.getLogger(__name__)
    
    def record_health_check(self, service_name: str, status: Dict[str, Any]):
        """Record health check result"""
        if service_name not in self.health_history:
            self.health_history[service_name] = []
        
        health_record = {
            'timestamp': datetime.now(),
            'status': status,
            'healthy': status.get('state') in ['healthy', 'recovering']
        }
        
        self.health_history[service_name].append(health_record)
        
        # Keep only last 24 hours of data
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.health_history[service_name] = [
            record for record in self.health_history[service_name]
            if record['timestamp'] > cutoff_time
        ]
    
    def get_health_trends(self, service_name: str) -> Dict[str, Any]:
        """Analyze health trends for a service"""
        if service_name not in self.health_history:
            return {'error': 'No health history available'}
        
        records = self.health_history[service_name]
        if not records:
            return {'error': 'No health records found'}
        
        total_checks = len(records)
        healthy_checks = sum(1 for record in records if record['healthy'])
        health_percentage = (healthy_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Calculate trend over last hour
        hour_ago = datetime.now() - timedelta(hours=1)
        recent_records = [r for r in records if r['timestamp'] > hour_ago]
        recent_health = (sum(1 for r in recent_records if r['healthy']) / len(recent_records) * 100) if recent_records else 0
        
        return {
            'service': service_name,
            'overall_health_percentage': round(health_percentage, 2),
            'recent_health_percentage': round(recent_health, 2),
            'total_checks': total_checks,
            'healthy_checks': healthy_checks,
            'trend': 'improving' if recent_health > health_percentage else 'stable' if recent_health == health_percentage else 'declining'
        }


# Integration decorator for easy service protection
def with_robust_integration(service_name: str):
    """Decorator to wrap functions with robust integration protection"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return robust_integration_manager.call_service(service_name, func, *args, **kwargs)
        return wrapper
    return decorator


# Global robust integration manager instance
robust_integration_manager = RobustIntegrationManager()


def initialize_robust_integrations():
    """Initialize robust integration system"""
    robust_integration_manager.initialize()
    logging.info("Robust integration system initialized successfully")


def get_integration_health_report() -> Dict[str, Any]:
    """Get comprehensive integration health report"""
    return robust_integration_manager.get_overall_status()


def get_integration_recommendations() -> List[Dict[str, Any]]:
    """Get integration improvement recommendations"""
    return robust_integration_manager.get_service_recommendations()