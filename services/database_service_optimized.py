"""
Optimized database service with connection pooling, query optimization, and error resilience
Production-ready database layer with comprehensive error handling and performance monitoring
"""
import logging
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from contextlib import contextmanager
from sqlalchemy import text, func, and_, or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, DisconnectionError, TimeoutError
from sqlalchemy.orm import sessionmaker, scoped_session
from functools import wraps
import time

logger = logging.getLogger(__name__)


class DatabaseMetrics:
    """Database performance metrics collector"""
    
    def __init__(self):
        self.query_count = 0
        self.total_query_time = 0
        self.slow_queries = []
        self.errors = []
        self.connection_pool_stats = {}
    
    def record_query(self, query_time: float, query: str):
        """Record query execution metrics"""
        self.query_count += 1
        self.total_query_time += query_time
        
        if query_time > 1.0:  # Slow query threshold
            self.slow_queries.append({
                'query': query[:200],
                'execution_time': query_time,
                'timestamp': datetime.utcnow()
            })
    
    def record_error(self, error: Exception, operation: str):
        """Record database errors"""
        self.errors.append({
            'error': str(error),
            'operation': operation,
            'timestamp': datetime.utcnow()
        })
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        avg_query_time = (self.total_query_time / self.query_count) if self.query_count > 0 else 0
        
        return {
            'total_queries': self.query_count,
            'average_query_time': avg_query_time,
            'slow_queries_count': len(self.slow_queries),
            'errors_count': len(self.errors),
            'uptime_minutes': (datetime.utcnow() - getattr(self, 'start_time', datetime.utcnow())).total_seconds() / 60
        }


def query_performance_monitor(operation_name: str):
    """Decorator to monitor database query performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Record metrics
                db_metrics.record_query(execution_time, operation_name)
                
                # Log slow queries
                if execution_time > 1.0:
                    logger.warning(f"Slow database operation {operation_name}: {execution_time:.2f}s")
                
                return result
                
            except Exception as e:
                db_metrics.record_error(e, operation_name)
                logger.error(f"Database operation {operation_name} failed: {e}")
                raise
        return wrapper
    return decorator


def retry_database_operation(max_attempts: int = 3, backoff_factor: float = 1.0):
    """Decorator to retry database operations with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (DisconnectionError, TimeoutError) as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = backoff_factor * (2 ** attempt)
                        logger.warning(f"Database connection issue, retrying in {wait_time}s: {e}")
                        time.sleep(wait_time)
                        
                        # Force engine disposal to recreate connections
                        from app import db
                        db.engine.dispose()
                    else:
                        logger.error(f"Database operation failed after {max_attempts} attempts: {e}")
                except Exception as e:
                    # Don't retry for other types of errors
                    logger.error(f"Database operation failed: {e}")
                    raise
            
            raise last_exception
        return wrapper
    return decorator


