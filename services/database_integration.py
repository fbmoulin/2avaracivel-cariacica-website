"""
Enhanced Database Integration Service
Provides robust database operations with connection pooling, 
transaction management, and error recovery
"""
import logging
from functools import wraps
from datetime import datetime
import time
from database import db
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseIntegrationService:
    """Manages database connections and operations robustly"""
    
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 1.0
        self.connection_timeout = 30
        
    @contextmanager
    def transaction_scope(self):
        """Provide a transactional scope with automatic rollback on error"""
        try:
            yield db.session
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Transaction rolled back: {str(e)}")
            raise
        finally:
            db.session.close()
    
    def retry_on_error(self, func):
        """Decorator to retry database operations on transient errors"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(self.max_retries):
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    last_error = e
                    if attempt < self.max_retries - 1:
                        logger.warning(f"Database operation failed (attempt {attempt + 1}), retrying: {str(e)}")
                        time.sleep(self.retry_delay * (attempt + 1))
                        # Try to recover the connection
                        try:
                            db.session.rollback()
                            db.session.close()
                        except:
                            pass
                    else:
                        logger.error(f"Database operation failed after {self.max_retries} attempts: {str(e)}")
                except IntegrityError as e:
                    # Don't retry integrity errors
                    db.session.rollback()
                    logger.error(f"Database integrity error: {str(e)}")
                    raise
                except Exception as e:
                    # Don't retry other errors
                    logger.error(f"Unexpected database error: {str(e)}")
                    raise
            
            if last_error:
                raise last_error
        
        return wrapper
    
    @retry_on_error
    def execute_query(self, query, params=None):
        """Execute a raw SQL query with retries"""
        try:
            result = db.session.execute(text(query), params or {})
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            raise
    
    @retry_on_error
    def batch_insert(self, model_class, records):
        """Perform batch insert with chunking for better performance"""
        chunk_size = 1000
        inserted_count = 0
        
        try:
            for i in range(0, len(records), chunk_size):
                chunk = records[i:i + chunk_size]
                db.session.bulk_insert_mappings(model_class, chunk)
                db.session.commit()
                inserted_count += len(chunk)
                logger.info(f"Inserted {inserted_count}/{len(records)} records")
            
            return inserted_count
        except Exception as e:
            db.session.rollback()
            logger.error(f"Batch insert failed: {str(e)}")
            raise
    
    @retry_on_error
    def optimized_query(self, model_class, filters=None, limit=100, offset=0, order_by=None):
        """Perform optimized queries with pagination"""
        query = db.session.query(model_class)
        
        if filters:
            for key, value in filters.items():
                if hasattr(model_class, key):
                    query = query.filter(getattr(model_class, key) == value)
        
        if order_by:
            if hasattr(model_class, order_by):
                query = query.order_by(getattr(model_class, order_by))
        
        # Use pagination for large datasets
        query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def health_check(self):
        """Perform comprehensive database health check"""
        health_status = {
            'status': 'unknown',
            'connection': False,
            'response_time': None,
            'pool_status': None,
            'errors': []
        }
        
        start_time = time.time()
        
        try:
            # Test basic connectivity
            result = db.session.execute(text('SELECT 1'))
            health_status['connection'] = True
            
            # Check connection pool status
            engine = db.engine
            pool = engine.pool
            health_status['pool_status'] = {
                'size': pool.size(),
                'checked_in': pool.checkedin(),
                'overflow': pool.overflow(),
                'total': pool.checkedout()
            }
            
            # Test write capability
            test_query = text("""
                CREATE TEMPORARY TABLE IF NOT EXISTS health_check_test (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                INSERT INTO health_check_test DEFAULT VALUES;
                DROP TABLE health_check_test;
            """)
            db.session.execute(test_query)
            db.session.commit()
            
            health_status['status'] = 'healthy'
            
        except OperationalError as e:
            health_status['status'] = 'connection_error'
            health_status['errors'].append(str(e))
            logger.error(f"Database connection error: {str(e)}")
        except Exception as e:
            health_status['status'] = 'error'
            health_status['errors'].append(str(e))
            logger.error(f"Database health check error: {str(e)}")
        finally:
            health_status['response_time'] = time.time() - start_time
            try:
                db.session.rollback()
                db.session.close()
            except:
                pass
        
        return health_status
    
    def optimize_connections(self):
        """Optimize database connections and cleanup idle connections"""
        try:
            # Close idle connections
            db.session.close_all()
            
            # Execute maintenance commands
            maintenance_queries = [
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < current_timestamp - INTERVAL '10 minutes';",
                "VACUUM ANALYZE;"
            ]
            
            for query in maintenance_queries:
                try:
                    db.session.execute(text(query))
                    db.session.commit()
                except Exception as e:
                    logger.warning(f"Maintenance query failed: {str(e)}")
                    db.session.rollback()
            
            logger.info("Database connections optimized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to optimize connections: {str(e)}")
            return False
    
    def create_indexes(self, index_definitions):
        """Create database indexes for better performance"""
        created_indexes = []
        
        for index_def in index_definitions:
            try:
                index_name = index_def['name']
                table_name = index_def['table']
                columns = index_def['columns']
                unique = index_def.get('unique', False)
                
                # Check if index exists
                check_query = text("""
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = :index_name
                """)
                result = db.session.execute(check_query, {'index_name': index_name})
                
                if not result.fetchone():
                    # Create index
                    unique_clause = "UNIQUE" if unique else ""
                    columns_str = ", ".join(columns)
                    create_query = text(f"""
                        CREATE {unique_clause} INDEX {index_name} 
                        ON {table_name} ({columns_str})
                    """)
                    db.session.execute(create_query)
                    db.session.commit()
                    created_indexes.append(index_name)
                    logger.info(f"Created index: {index_name}")
                else:
                    logger.info(f"Index already exists: {index_name}")
                    
            except Exception as e:
                logger.error(f"Failed to create index {index_def.get('name', 'unknown')}: {str(e)}")
                db.session.rollback()
        
        return created_indexes

# Create singleton instance
db_integration = DatabaseIntegrationService()

# Export convenience functions
transaction_scope = db_integration.transaction_scope
retry_on_error = db_integration.retry_on_error