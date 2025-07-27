"""
Refactored Database Configuration and Optimization Module
Enhanced performance, monitoring, and connection management
"""
import os
import logging
from contextlib import contextmanager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text, event, create_engine
from sqlalchemy.pool import QueuePool
from typing import Optional, Tuple, Dict, Any

# Configure structured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    """Base model class for all database models"""
    pass

# Initialize SQLAlchemy with custom base
db = SQLAlchemy(model_class=Base)

class DatabaseManager:
    """Enhanced database management with monitoring and optimization"""
    
    def __init__(self):
        self.connection_count = 0
        self.query_count = 0
        self.slow_queries = []
        
    def configure_database(self, app):
        """Configure database with optimized production settings"""
        
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            # Fallback to SQLite for development
            database_url = 'sqlite:///court_app.db'
            logger.warning("Using SQLite fallback database for development")
        
        # Fix postgres:// to postgresql:// for SQLAlchemy compatibility
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        
        # Optimized engine options
        engine_options = {
            'pool_size': 20,  # Increased for better concurrency
            'max_overflow': 40,  # Allow more overflow connections
            'pool_timeout': 30,
            'pool_recycle': 1800,  # Recycle connections every 30 minutes
            'pool_pre_ping': True,  # Test connections before use
            'echo': False,  # Disable SQL logging in production
        }
        
        # PostgreSQL-specific optimizations
        if self._is_postgresql(database_url):
            engine_options.update({
                'pool_reset_on_return': 'commit',
                'connect_args': {
                    'sslmode': 'require',
                    'connect_timeout': 10,
                    'application_name': 'vara_civil_cariacica',
                    'options': '-c statement_timeout=30000'  # 30 second timeout
                }
            })
            logger.info("Configured for PostgreSQL/Supabase database")
        
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_options
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize database
        db.init_app(app)
        
        # Setup event listeners for monitoring
        self._setup_event_listeners(app)
        
        logger.info("Database configuration completed successfully")
    
    def _is_postgresql(self, database_url: str) -> bool:
        """Check if database is PostgreSQL"""
        return any(prefix in database_url for prefix in ['postgresql', 'postgres'])
    
    def _setup_event_listeners(self, app):
        """Setup SQLAlchemy event listeners for monitoring"""
        
        @event.listens_for(db.engine, "before_cursor_execute", propagate=True)
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())
            self.query_count += 1
        
        @event.listens_for(db.engine, "after_cursor_execute", propagate=True)
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total_time = time.time() - conn.info['query_start_time'].pop(-1)
            
            # Track slow queries (> 1 second)
            if total_time > 1.0:
                self.slow_queries.append({
                    'query': statement[:100],  # First 100 chars
                    'duration': total_time,
                    'timestamp': time.time()
                })
                logger.warning(f"Slow query detected ({total_time:.2f}s): {statement[:50]}...")
    
    @contextmanager
    def get_db_session(self):
        """Context manager for database sessions"""
        session = db.session
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def create_all_tables(self, app):
        """Create all database tables with error handling"""
        with app.app_context():
            try:
                # Import models to register them
                from models import (Contact, NewsItem, ProcessConsultation, 
                                  ChatMessage, AssessorMeeting, HearingSchedule, 
                                  AvailableTimeSlot)
                
                # Create tables
                db.create_all()
                
                # Create indexes for better performance
                self._create_indexes()
                
                logger.info("Database tables created successfully")
                
            except Exception as e:
                logger.error(f"Error creating database tables: {e}")
                raise
    
    def _create_indexes(self):
        """Create database indexes for improved query performance"""
        try:
            # Create indexes for frequently queried columns
            index_statements = [
                "CREATE INDEX IF NOT EXISTS idx_contact_email ON contact(email);",
                "CREATE INDEX IF NOT EXISTS idx_contact_created_at ON contact(created_at);",
                "CREATE INDEX IF NOT EXISTS idx_process_consultation_number ON process_consultation(process_number);",
                "CREATE INDEX IF NOT EXISTS idx_chat_message_session ON chat_message(session_id);",
                "CREATE INDEX IF NOT EXISTS idx_assessor_meeting_date ON assessor_meeting(preferred_date);",
                "CREATE INDEX IF NOT EXISTS idx_assessor_meeting_status ON assessor_meeting(status);",
                "CREATE INDEX IF NOT EXISTS idx_hearing_schedule_date ON hearing_schedule(scheduled_date);",
                "CREATE INDEX IF NOT EXISTS idx_news_published ON news_item(published_at, is_active);"
            ]
            
            for statement in index_statements:
                try:
                    db.session.execute(text(statement))
                except Exception as e:
                    # Index might already exist
                    logger.debug(f"Index creation note: {e}")
            
            db.session.commit()
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
            db.session.rollback()
    
    def optimize_database_performance(self):
        """Apply database performance optimizations"""
        try:
            database_url = os.environ.get('DATABASE_URL', '')
            
            if self._is_postgresql(database_url):
                # PostgreSQL optimizations
                optimization_queries = [
                    "ANALYZE;",  # Update statistics
                    "VACUUM ANALYZE;",  # Clean up and analyze
                    "REINDEX DATABASE CONCURRENTLY;",  # Rebuild indexes
                ]
                
                for query in optimization_queries:
                    try:
                        db.session.execute(text(query))
                        db.session.commit()
                        logger.info(f"PostgreSQL optimization applied: {query}")
                    except Exception as e:
                        logger.warning(f"Optimization query failed: {e}")
                        db.session.rollback()
            else:
                # SQLite optimizations
                sqlite_optimizations = [
                    "PRAGMA optimize;",
                    "PRAGMA analysis_limit=1000;",
                    "PRAGMA cache_size=-64000;",  # 64MB cache
                    "PRAGMA temp_store=MEMORY;",
                    "PRAGMA journal_mode=WAL;",  # Write-Ahead Logging
                ]
                
                for query in sqlite_optimizations:
                    try:
                        db.session.execute(text(query))
                        logger.info(f"SQLite optimization applied: {query}")
                    except Exception as e:
                        logger.warning(f"SQLite optimization failed: {e}")
                
                db.session.commit()
                
        except Exception as e:
            logger.error(f"Database optimization error: {e}")
    
    def check_database_health(self) -> Tuple[bool, str]:
        """Enhanced database health check with detailed diagnostics"""
        try:
            from flask import has_app_context
            
            if not has_app_context():
                return False, "No application context available"
            
            # Test basic connectivity
            result = db.session.execute(text("SELECT 1"))
            db.session.commit()
            
            # Get connection pool stats
            pool_status = self._get_pool_status()
            
            # Check for issues
            if pool_status['overflow'] > pool_status['max_overflow'] * 0.8:
                return True, f"Database healthy but high connection usage: {pool_status}"
            
            return True, f"Database connection healthy. Pool: {pool_status}"
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False, f"Database connection error: {str(e)}"
    
    def _get_pool_status(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        try:
            pool = db.engine.pool
            return {
                'size': pool.size(),
                'checked_in': pool.checkedin(),
                'overflow': pool.overflow(),
                'max_overflow': pool._max_overflow,
                'total': pool.checkedin() + pool.checkedout()
            }
        except:
            return {'status': 'unavailable'}
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        try:
            from models import (Contact, ProcessConsultation, AssessorMeeting, 
                              ChatMessage, NewsItem, HearingSchedule)
            
            stats = {
                'tables': {
                    'contacts': Contact.query.count(),
                    'consultations': ProcessConsultation.query.count(),
                    'meetings': AssessorMeeting.query.count(),
                    'chat_messages': ChatMessage.query.count(),
                    'news_items': NewsItem.query.count(),
                    'hearings': HearingSchedule.query.count()
                },
                'performance': {
                    'total_queries': self.query_count,
                    'slow_queries': len(self.slow_queries),
                    'connection_pool': self._get_pool_status()
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {'error': str(e)}

# Import time for monitoring
import time

# Create global database manager instance
db_manager = DatabaseManager()

# Export functions for backward compatibility
configure_database = db_manager.configure_database
create_all_tables = db_manager.create_all_tables
optimize_database_performance = db_manager.optimize_database_performance
check_database_health = db_manager.check_database_health
get_database_stats = db_manager.get_database_stats