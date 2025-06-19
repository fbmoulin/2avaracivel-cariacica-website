"""
Database Management - Modular Backend
Centralized database configuration and utilities
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask import current_app
import logging

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base model class with common utilities"""
    pass


# Global database instance
db = SQLAlchemy(model_class=Base)


def init_database(app):
    """Initialize database with the Flask app"""
    try:
        db.init_app(app)
        
        with app.app_context():
            # Import models to ensure they're registered
            from src.backend.models import Contact, ProcessConsultation, ChatMessage, AssessorMeeting
            
            # Create all tables
            db.create_all()
            logger.info("Database initialized successfully")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def get_db():
    """Get database instance"""
    return db


def check_database_health():
    """Check database connection health"""
    try:
        # Simple query to test connection
        db.session.execute(db.text('SELECT 1'))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


def optimize_database():
    """Apply database optimizations"""
    try:
        if current_app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('postgresql'):
            # PostgreSQL specific optimizations
            db.session.execute(db.text('ANALYZE;'))
            db.session.commit()
            logger.info("Database optimization completed")
    except Exception as e:
        logger.warning(f"Database optimization failed: {e}")