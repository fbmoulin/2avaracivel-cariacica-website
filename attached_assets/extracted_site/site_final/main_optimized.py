"""
Optimized main entry point for 2ª Vara Cível de Cariacica
Production-ready with all optimizations integrated
"""
import os
import logging
from app_optimized import create_optimized_app
from services.cache_service_optimized import cache_service
from services.database_service_optimized import db_service
from services.chatbot_optimized import chatbot_service
from services.content_optimized import content_service

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def initialize_optimized_services():
    """Initialize all optimized services"""
    logger.info("Initializing optimized services...")
    
    # Warm up cache service
    try:
        cache_stats = cache_service.get_stats()
        logger.info(f"Cache service initialized: {cache_stats['backend']}")
    except Exception as e:
        logger.warning(f"Cache service initialization warning: {e}")
    
    # Check database health
    try:
        health, message = db_service.check_connection()
        if health:
            logger.info(f"Database service healthy: {message}")
        else:
            logger.error(f"Database service unhealthy: {message}")
    except Exception as e:
        logger.error(f"Database service check failed: {e}")
    
    # Initialize chatbot
    try:
        stats = chatbot_service.get_statistics()
        logger.info(f"Chatbot service initialized with {stats['predefined_responses']} predefined responses")
    except Exception as e:
        logger.warning(f"Chatbot service initialization warning: {e}")
    
    # Initialize content service
    try:
        content_stats = content_service.get_cache_stats()
        logger.info(f"Content service initialized with {content_stats['entries']} cached entries")
    except Exception as e:
        logger.warning(f"Content service initialization warning: {e}")
    
    logger.info("All optimized services initialized successfully")


# Create optimized application instance
app = create_optimized_app()

# Initialize services after app creation
with app.app_context():
    initialize_optimized_services()

if __name__ == '__main__':
    logger.info("Starting optimized Court Website v3.0.0")
    
    # Production configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )