"""
Optimized Database Configuration
Enhanced with connection pooling, monitoring, and performance optimizations
"""
import os
import logging
import time
from datetime import datetime, timedelta
from contextlib import contextmanager
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import QueuePool
from flask_sqlalchemy import SQLAlchemy
import psutil

logger = logging.getLogger(__name__)

class OptimizedBase(DeclarativeBase):
    """Enhanced base class with utility methods"""
    
    def save(self):
        """Save instance to database"""
        from flask import current_app
        if current_app:
            db.session.add(self)
            db.session.commit()
    
    def delete(self):
        """Delete instance from database"""
        from flask import current_app
        if current_app:
            db.session.delete(self)
            db.session.commit()
    
    @classmethod
    def get_or_404(cls, id):
        """Get instance or raise 404"""
        return cls.query.get_or_404(id)
    
    @classmethod
    def create(cls, **kwargs):
        """Create and save new instance"""
        instance = cls(**kwargs)
        instance.save()
        return instance

# Enhanced SQLAlchemy instance
db = SQLAlchemy(model_class=OptimizedBase)

class DatabaseMonitor:
    """Database performance monitoring"""
    
    def __init__(self):
        self.connection_count = 0
        self.query_times = []
        self.slow_queries = []
        self.error_count = 0
    
    def log_connection(self):
        """Log database connection"""
        self.connection_count += 1
    
    def log_query_time(self, duration, query=None):
        """Log query execution time"""
        self.query_times.append(duration)
        
        # Log slow queries (> 1 second)
        if duration > 1.0:
            self.slow_queries.append({
                'duration': duration,
                'query': str(query)[:200] if query else 'Unknown',
                'timestamp': datetime.utcnow()
            })
            logger.warning(f"Slow query detected: {duration:.3f}s")
    
    def log_error(self, error):
        """Log database error"""
        self.error_count += 1
        logger.error(f"Database error: {error}")
    
    def get_stats(self):
        """Get performance statistics"""
        return {
            'connections': self.connection_count,
            'total_queries': len(self.query_times),
            'avg_query_time': sum(self.query_times) / len(self.query_times) if self.query_times else 0,
            'slow_queries': len(self.slow_queries),
            'errors': self.error_count,
            'recent_slow_queries': self.slow_queries[-5:]  # Last 5 slow queries
        }

# Global monitor instance
db_monitor = DatabaseMonitor()

def configure_optimized_database(app):
    """Configure database with advanced optimizations"""
    
    # Enhanced connection configuration
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        raise ValueError("DATABASE_URL is required")
    
    # Optimize engine configuration based on environment
    engine_options = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', '15')),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', '30')),
        'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', '30')),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', '1800')),
        'pool_pre_ping': True,
        'poolclass': QueuePool,
        'connect_args': {
            'sslmode': 'require',
            'application_name': '2vara_civil_cariacica_optimized',
            'options': '-c statement_timeout=30000'  # 30 second timeout
        }
    }
    
    # Additional PostgreSQL optimizations
    if 'postgresql' in database_url.lower():
        engine_options['connect_args'].update({
            'options': '-c work_mem=32MB -c maintenance_work_mem=64MB -c effective_cache_size=256MB'
        })
    
    app.config.update({
        'SQLALCHEMY_DATABASE_URI': database_url,
        'SQLALCHEMY_ENGINE_OPTIONS': engine_options,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_RECORD_QUERIES': True,
        'DATABASE_QUERY_TIMEOUT': 30
    })
    
    # Initialize database
    db.init_app(app)
    
    # Set up event listeners for monitoring
    setup_database_monitoring(app)
    
    logger.info("Optimized database configuration completed")
    return db

