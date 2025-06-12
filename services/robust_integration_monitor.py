"""
Robust Integration Monitor for 2ª Vara Cível de Cariacica
Comprehensive health monitoring, auto-recovery, and stability management
"""

import os
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
import traceback

try:
    from services.integration_service import CircuitBreaker, ServiceStatus
except ImportError:
    # Fallback circuit breaker implementation
    class ServiceStatus:
        HEALTHY = "healthy"
        DEGRADED = "degraded"
        FAILING = "failing"
        DOWN = "down"
    
    class CircuitBreaker:
        def __init__(self, failure_threshold=3, recovery_timeout=30, success_threshold=2):
            self.failure_threshold = failure_threshold
            self.recovery_timeout = recovery_timeout
            self.success_threshold = success_threshold
            self.state = type('State', (), {'failure_count': 0, 'status': ServiceStatus.HEALTHY})()
        
        def _on_failure(self):
            self.state.failure_count += 1

try:
    from services.database_service import DatabaseService
except ImportError:
    DatabaseService = None

try:
    from services.chatbot import ChatbotService
except ImportError:
    ChatbotService = None

try:
    from services.cache_service import CacheService
except ImportError:
    CacheService = None

try:
    from services.email_service import EmailService
except ImportError:
    EmailService = None


class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DOWN = "down"


@dataclass
class ServiceHealth:
    name: str
    status: HealthStatus
    last_check: datetime
    response_time: float
    error_count: int
    uptime_percentage: float
    details: Dict[str, Any]
    recovery_attempts: int = 0


class RobustIntegrationMonitor:
    """Comprehensive integration monitoring and auto-recovery system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.services = {}
        self.circuit_breakers = {}
        self.health_history = []
        self.monitoring_active = False
        self.recovery_strategies = {}
        self._lock = threading.Lock()
        
        # Initialize service monitors
        self._initialize_service_monitors()
        self._setup_recovery_strategies()
        
    def _initialize_service_monitors(self):
        """Initialize monitoring for available critical services"""
        self.services = {}
        
        # Only initialize services that are available
        if DatabaseService:
            try:
                self.services['database'] = DatabaseService()
            except Exception as e:
                self.logger.warning(f"Failed to initialize database service: {e}")
        
        if ChatbotService:
            try:
                self.services['chatbot'] = ChatbotService()
            except Exception as e:
                self.logger.warning(f"Failed to initialize chatbot service: {e}")
                
        if CacheService:
            try:
                self.services['cache'] = CacheService()
            except Exception as e:
                self.logger.warning(f"Failed to initialize cache service: {e}")
                
        if EmailService:
            try:
                self.services['email'] = EmailService()
            except Exception as e:
                self.logger.warning(f"Failed to initialize email service: {e}")
        
        # Initialize circuit breakers for each available service
        for service_name in self.services.keys():
            self.circuit_breakers[service_name] = CircuitBreaker(
                failure_threshold=3,
                recovery_timeout=30,
                success_threshold=2
            )
    
    def _setup_recovery_strategies(self):
        """Define auto-recovery strategies for each service"""
        self.recovery_strategies = {
            'database': self._recover_database,
            'chatbot': self._recover_chatbot,
            'cache': self._recover_cache,
            'email': self._recover_email
        }
    
    def start_monitoring(self, check_interval: int = 30):
        """Start continuous health monitoring"""
        if self.monitoring_active:
            self.logger.warning("Monitoring already active")
            return
            
        self.monitoring_active = True
        self.logger.info("Starting robust integration monitoring")
        
        def monitor_loop():
            while self.monitoring_active:
                try:
                    self._perform_health_checks()
                    self._analyze_trends()
                    self._trigger_recovery_if_needed()
                    time.sleep(check_interval)
                except Exception as e:
                    self.logger.error(f"Monitoring loop error: {e}")
                    time.sleep(5)  # Brief pause before retry
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def _perform_health_checks(self):
        """Perform comprehensive health checks on all services"""
        with self._lock:
            for service_name, service in self.services.items():
                try:
                    start_time = time.time()
                    health = self._check_service_health(service_name, service)
                    response_time = time.time() - start_time
                    
                    # Update service health record
                    self._update_service_health(service_name, health, response_time)
                    
                except Exception as e:
                    self.logger.error(f"Health check failed for {service_name}: {e}")
                    self._record_service_failure(service_name, str(e))
    
    def _check_service_health(self, service_name: str, service) -> Dict[str, Any]:
        """Check health of individual service"""
        health_data = {'status': 'unknown', 'details': {}}
        
        try:
            if service_name == 'database':
                is_healthy, message = service.check_connection()
                health_data['status'] = 'healthy' if is_healthy else 'critical'
                health_data['details'] = {'message': message}
                
            elif service_name == 'chatbot':
                # Test basic chatbot functionality
                if service.openai_client:
                    health_data['status'] = 'healthy'
                    health_data['details'] = {'openai_available': True}
                else:
                    health_data['status'] = 'warning'
                    health_data['details'] = {'openai_available': False, 'fallback_active': True}
                    
            elif service_name == 'cache':
                # Test cache operations
                test_key = f"health_check_{int(time.time())}"
                service.set(test_key, "test_value", 10)
                retrieved = service.get(test_key)
                if retrieved == "test_value":
                    health_data['status'] = 'healthy'
                else:
                    health_data['status'] = 'warning'
                health_data['details'] = {'cache_test': retrieved == "test_value"}
                
            elif service_name == 'email':
                # Check email configuration
                if service.email_user and service.email_password:
                    health_data['status'] = 'healthy'
                    health_data['details'] = {'configured': True}
                else:
                    health_data['status'] = 'warning'
                    health_data['details'] = {'configured': False}
                    
        except Exception as e:
            health_data['status'] = 'critical'
            health_data['details'] = {'error': str(e)}
            
        return health_data
    
    def _update_service_health(self, service_name: str, health_data: Dict, response_time: float):
        """Update service health metrics"""
        status_map = {
            'healthy': HealthStatus.HEALTHY,
            'warning': HealthStatus.WARNING,
            'critical': HealthStatus.CRITICAL,
            'unknown': HealthStatus.DOWN
        }
        
        current_time = datetime.now()
        
        # Calculate uptime percentage (last 24 hours)
        uptime_percentage = self._calculate_uptime(service_name)
        
        # Get error count from circuit breaker
        circuit_breaker = self.circuit_breakers.get(service_name)
        error_count = circuit_breaker.state.failure_count if circuit_breaker else 0
        
        service_health = ServiceHealth(
            name=service_name,
            status=status_map.get(health_data['status'], HealthStatus.DOWN),
            last_check=current_time,
            response_time=response_time,
            error_count=error_count,
            uptime_percentage=uptime_percentage,
            details=health_data['details']
        )
        
        # Store in history for trend analysis
        self.health_history.append({
            'timestamp': current_time,
            'service': service_name,
            'health': asdict(service_health)
        })
        
        # Trim history to last 24 hours
        cutoff_time = current_time - timedelta(hours=24)
        self.health_history = [
            h for h in self.health_history 
            if h['timestamp'] > cutoff_time
        ]
    
    def _calculate_uptime(self, service_name: str) -> float:
        """Calculate service uptime percentage over last 24 hours"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        service_records = [
            h for h in self.health_history 
            if h['service'] == service_name and h['timestamp'] > cutoff_time
        ]
        
        if not service_records:
            return 100.0  # Assume healthy if no history
            
        healthy_count = sum(
            1 for record in service_records 
            if record['health']['status'] in ['healthy', 'warning']
        )
        
        return (healthy_count / len(service_records)) * 100.0
    
    def _analyze_trends(self):
        """Analyze health trends and predict issues"""
        for service_name in self.services.keys():
            recent_records = [
                h for h in self.health_history[-10:]  # Last 10 checks
                if h['service'] == service_name
            ]
            
            if len(recent_records) >= 3:
                # Check for degrading trend
                recent_statuses = [r['health']['status'] for r in recent_records[-3:]]
                if all(status in ['critical', 'down'] for status in recent_statuses):
                    self.logger.warning(f"Service {service_name} showing degrading trend")
                    self._trigger_proactive_recovery(service_name)
    
    def _trigger_recovery_if_needed(self):
        """Trigger recovery for services that need it"""
        for service_name, circuit_breaker in self.circuit_breakers.items():
            if circuit_breaker.state.status in [ServiceStatus.DOWN, ServiceStatus.FAILING]:
                self._attempt_service_recovery(service_name)
    
    def _trigger_proactive_recovery(self, service_name: str):
        """Trigger proactive recovery before complete failure"""
        self.logger.info(f"Triggering proactive recovery for {service_name}")
        self._attempt_service_recovery(service_name)
    
    def _attempt_service_recovery(self, service_name: str):
        """Attempt to recover a failing service"""
        if service_name not in self.recovery_strategies:
            self.logger.warning(f"No recovery strategy for {service_name}")
            return
            
        try:
            recovery_func = self.recovery_strategies[service_name]
            success = recovery_func()
            
            if success:
                self.logger.info(f"Successfully recovered service: {service_name}")
                # Reset circuit breaker on successful recovery
                self.circuit_breakers[service_name].state.failure_count = 0
                self.circuit_breakers[service_name].state.status = ServiceStatus.HEALTHY
            else:
                self.logger.error(f"Failed to recover service: {service_name}")
                
        except Exception as e:
            self.logger.error(f"Recovery attempt failed for {service_name}: {e}")
    
    def _recover_database(self) -> bool:
        """Attempt database recovery"""
        try:
            from app_factory import db
            # Force connection pool refresh
            db.engine.dispose()
            db.session.remove()
            
            # Test reconnection
            is_healthy, _ = DatabaseService.check_connection()
            return is_healthy
        except Exception as e:
            self.logger.error(f"Database recovery failed: {e}")
            return False
    
    def _recover_chatbot(self) -> bool:
        """Attempt chatbot service recovery"""
        try:
            chatbot_service = self.services['chatbot']
            chatbot_service.setup_openai()
            return chatbot_service.openai_client is not None
        except Exception as e:
            self.logger.error(f"Chatbot recovery failed: {e}")
            return False
    
    def _recover_cache(self) -> bool:
        """Attempt cache service recovery"""
        try:
            cache_service = self.services['cache']
            # Reinitialize cache backend
            cache_service.cache_backend = cache_service._initialize_cache_backend()
            return True
        except Exception as e:
            self.logger.error(f"Cache recovery failed: {e}")
            return False
    
    def _recover_email(self) -> bool:
        """Attempt email service recovery"""
        try:
            # Email service doesn't need active recovery, just validation
            email_service = self.services['email']
            return bool(email_service.email_user and email_service.email_password)
        except Exception as e:
            self.logger.error(f"Email recovery failed: {e}")
            return False
    
    def _record_service_failure(self, service_name: str, error_message: str):
        """Record service failure"""
        circuit_breaker = self.circuit_breakers.get(service_name)
        if circuit_breaker:
            circuit_breaker._on_failure()
        
        self.logger.error(f"Service failure recorded for {service_name}: {error_message}")
    
    def get_system_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive system health report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'services': {},
            'summary': {
                'total_services': len(self.services),
                'healthy_services': 0,
                'warning_services': 0,
                'critical_services': 0
            }
        }
        
        # Get latest health for each service
        for service_name in self.services.keys():
            service_records = [
                h for h in self.health_history 
                if h['service'] == service_name
            ]
            
            if service_records:
                latest = service_records[-1]['health']
                report['services'][service_name] = latest
                
                # Update summary counts
                status = latest['status']
                if status == 'healthy':
                    report['summary']['healthy_services'] += 1
                elif status == 'warning':
                    report['summary']['warning_services'] += 1
                else:
                    report['summary']['critical_services'] += 1
            
        # Determine overall status
        if report['summary']['critical_services'] > 0:
            report['overall_status'] = 'critical'
        elif report['summary']['warning_services'] > 0:
            report['overall_status'] = 'warning'
        else:
            report['overall_status'] = 'healthy'
            
        return report
    
    def stop_monitoring(self):
        """Stop monitoring system"""
        self.monitoring_active = False
        self.logger.info("Integration monitoring stopped")


# Global monitor instance
integration_monitor = RobustIntegrationMonitor()