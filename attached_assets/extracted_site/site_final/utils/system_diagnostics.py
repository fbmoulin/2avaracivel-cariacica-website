"""
Comprehensive system diagnostics and health monitoring for court website
Advanced diagnostic capabilities with performance analysis and optimization recommendations
"""
import os
import sys
import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class SystemDiagnostics:
    """Enterprise-grade system diagnostics and monitoring"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.diagnostic_history = []
        
    def run_comprehensive_diagnostics(self) -> Dict[str, Any]:
        """Execute comprehensive system diagnostics"""
        logger.info("Starting comprehensive system diagnostics")
        
        diagnostic_report = {
            'timestamp': datetime.utcnow().isoformat(),
            'system_info': self._get_system_information(),
            'environment_check': self._check_environment_variables(),
            'application_health': self._check_application_health(),
            'database_diagnostics': self._check_database_health(),
            'cache_diagnostics': self._check_cache_performance(),
            'performance_metrics': self._collect_performance_metrics(),
            'security_check': self._run_security_diagnostics(),
            'recommendations': []
        }
        
        # Generate recommendations based on findings
        diagnostic_report['recommendations'] = self._generate_recommendations(diagnostic_report)
        
        # Store diagnostic report
        self.diagnostic_history.append(diagnostic_report)
        
        # Keep only last 24 hours of diagnostics
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.diagnostic_history = [
            d for d in self.diagnostic_history 
            if datetime.fromisoformat(d['timestamp']) > cutoff
        ]
        
        logger.info("Comprehensive diagnostics completed")
        return diagnostic_report
    
    def _get_system_information(self) -> Dict[str, Any]:
        """Collect comprehensive system information"""
        try:
            cpu_info = psutil.cpu_freq()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'platform': sys.platform,
                'python_version': sys.version.split()[0],
                'cpu_count': psutil.cpu_count(),
                'cpu_physical_cores': psutil.cpu_count(logical=False),
                'cpu_frequency_mhz': cpu_info.current if cpu_info else None,
                'total_memory_gb': round(memory.total / (1024**3), 2),
                'available_memory_gb': round(memory.available / (1024**3), 2),
                'memory_usage_percent': memory.percent,
                'total_disk_gb': round(disk.total / (1024**3), 2),
                'available_disk_gb': round(disk.free / (1024**3), 2),
                'disk_usage_percent': round((disk.used / disk.total) * 100, 2),
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                'uptime_hours': round((time.time() - psutil.boot_time()) / 3600, 2)
            }
        except Exception as e:
            logger.error(f"System information collection failed: {e}")
            return {'error': str(e)}
    
    def _check_environment_variables(self) -> Dict[str, Any]:
        """Verify critical environment variables"""
        critical_vars = {
            'DATABASE_URL': 'Database connection string',
            'SESSION_SECRET': 'Session security key',
            'OPENAI_API_KEY': 'OpenAI API access key'
        }
        
        optional_vars = {
            'REDIS_URL': 'Redis cache connection',
            'FLASK_ENV': 'Application environment',
            'PORT': 'Application port'
        }
        
        env_status = {
            'critical_variables': {},
            'optional_variables': {},
            'missing_critical': [],
            'recommendations': []
        }
        
        # Check critical variables
        for var, description in critical_vars.items():
            value = os.environ.get(var)
            env_status['critical_variables'][var] = {
                'set': bool(value),
                'description': description,
                'length': len(value) if value else 0
            }
            if not value:
                env_status['missing_critical'].append(var)
        
        # Check optional variables
        for var, description in optional_vars.items():
            value = os.environ.get(var)
            env_status['optional_variables'][var] = {
                'set': bool(value),
                'description': description,
                'value': value if var in ['FLASK_ENV', 'PORT'] else None
            }
        
        # Generate recommendations
        if env_status['missing_critical']:
            env_status['recommendations'].append(
                f"Set missing critical variables: {', '.join(env_status['missing_critical'])}"
            )
        
        if not os.environ.get('REDIS_URL'):
            env_status['recommendations'].append(
                "Consider setting REDIS_URL for improved cache performance"
            )
        
        return env_status
    
    def _check_application_health(self) -> Dict[str, Any]:
        """Comprehensive application health check"""
        app_health = {
            'status': 'unknown',
            'response_time_ms': 0,
            'endpoints': {},
            'errors': []
        }
        
        # Test critical endpoints
        endpoints_to_test = [
            ('/', 'Homepage'),
            ('/health', 'Health Check'),
            ('/sobre', 'About Page'),
            ('/faq', 'FAQ Page'),
            ('/contato', 'Contact Page')
        ]
        
        healthy_endpoints = 0
        total_response_time = 0
        
        for endpoint, description in endpoints_to_test:
            try:
                start_time = time.time()
                response = requests.get(f'http://localhost:5000{endpoint}', timeout=15)
                response_time = (time.time() - start_time) * 1000
                
                endpoint_status = {
                    'status_code': response.status_code,
                    'response_time_ms': round(response_time, 2),
                    'content_length': len(response.content),
                    'healthy': 200 <= response.status_code < 400
                }
                
                if endpoint_status['healthy']:
                    healthy_endpoints += 1
                    total_response_time += response_time
                
                app_health['endpoints'][endpoint] = endpoint_status
                
            except Exception as e:
                app_health['endpoints'][endpoint] = {
                    'error': str(e),
                    'healthy': False
                }
                app_health['errors'].append(f"{endpoint}: {str(e)}")
        
        # Overall application status
        if healthy_endpoints == len(endpoints_to_test):
            app_health['status'] = 'healthy'
            app_health['response_time_ms'] = round(total_response_time / healthy_endpoints, 2)
        elif healthy_endpoints > 0:
            app_health['status'] = 'partially_healthy'
            app_health['response_time_ms'] = round(total_response_time / healthy_endpoints, 2)
        else:
            app_health['status'] = 'unhealthy'
        
        return app_health
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Comprehensive database health diagnostics"""
        try:
            from app import app
            with app.app_context():
                from services.database_service_optimized import db_service
                from sqlalchemy import text
                from models import db
                
                db_diagnostics = {
                    'connection_health': {},
                    'performance_metrics': {},
                    'table_statistics': {},
                    'index_performance': {},
                    'recommendations': []
                }
                
                # Connection health
                health, message = db_service.check_connection()
                db_diagnostics['connection_health'] = {
                    'healthy': health,
                    'message': message,
                    'connection_time_ms': 0
                }
                
                if health:
                    # Performance metrics
                    start_time = time.time()
                    result = db.session.execute(text("SELECT COUNT(*) FROM contact"))
                    query_time = (time.time() - start_time) * 1000
                    
                    db_diagnostics['performance_metrics'] = {
                        'simple_query_time_ms': round(query_time, 2),
                        'connection_pool_size': 15,  # From configuration
                        'active_connections': 1  # Current session
                    }
                    
                    # Table statistics
                    tables_stats = db.session.execute(text("""
                        SELECT table_name, 
                               pg_size_pretty(pg_total_relation_size('public.'||table_name)) as size,
                               pg_total_relation_size('public.'||table_name) as size_bytes
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                        ORDER BY pg_total_relation_size('public.'||table_name) DESC
                    """)).fetchall()
                    
                    db_diagnostics['table_statistics'] = [
                        {
                            'table_name': row.table_name,
                            'size_pretty': row.size,
                            'size_bytes': row.size_bytes
                        }
                        for row in tables_stats
                    ]
                    
                    # Index performance check
                    try:
                        index_stats = db.session.execute(text("""
                            SELECT indexrelname, idx_tup_read, idx_tup_fetch
                            FROM pg_stat_user_indexes 
                            WHERE idx_tup_read > 0
                            ORDER BY idx_tup_read DESC
                            LIMIT 10
                        """)).fetchall()
                        
                        db_diagnostics['index_performance'] = [
                            {
                                'index_name': row.indexrelname,
                                'tuples_read': row.idx_tup_read,
                                'tuples_fetched': row.idx_tup_fetch,
                                'efficiency': round((row.idx_tup_fetch / row.idx_tup_read) * 100, 2) if row.idx_tup_read > 0 else 0
                            }
                            for row in index_stats
                        ]
                    except Exception as e:
                        db_diagnostics['index_performance'] = {'error': str(e)}
                
                return db_diagnostics
                
        except Exception as e:
            logger.error(f"Database diagnostics failed: {e}")
            return {
                'error': str(e),
                'connection_health': {'healthy': False, 'message': str(e)}
            }
    
    def _check_cache_performance(self) -> Dict[str, Any]:
        """Comprehensive cache performance diagnostics"""
        try:
            from services.cache_service_optimized import cache_service
            
            cache_stats = cache_service.get_stats()
            
            cache_diagnostics = {
                'primary_backend': cache_stats.get('primary_backend', {}),
                'fallback_backend': cache_stats.get('fallback_backend', {}),
                'performance_analysis': {},
                'recommendations': []
            }
            
            # Analyze cache performance
            primary = cache_diagnostics['primary_backend']
            hit_rate = primary.get('hit_rate', 0)
            
            if hit_rate < 50:
                cache_diagnostics['recommendations'].append(
                    f"Low cache hit rate ({hit_rate:.1f}%) - consider cache warming or TTL optimization"
                )
            elif hit_rate > 85:
                cache_diagnostics['performance_analysis']['status'] = 'excellent'
            elif hit_rate > 70:
                cache_diagnostics['performance_analysis']['status'] = 'good'
            else:
                cache_diagnostics['performance_analysis']['status'] = 'needs_improvement'
            
            return cache_diagnostics
            
        except Exception as e:
            logger.error(f"Cache diagnostics failed: {e}")
            return {'error': str(e)}
    
    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive performance metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network metrics
            net_io = psutil.net_io_counters()
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return {
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': round((disk.used / disk.total) * 100, 2),
                    'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                },
                'process': {
                    'memory_rss_mb': round(process_memory.rss / (1024 * 1024), 2),
                    'memory_vms_mb': round(process_memory.vms / (1024 * 1024), 2),
                    'cpu_percent': process.cpu_percent(),
                    'num_threads': process.num_threads(),
                    'open_files': len(process.open_files()),
                    'connections': len(process.connections())
                }
            }
            
        except Exception as e:
            logger.error(f"Performance metrics collection failed: {e}")
            return {'error': str(e)}
    
    def _run_security_diagnostics(self) -> Dict[str, Any]:
        """Basic security diagnostics"""
        security_check = {
            'environment_security': {},
            'application_security': {},
            'recommendations': []
        }
        
        # Environment security
        security_check['environment_security'] = {
            'debug_mode': os.environ.get('FLASK_DEBUG', '0') == '1',
            'session_secret_set': bool(os.environ.get('SESSION_SECRET')),
            'production_ready': os.environ.get('FLASK_ENV') == 'production'
        }
        
        # Application security recommendations
        if security_check['environment_security']['debug_mode']:
            security_check['recommendations'].append("Disable debug mode in production")
        
        if not security_check['environment_security']['session_secret_set']:
            security_check['recommendations'].append("Set a strong SESSION_SECRET")
        
        return security_check
    
    def _generate_recommendations(self, diagnostic_report: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on diagnostic results"""
        recommendations = []
        
        # System performance recommendations
        system_metrics = diagnostic_report.get('performance_metrics', {}).get('system', {})
        if system_metrics.get('cpu_percent', 0) > 80:
            recommendations.append("High CPU usage detected - consider optimization or scaling")
        
        if system_metrics.get('memory_percent', 0) > 85:
            recommendations.append("High memory usage - consider memory optimization or increase resources")
        
        # Application health recommendations
        app_health = diagnostic_report.get('application_health', {})
        if app_health.get('status') != 'healthy':
            recommendations.append("Application health issues detected - investigate endpoint failures")
        
        if app_health.get('response_time_ms', 0) > 1000:
            recommendations.append("Slow response times - consider caching or database optimization")
        
        # Database recommendations
        db_health = diagnostic_report.get('database_diagnostics', {})
        if not db_health.get('connection_health', {}).get('healthy', False):
            recommendations.append("Database connection issues - check configuration and connectivity")
        
        # Cache recommendations
        cache_diagnostics = diagnostic_report.get('cache_diagnostics', {})
        if isinstance(cache_diagnostics.get('recommendations'), list):
            recommendations.extend(cache_diagnostics['recommendations'])
        
        # Environment recommendations
        env_check = diagnostic_report.get('environment_check', {})
        if env_check.get('missing_critical'):
            recommendations.append(f"Set missing environment variables: {', '.join(env_check['missing_critical'])}")
        
        # Security recommendations
        security_check = diagnostic_report.get('security_check', {})
        if isinstance(security_check.get('recommendations'), list):
            recommendations.extend(security_check['recommendations'])
        
        return list(set(recommendations))  # Remove duplicates
    
    def get_diagnostic_summary(self) -> Dict[str, Any]:
        """Get summary of recent diagnostics"""
        if not self.diagnostic_history:
            return {'status': 'no_diagnostics', 'message': 'No diagnostics available'}
        
        latest = self.diagnostic_history[-1]
        
        return {
            'last_run': latest['timestamp'],
            'system_status': self._determine_overall_status(latest),
            'critical_issues': self._extract_critical_issues(latest),
            'recommendations_count': len(latest.get('recommendations', [])),
            'total_diagnostics_run': len(self.diagnostic_history)
        }
    
    def _determine_overall_status(self, diagnostic_report: Dict[str, Any]) -> str:
        """Determine overall system status from diagnostic report"""
        app_status = diagnostic_report.get('application_health', {}).get('status', 'unknown')
        db_healthy = diagnostic_report.get('database_diagnostics', {}).get('connection_health', {}).get('healthy', False)
        
        if app_status == 'healthy' and db_healthy:
            return 'healthy'
        elif app_status in ['healthy', 'partially_healthy'] and db_healthy:
            return 'warning'
        else:
            return 'critical'
    
    def _extract_critical_issues(self, diagnostic_report: Dict[str, Any]) -> List[str]:
        """Extract critical issues from diagnostic report"""
        critical_issues = []
        
        # Application issues
        app_health = diagnostic_report.get('application_health', {})
        if app_health.get('status') == 'unhealthy':
            critical_issues.append("Application is unhealthy")
        
        # Database issues
        db_health = diagnostic_report.get('database_diagnostics', {})
        if not db_health.get('connection_health', {}).get('healthy', False):
            critical_issues.append("Database connection failed")
        
        # Environment issues
        env_check = diagnostic_report.get('environment_check', {})
        if env_check.get('missing_critical'):
            critical_issues.append(f"Missing critical environment variables: {', '.join(env_check['missing_critical'])}")
        
        return critical_issues


# Global diagnostics instance
system_diagnostics = SystemDiagnostics()


def run_system_diagnostics() -> Dict[str, Any]:
    """Run comprehensive system diagnostics"""
    return system_diagnostics.run_comprehensive_diagnostics()


def get_diagnostics_summary() -> Dict[str, Any]:
    """Get diagnostic summary"""
    return system_diagnostics.get_diagnostic_summary()


if __name__ == '__main__':
    # Run diagnostics when executed directly
    print("Running Court Website System Diagnostics...")
    result = run_system_diagnostics()
    
    print(f"\nDiagnostic Results:")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Recommendations: {len(result.get('recommendations', []))}")
    
    if result.get('recommendations'):
        print("\nRecommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"{i}. {rec}")