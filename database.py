"""
Database configuration and optimization module
Provides centralized database management for the court application
"""
import os
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    """Base model class for all database models"""
    pass

# Initialize SQLAlchemy with the custom base
db = SQLAlchemy(model_class=Base)

def configure_database(app):
    """Configure database with optimized settings for production"""
    
    # Database URI configuration
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        # Fallback to SQLite for development
        database_url = 'sqlite:///court_app.db'
        logger.warning("Using SQLite fallback database")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    # Optimized engine options for PostgreSQL/SQLite compatibility
    engine_options = {
        'pool_recycle': 1800,
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'max_overflow': 20,
        'pool_size': 10
    }
    
    # Add PostgreSQL-specific options if using PostgreSQL
    if database_url and database_url.startswith('postgresql'):
        engine_options.update({
            'pool_reset_on_return': 'commit',
            'echo': False,
            'isolation_level': 'READ_COMMITTED'
        })
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_options
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the database with the app
    db.init_app(app)
    
    logger.info("Database configuration completed")

def create_all_tables(app):
    """Create all database tables"""
    with app.app_context():
        try:
            # Import models to ensure they're registered
            from models import Contact, ProcessConsultation, AssessorMeeting, ChatMessage
            
            # Create all tables
            db.create_all()
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise

def optimize_database_performance():
    """Apply database performance optimizations"""
    try:
        # Check if we're using PostgreSQL
        database_url = os.environ.get('DATABASE_URL', '')
        
        if database_url.startswith('postgresql'):
            # PostgreSQL-specific optimizations
            try:
                # Analyze tables for better query planning
                db.session.execute(text("ANALYZE;"))
                db.session.commit()
                logger.info("PostgreSQL performance optimization applied")
            except Exception as e:
                logger.warning(f"PostgreSQL optimization failed: {e}")
                db.session.rollback()
        else:
            # SQLite optimizations
            try:
                db.session.execute(text("PRAGMA optimize;"))
                db.session.commit()
                logger.info("SQLite performance optimization applied")
            except Exception as e:
                logger.warning(f"SQLite optimization failed: {e}")
                db.session.rollback()
                
    except Exception as e:
        logger.warning(f"Database optimization error: {e}")

def check_database_health():
    """Check database connection health"""
    try:
        # Simple connection test
        db.session.execute(text("SELECT 1"))
        db.session.commit()
        return True, "Database connection healthy"
    except Exception as e:
        return False, f"Database connection error: {e}"

def get_database_stats():
    """Get basic database statistics"""
    try:
        stats = {}
        
        # Import models for table counting
        from models import Contact, ProcessConsultation, AssessorMeeting, ChatMessage
        
        stats['contacts'] = Contact.query.count()
        stats['consultations'] = ProcessConsultation.query.count() 
        stats['meetings'] = AssessorMeeting.query.count()
        stats['chat_messages'] = ChatMessage.query.count()
        
        return stats
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {}