"""
Centralized database configuration and model initialization
Prevents circular import issues and optimizes database connections
"""
import os
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def configure_database(app):
    """Configure database with optimized settings"""
    
    # Enhanced database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///court_site.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_timeout": 30,
        "max_overflow": 20,
        "pool_size": 10,
        "echo": False,
        "connect_args": {"check_same_thread": False} if "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"] else {}
    }
    
    # SQLite optimization
    if "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]:
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            if isinstance(dbapi_connection, sqlite3.Connection):
                cursor = dbapi_connection.cursor()
                # Enable WAL mode for better concurrency
                cursor.execute("PRAGMA journal_mode=WAL")
                # Optimize for performance
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=10000")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
                cursor.close()
    
    # Initialize database
    db.init_app(app)
    logging.info("Database configured successfully")

def create_all_tables(app):
    """Create all database tables with proper context"""
    with app.app_context():
        try:
            # Import all models to ensure they're registered
            from models import Contact, NewsItem, ProcessConsultation, ChatMessage, HearingSchedule, AvailableTimeSlot, AssessorMeeting
            
            # Create tables
            db.create_all()
            logging.info("All database tables created successfully")
            
        except Exception as e:
            logging.error(f"Error creating database tables: {e}")
            raise

def optimize_database_performance():
    """Apply database performance optimizations"""
    try:
        # Get all table names in the database
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        # PostgreSQL optimizations
        if "postgresql" in db.engine.url.drivername:
            with db.engine.connect() as conn:
                # Create indexes only for existing tables
                if 'contact' in existing_tables:
                    conn.execute(db.text("CREATE INDEX IF NOT EXISTS idx_contact_created_at ON contact(created_at)"))
                if 'news_item' in existing_tables or 'newsitem' in existing_tables:
                    table_name = 'news_item' if 'news_item' in existing_tables else 'newsitem'
                    conn.execute(db.text(f"CREATE INDEX IF NOT EXISTS idx_news_published_at ON {table_name}(published_at)"))
                if 'process_consultation' in existing_tables or 'processconsultation' in existing_tables:
                    table_name = 'process_consultation' if 'process_consultation' in existing_tables else 'processconsultation'
                    conn.execute(db.text(f"CREATE INDEX IF NOT EXISTS idx_process_consultation_created ON {table_name}(consulted_at)"))
                if 'chat_message' in existing_tables or 'chatmessage' in existing_tables:
                    table_name = 'chat_message' if 'chat_message' in existing_tables else 'chatmessage'
                    conn.execute(db.text(f"CREATE INDEX IF NOT EXISTS idx_chat_session ON {table_name}(session_id)"))
                conn.commit()
                
        logging.info(f"Database performance optimizations applied for tables: {existing_tables}")
        
    except Exception as e:
        logging.warning(f"Could not apply database optimizations: {e}")

def get_database_stats():
    """Get database connection and performance statistics"""
    try:
        stats = {
            'engine': str(db.engine.url),
            'pool_size': db.engine.pool.size(),
            'checked_in': db.engine.pool.checkedin(),
            'checked_out': db.engine.pool.checkedout(),
            'overflow': db.engine.pool.overflow(),
            'status': 'healthy'
        }
        return stats
    except Exception as e:
        logging.error(f"Error getting database stats: {e}")
        return {'status': 'error', 'error': str(e)}