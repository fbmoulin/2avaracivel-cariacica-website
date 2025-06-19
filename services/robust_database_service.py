"""
Robust Database Service with Advanced Connection Management
Provides connection pooling, transaction management, and automatic recovery
"""
import logging
import time
import threading
from typing import Dict, Any, Optional, Callable, List, Tuple
from datetime import datetime, timedelta
from contextlib import contextmanager
from sqlalchemy import create_engine, text, event
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError, OperationalError
from sqlalchemy.pool import QueuePool
from functools import wraps
import os


class DatabaseConfig:
    """Advanced database configuration"""
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL', 'sqlite:///court.db')
        self.pool_size = int(os.environ.get('DB_POOL_SIZE', '20'))
        self.max_overflow = int(os.environ.get('DB_MAX_OVERFLOW', '30'))
        self.pool_timeout = int(os.environ.get('DB_POOL_TIMEOUT', '30'))
        self.pool_recycle = int(os.environ.get('DB_POOL_RECYCLE', '3600'))
        self.pool_pre_ping = True
        self.echo = os.environ.get('DB_ECHO', 'false').lower() == 'true'
        
        # Connection retry settings
        self.max_retries = 3
        self.retry_delay = 1.0
        self.exponential_backoff = True
        
        # Health check settings
        self.health_check_interval = 60
        self.connection_timeout = 10


class ConnectionPoolMonitor:
    """Monitor database connection pool performance"""
    
    def __init__(self):
        self.stats = {
            'total_connections_created': 0,
            'total_connections_closed': 0,
            'active_connections': 0,
            'pool_hits': 0,
            'pool_misses': 0,
            'connection_errors': 0,
            'query_count': 0,
            'slow_queries': 0,
            'average_query_time': 0.0
        }
        self._lock = threading.Lock()
        self.slow_query_threshold = 2.0  # seconds
        
    def record_connection_created(self):
        with self._lock:
            self.stats['total_connections_created'] += 1
            self.stats['active_connections'] += 1
    
    def record_connection_closed(self):
        with self._lock:
            self.stats['total_connections_closed'] += 1
            self.stats['active_connections'] = max(0, self.stats['active_connections'] - 1)
    
    def record_pool_hit(self):
        with self._lock:
            self.stats['pool_hits'] += 1
    
    def record_pool_miss(self):
        with self._lock:
            self.stats['pool_misses'] += 1
    
    def record_connection_error(self):
        with self._lock:
            self.stats['connection_errors'] += 1
    
    def record_query(self, execution_time: float):
        with self._lock:
            self.stats['query_count'] += 1
            
            # Update average query time (exponential moving average)
            if self.stats['average_query_time'] == 0:
                self.stats['average_query_time'] = execution_time
            else:
                self.stats['average_query_time'] = (
                    self.stats['average_query_time'] * 0.9 + execution_time * 0.1
                )
            
            if execution_time > self.slow_query_threshold:
                self.stats['slow_queries'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            pool_efficiency = 0
            total_pool_requests = self.stats['pool_hits'] + self.stats['pool_misses']
            if total_pool_requests > 0:
                pool_efficiency = (self.stats['pool_hits'] / total_pool_requests) * 100
            
            return {
                **self.stats.copy(),
                'pool_efficiency_percentage': round(pool_efficiency, 2),
                'slow_query_percentage': round(
                    (self.stats['slow_queries'] / max(1, self.stats['query_count'])) * 100, 2
                ),
                'timestamp': datetime.now().isoformat()
            }


class RobustDatabaseService:
    """Enhanced database service with comprehensive reliability features"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = None
        self.monitor = ConnectionPoolMonitor()
        self.logger = logging.getLogger(__name__)
        self._health_status = 'unknown'
        self._last_health_check = None
        self._connection_retries = {}
        self._lock = threading.Lock()
        
    def initialize(self):
        """Initialize robust database service"""
        try:
            engine_config = {
                'poolclass': QueuePool,
                'pool_size': self.config.pool_size,
                'max_overflow': self.config.max_overflow,
                'pool_timeout': self.config.pool_timeout,
                'pool_recycle': self.config.pool_recycle,
                'pool_pre_ping': self.config.pool_pre_ping,
                'echo': self.config.echo,
                'connect_args': {}
            }
            
            # PostgreSQL-specific optimizations
            if 'postgresql' in self.config.database_url:
                engine_config['connect_args'].update({
                    'connect_timeout': self.config.connection_timeout,
                    'options': '-c default_transaction_isolation=read_committed'
                })
            
            self.engine = create_engine(self.config.database_url, **engine_config)
            
            # Set up event listeners for monitoring
            self._setup_event_listeners()
            
            # Verify connection
            self._verify_connection()
            
            self._health_status = 'healthy'
            self.logger.info("Robust database service initialized successfully")
            
        except Exception as e:
            self._health_status = 'failed'
            self.logger.error(f"Failed to initialize database service: {str(e)}")
            raise
    
    def _setup_event_listeners(self):
        """Setup SQLAlchemy event listeners for monitoring"""
        
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            self.monitor.record_connection_created()
            self.logger.debug("Database connection created")
        
        @event.listens_for(self.engine, "close")
        def receive_close(dbapi_connection, connection_record):
            self.monitor.record_connection_closed()
            self.logger.debug("Database connection closed")
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            self.monitor.record_pool_hit()
        
        @event.listens_for(self.engine, "connect")
        def receive_connect_error(dbapi_connection, connection_record):
            if hasattr(connection_record, 'info') and connection_record.info.get('error'):
                self.monitor.record_connection_error()
    
    def _verify_connection(self):
        """Verify database connection is working"""
        with self.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        self.logger.info("Database connection verified successfully")
    
    @contextmanager
    def get_connection(self, retries: int = None):
        """Get database connection with automatic retry logic"""
        if retries is None:
            retries = self.config.max_retries
        
        connection = None
        last_error = None
        
        for attempt in range(retries + 1):
            try:
                connection = self.engine.connect()
                yield connection
                return
                
            except (DisconnectionError, OperationalError) as e:
                last_error = e
                self.monitor.record_connection_error()
                self.logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < retries:
                    delay = self._calculate_retry_delay(attempt)
                    self.logger.info(f"Retrying database connection in {delay} seconds...")
                    time.sleep(delay)
                else:
                    self.logger.error(f"All database connection attempts failed")
                    
            except Exception as e:
                last_error = e
                self.logger.error(f"Unexpected database error: {str(e)}")
                break
                
            finally:
                if connection:
                    try:
                        connection.close()
                    except Exception:
                        pass
        
        if last_error:
            raise last_error
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay with exponential backoff"""
        if self.config.exponential_backoff:
            return min(self.config.retry_delay * (2 ** attempt), 30.0)
        return self.config.retry_delay
    
    def execute_query(self, query: str, parameters: Dict = None, retries: int = None) -> Any:
        """Execute query with monitoring and retry logic"""
        start_time = time.time()
        
        try:
            with self.get_connection(retries=retries) as conn:
                if parameters:
                    result = conn.execute(text(query), parameters)
                else:
                    result = conn.execute(text(query))
                
                execution_time = time.time() - start_time
                self.monitor.record_query(execution_time)
                
                if execution_time > self.monitor.slow_query_threshold:
                    self.logger.warning(f"Slow query detected: {execution_time:.2f}s - {query[:100]}...")
                
                return result
                
        except Exception as e:
            execution_time = time.time() - start_time
            self.monitor.record_query(execution_time)
            self.logger.error(f"Query execution failed: {str(e)} - Query: {query[:100]}...")
            raise
    
    def execute_transaction(self, operations: List[Callable], retries: int = None) -> Any:
        """Execute multiple operations in a transaction with retry logic"""
        if retries is None:
            retries = self.config.max_retries
        
        for attempt in range(retries + 1):
            try:
                with self.get_connection() as conn:
                    trans = conn.begin()
                    try:
                        results = []
                        for operation in operations:
                            result = operation(conn)
                            results.append(result)
                        
                        trans.commit()
                        self.logger.debug(f"Transaction completed successfully with {len(operations)} operations")
                        return results
                        
                    except Exception as e:
                        trans.rollback()
                        self.logger.warning(f"Transaction rolled back due to error: {str(e)}")
                        raise
                        
            except Exception as e:
                if attempt < retries:
                    delay = self._calculate_retry_delay(attempt)
                    self.logger.info(f"Retrying transaction in {delay} seconds...")
                    time.sleep(delay)
                else:
                    self.logger.error(f"Transaction failed after {retries + 1} attempts")
                    raise
    
    def check_health(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health_data = {
            'status': 'unknown',
            'timestamp': datetime.now().isoformat(),
            'connection_pool': {},
            'performance': {},
            'errors': []
        }
        
        try:
            # Test basic connectivity
            start_time = time.time()
            with self.get_connection(retries=1) as conn:
                conn.execute(text("SELECT 1"))
            
            connection_time = time.time() - start_time
            
            # Get pool statistics
            pool_stats = self.monitor.get_stats()
            
            health_data.update({
                'status': 'healthy',
                'connection_time_ms': round(connection_time * 1000, 2),
                'connection_pool': {
                    'size': self.config.pool_size,
                    'max_overflow': self.config.max_overflow,
                    'active_connections': pool_stats['active_connections'],
                    'pool_efficiency': pool_stats['pool_efficiency_percentage']
                },
                'performance': {
                    'total_queries': pool_stats['query_count'],
                    'average_query_time_ms': round(pool_stats['average_query_time'] * 1000, 2),
                    'slow_query_percentage': pool_stats['slow_query_percentage'],
                    'connection_errors': pool_stats['connection_errors']
                }
            })
            
            # Add warnings for performance issues
            if pool_stats['slow_query_percentage'] > 10:
                health_data['errors'].append("High percentage of slow queries detected")
            
            if pool_stats['connection_errors'] > 10:
                health_data['errors'].append("High number of connection errors detected")
                
            if pool_stats['pool_efficiency_percentage'] < 80:
                health_data['errors'].append("Low connection pool efficiency")
            
            self._health_status = 'healthy'
            
        except Exception as e:
            health_data.update({
                'status': 'unhealthy',
                'error': str(e),
                'errors': [f"Health check failed: {str(e)}"]
            })
            self._health_status = 'unhealthy'
            self.logger.error(f"Database health check failed: {str(e)}")
        
        self._last_health_check = datetime.now()
        return health_data
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        pool_stats = self.monitor.get_stats()
        
        # Calculate additional metrics
        error_rate = 0
        if pool_stats['query_count'] > 0:
            error_rate = (pool_stats['connection_errors'] / pool_stats['query_count']) * 100
        
        return {
            'database_metrics': pool_stats,
            'connection_pool_status': {
                'configured_pool_size': self.config.pool_size,
                'configured_max_overflow': self.config.max_overflow,
                'pool_timeout': self.config.pool_timeout,
                'pool_recycle_time': self.config.pool_recycle
            },
            'performance_analysis': {
                'error_rate_percentage': round(error_rate, 2),
                'queries_per_connection': round(
                    pool_stats['query_count'] / max(1, pool_stats['total_connections_created']), 2
                ),
                'connection_reuse_efficiency': round(
                    (pool_stats['total_connections_created'] - pool_stats['total_connections_closed']) 
                    / max(1, pool_stats['total_connections_created']) * 100, 2
                )
            },
            'recommendations': self._get_performance_recommendations(pool_stats)
        }
    
    def _get_performance_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        if stats['slow_query_percentage'] > 15:
            recommendations.append("Consider optimizing slow queries or adding database indexes")
        
        if stats['pool_efficiency_percentage'] < 70:
            recommendations.append("Consider increasing connection pool size")
        
        if stats['connection_errors'] > stats['query_count'] * 0.05:
            recommendations.append("High connection error rate - check database server health")
        
        if stats['average_query_time'] > 1.0:
            recommendations.append("Average query time is high - consider query optimization")
        
        return recommendations
    
    def optimize_performance(self) -> Dict[str, Any]:
        """Apply automatic performance optimizations"""
        optimizations_applied = []
        
        try:
            # Clear connection pool to refresh connections
            if hasattr(self.engine.pool, 'dispose'):
                self.engine.pool.dispose()
                optimizations_applied.append("Connection pool refreshed")
            
            # Reset monitoring statistics
            self.monitor = ConnectionPoolMonitor()
            optimizations_applied.append("Performance monitoring statistics reset")
            
            self.logger.info("Database performance optimizations applied")
            
            return {
                'status': 'success',
                'optimizations_applied': optimizations_applied,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to apply database optimizations: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# Database transaction decorator with robust error handling
def with_db_transaction(retries: int = 3):
    """Decorator for database operations with transaction support"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return robust_db_service.execute_transaction([
                lambda conn: func(conn, *args, **kwargs)
            ], retries=retries)[0]
        return wrapper
    return decorator


# Database query decorator with monitoring
def with_db_monitoring(query_name: str = None):
    """Decorator to monitor database query performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                robust_db_service.monitor.record_query(execution_time)
                
                if query_name and execution_time > 2.0:
                    logging.warning(f"Slow query '{query_name}': {execution_time:.2f}s")
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                robust_db_service.monitor.record_query(execution_time)
                logging.error(f"Query '{query_name or 'unknown'}' failed: {str(e)}")
                raise
        return wrapper
    return decorator


# Global robust database service instance
robust_db_service = RobustDatabaseService(DatabaseConfig())


def initialize_robust_database():
    """Initialize robust database service"""
    robust_db_service.initialize()
    logging.info("Robust database service initialized successfully")


def get_database_health() -> Dict[str, Any]:
    """Get comprehensive database health status"""
    return robust_db_service.check_health()


def get_database_performance_report() -> Dict[str, Any]:
    """Get detailed database performance report"""
    return robust_db_service.get_performance_metrics()