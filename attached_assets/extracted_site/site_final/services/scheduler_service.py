"""
Advanced scheduler service for automated court website workflows
Comprehensive task scheduling, monitoring, and optimization automation
"""
import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Callable
from concurrent.futures import ThreadPoolExecutor
import threading
from functools import wraps

logger = logging.getLogger(__name__)


class SchedulerService:
    """Enterprise-grade task scheduler with monitoring and error handling"""
    
    def __init__(self):
        self.running = False
        self.scheduler_thread = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.task_history = []
        self.active_tasks = {}
        
    def task_wrapper(self, task_name: str):
        """Decorator to wrap scheduled tasks with monitoring"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = datetime.utcnow()
                task_id = f"{task_name}_{int(start_time.timestamp())}"
                
                self.active_tasks[task_id] = {
                    'name': task_name,
                    'start_time': start_time,
                    'status': 'running'
                }
                
                try:
                    logger.info(f"Starting scheduled task: {task_name}")
                    result = func(*args, **kwargs)
                    
                    end_time = datetime.utcnow()
                    duration = (end_time - start_time).total_seconds()
                    
                    self.task_history.append({
                        'task_name': task_name,
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration_seconds': duration,
                        'status': 'completed',
                        'result': str(result)[:500] if result else None
                    })
                    
                    logger.info(f"Task {task_name} completed in {duration:.2f}s")
                    
                except Exception as e:
                    end_time = datetime.utcnow()
                    duration = (end_time - start_time).total_seconds()
                    
                    self.task_history.append({
                        'task_name': task_name,
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration_seconds': duration,
                        'status': 'failed',
                        'error': str(e)
                    })
                    
                    logger.error(f"Task {task_name} failed after {duration:.2f}s: {e}")
                    
                finally:
                    self.active_tasks.pop(task_id, None)
                    
            return wrapper
        return decorator
    
    def schedule_database_maintenance(self):
        """Schedule comprehensive database maintenance tasks"""
        
        @self.task_wrapper("database_cleanup")
        def database_cleanup():
            """Clean up old database records"""
            from app import app
            with app.app_context():
                from services.database_service_optimized import db_service
                result = db_service.cleanup_old_data(90)
                return f"Cleaned up: {result}"
        
        @self.task_wrapper("database_optimization")
        def database_optimization():
            """Optimize database performance"""
            from app import app
            with app.app_context():
                from sqlalchemy import text
                from models import db
                
                # Update statistics
                db.session.execute(text("ANALYZE"))
                db.session.commit()
                
                # Refresh materialized views
                try:
                    db.session.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY daily_consultation_stats"))
                    db.session.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY chatbot_performance_stats"))
                    db.session.commit()
                    return "Database optimized and views refreshed"
                except Exception as e:
                    return f"Optimization completed with view refresh warning: {e}"
        
        @self.task_wrapper("performance_metrics_collection")
        def collect_performance_metrics():
            """Collect and store performance metrics"""
            from app import app
            with app.app_context():
                from services.database_service_optimized import db_service
                from services.cache_service_optimized import cache_service
                from models import db
                from sqlalchemy import text
                
                # Database metrics
                health, msg = db_service.check_connection()
                
                # Cache metrics
                cache_stats = cache_service.get_stats()
                primary_backend = cache_stats.get('primary_backend', {})
                
                # Store metrics
                metrics_data = [
                    ('database_health', 1 if health else 0, 'boolean', 'database'),
                    ('cache_hit_rate', primary_backend.get('hit_rate', 0), 'percentage', 'cache'),
                    ('cache_entries', primary_backend.get('total_keys', 0), 'count', 'cache')
                ]
                
                for metric_name, value, unit, component in metrics_data:
                    db.session.execute(
                        text("INSERT INTO performance_metrics (metric_name, metric_value, metric_unit, component) VALUES (:name, :value, :unit, :component)"),
                        {'name': metric_name, 'value': value, 'unit': unit, 'component': component}
                    )
                
                db.session.commit()
                return f"Collected {len(metrics_data)} performance metrics"
        
        # Schedule tasks
        schedule.every().day.at("02:00").do(database_cleanup)
        schedule.every().day.at("03:00").do(database_optimization)
        schedule.every().hour.do(collect_performance_metrics)
        
        logger.info("Database maintenance tasks scheduled")
    
    def schedule_cache_management(self):
        """Schedule cache optimization and management tasks"""
        
        @self.task_wrapper("cache_optimization")
        def optimize_cache():
            """Optimize cache performance"""
            from services.cache_service_optimized import cache_service
            
            stats = cache_service.get_stats()
            primary_backend = stats.get('primary_backend', {})
            hit_rate = primary_backend.get('hit_rate', 0)
            
            # Clear cache if hit rate is too low
            if hit_rate < 30 and primary_backend.get('total_keys', 0) > 100:
                cache_service.clear()
                return f"Cache cleared due to low hit rate: {hit_rate:.1f}%"
            
            return f"Cache performance acceptable: {hit_rate:.1f}% hit rate"
        
        @self.task_wrapper("cache_statistics")
        def log_cache_statistics():
            """Log cache performance statistics"""
            from services.cache_service_optimized import cache_service
            from app import app
            
            with app.app_context():
                from models import db
                from sqlalchemy import text
                
                stats = cache_service.get_stats()
                
                # Log to system_logs
                db.session.execute(
                    text("INSERT INTO system_logs (log_level, message, component, metadata) VALUES (:level, :message, :component, :metadata)"),
                    {
                        'level': 'INFO',
                        'message': 'Cache statistics collected',
                        'component': 'cache_management',
                        'metadata': str(stats)
                    }
                )
                db.session.commit()
                
                return f"Cache statistics logged: {stats}"
        
        # Schedule cache tasks
        schedule.every(30).minutes.do(optimize_cache)
        schedule.every().hour.at(":30").do(log_cache_statistics)
        
        logger.info("Cache management tasks scheduled")
    
    def schedule_health_monitoring(self):
        """Schedule comprehensive health monitoring tasks"""
        
        @self.task_wrapper("system_health_check")
        def system_health_check():
            """Comprehensive system health verification"""
            import psutil
            import requests
            
            health_report = {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
            
            # Application health
            try:
                response = requests.get('http://localhost:5000/health', timeout=10)
                health_report['app_status'] = response.status_code
                health_report['response_time_ms'] = response.elapsed.total_seconds() * 1000
            except Exception as e:
                health_report['app_status'] = 0
                health_report['app_error'] = str(e)
            
            # Database health
            from app import app
            with app.app_context():
                from services.database_service_optimized import db_service
                db_health, db_msg = db_service.check_connection()
                health_report['database_healthy'] = db_health
                health_report['database_message'] = db_msg
            
            # Check for alerts
            alerts = []
            if health_report['cpu_percent'] > 80:
                alerts.append(f"High CPU: {health_report['cpu_percent']:.1f}%")
            if health_report['memory_percent'] > 85:
                alerts.append(f"High Memory: {health_report['memory_percent']:.1f}%")
            if health_report.get('response_time_ms', 0) > 2000:
                alerts.append(f"Slow Response: {health_report['response_time_ms']:.0f}ms")
            
            if alerts:
                logger.warning(f"Health alerts: {', '.join(alerts)}")
                
                # Store critical alerts
                from models import db
                from sqlalchemy import text
                
                db.session.execute(
                    text("INSERT INTO system_logs (log_level, message, component, metadata) VALUES (:level, :message, :component, :metadata)"),
                    {
                        'level': 'WARNING',
                        'message': f"System health alerts: {', '.join(alerts)}",
                        'component': 'health_monitor',
                        'metadata': str(health_report)
                    }
                )
                db.session.commit()
            
            return f"Health check completed - {len(alerts)} alerts"
        
        @self.task_wrapper("chatbot_performance_check")
        def chatbot_performance_check():
            """Monitor chatbot performance and optimize if needed"""
            from services.chatbot_optimized import chatbot_service
            
            stats = chatbot_service.get_statistics()
            cache_stats = stats.get('cache_statistics', {})
            
            # Check cache hit rate
            hit_rate = cache_stats.get('hit_rate', 0)
            if hit_rate < 60:
                logger.warning(f"Low chatbot cache hit rate: {hit_rate:.1f}%")
            
            return f"Chatbot performance: {hit_rate:.1f}% cache hit rate, {stats.get('active_sessions', 0)} active sessions"
        
        # Schedule health monitoring
        schedule.every(5).minutes.do(system_health_check)
        schedule.every(15).minutes.do(chatbot_performance_check)
        
        logger.info("Health monitoring tasks scheduled")
    
    def schedule_content_management(self):
        """Schedule content optimization and management tasks"""
        
        @self.task_wrapper("content_cache_refresh")
        def refresh_content_cache():
            """Refresh content caches for optimal performance"""
            from services.content_optimized import content_service
            
            # Clear and refresh content cache
            content_service.clear_cache()
            
            # Pre-load frequently accessed content
            content_service.get_homepage_content()
            content_service.get_faq_data()
            content_service.get_news_data()
            
            cache_stats = content_service.get_cache_stats()
            return f"Content cache refreshed: {cache_stats['entries']} entries"
        
        @self.task_wrapper("news_validation")
        def validate_news_content():
            """Validate and optimize news content"""
            from services.content_optimized import content_service
            
            news_data = content_service.get_news_data()
            active_news = [item for item in news_data if item.get('ativo', True)]
            
            # Archive old news (older than 6 months)
            cutoff_date = datetime.utcnow() - timedelta(days=180)
            old_news = 0
            
            for item in active_news:
                try:
                    pub_date = datetime.fromisoformat(item.get('data_publicacao', ''))
                    if pub_date < cutoff_date:
                        old_news += 1
                except:
                    pass
            
            return f"News validation: {len(active_news)} active, {old_news} candidates for archival"
        
        # Schedule content management
        schedule.every().day.at("01:00").do(refresh_content_cache)
        schedule.every().week.do(validate_news_content)
        
        logger.info("Content management tasks scheduled")
    
    def start_scheduler(self):
        """Start the task scheduler"""
        if self.running:
            logger.info("Scheduler already running")
            return
        
        self.running = True
        
        # Schedule all task categories
        self.schedule_database_maintenance()
        self.schedule_cache_management()
        self.schedule_health_monitoring()
        self.schedule_content_management()
        
        def scheduler_loop():
            logger.info("Scheduler service started")
            while self.running:
                try:
                    schedule.run_pending()
                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    logger.error(f"Scheduler error: {e}")
                    time.sleep(60)
            
            logger.info("Scheduler service stopped")
        
        # Start scheduler in background thread
        self.scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Automated scheduler service initialized with comprehensive task management")
    
    def stop_scheduler(self):
        """Stop the task scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        self.executor.shutdown(wait=True)
        logger.info("Scheduler service stopped")
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status and task history"""
        # Clean old history (keep last 100 tasks)
        if len(self.task_history) > 100:
            self.task_history = self.task_history[-100:]
        
        # Recent task summary
        recent_tasks = self.task_history[-10:] if self.task_history else []
        
        return {
            'running': self.running,
            'active_tasks': len(self.active_tasks),
            'total_scheduled_jobs': len(schedule.jobs),
            'recent_tasks': recent_tasks,
            'next_run': schedule.next_run().isoformat() if schedule.jobs else None,
            'task_history_count': len(self.task_history)
        }
    
    def force_run_task(self, task_name: str) -> Dict[str, Any]:
        """Manually trigger a specific task"""
        try:
            # Find and run the task
            for job in schedule.jobs:
                if hasattr(job.job_func, '__name__') and task_name in job.job_func.__name__:
                    job.run()
                    return {'status': 'success', 'message': f'Task {task_name} executed'}
            
            return {'status': 'error', 'message': f'Task {task_name} not found'}
        except Exception as e:
            return {'status': 'error', 'message': f'Task execution failed: {e}'}


# Global scheduler service instance
scheduler_service = SchedulerService()


def start_automated_workflows():
    """Start all automated workflow processes"""
    try:
        scheduler_service.start_scheduler()
        
        # Also start workflow optimizer if available
        try:
            from utils.workflow_optimizer import start_production_workflows
            start_production_workflows()
        except ImportError:
            logger.info("Workflow optimizer not available, using scheduler only")
        
        return True
    except Exception as e:
        logger.error(f"Failed to start automated workflows: {e}")
        return False


def stop_automated_workflows():
    """Stop all automated workflow processes"""
    try:
        scheduler_service.stop_scheduler()
        
        # Also stop workflow optimizer if available
        try:
            from utils.workflow_optimizer import stop_production_workflows
            stop_production_workflows()
        except ImportError:
            pass
        
        return True
    except Exception as e:
        logger.error(f"Failed to stop automated workflows: {e}")
        return False