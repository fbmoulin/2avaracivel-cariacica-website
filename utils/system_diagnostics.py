"""
Advanced system diagnostics and health monitoring
Provides comprehensive system analysis and automated issue detection
"""
import os
import sys
import psutil
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import subprocess
import socket


class SystemDiagnostics:
    """Comprehensive system diagnostics and monitoring"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.start_time = datetime.now()
    
    def run_full_diagnostic(self) -> Dict[str, Any]:
        """Run complete system diagnostic check"""
        diagnostics = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self.get_system_info(),
            'resource_usage': self.get_resource_usage(),
            'network_status': self.check_network_connectivity(),
            'database_status': self.check_database_connection(),
            'service_health': self.check_service_health(),
            'environment_variables': self.check_environment_variables(),
            'disk_usage': self.get_disk_usage(),
            'process_info': self.get_process_info(),
            'recommendations': []
        }
        
        # Generate recommendations based on diagnostics
        diagnostics['recommendations'] = self.generate_recommendations(diagnostics)
        
        return diagnostics
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information"""
        try:
            return {
                'platform': sys.platform,
                'python_version': sys.version,
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'uptime': str(datetime.now() - self.start_time),
                'hostname': socket.gethostname()
            }
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {'error': str(e)}
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': memory.percent,
                'memory_available': memory.available,
                'disk_percent': (disk.used / disk.total) * 100,
                'disk_free': disk.free,
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
        except Exception as e:
            self.logger.error(f"Error getting resource usage: {e}")
            return {'error': str(e)}
    
    def check_network_connectivity(self) -> Dict[str, Any]:
        """Check network connectivity to essential services"""
        endpoints = {
            'google_dns': '8.8.8.8',
            'cloudflare_dns': '1.1.1.1',
            'openai_api': 'api.openai.com'
        }
        
        results = {}
        for name, endpoint in endpoints.items():
            try:
                if endpoint.startswith('api.'):
                    # HTTP check for APIs
                    import requests
                    response = requests.get(f"https://{endpoint}", timeout=5)
                    results[name] = {'status': 'connected', 'response_code': response.status_code}
                else:
                    # Socket check for IP addresses
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    result = sock.connect_ex((endpoint, 53))
                    sock.close()
                    results[name] = {'status': 'connected' if result == 0 else 'failed'}
            except Exception as e:
                results[name] = {'status': 'failed', 'error': str(e)}
        
        return results
    
    def check_database_connection(self) -> Dict[str, Any]:
        """Check database connection status"""
        try:
            from app import db
            from flask import current_app
            
            # Simple query to test connection
            result = db.session.execute(db.text("SELECT 1")).scalar()
            
            return {
                'status': 'connected' if result == 1 else 'failed',
                'database_url': current_app.config.get('SQLALCHEMY_DATABASE_URI', '').split('@')[-1] if '@' in current_app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'local'
            }
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def check_service_health(self) -> Dict[str, Any]:
        """Check health of application services"""
        services = {}
        
        # Check OpenAI service
        try:
            openai_key = os.environ.get('OPENAI_API_KEY')
            services['openai'] = {
                'configured': bool(openai_key),
                'key_length': len(openai_key) if openai_key else 0
            }
        except Exception as e:
            services['openai'] = {'status': 'error', 'error': str(e)}
        
        # Check cache service
        try:
            from services.cache_service import cache_service
            test_key = 'health_check_test'
            cache_service.set(test_key, 'test_value', 60)
            retrieved = cache_service.get(test_key)
            cache_service.delete(test_key)
            
            services['cache'] = {
                'status': 'working' if retrieved == 'test_value' else 'failed',
                'backend': type(cache_service.cache_backend).__name__
            }
        except Exception as e:
            services['cache'] = {'status': 'error', 'error': str(e)}
        
        # Check integration service
        try:
            from services.integration_service import integration_service
            health = integration_service.get_system_health()
            services['integration'] = {
                'status': health.get('overall_status', 'unknown'),
                'registered_services': len(integration_service._service_registry)
            }
        except Exception as e:
            services['integration'] = {'status': 'error', 'error': str(e)}
        
        return services
    
    def check_environment_variables(self) -> Dict[str, Any]:
        """Check required environment variables"""
        required_vars = [
            'DATABASE_URL',
            'SESSION_SECRET',
            'OPENAI_API_KEY'
        ]
        
        results = {}
        for var in required_vars:
            value = os.environ.get(var)
            results[var] = {
                'present': bool(value),
                'length': len(value) if value else 0,
                'type': 'set' if value else 'missing'
            }
        
        return results
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information"""
        try:
            usage = psutil.disk_usage('/')
            return {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': (usage.used / usage.total) * 100
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_process_info(self) -> Dict[str, Any]:
        """Get current process information"""
        try:
            process = psutil.Process()
            return {
                'pid': process.pid,
                'memory_info': process.memory_info()._asdict(),
                'cpu_percent': process.cpu_percent(),
                'num_threads': process.num_threads(),
                'create_time': datetime.fromtimestamp(process.create_time()).isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def generate_recommendations(self, diagnostics: Dict[str, Any]) -> List[str]:
        """Generate system optimization recommendations"""
        recommendations = []
        
        # Memory usage recommendations
        memory_percent = diagnostics.get('resource_usage', {}).get('memory_percent', 0)
        if memory_percent > 80:
            recommendations.append("High memory usage detected. Consider optimizing memory-intensive operations.")
        
        # CPU usage recommendations
        cpu_percent = diagnostics.get('resource_usage', {}).get('cpu_percent', 0)
        if cpu_percent > 80:
            recommendations.append("High CPU usage detected. Consider optimizing computational operations.")
        
        # Disk space recommendations
        disk_percent = diagnostics.get('disk_usage', {}).get('percent', 0)
        if disk_percent > 85:
            recommendations.append("Low disk space. Consider cleaning up temporary files or logs.")
        
        # Service health recommendations
        services = diagnostics.get('service_health', {})
        for service, status in services.items():
            if status.get('status') in ['failed', 'error']:
                recommendations.append(f"Service {service} is not functioning properly. Check configuration.")
        
        # Environment variable recommendations
        env_vars = diagnostics.get('environment_variables', {})
        missing_vars = [var for var, info in env_vars.items() if not info.get('present')]
        if missing_vars:
            recommendations.append(f"Missing environment variables: {', '.join(missing_vars)}")
        
        return recommendations
    
    def export_diagnostics(self, filepath: str = None) -> str:
        """Export diagnostics to file"""
        if not filepath:
            filepath = f"system_diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        diagnostics = self.run_full_diagnostic()
        
        try:
            with open(filepath, 'w') as f:
                json.dump(diagnostics, f, indent=2, default=str)
            
            self.logger.info(f"Diagnostics exported to {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Error exporting diagnostics: {e}")
            return None


# Global diagnostics instance
system_diagnostics = SystemDiagnostics()