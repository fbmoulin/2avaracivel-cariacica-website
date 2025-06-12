"""
Advanced workflow optimization system for 2ª Vara Cível de Cariacica
Automated performance monitoring, maintenance, and optimization workflows
"""
import os
import time
import logging
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
import schedule
import threading

logger = logging.getLogger(__name__)

def start_workflow_engine():
    """Start the workflow optimization engine"""
    optimizer = WorkflowOptimizer()
    return optimizer.start_monitoring()


class WorkflowOptimizer:
    """Comprehensive workflow automation and optimization system"""
    
    def __init__(self):
        self.is_running = False
        self.monitoring_active = False
        self.maintenance_active = False
        self.performance_metrics = []
        self.alert_thresholds = {
            'cpu_percent': 80,
            'memory_percent': 85,
            'response_time_ms': 2000,
            'error_rate_percent': 5
        }
    
    def start_monitoring_workflow(self):
        """Start comprehensive system monitoring workflow"""
        if self.monitoring_active:
            logger.info("Monitoring workflow already active")
            return
        
        self.monitoring_active = True
        logger.info("Starting performance monitoring workflow")
        
        def monitor_loop():
            while self.monitoring_active:
                try:
                    metrics = self._collect_system_metrics()
                    self._analyze_performance(metrics)
                    self._check_alerts(metrics)
                    time.sleep(30)  # Monitor every 30 seconds
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(60)
        
        # Run monitoring in background thread
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system performance metrics"""
        metrics = {
            'timestamp': datetime.utcnow(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory()._asdict(),
            'disk': psutil.disk_usage('/')._asdict(),
            'network': self._get_network_stats(),
            'application': self._get_application_metrics()
        }
        
        # Store metrics for trend analysis
        self.performance_metrics.append(metrics)
        
        # Keep only last 24 hours of metrics
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.performance_metrics = [
            m for m in self.performance_metrics 
            if m['timestamp'] > cutoff
        ]
        
        return metrics
    
    def _get_network_stats(self) -> Dict[str, Any]:
        """Get network I/O statistics"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        except Exception as e:
            logger.warning(f"Network stats collection failed: {e}")
            return {}
    
    def _get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific performance metrics"""
        try:
            # Health check
            start_time = time.time()
            response = requests.get('http://localhost:5000/health', timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            app_metrics = {
                'status_code': response.status_code,
                'response_time_ms': response_time,
                'is_healthy': response.status_code == 200,
                'content_length': len(response.content)
            }
            
            # Database metrics
            try:
                from services.database_service_optimized import db_service
                db_health, db_msg = db_service.check_connection()
                app_metrics.update({
                    'database_healthy': db_health,
                    'database_message': db_msg
                })
            except Exception as e:
                app_metrics.update({
                    'database_healthy': False,
                    'database_message': str(e)
                })
            
            # Cache metrics
            try:
                from services.cache_service_optimized import cache_service
                cache_stats = cache_service.get_stats()
                app_metrics.update({
                    'cache_hit_rate': cache_stats.get('primary_backend', {}).get('hit_rate', 0),
                    'cache_backend': cache_stats.get('primary_backend', {}).get('backend', 'unknown')
                })
            except Exception as e:
                app_metrics['cache_error'] = str(e)
            
            return app_metrics
            
        except Exception as e:
            logger.error(f"Application metrics collection failed: {e}")
            return {
                'status_code': 0,
                'response_time_ms': 0,
                'is_healthy': False,
                'error': str(e)
            }
    
    def _analyze_performance(self, metrics: Dict[str, Any]):
        """Analyze performance trends and optimization opportunities"""
        try:
            # CPU trend analysis
            if len(self.performance_metrics) >= 10:
                recent_cpu = [m['cpu_percent'] for m in self.performance_metrics[-10:]]
                avg_cpu = sum(recent_cpu) / len(recent_cpu)
                
                if avg_cpu > 70:
                    logger.warning(f"High average CPU usage: {avg_cpu:.1f}%")
                    self._suggest_cpu_optimization()
            
            # Memory usage analysis
            memory_percent = metrics['memory']['percent']
            if memory_percent > 75:
                logger.warning(f"High memory usage: {memory_percent:.1f}%")
                self._suggest_memory_optimization()
            
            # Response time analysis
            app_metrics = metrics.get('application', {})
            response_time = app_metrics.get('response_time_ms', 0)
            if response_time > 1000:
                logger.warning(f"Slow response time: {response_time:.0f}ms")
                self._suggest_response_optimization()
                
        except Exception as e:
            logger.error(f"Performance analysis error: {e}")
    
    def _check_alerts(self, metrics: Dict[str, Any]):
        """Check for alert conditions and trigger notifications"""
        alerts = []
        
        # CPU alert
        if metrics['cpu_percent'] > self.alert_thresholds['cpu_percent']:
            alerts.append(f"High CPU usage: {metrics['cpu_percent']:.1f}%")
        
        # Memory alert
        if metrics['memory']['percent'] > self.alert_thresholds['memory_percent']:
            alerts.append(f"High memory usage: {metrics['memory']['percent']:.1f}%")
        
        # Response time alert
        app_metrics = metrics.get('application', {})
        response_time = app_metrics.get('response_time_ms', 0)
        if response_time > self.alert_thresholds['response_time_ms']:
            alerts.append(f"Slow response: {response_time:.0f}ms")
        
        # Application health alert
        if not app_metrics.get('is_healthy', False):
            alerts.append("Application unhealthy")
        
        if alerts:
            self._trigger_alerts(alerts)
    
    def _trigger_alerts(self, alerts: List[str]):
        """Trigger alert notifications"""
        alert_message = f"[{datetime.now().strftime('%H:%M:%S')}] ALERTS: {', '.join(alerts)}"
        logger.warning(alert_message)
        print(f"🚨 {alert_message}")
        
        # Store alert in database if available
        try:
            from services.database_service_optimized import db_service
            from app import app
            with app.app_context():
                from models import db
                from sqlalchemy import text
                
                db.session.execute(
                    text("INSERT INTO system_logs (log_level, message, component, metadata) VALUES (:level, :message, :component, :metadata)"),
                    {
                        'level': 'WARNING',
                        'message': alert_message,
                        'component': 'workflow_optimizer',
                        'metadata': '{"alert_type": "performance"}'
                    }
                )
                db.session.commit()
        except Exception as e:
            logger.error(f"Failed to store alert: {e}")
    
    def _suggest_cpu_optimization(self):
        """Suggest CPU optimization strategies"""
        suggestions = [
            "Consider enabling cache compression",
            "Optimize database queries",
            "Review background processes",
            "Consider horizontal scaling"
        ]
        logger.info(f"CPU optimization suggestions: {', '.join(suggestions)}")
    
    def _suggest_memory_optimization(self):
        """Suggest memory optimization strategies"""
        suggestions = [
            "Clear cache if hit rate is low",
            "Optimize database connection pool",
            "Review memory leaks in application",
            "Consider garbage collection tuning"
        ]
        logger.info(f"Memory optimization suggestions: {', '.join(suggestions)}")
    
    def _suggest_response_optimization(self):
        """Suggest response time optimization strategies"""
        suggestions = [
            "Increase cache timeout",
            "Optimize database indexes",
            "Review slow queries",
            "Consider CDN for static assets"
        ]
        logger.info(f"Response optimization suggestions: {', '.join(suggestions)}")
    
    def start_maintenance_workflow(self):
        """Start automated maintenance workflow"""
        if self.maintenance_active:
            logger.info("Maintenance workflow already active")
            return
        
        self.maintenance_active = True
        logger.info("Starting automated maintenance workflow")
        
        # Schedule maintenance tasks
        schedule.every().day.at("02:00").do(self._daily_maintenance)
        schedule.every().hour.at(":00").do(self._hourly_maintenance)
        schedule.every(15).minutes.do(self._periodic_maintenance)
        
        def maintenance_loop():
            while self.maintenance_active:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Maintenance scheduler error: {e}")
                    time.sleep(300)  # Wait 5 minutes on error
        
        # Run maintenance scheduler in background
        maintenance_thread = threading.Thread(target=maintenance_loop, daemon=True)
        maintenance_thread.start()
    
    def _daily_maintenance(self):
        """Daily maintenance tasks"""
        logger.info("Starting daily maintenance")
        
        try:
            from app import app
            with app.app_context():
                from services.database_service_optimized import db_service
                
                # Database cleanup
                cleanup_result = db_service.cleanup_old_data(90)
                logger.info(f"Data cleanup completed: {cleanup_result}")
                
                # Refresh materialized views
                from sqlalchemy import text
                from models import db
                
                try:
                    db.session.execute(text("REFRESH MATERIALIZED VIEW daily_consultation_stats"))
                    db.session.execute(text("REFRESH MATERIALIZED VIEW chatbot_performance_stats"))
                    db.session.commit()
                    logger.info("Materialized views refreshed")
                except Exception as e:
                    logger.warning(f"Materialized view refresh failed: {e}")
                
                # Performance metrics cleanup
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                db.session.execute(
                    text("DELETE FROM performance_metrics WHERE recorded_at < :cutoff"),
                    {'cutoff': cutoff_date}
                )
                db.session.commit()
                logger.info("Performance metrics cleaned up")
                
        except Exception as e:
            logger.error(f"Daily maintenance error: {e}")
    
    def _hourly_maintenance(self):
        """Hourly maintenance tasks"""
        logger.info("Starting hourly maintenance")
        
        try:
            # Cache statistics update
            from services.cache_service_optimized import cache_service
            stats = cache_service.get_stats()
            
            # Log cache performance
            primary_stats = stats.get('primary_backend', {})
            hit_rate = primary_stats.get('hit_rate', 0)
            
            if hit_rate < 50:
                logger.warning(f"Low cache hit rate: {hit_rate:.1f}%")
            
            logger.info(f"Cache performance: {hit_rate:.1f}% hit rate")
            
        except Exception as e:
            logger.error(f"Hourly maintenance error: {e}")
    
    def _periodic_maintenance(self):
        """15-minute periodic maintenance tasks"""
        try:
            # Application health verification
            from app import app
            with app.app_context():
                from services.database_service_optimized import db_service
                
                health, msg = db_service.check_connection()
                if not health:
                    logger.error(f"Database health check failed: {msg}")
                
        except Exception as e:
            logger.error(f"Periodic maintenance error: {e}")
    
    def stop_workflows(self):
        """Stop all workflow processes"""
        self.monitoring_active = False
        self.maintenance_active = False
        logger.info("All workflows stopped")
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status and metrics"""
        return {
            'monitoring_active': self.monitoring_active,
            'maintenance_active': self.maintenance_active,
            'metrics_collected': len(self.performance_metrics),
            'last_update': datetime.utcnow().isoformat(),
            'alert_thresholds': self.alert_thresholds
        }


# Global workflow optimizer instance
workflow_optimizer = WorkflowOptimizer()


def start_production_workflows():
    """Start all production workflows"""
    try:
        workflow_optimizer.start_monitoring_workflow()
        workflow_optimizer.start_maintenance_workflow()
        logger.info("Production workflows started successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to start production workflows: {e}")
        return False


def stop_production_workflows():
    """Stop all production workflows"""
    try:
        workflow_optimizer.stop_workflows()
        logger.info("Production workflows stopped successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to stop production workflows: {e}")
        return False


if __name__ == '__main__':
    # Start workflows when run directly
    print("Starting Court Website Workflow Optimizer...")
    start_production_workflows()
    
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Stopping workflows...")
        stop_production_workflows()