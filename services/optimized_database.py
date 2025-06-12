"""
Optimized Database Service for 2ª Vara Cível de Cariacica
Advanced connection pooling, query optimization, and transaction management
"""

import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from contextlib import contextmanager
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine
from flask import g, current_app
import psutil
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Advanced database optimization and monitoring"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self.connection_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'slow_queries': 0,
            'failed_queries': 0,
            'avg_query_time': 0.0
        }
        self.query_times = []
        self.lock = threading.Lock()
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize optimized database engine"""
        engine_options = {
            'poolclass': QueuePool,
            'pool_size': 20,
            'max_overflow': 30,
            'pool_pre_ping': True,
            'pool_recycle': 1800,
            'pool_timeout': 30,
            'echo': False,
            'connect_args': {
                'connect_timeout': 10,
                'application_name': 'court_system_optimized'
            }
        }
        
        # PostgreSQL specific optimizations
        if 'postgresql' in self.database_url:
            engine_options['connect_args'].update({
                'options': '-c default_transaction_isolation=read_committed -c statement_timeout=30000'
            })
        
        self.engine = create_engine(self.database_url, **engine_options)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Register event listeners
        self._register_event_listeners()
        
        logger.info("Optimized database engine initialized")
    
    def _register_event_listeners(self):
        """Register database event listeners for monitoring"""
        
        @event.listens_for(self.engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()
        
        @event.listens_for(self.engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            query_time = time.time() - context._query_start_time
            
            with self.lock:
                self.query_times.append(query_time)
                if len(self.query_times) > 1000:
                    self.query_times = self.query_times[-1000:]
                
                self.connection_stats['avg_query_time'] = sum(self.query_times) / len(self.query_times)
                
                if query_time > 1.0:  # Slow query threshold
                    self.connection_stats['slow_queries'] += 1
                    logger.warning(f"Slow query detected: {query_time:.3f}s - {statement[:100]}")
        
        @event.listens_for(self.engine, "connect")
        def connect(dbapi_connection, connection_record):
            with self.lock:
                self.connection_stats['total_connections'] += 1
                self.connection_stats['active_connections'] += 1
        
        @event.listens_for(self.engine, "close")
        def close(dbapi_connection, connection_record):
            with self.lock:
                self.connection_stats['active_connections'] -= 1
    
    @contextmanager
    def get_session(self):
        """Get optimized database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            with self.lock:
                self.connection_stats['failed_queries'] += 1
            raise
        finally:
            session.close()
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute optimized query with monitoring"""
        start_time = time.time()
        
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params or {})
                
                if result.returns_rows:
                    return [dict(row._mapping) for row in result]
                else:
                    return []
        
        except Exception as e:
            query_time = time.time() - start_time
            logger.error(f"Query failed after {query_time:.3f}s: {e}")
            raise
    
    def bulk_insert(self, table_name: str, data: List[Dict]) -> int:
        """Optimized bulk insert operation"""
        if not data:
            return 0
        
        try:
            with self.get_session() as session:
                result = session.execute(
                    text(f"INSERT INTO {table_name} ({', '.join(data[0].keys())}) VALUES {', '.join(['(' + ', '.join([f':{k}_{i}' for k in data[0].keys()]) + ')' for i in range(len(data))])}"),
                    {f"{k}_{i}": v for i, row in enumerate(data) for k, v in row.items()}
                )
                return result.rowcount
        
        except Exception as e:
            logger.error(f"Bulk insert failed: {e}")
            raise
    
    def optimize_tables(self) -> Dict[str, Any]:
        """Run database optimization maintenance"""
        optimization_results = {}
        
        try:
            with self.get_session() as session:
                # PostgreSQL optimizations
                if 'postgresql' in self.database_url:
                    # Update table statistics
                    session.execute(text("ANALYZE"))
                    optimization_results['analyze'] = 'completed'
                    
                    # Get table sizes
                    table_sizes = session.execute(text("""
                        SELECT schemaname, tablename, 
                               pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                        FROM pg_tables 
                        WHERE schemaname = 'public'
                        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                    """))
                    
                    optimization_results['table_sizes'] = [dict(row._mapping) for row in table_sizes]
                
                # SQLite optimizations
                elif 'sqlite' in self.database_url:
                    session.execute(text("VACUUM"))
                    session.execute(text("ANALYZE"))
                    optimization_results['vacuum'] = 'completed'
                    optimization_results['analyze'] = 'completed'
                
                optimization_results['timestamp'] = datetime.now().isoformat()
                
        except Exception as e:
            logger.error(f"Table optimization failed: {e}")
            optimization_results['error'] = str(e)
        
        return optimization_results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive database performance statistics"""
        stats = self.connection_stats.copy()
        
        # Pool statistics
        try:
            pool = self.engine.pool
            stats['pool_stats'] = {
                'size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'invalid': pool.invalid()
            }
        except Exception as e:
            logger.error(f"Error getting pool stats: {e}")
            stats['pool_stats'] = {}
        
        # Query performance
        if self.query_times:
            stats['query_performance'] = {
                'min_time': min(self.query_times),
                'max_time': max(self.query_times),
                'avg_time': sum(self.query_times) / len(self.query_times),
                'total_queries': len(self.query_times)
            }
        
        return stats

