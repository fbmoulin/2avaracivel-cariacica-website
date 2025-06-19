"""
Flask Extensions Initialization - Modular Backend
Centralized extension management for the application
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
import logging

logger = logging.getLogger(__name__)

# Initialize extensions
limiter = Limiter(key_func=get_remote_address)
cache = Cache()
csrf = CSRFProtect()


def init_extensions(app):
    """Initialize all Flask extensions"""
    try:
        # Rate limiting
        limiter.init_app(app)
        
        # Caching
        cache.init_app(app)
        
        # CSRF protection
        csrf.init_app(app)
        
        logger.info("Extensions initialized successfully")
        
    except Exception as e:
        logger.error(f"Extension initialization failed: {e}")
        raise


def get_cache():
    """Get cache instance"""
    return cache


def get_limiter():
    """Get limiter instance"""
    return limiter