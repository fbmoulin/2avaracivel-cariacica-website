"""
Centralized Integration Manager for Robust System Operations
Coordinates all service integrations with comprehensive monitoring and health management
"""
import logging
import threading
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from services.robust_integration_service import (
    robust_integration_manager, 
    initialize_robust_integrations
)
from services.robust_database_service import (
    robust_db_service, 
    initialize_robust_database,
    get_database_health
)
from services.robust_openai_service import (
    robust_openai_service,
    initialize_robust_openai,
    get_openai_health
)


@dataclass
class SystemHealthMetrics:
    """Comprehensive system health metrics"""
    overall_status: str
    healthy_services: int
    total_services: int
    critical_issues: List[str]
    warnings: List[str]
    performance_score: float
    uptime_percentage: float
    last_check: datetime


class IntegrationManager:
    """Central coordination for all system integrations"""
    
    def __init__(self):
        self.services = {}
        self.health_monitor = None
        self.logger = logging.getLogger(__name__)
        self._initialized = False
        self._health_cache = {}
        self._cache_ttl = 30  # Cache health checks for 30 seconds
        self._monitoring_thread = None
        self._monitoring_active = False
        
    def initialize(self):
        """Initialize all integration services"""
        if self._initialized:
            return
        
        try:
            # Initialize robust integration manager
            initialize_robust_integrations()
            
            # Initialize database service
            initialize_robust_database()
            
            # Initialize OpenAI service (if API key available)
            import os
            if os.environ.get('OPENAI_API_KEY'):
                initialize_robust_openai()
                self.logger.info("OpenAI service initialized with API key")
            else:
                self.logger.warning("OpenAI API key not found - service will use fallback responses")
            
            # Register services for monitoring
            self.services = {
                'database': {
                    'service': robust_db_service,
                    'health_check': get_database_health,
                    'critical': True
                },
                'openai': {
                    'service': robust_openai_service,
                    'health_check': get_openai_health,
                    'critical': False
                },
                'integration_manager': {
                    'service': robust_integration_manager,
                    'health_check': lambda: robust_integration_manager.get_overall_status(),
                    'critical': True
                }
            }
            
            # Start background monitoring
            self._start_monitoring()
            
            self._initialized = True
            self.logger.info("Integration manager initialized successfully with robust services")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize integration manager: {str(e)}")
            raise
    
    def _start_monitoring(self):
        """Start background health monitoring"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        self.logger.info("Background health monitoring started")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self._monitoring_active:
            try:
                # Perform health checks on all services
                for service_name in self.services:
                    self._check_service_health(service_name)
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(30)  # Shorter delay on error
    
    def _check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check health of a specific service with caching"""
        cache_key = f"health_{service_name}"
        now = datetime.now()
        
        # Check cache first
        if cache_key in self._health_cache:
            cached_data, cache_time = self._health_cache[cache_key]
            if now - cache_time < timedelta(seconds=self._cache_ttl):
                return cached_data
        
        # Perform health check
        try:
            if service_name not in self.services:
                return {'status': 'unknown', 'error': 'Service not registered'}
            
            service_config = self.services[service_name]
            health_data = service_config['health_check']()
            
            # Cache result
            self._health_cache[cache_key] = (health_data, now)
            
            return health_data
            
        except Exception as e:
            error_data = {
                'status': 'error',
                'error': str(e),
                'timestamp': now.isoformat()
            }
            self._health_cache[cache_key] = (error_data, now)
            return error_data
    
    def get_system_health(self) -> SystemHealthMetrics:
        """Get comprehensive system health status"""
        healthy_services = 0
        total_services = len(self.services)
        critical_issues = []
        warnings = []
        performance_scores = []
        
        for service_name, service_config in self.services.items():
            health_data = self._check_service_health(service_name)
            
            status = health_data.get('status', 'unknown')
            is_critical = service_config.get('critical', False)
            
            if status in ['healthy', 'operational']:
                healthy_services += 1
                performance_scores.append(100)
            elif status in ['degraded', 'warning']:
                if is_critical:
                    warnings.append(f"{service_name}: {health_data.get('error', 'Service degraded')}")
                performance_scores.append(70)
            else:  # unhealthy, error, failed
                if is_critical:
                    critical_issues.append(f"{service_name}: {health_data.get('error', 'Service failed')}")
                else:
                    warnings.append(f"{service_name}: {health_data.get('error', 'Service failed')}")
                performance_scores.append(0)
        
        # Calculate overall metrics
        overall_status = 'healthy'
        if critical_issues:
            overall_status = 'critical'
        elif warnings:
            overall_status = 'degraded'
        
        performance_score = sum(performance_scores) / len(performance_scores) if performance_scores else 0
        uptime_percentage = (healthy_services / total_services * 100) if total_services > 0 else 0
        
        return SystemHealthMetrics(
            overall_status=overall_status,
            healthy_services=healthy_services,
            total_services=total_services,
            critical_issues=critical_issues,
            warnings=warnings,
            performance_score=round(performance_score, 2),
            uptime_percentage=round(uptime_percentage, 2),
            last_check=datetime.now()
        )
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed status of all services"""
        system_health = self.get_system_health()
        service_details = {}
        
        for service_name in self.services:
            service_details[service_name] = self._check_service_health(service_name)
        
        return {
            'system_overview': {
                'status': system_health.overall_status,
                'healthy_services': system_health.healthy_services,
                'total_services': system_health.total_services,
                'performance_score': system_health.performance_score,
                'uptime_percentage': system_health.uptime_percentage
            },
            'critical_issues': system_health.critical_issues,
            'warnings': system_health.warnings,
            'service_details': service_details,
            'last_updated': system_health.last_check.isoformat(),
            'recommendations': self._get_system_recommendations(system_health, service_details)
        }
    
    def _get_system_recommendations(self, health: SystemHealthMetrics, details: Dict[str, Any]) -> List[str]:
        """Generate system improvement recommendations"""
        recommendations = []
        
        if health.performance_score < 80:
            recommendations.append("System performance below optimal - review service configurations")
        
        if health.uptime_percentage < 95:
            recommendations.append("Service availability concerns - consider implementing redundancy")
        
        if health.critical_issues:
            recommendations.append("Critical issues detected - immediate attention required")
        
        # Service-specific recommendations
        for service_name, service_health in details.items():
            if service_health.get('recommendations'):
                for rec in service_health['recommendations']:
                    recommendations.append(f"{service_name}: {rec}")
        
        return recommendations
    
    def optimize_system(self) -> Dict[str, Any]:
        """Apply system-wide optimizations"""
        optimization_results = {
            'optimizations_applied': [],
            'errors': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Optimize database service
            if 'database' in self.services and hasattr(robust_db_service, 'optimize_performance'):
                db_optimization = robust_db_service.optimize_performance()
                if db_optimization['status'] == 'success':
                    optimization_results['optimizations_applied'].extend([
                        f"Database: {opt}" for opt in db_optimization.get('optimizations_applied', [])
                    ])
                else:
                    optimization_results['errors'].append(f"Database optimization failed: {db_optimization.get('error')}")
            
            # Clear health cache to force fresh checks
            self._health_cache.clear()
            optimization_results['optimizations_applied'].append("Health check cache cleared")
            
            # Reset circuit breakers if needed
            for service_name in ['database', 'openai', 'external_api']:
                if robust_integration_manager.force_reset_circuit(service_name):
                    optimization_results['optimizations_applied'].append(f"Circuit breaker reset for {service_name}")
            
            self.logger.info("System optimizations completed successfully")
            
        except Exception as e:
            optimization_results['errors'].append(f"System optimization error: {str(e)}")
            self.logger.error(f"System optimization failed: {str(e)}")
        
        return optimization_results
    
    def get_integration_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration report"""
        system_health = self.get_system_health()
        detailed_status = self.get_detailed_status()
        
        # Get performance metrics from individual services
        performance_data = {}
        try:
            if hasattr(robust_db_service, 'get_performance_metrics'):
                performance_data['database'] = robust_db_service.get_performance_metrics()
            
            if robust_openai_service and hasattr(robust_openai_service, 'get_performance_metrics'):
                performance_data['openai'] = robust_openai_service.get_performance_metrics()
            
            performance_data['integration_manager'] = robust_integration_manager.get_overall_status()
            
        except Exception as e:
            self.logger.warning(f"Could not gather all performance metrics: {str(e)}")
        
        return {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_type': 'comprehensive_integration_analysis',
                'system_version': '2.0_robust'
            },
            'executive_summary': {
                'overall_health': system_health.overall_status,
                'system_uptime': system_health.uptime_percentage,
                'performance_score': system_health.performance_score,
                'services_operational': f"{system_health.healthy_services}/{system_health.total_services}",
                'critical_issues_count': len(system_health.critical_issues),
                'warnings_count': len(system_health.warnings)
            },
            'detailed_analysis': detailed_status,
            'performance_metrics': performance_data,
            'reliability_assessment': {
                'circuit_breaker_states': self._get_circuit_breaker_summary(),
                'error_rates': self._calculate_error_rates(performance_data),
                'response_times': self._analyze_response_times(performance_data)
            }
        }
    
    def _get_circuit_breaker_summary(self) -> Dict[str, str]:
        """Get summary of circuit breaker states"""
        try:
            integration_status = robust_integration_manager.get_overall_status()
            circuit_states = {}
            
            for service_name, details in integration_status.get('service_details', {}).items():
                state = details.get('state', 'unknown')
                circuit_states[service_name] = state
            
            return circuit_states
        except Exception:
            return {}
    
    def _calculate_error_rates(self, performance_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate error rates for services"""
        error_rates = {}
        
        try:
            # Database error rate
            if 'database' in performance_data:
                db_metrics = performance_data['database'].get('performance_analysis', {})
                error_rates['database'] = db_metrics.get('error_rate_percentage', 0)
            
            # OpenAI error rate
            if 'openai' in performance_data:
                openai_metrics = performance_data['openai'].get('openai_metrics', {})
                total_requests = openai_metrics.get('total_requests', 1)
                failed_requests = openai_metrics.get('failed_requests', 0)
                error_rates['openai'] = (failed_requests / total_requests) * 100 if total_requests > 0 else 0
            
        except Exception as e:
            self.logger.warning(f"Error calculating error rates: {str(e)}")
        
        return error_rates
    
    def _analyze_response_times(self, performance_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze response times across services"""
        response_times = {}
        
        try:
            # Database response time
            if 'database' in performance_data:
                db_metrics = performance_data['database'].get('database_metrics', {})
                response_times['database_ms'] = db_metrics.get('average_query_time_ms', 0)
            
            # OpenAI response time
            if 'openai' in performance_data:
                openai_metrics = performance_data['openai'].get('openai_metrics', {})
                response_times['openai_ms'] = openai_metrics.get('average_response_time_ms', 0)
            
        except Exception as e:
            self.logger.warning(f"Error analyzing response times: {str(e)}")
        
        return response_times
    
    def shutdown(self):
        """Graceful shutdown of integration manager"""
        self.logger.info("Shutting down integration manager...")
        
        self._monitoring_active = False
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5)
        
        # Perform graceful shutdown of services
        try:
            if hasattr(robust_integration_manager, 'graceful_shutdown'):
                robust_integration_manager.graceful_shutdown()
        except Exception as e:
            self.logger.error(f"Error during integration manager shutdown: {str(e)}")
        
        self.logger.info("Integration manager shutdown completed")


# Global integration manager instance
integration_manager = IntegrationManager()


def initialize_integration_system():
    """Initialize the complete integration system"""
    integration_manager.initialize()
    logging.info("Complete integration system initialized with robust services")


def get_system_status() -> Dict[str, Any]:
    """Get comprehensive system status"""
    return integration_manager.get_detailed_status()


def get_system_health_metrics() -> SystemHealthMetrics:
    """Get system health metrics"""
    return integration_manager.get_system_health()


def optimize_integrations() -> Dict[str, Any]:
    """Apply system-wide optimizations"""
    return integration_manager.optimize_system()


def generate_integration_report() -> Dict[str, Any]:
    """Generate comprehensive integration report"""
    return integration_manager.get_integration_report()