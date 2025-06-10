"""
Performance monitoring and optimization utilities
Real-time monitoring of application performance metrics
"""
import time
import psutil
import threading
from datetime import datetime, timedelta
from collections import deque
from flask import current_app, request, g
import functools


class PerformanceMonitor:
    """Monitor application performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'response_times': deque(maxlen=1000),
            'memory_usage': deque(maxlen=100),
            'cpu_usage': deque(maxlen=100),
            'request_count': 0,
            'error_count': 0,
            'slow_requests': deque(maxlen=100)
        }
        self.monitoring = True
        self.slow_request_threshold = 2.0  # seconds
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        def monitor_system():
            while self.monitoring:
                try:
                    # Monitor system resources
                    memory = psutil.virtual_memory().percent
                    cpu = psutil.cpu_percent(interval=1)
                    
                    self.metrics['memory_usage'].append({
                        'timestamp': datetime.now(),
                        'value': memory
                    })
                    
                    self.metrics['cpu_usage'].append({
                        'timestamp': datetime.now(),
                        'value': cpu
                    })
                    
                    # Log alerts if thresholds exceeded
                    if memory > 85:
                        current_app.logger.warning(f"High memory usage: {memory}%")
                    
                    if cpu > 85:
                        current_app.logger.warning(f"High CPU usage: {cpu}%")
                
                except Exception as e:
                    if current_app:
                        current_app.logger.error(f"Performance monitoring error: {e}")
                
                time.sleep(30)  # Monitor every 30 seconds
        
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()
    
    def measure_request_time(self, f):
        """Decorator to measure request execution time"""
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                duration = end_time - start_time
                
                # Record metrics
                self.metrics['response_times'].append({
                    'timestamp': datetime.now(),
                    'duration': duration,
                    'endpoint': request.endpoint if request else 'unknown'
                })
                
                self.metrics['request_count'] += 1
                
                # Log slow requests
                if duration > self.slow_request_threshold:
                    self.metrics['slow_requests'].append({
                        'timestamp': datetime.now(),
                        'duration': duration,
                        'endpoint': request.endpoint if request else 'unknown',
                        'url': request.url if request else 'unknown'
                    })
                    
                    if current_app:
                        current_app.logger.warning(
                            f"Slow request: {request.endpoint} took {duration:.2f}s"
                        )
        
        return decorated_function
    
    def get_performance_stats(self):
        """Get current performance statistics"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        # Recent response times
        recent_times = [
            m for m in self.metrics['response_times']
            if m['timestamp'] > hour_ago
        ]
        
        # Calculate statistics
        if recent_times:
            durations = [m['duration'] for m in recent_times]
            avg_response_time = sum(durations) / len(durations)
            max_response_time = max(durations)
            min_response_time = min(durations)
        else:
            avg_response_time = max_response_time = min_response_time = 0
        
        # Recent system metrics
        recent_memory = [
            m for m in self.metrics['memory_usage']
            if m['timestamp'] > hour_ago
        ]
        
        recent_cpu = [
            m for m in self.metrics['cpu_usage']
            if m['timestamp'] > hour_ago
        ]
        
        current_memory = recent_memory[-1]['value'] if recent_memory else 0
        current_cpu = recent_cpu[-1]['value'] if recent_cpu else 0
        
        return {
            'response_times': {
                'average': round(avg_response_time, 3),
                'maximum': round(max_response_time, 3),
                'minimum': round(min_response_time, 3),
                'count': len(recent_times)
            },
            'system': {
                'memory_usage': round(current_memory, 1),
                'cpu_usage': round(current_cpu, 1)
            },
            'requests': {
                'total': self.metrics['request_count'],
                'errors': self.metrics['error_count'],
                'slow_requests': len(self.metrics['slow_requests'])
            },
            'timestamp': now.isoformat()
        }
    
    def record_error(self):
        """Record an error occurrence"""
        self.metrics['error_count'] += 1


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def setup_performance_monitoring(app):
    """Setup Flask performance monitoring"""
    
    # Start background monitoring
    performance_monitor.start_monitoring()
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # Record metrics
            performance_monitor.metrics['response_times'].append({
                'timestamp': datetime.now(),
                'duration': duration,
                'endpoint': request.endpoint,
                'status_code': response.status_code
            })
            
            performance_monitor.metrics['request_count'] += 1
            
            # Log slow requests
            if duration > performance_monitor.slow_request_threshold:
                performance_monitor.metrics['slow_requests'].append({
                    'timestamp': datetime.now(),
                    'duration': duration,
                    'endpoint': request.endpoint,
                    'url': request.url,
                    'method': request.method
                })
                
                app.logger.warning(
                    f"Slow request: {request.method} {request.endpoint} took {duration:.2f}s"
                )
            
            # Record errors
            if response.status_code >= 400:
                performance_monitor.record_error()
        
        return response