class OptimizedDatabaseService:
    """Advanced database service with connection management and query optimization"""
    
    def __init__(self):
        self.metrics = DatabaseMetrics()
        self.metrics.start_time = datetime.utcnow()
    
    @contextmanager
    def transaction_scope(self):
        """Provide a transactional scope with automatic rollback on error"""
        from app import db
        
        try:
            yield db.session
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise
        finally:
            db.session.close()
    
    @retry_database_operation(max_attempts=3)
    @query_performance_monitor("health_check")
    def check_connection(self) -> Tuple[bool, str]:
        """Enhanced database connection health check"""
        try:
            from app import db
            
            # Test basic connectivity
            result = db.session.execute(text('SELECT 1 as health_check'))
            if not result.fetchone():
                return False, "Health check query returned no result"
            
            # Test connection pool status
            pool = db.engine.pool
            pool_status = {
                'size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'invalid': pool.invalid()
            }
            
            logger.debug(f"Connection pool status: {pool_status}")
            
            # Check for connection pool issues
            if pool_status['checked_out'] > pool_status['size'] * 0.8:
                logger.warning("High connection pool utilization")
            
            return True, f"Connection healthy. Pool: {pool_status['checked_out']}/{pool_status['size']} in use"
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False, str(e)
    
    @retry_database_operation(max_attempts=2)
    @query_performance_monitor("create_contact")
    def create_contact(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Create contact record with validation and error handling"""
        try:
            from models import Contact
            
            # Validate required fields
            required_fields = ['name', 'email', 'subject', 'message']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return False, f"Missing required fields: {', '.join(missing_fields)}"
            
            # Data sanitization
            sanitized_data = {
                'name': data['name'][:100],  # Limit name length
                'email': data['email'][:120].lower(),  # Normalize email
                'phone': data.get('phone', '')[:20],
                'subject': data['subject'][:200],
                'message': data['message'][:2000],  # Limit message length
                'created_at': datetime.utcnow()
            }
            
            with self.transaction_scope() as session:
                contact = Contact(**sanitized_data)
                session.add(contact)
                session.flush()  # Get ID without committing
                
                contact_id = contact.id
                logger.info(f"Contact created successfully: ID {contact_id}")
                
                return True, f"Contact created with ID {contact_id}"
                
        except IntegrityError as e:
            logger.warning(f"Contact creation integrity error: {e}")
            return False, "Email address may already be in use"
        except Exception as e:
            logger.error(f"Contact creation failed: {e}")
            return False, f"Database error: {str(e)[:100]}"
    
    @retry_database_operation(max_attempts=2)
    @query_performance_monitor("log_process_consultation")
    def log_process_consultation(self, process_number: str, ip_address: str) -> bool:
        """Log process consultation with rate limiting"""
        try:
            from models import ProcessConsultation
            
            # Check for recent consultations from same IP (rate limiting)
            cutoff_time = datetime.utcnow() - timedelta(minutes=5)
            
            with self.transaction_scope() as session:
                recent_count = session.query(ProcessConsultation).filter(
                    and_(
                        ProcessConsultation.ip_address == ip_address,
                        ProcessConsultation.consulted_at > cutoff_time
                    )
                ).count()
                
                if recent_count > 10:  # Rate limit
                    logger.warning(f"Rate limit exceeded for IP {ip_address}")
                    return False
                
                consultation = ProcessConsultation(
                    process_number=process_number[:50],
                    ip_address=ip_address,
                    consulted_at=datetime.utcnow()
                )
                
                session.add(consultation)
                return True
                
        except Exception as e:
            logger.error(f"Process consultation logging failed: {e}")
            return False
    
    @retry_database_operation(max_attempts=2)
    @query_performance_monitor("log_chatbot_interaction")
    def log_chatbot_interaction(self, user_message: str, bot_response: str, session_id: str) -> bool:
        """Log chatbot interaction with session tracking"""
        try:
            from models import ChatMessage
            
            # Limit message lengths
            user_message = user_message[:1000]
            bot_response = bot_response[:2000]
            session_id = session_id[:100]
            
            with self.transaction_scope() as session:
                chat_message = ChatMessage(
                    user_message=user_message,
                    bot_response=bot_response,
                    session_id=session_id,
                    created_at=datetime.utcnow()
                )
                
                session.add(chat_message)
                return True
                
        except Exception as e:
            logger.error(f"Chatbot interaction logging failed: {e}")
            return False
    
    @query_performance_monitor("get_recent_contacts")
    def get_recent_contacts(self, limit: int = 10, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent contacts with optimized query"""
        try:
            from models import Contact
            from app import db
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            contacts = db.session.query(Contact).filter(
                Contact.created_at > cutoff_date
            ).order_by(
                Contact.created_at.desc()
            ).limit(limit).all()
            
            return [
                {
                    'id': contact.id,
                    'name': contact.name,
                    'email': contact.email,
                    'subject': contact.subject,
                    'created_at': contact.created_at.isoformat()
                }
                for contact in contacts
            ]
            
        except Exception as e:
            logger.error(f"Failed to get recent contacts: {e}")
            return []
    
    @query_performance_monitor("get_consultation_stats")
    def get_consultation_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get process consultation statistics"""
        try:
            from models import ProcessConsultation
            from app import db
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Total consultations
            total_consultations = db.session.query(ProcessConsultation).filter(
                ProcessConsultation.consulted_at > cutoff_date
            ).count()
            
            # Unique processes consulted
            unique_processes = db.session.query(
                func.count(func.distinct(ProcessConsultation.process_number))
            ).filter(
                ProcessConsultation.consulted_at > cutoff_date
            ).scalar()
            
            # Daily consultation counts
            daily_stats = db.session.query(
                func.date(ProcessConsultation.consulted_at).label('date'),
                func.count(ProcessConsultation.id).label('count')
            ).filter(
                ProcessConsultation.consulted_at > cutoff_date
            ).group_by(
                func.date(ProcessConsultation.consulted_at)
            ).order_by('date').all()
            
            return {
                'total_consultations': total_consultations,
                'unique_processes': unique_processes,
                'daily_stats': [
                    {'date': stat.date.isoformat(), 'count': stat.count}
                    for stat in daily_stats
                ],
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Failed to get consultation stats: {e}")
            return {'error': str(e)}
    
    @query_performance_monitor("cleanup_old_data")
    def cleanup_old_data(self, days_to_keep: int = 90) -> Dict[str, int]:
        """Clean up old data to maintain performance"""
        try:
            from models import ProcessConsultation, ChatMessage
            from app import db
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            cleanup_stats = {}
            
            with self.transaction_scope() as session:
                # Clean old process consultations
                old_consultations = session.query(ProcessConsultation).filter(
                    ProcessConsultation.consulted_at < cutoff_date
                ).delete()
                cleanup_stats['consultations_deleted'] = old_consultations
                
                # Clean old chat messages
                old_chats = session.query(ChatMessage).filter(
                    ChatMessage.created_at < cutoff_date
                ).delete()
                cleanup_stats['chat_messages_deleted'] = old_chats
            
            logger.info(f"Data cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")
            return {'error': str(e)}
    
    @query_performance_monitor("optimize_database")
    def optimize_database(self) -> Dict[str, Any]:
        """Perform database optimization operations"""
        try:
            from app import db
            results = {}
            
            # Analyze query performance
            if db.engine.dialect.name == 'postgresql':
                # PostgreSQL-specific optimizations
                db.session.execute(text('ANALYZE'))
                results['analyze'] = 'completed'
                
                # Get table sizes
                table_sizes = db.session.execute(text("""
                    SELECT schemaname, tablename, 
                           pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                """)).fetchall()
                
                results['table_sizes'] = [
                    {'table': row.tablename, 'size': row.size}
                    for row in table_sizes
                ]
            
            elif db.engine.dialect.name == 'sqlite':
                # SQLite-specific optimizations
                db.session.execute(text('VACUUM'))
                db.session.execute(text('ANALYZE'))
                results['vacuum'] = 'completed'
                results['analyze'] = 'completed'
            
            db.session.commit()
            return results
            
        except Exception as e:
            logger.error(f"Database optimization failed: {e}")
            return {'error': str(e)}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive database performance metrics"""
        return {
            'service_metrics': self.metrics.get_stats(),
            'connection_health': self.check_connection(),
            'timestamp': datetime.utcnow().isoformat()
        }


# Global database service instance
db_service = OptimizedDatabaseService()
db_metrics = db_service.metrics


# Convenience functions for backward compatibility
def safe_commit():
    """Legacy function - use transaction_scope instead"""
    return db_service.check_connection()


def check_connection():
    """Check database connection health"""
    return db_service.check_connection()


def create_contact(data: Dict[str, Any]):
    """Create contact record"""
    return db_service.create_contact(data)


def log_process_consultation(process_number: str, ip_address: str):
    """Log process consultation"""
    return db_service.log_process_consultation(process_number, ip_address)


def log_chatbot_interaction(user_message: str, bot_response: str, session_id: str):
    """Log chatbot interaction"""
    return db_service.log_chatbot_interaction(user_message, bot_response, session_id)