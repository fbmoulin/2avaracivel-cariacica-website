"""
Database service layer for 2ª Vara Cível de Cariacica
Optimized for performance and data integrity with robust error handling
"""
from sqlalchemy import text, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, DisconnectionError, TimeoutError
from flask import current_app
from app_factory import db
from models import Contact, ProcessConsultation, ChatMessage
from services.integration_service import RetryManager
from datetime import datetime, timedelta
import logging
import time


class DatabaseService:
    """Centralized database operations service"""
    
    @staticmethod
    @RetryManager.with_retry(max_attempts=3, backoff_factor=2.0, initial_delay=0.5)
    def safe_commit():
        """Safely commit database transaction with rollback on error and retry logic"""
        try:
            db.session.commit()
            return True, None
        except (DisconnectionError, TimeoutError) as e:
            db.session.rollback()
            current_app.logger.warning(f"Database connection issue, retrying: {e}")
            # Force reconnection
            db.engine.dispose()
            raise e  # Trigger retry
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database commit failed: {e}")
            return False, str(e)
    
    @staticmethod
    def check_connection():
        """Check database connection health"""
        try:
            # Simple connectivity test
            db.session.execute(text('SELECT 1'))
            return True, "Connection healthy"
        except Exception as e:
            current_app.logger.error(f"Database connection check failed: {e}")
            return False, str(e)
    
    @staticmethod
    def create_contact(data):
        """Create a new contact record with validation"""
        try:
            contact = Contact(
                name=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone'),
                subject=data.get('subject'),
                message=data.get('message'),
                created_at=datetime.utcnow()
            )
            
            db.session.add(contact)
            success, error = DatabaseService.safe_commit()
            
            if success:
                return contact, None
            return None, error
            
        except Exception as e:
            current_app.logger.error(f"Error creating contact: {e}")
            return None, str(e)
    
    @staticmethod
    def create_process_consultation(process_number, ip_address=None):
        """Record process consultation with rate limiting"""
        try:
            # Check if same IP consulted this process recently (spam protection)
            if ip_address:
                recent_consultation = ProcessConsultation.query.filter_by(
                    process_number=process_number,
                    ip_address=ip_address
                ).filter(
                    ProcessConsultation.consulted_at > datetime.utcnow() - timedelta(minutes=5)
                ).first()
                
                if recent_consultation:
                    return None, "Consulta muito recente. Aguarde alguns minutos."
            
            consultation = ProcessConsultation(
                process_number=process_number,
                ip_address=ip_address,
                consulted_at=datetime.utcnow()
            )
            
            db.session.add(consultation)
            success, error = DatabaseService.safe_commit()
            
            if success:
                return consultation, None
            return None, error
            
        except Exception as e:
            current_app.logger.error(f"Error creating process consultation: {e}")
            return None, str(e)
    
    @staticmethod
    def create_chat_message(user_message, bot_response, session_id=None):
        """Record chatbot interaction"""
        try:
            chat = ChatMessage(
                user_message=user_message,
                bot_response=bot_response,
                session_id=session_id,
                created_at=datetime.utcnow()
            )
            
            db.session.add(chat)
            success, error = DatabaseService.safe_commit()
            
            if success:
                return chat, None
            return None, error
            
        except Exception as e:
            current_app.logger.error(f"Error creating chat message: {e}")
            return None, str(e)
    
    @staticmethod
    def get_recent_news(limit=5):
        """Get recent news items with caching"""
        try:
            news = NewsItem.query.filter_by(is_active=True)\
                .order_by(NewsItem.published_at.desc())\
                .limit(limit).all()
            return news, None
        except Exception as e:
            current_app.logger.error(f"Error fetching news: {e}")
            return [], str(e)
    
    @staticmethod
    def get_contact_statistics():
        """Get contact form statistics"""
        try:
            total_contacts = Contact.query.count()
            recent_contacts = Contact.query.filter(
                Contact.created_at > datetime.utcnow() - timedelta(days=30)
            ).count()
            
            return {
                'total': total_contacts,
                'recent': recent_contacts
            }, None
            
        except Exception as e:
            current_app.logger.error(f"Error getting contact stats: {e}")
            return {}, str(e)
    
    @staticmethod
    def get_process_consultation_statistics():
        """Get process consultation statistics"""
        try:
            total_consultations = ProcessConsultation.query.count()
            recent_consultations = ProcessConsultation.query.filter(
                ProcessConsultation.consulted_at > datetime.utcnow() - timedelta(days=30)
            ).count()
            
            # Most consulted processes
            popular_processes = db.session.query(
                ProcessConsultation.process_number,
                func.count(ProcessConsultation.id).label('count')
            ).group_by(ProcessConsultation.process_number)\
            .order_by(func.count(ProcessConsultation.id).desc())\
            .limit(10).all()
            
            return {
                'total': total_consultations,
                'recent': recent_consultations,
                'popular': [{'process': p[0], 'count': p[1]} for p in popular_processes]
            }, None
            
        except Exception as e:
            current_app.logger.error(f"Error getting consultation stats: {e}")
            return {}, str(e)
    
    @staticmethod
    def get_chatbot_statistics():
        """Get chatbot usage statistics"""
        try:
            total_messages = ChatMessage.query.count()
            recent_messages = ChatMessage.query.filter(
                ChatMessage.created_at > datetime.utcnow() - timedelta(days=30)
            ).count()
            
            # Unique sessions
            unique_sessions = db.session.query(
                func.count(func.distinct(ChatMessage.session_id))
            ).scalar() or 0
            
            return {
                'total_messages': total_messages,
                'recent_messages': recent_messages,
                'unique_sessions': unique_sessions
            }, None
            
        except Exception as e:
            current_app.logger.error(f"Error getting chatbot stats: {e}")
            return {}, str(e)
    
    @staticmethod
    def cleanup_old_data(days=90):
        """Clean up old data to maintain performance"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Clean old process consultations
            old_consultations = ProcessConsultation.query.filter(
                ProcessConsultation.consulted_at < cutoff_date
            ).delete()
            
            # Clean old chat messages (keep more recent ones)
            chat_cutoff = datetime.utcnow() - timedelta(days=30)
            old_chats = ChatMessage.query.filter(
                ChatMessage.created_at < chat_cutoff
            ).delete()
            
            success, error = DatabaseService.safe_commit()
            
            if success:
                current_app.logger.info(f"Cleaned up {old_consultations} consultations and {old_chats} chat messages")
                return True, f"Cleaned {old_consultations + old_chats} records"
            
            return False, error
            
        except Exception as e:
            current_app.logger.error(f"Error during cleanup: {e}")
            return False, str(e)
    
    @staticmethod
    def check_database_health():
        """Check database health and performance"""
        try:
            # Test basic connectivity
            result = db.session.execute(text("SELECT 1")).scalar()
            
            # Check table sizes
            tables_info = {}
            for model in [Contact, NewsItem, ProcessConsultation, ChatMessage]:
                count = model.query.count()
                tables_info[model.__tablename__] = count
            
            # Check for any locked transactions (PostgreSQL specific)
            if 'postgresql' in current_app.config['SQLALCHEMY_DATABASE_URI']:
                locks = db.session.execute(text(
                    "SELECT count(*) FROM pg_locks WHERE NOT granted"
                )).scalar()
                tables_info['blocked_queries'] = locks
            
            return {
                'status': 'healthy',
                'connectivity': 'ok' if result == 1 else 'failed',
                'tables': tables_info
            }, None
            
        except Exception as e:
            current_app.logger.error(f"Database health check failed: {e}")
            return {'status': 'unhealthy'}, str(e)