def optimize_database_queries():
    """Database optimization recommendations"""
    recommendations = []
    
    try:
        from app_factory import db
        from sqlalchemy import text
        
        # Check for missing indexes (PostgreSQL specific)
        if 'postgresql' in current_app.config.get('SQLALCHEMY_DATABASE_URI', ''):
            result = db.session.execute(text("""
                SELECT schemaname, tablename, attname, n_distinct, correlation
                FROM pg_stats
                WHERE schemaname = 'public'
                AND n_distinct > 100
                AND correlation < 0.1
            """)).fetchall()
            
            if result:
                recommendations.append({
                    'type': 'missing_indexes',
                    'description': 'Consider adding indexes for frequently queried columns',
                    'details': [dict(row) for row in result]
                })
        
        # Check for large tables without recent VACUUM (PostgreSQL)
        if 'postgresql' in current_app.config.get('SQLALCHEMY_DATABASE_URI', ''):
            result = db.session.execute(text("""
                SELECT schemaname, tablename, n_tup_ins + n_tup_upd + n_tup_del as total_changes
                FROM pg_stat_user_tables
                WHERE n_tup_ins + n_tup_upd + n_tup_del > 1000
                ORDER BY total_changes DESC
                LIMIT 5
            """)).fetchall()
            
            if result:
                recommendations.append({
                    'type': 'maintenance_needed',
                    'description': 'Tables with high modification rates may need VACUUM',
                    'details': [dict(row) for row in result]
                })
    
    except Exception as e:
        current_app.logger.error(f"Database optimization check failed: {e}")
    
    return recommendations


def get_optimization_recommendations():
    """Get performance optimization recommendations"""
    recommendations = []
    stats = performance_monitor.get_performance_stats()
    
    # Response time recommendations
    if stats['response_times']['average'] > 1.0:
        recommendations.append({
            'category': 'response_time',
            'priority': 'high',
            'description': f"Average response time is {stats['response_times']['average']}s. Consider caching frequently accessed data.",
            'actions': [
                'Implement Redis caching',
                'Optimize database queries',
                'Add CDN for static assets'
            ]
        })
    
    # Memory usage recommendations
    if stats['system']['memory_usage'] > 80:
        recommendations.append({
            'category': 'memory',
            'priority': 'high',
            'description': f"High memory usage: {stats['system']['memory_usage']}%",
            'actions': [
                'Implement pagination for large datasets',
                'Clear unused cache entries',
                'Optimize database connection pooling'
            ]
        })
    
    # CPU usage recommendations
    if stats['system']['cpu_usage'] > 80:
        recommendations.append({
            'category': 'cpu',
            'priority': 'high',
            'description': f"High CPU usage: {stats['system']['cpu_usage']}%",
            'actions': [
                'Implement async processing for heavy tasks',
                'Optimize algorithms in hot paths',
                'Consider horizontal scaling'
            ]
        })
    
    # Error rate recommendations
    error_rate = (stats['requests']['errors'] / max(stats['requests']['total'], 1)) * 100
    if error_rate > 5:
        recommendations.append({
            'category': 'errors',
            'priority': 'medium',
            'description': f"Error rate is {error_rate:.1f}%",
            'actions': [
                'Review error logs for common issues',
                'Implement better input validation',
                'Add circuit breaker pattern'
            ]
        })
    
    # Database recommendations
    db_recommendations = optimize_database_queries()
    recommendations.extend(db_recommendations)
    
    return recommendations