def setup_database_monitoring(app):
    """Set up database event listeners for monitoring"""
    
    @event.listens_for(db.engine, "connect")
    def receive_connect(dbapi_connection, connection_record):
        """Monitor database connections"""
        db_monitor.log_connection()
        logger.debug("Database connection established")
    
    @event.listens_for(db.engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Start query timing"""
        context._query_start_time = time.time()
    
    @event.listens_for(db.engine, "after_cursor_execute")
    def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Log query execution time"""
        if hasattr(context, '_query_start_time'):
            duration = time.time() - context._query_start_time
            db_monitor.log_query_time(duration, statement)

@contextmanager
def database_transaction():
    """Context manager for database transactions with error handling"""
    try:
        yield db.session
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        db_monitor.log_error(e)
        logger.error(f"Database transaction failed: {e}")
        raise
    finally:
        db.session.close()

def create_optimized_tables(app):
    """Create database tables with optimizations"""
    with app.app_context():
        try:
            # Import models to ensure they're registered
            from optimized_models import (
                Contact, NewsItem, ProcessConsultation, 
                AssessorMeeting, ChatMessage
            )
            
            # Create all tables
            db.create_all()
            
            # Apply PostgreSQL-specific optimizations
            if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI'].lower():
                apply_postgresql_optimizations()
            
            logger.info("Optimized database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise

def apply_postgresql_optimizations():
    """Apply PostgreSQL-specific performance optimizations"""
    try:
        with db.engine.connect() as connection:
            # Analyze tables for better query planning
            tables = ['contact', 'news_item', 'process_consultation', 'assessor_meeting', 'chat_message']
            
            for table in tables:
                try:
                    connection.execute(text(f"ANALYZE {table}"))
                    logger.debug(f"Analyzed table: {table}")
                except Exception as e:
                    logger.warning(f"Could not analyze table {table}: {e}")
            
            # Update table statistics
            connection.execute(text("UPDATE pg_stat_user_tables SET last_analyze = NOW()"))
            connection.commit()
            
            logger.info("PostgreSQL optimizations applied")
            
    except Exception as e:
        logger.warning(f"PostgreSQL optimizations failed: {e}")

def check_optimized_database_health():
    """Enhanced database health check with performance metrics"""
    try:
        start_time = time.time()
        
        # Test basic connectivity
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Get connection pool stats
        pool = db.engine.pool
        pool_stats = {
            'size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'status': 'healthy' if response_time < 1.0 else 'slow'
        }
        
        # Get monitor stats
        monitor_stats = db_monitor.get_stats()
        
        # System memory info
        memory = psutil.virtual_memory()
        
        return True, {
            'status': 'healthy',
            'response_time': round(response_time, 3),
            'pool': pool_stats,
            'monitor': monitor_stats,
            'system_memory_percent': memory.percent,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False, {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

def get_database_performance_stats():
    """Get comprehensive database performance statistics"""
    try:
        stats = {
            'monitor': db_monitor.get_stats(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add connection pool information
        if hasattr(db.engine, 'pool'):
            pool = db.engine.pool
            stats['pool'] = {
                'size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow()
            }
        
        # Add system metrics
        memory = psutil.virtual_memory()
        stats['system'] = {
            'memory_percent': memory.percent,
            'memory_available_gb': round(memory.available / (1024**3), 2)
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {'error': str(e)}

def optimize_database_queries():
    """Apply runtime query optimizations"""
    try:
        with db.engine.connect() as connection:
            # Set session-level optimizations for PostgreSQL
            if 'postgresql' in db.engine.url.drivername:
                optimizations = [
                    "SET work_mem = '32MB'",
                    "SET effective_cache_size = '256MB'",
                    "SET random_page_cost = 1.1",
                    "SET seq_page_cost = 1.0"
                ]
                
                for optimization in optimizations:
                    try:
                        connection.execute(text(optimization))
                    except Exception as e:
                        logger.warning(f"Could not apply optimization '{optimization}': {e}")
                
                connection.commit()
                logger.info("Database query optimizations applied")
            
    except Exception as e:
        logger.warning(f"Query optimization failed: {e}")

# Utility functions for common database operations
def bulk_insert(model_class, data_list, batch_size=1000):
    """Efficient bulk insert operation"""
    try:
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            db.session.bulk_insert_mappings(model_class, batch)
            db.session.commit()
        
        logger.info(f"Bulk inserted {len(data_list)} records for {model_class.__name__}")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Bulk insert failed for {model_class.__name__}: {e}")
        raise

def cleanup_old_records(model_class, date_field, days_to_keep=90):
    """Clean up old records efficiently"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        deleted = db.session.query(model_class).filter(
            getattr(model_class, date_field) < cutoff_date
        ).delete(synchronize_session=False)
        
        db.session.commit()
        logger.info(f"Cleaned up {deleted} old records from {model_class.__name__}")
        return deleted
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Cleanup failed for {model_class.__name__}: {e}")
        raise