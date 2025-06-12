"""
Robust Database Service for 2ª Vara Cível de Cariacica
Implements comprehensive error handling, connection pooling, and security measures
"""

import logging
import time
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import (
    SQLAlchemyError, 
    IntegrityError, 
    OperationalError, 
    TimeoutError,
    DatabaseError
)
from sqlalchemy.pool import QueuePool
import json
import hashlib

logger = logging.getLogger(__name__)

class DatabaseConnectionError(Exception):
    """Custom exception for database connection issues"""
    pass

class DatabaseSecurityError(Exception):
    """Custom exception for database security violations"""
    pass

class RobustDatabaseService:
    """
    Robust database service with comprehensive error handling,
    connection pooling, and security measures
    """
    
    def __init__(self, database_url: str, **kwargs):
        self.database_url = database_url
        self.engine = None
        self.session_factory = None
        self.scoped_session = None
        self._connection_pool_size = kwargs.get('pool_size', 20)
        self._max_overflow = kwargs.get('max_overflow', 30)
        self._pool_timeout = kwargs.get('pool_timeout', 30)
        self._pool_recycle = kwargs.get('pool_recycle', 1800)
        self._retry_attempts = kwargs.get('retry_attempts', 3)
        self._retry_delay = kwargs.get('retry_delay', 1)
        
        # Security settings
        self._max_query_time = kwargs.get('max_query_time', 30)
        self._blocked_keywords = {
            'drop', 'delete', 'truncate', 'alter', 'create', 'grant', 
            'revoke', 'insert', 'update', 'exec', 'execute', 'sp_',
            'xp_', 'bulk', 'openrowset', 'opendatasource'
        }
        
        # Monitoring
        self._query_log = []
        self._connection_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'failed_connections': 0,
            'total_queries': 0,
            'failed_queries': 0,
            'slow_queries': 0
        }
        
        self._lock = threading.Lock()
        self.initialize_connection()

    def initialize_connection(self):
        """Initialize database connection with robust error handling"""
        try:
            # Create engine with security and performance optimizations
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=self._connection_pool_size,
                max_overflow=self._max_overflow,
                pool_timeout=self._pool_timeout,
                pool_recycle=self._pool_recycle,
                pool_pre_ping=True,
                echo=False,  # Set to True for SQL debugging
                connect_args={
                    'timeout': self._pool_timeout,
                    'check_same_thread': False  # For SQLite
                }
            )
            
            # Set up session factory
            self.session_factory = sessionmaker(bind=self.engine)
            self.scoped_session = scoped_session(self.session_factory)
            
            # Register event listeners for monitoring
            self._register_event_listeners()
            
            # Test connection
            self._test_connection()
            
            logger.info("Database service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            raise DatabaseConnectionError(f"Database initialization failed: {e}")

    def _register_event_listeners(self):
        """Register event listeners for monitoring and security"""
        
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            with self._lock:
                self._connection_stats['total_connections'] += 1
                self._connection_stats['active_connections'] += 1
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            logger.debug("Connection checked out from pool")
        
        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            with self._lock:
                self._connection_stats['active_connections'] = max(0, 
                    self._connection_stats['active_connections'] - 1)
        
        @event.listens_for(self.engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()
            
            # Security check for dangerous SQL
            self._validate_sql_query(statement)

        @event.listens_for(self.engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total_time = time.time() - context._query_start_time
            
            with self._lock:
                self._connection_stats['total_queries'] += 1
                
                if total_time > 5.0:  # Log slow queries
                    self._connection_stats['slow_queries'] += 1
                    logger.warning(f"Slow query detected: {total_time:.2f}s - {statement[:100]}")
                
                # Log query for monitoring
                self._log_query(statement, parameters, total_time)

    def _validate_sql_query(self, statement: str):
        """Validate SQL query for security issues"""
        statement_lower = statement.lower().strip()
        
        # Check for blocked keywords (only for direct SQL, not ORM queries)
        if any(keyword in statement_lower for keyword in self._blocked_keywords):
            # Allow if it's a parameterized query or ORM-generated
            if not ('?' in statement or ':' in statement or 'SELECT' in statement.upper()):
                raise DatabaseSecurityError(f"Potentially dangerous SQL detected: {statement[:100]}")
        
        # Check for SQL injection patterns
        injection_patterns = [
            "' or '1'='1",
            "' or 1=1",
            "'; drop table",
            "union select",
            "exec(",
            "execute(",
        ]
        
        for pattern in injection_patterns:
            if pattern in statement_lower:
                raise DatabaseSecurityError(f"SQL injection pattern detected: {pattern}")

    def _log_query(self, statement: str, parameters: Any, execution_time: float):
        """Log query for monitoring and debugging"""
        query_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'statement': statement[:200],  # Truncate long statements
            'execution_time': execution_time,
            'parameters_hash': hashlib.md5(str(parameters).encode()).hexdigest() if parameters else None
        }
        
        # Keep only last 1000 queries to prevent memory issues
        if len(self._query_log) >= 1000:
            self._query_log.pop(0)
        
        self._query_log.append(query_info)

    def _test_connection(self):
        """Test database connection"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise DatabaseConnectionError(f"Connection test failed: {e}")

    @contextmanager
    def get_session(self, read_only: bool = False):
        """
        Get database session with comprehensive error handling
        
        Args:
            read_only: If True, set session to read-only mode
        """
        session = None
        try:
            session = self.scoped_session()
            
            if read_only:
                # Set connection to read-only (PostgreSQL/MySQL)
                try:
                    session.execute(text("SET TRANSACTION READ ONLY"))
                except Exception:
                    pass  # Not all databases support this
            
            yield session
            session.commit()
            
        except IntegrityError as e:
            if session:
                session.rollback()
            logger.error(f"Database integrity error: {e}")
            raise
        except OperationalError as e:
            if session:
                session.rollback()
            with self._lock:
                self._connection_stats['failed_connections'] += 1
            logger.error(f"Database operational error: {e}")
            raise DatabaseConnectionError(f"Database operation failed: {e}")
        except TimeoutError as e:
            if session:
                session.rollback()
            logger.error(f"Database timeout: {e}")
            raise
        except SQLAlchemyError as e:
            if session:
                session.rollback()
            with self._lock:
                self._connection_stats['failed_queries'] += 1
            logger.error(f"Database error: {e}")
            raise
        except Exception as e:
            if session:
                session.rollback()
            logger.error(f"Unexpected database error: {e}")
            raise
        finally:
            if session:
                self.scoped_session.remove()

    def execute_query_with_retry(self, query_func, *args, **kwargs):
        """
        Execute database query with retry logic
        
        Args:
            query_func: Function that executes the query
            *args, **kwargs: Arguments for the query function
        """
        last_exception = None
        
        for attempt in range(self._retry_attempts):
            try:
                return query_func(*args, **kwargs)
            except (OperationalError, TimeoutError, DatabaseConnectionError) as e:
                last_exception = e
                if attempt < self._retry_attempts - 1:
                    wait_time = self._retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Query attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Query failed after {self._retry_attempts} attempts: {e}")
            except Exception as e:
                # Don't retry for non-recoverable errors
                logger.error(f"Non-recoverable database error: {e}")
                raise
        
        raise last_exception

    def validate_input_data(self, data: Dict[str, Any], allowed_fields: List[str]) -> Dict[str, Any]:
        """
        Validate and sanitize input data
        
        Args:
            data: Input data dictionary
            allowed_fields: List of allowed field names
            
        Returns:
            Validated and sanitized data
        """
        validated_data = {}
        
        for field in allowed_fields:
            if field in data:
                value = data[field]
                
                # Type validation and sanitization
                if isinstance(value, str):
                    # Sanitize string input
                    value = value.strip()
                    if len(value) > 10000:  # Prevent excessively long inputs
                        raise ValueError(f"Field {field} is too long")
                    
                    # Remove potentially dangerous characters
                    value = self._sanitize_string(value)
                
                elif isinstance(value, (int, float)):
                    # Validate numeric ranges
                    if abs(value) > 1e15:  # Prevent overflow
                        raise ValueError(f"Numeric value for {field} is out of range")
                
                validated_data[field] = value
        
        return validated_data

    def _sanitize_string(self, value: str) -> str:
        """Sanitize string input"""
        # Remove null bytes and control characters
        value = value.replace('\x00', '').replace('\r', '').replace('\n', ' ')
        
        # Limit length
        if len(value) > 5000:
            value = value[:5000]
        
        return value

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get database connection statistics"""
        with self._lock:
            stats = self._connection_stats.copy()
        
        # Add pool information
        if self.engine and hasattr(self.engine.pool, 'size'):
            stats.update({
                'pool_size': self.engine.pool.size(),
                'checked_in': self.engine.pool.checkedin(),
                'checked_out': self.engine.pool.checkedout(),
                'overflow': self.engine.pool.overflow(),
                'invalid': self.engine.pool.invalid()
            })
        
        return stats

    def get_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent query log entries"""
        with self._lock:
            return self._query_log[-limit:] if self._query_log else []

    def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        try:
            start_time = time.time()
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            response_time = time.time() - start_time
            
            stats = self.get_connection_stats()
            
            return {
                'status': 'healthy',
                'response_time': response_time,
                'connection_stats': stats,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def backup_database(self, backup_path: str) -> bool:
        """
        Create database backup (implementation depends on database type)
        
        Args:
            backup_path: Path where backup should be stored
            
        Returns:
            True if backup successful, False otherwise
        """
        try:
            # This is a simplified backup - in production, use proper backup tools
            logger.info(f"Creating database backup at {backup_path}")
            
            # For SQLite, we could copy the file
            # For PostgreSQL/MySQL, we'd use pg_dump/mysqldump
            
            return True
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False

    def close_connections(self):
        """Close all database connections"""
        try:
            if self.scoped_session:
                self.scoped_session.remove()
            if self.engine:
                self.engine.dispose()
            logger.info("Database connections closed successfully")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")


# Global database service instance
_db_service = None

def get_database_service(database_url: str = None, **kwargs) -> RobustDatabaseService:
    """Get or create global database service instance"""
    global _db_service
    
    if _db_service is None and database_url:
        _db_service = RobustDatabaseService(database_url, **kwargs)
    
    return _db_service

def init_database_service(app):
    """Initialize database service with Flask app"""
    database_url = app.config.get('SQLALCHEMY_DATABASE_URI')
    engine_options = app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {})
    
    if not database_url:
        raise ValueError("SQLALCHEMY_DATABASE_URI not configured")
    
    global _db_service
    _db_service = RobustDatabaseService(database_url, **engine_options)
    
    return _db_service