class QueryBuilder:
    """Advanced query builder with optimization"""
    
    def __init__(self, db_optimizer: DatabaseOptimizer):
        self.db = db_optimizer
        self.query_cache = {}
        self.cache_timeout = 300  # 5 minutes
    
    def select(self, table: str, columns: str = "*", where: Optional[str] = None, 
               limit: Optional[int] = None, offset: Optional[int] = None,
               order_by: Optional[str] = None) -> List[Dict]:
        """Build and execute optimized SELECT query"""
        
        query_parts = [f"SELECT {columns} FROM {table}"]
        params = {}
        
        if where:
            query_parts.append(f"WHERE {where}")
        
        if order_by:
            query_parts.append(f"ORDER BY {order_by}")
        
        if limit:
            query_parts.append(f"LIMIT {limit}")
        
        if offset:
            query_parts.append(f"OFFSET {offset}")
        
        query = " ".join(query_parts)
        
        # Check cache
        cache_key = f"{query}_{hash(str(params))}"
        if cache_key in self.query_cache:
            cached_result, cached_time = self.query_cache[cache_key]
            if time.time() - cached_time < self.cache_timeout:
                return cached_result
        
        # Execute query
        result = self.db.execute_query(query, params)
        
        # Cache result
        self.query_cache[cache_key] = (result, time.time())
        
        return result
    
    def insert(self, table: str, data: Dict) -> int:
        """Build and execute optimized INSERT query"""
        columns = list(data.keys())
        placeholders = [f":{col}" for col in columns]
        
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        
        with self.db.get_session() as session:
            result = session.execute(text(query), data)
            return result.rowcount
    
    def update(self, table: str, data: Dict, where: str, where_params: Optional[Dict] = None) -> int:
        """Build and execute optimized UPDATE query"""
        set_clauses = [f"{col} = :{col}" for col in data.keys()]
        query = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {where}"
        
        params = {**data, **(where_params or {})}
        
        with self.db.get_session() as session:
            result = session.execute(text(query), params)
            return result.rowcount
    
    def delete(self, table: str, where: str, where_params: Optional[Dict] = None) -> int:
        """Build and execute optimized DELETE query"""
        query = f"DELETE FROM {table} WHERE {where}"
        
        with self.db.get_session() as session:
            result = session.execute(text(query), where_params or {})
            return result.rowcount

class ConnectionManager:
    """Advanced database connection management"""
    
    def __init__(self, db_optimizer: DatabaseOptimizer):
        self.db = db_optimizer
        self.connection_pool = {}
        self.connection_timeout = 300  # 5 minutes
        self.cleanup_interval = 60  # 1 minute
        self.last_cleanup = time.time()
    
    def get_connection(self, connection_id: str = None):
        """Get managed database connection"""
        if connection_id is None:
            connection_id = f"conn_{threading.current_thread().ident}"
        
        # Cleanup expired connections
        if time.time() - self.last_cleanup > self.cleanup_interval:
            self._cleanup_expired_connections()
        
        # Return existing connection if available
        if connection_id in self.connection_pool:
            conn_info = self.connection_pool[connection_id]
            if time.time() - conn_info['created'] < self.connection_timeout:
                return conn_info['session']
            else:
                # Close expired connection
                conn_info['session'].close()
                del self.connection_pool[connection_id]
        
        # Create new connection
        session = self.db.SessionLocal()
        self.connection_pool[connection_id] = {
            'session': session,
            'created': time.time()
        }
        
        return session
    
    def _cleanup_expired_connections(self):
        """Clean up expired database connections"""
        current_time = time.time()
        expired_connections = []
        
        for conn_id, conn_info in self.connection_pool.items():
            if current_time - conn_info['created'] > self.connection_timeout:
                expired_connections.append(conn_id)
        
        for conn_id in expired_connections:
            try:
                self.connection_pool[conn_id]['session'].close()
                del self.connection_pool[conn_id]
            except Exception as e:
                logger.error(f"Error closing expired connection {conn_id}: {e}")
        
        self.last_cleanup = current_time
        
        if expired_connections:
            logger.info(f"Cleaned up {len(expired_connections)} expired connections")

# Global database optimizer instance
db_optimizer = None
query_builder = None
connection_manager = None

def initialize_optimized_database(database_url: str):
    """Initialize optimized database components"""
    global db_optimizer, query_builder, connection_manager
    
    db_optimizer = DatabaseOptimizer(database_url)
    query_builder = QueryBuilder(db_optimizer)
    connection_manager = ConnectionManager(db_optimizer)
    
    logger.info("Optimized database services initialized")

def get_database_health() -> Dict[str, Any]:
    """Get comprehensive database health information"""
    if not db_optimizer:
        return {'status': 'not_initialized'}
    
    try:
        # Test connection
        with db_optimizer.get_session() as session:
            session.execute(text("SELECT 1"))
        
        # Get performance stats
        stats = db_optimizer.get_performance_stats()
        
        # Get system resources
        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent()
            
            system_stats = {
                'memory_usage': memory.percent,
                'memory_available': memory.available,
                'cpu_usage': cpu
            }
        except:
            system_stats = {}
        
        return {
            'status': 'healthy',
            'database_stats': stats,
            'system_stats': system_stats,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }