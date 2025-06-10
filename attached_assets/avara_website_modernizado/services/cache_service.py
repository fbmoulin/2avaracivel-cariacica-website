"""
Caching service for 2ª Vara Cível de Cariacica
Optimized for performance and scalability
"""
from functools import wraps
from flask import current_app
from app_factory import cache
import json
import hashlib


class CacheService:
    """Centralized caching service"""
    
    # Cache timeouts (in seconds)
    SHORT_CACHE = 300      # 5 minutes
    MEDIUM_CACHE = 1800    # 30 minutes
    LONG_CACHE = 3600      # 1 hour
    VERY_LONG_CACHE = 86400  # 24 hours
    
    @staticmethod
    def generate_cache_key(*args, **kwargs):
        """Generate a consistent cache key from arguments"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    @staticmethod
    def cached_route(timeout=MEDIUM_CACHE, key_prefix='route'):
        """Decorator for caching route responses"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                cache_key = f"{key_prefix}:{f.__name__}:{CacheService.generate_cache_key(*args, **kwargs)}"
                
                # Try to get from cache
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = f(*args, **kwargs)
                cache.set(cache_key, result, timeout=timeout)
                return result
            
            return decorated_function
        return decorator
    
    @staticmethod
    def cached_data(timeout=MEDIUM_CACHE, key_prefix='data'):
        """Decorator for caching data functions"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                cache_key = f"{key_prefix}:{f.__name__}:{CacheService.generate_cache_key(*args, **kwargs)}"
                
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                result = f(*args, **kwargs)
                cache.set(cache_key, result, timeout=timeout)
                return result
            
            return decorated_function
        return decorator
    
    @staticmethod
    def invalidate_pattern(pattern):
        """Invalidate all cache keys matching a pattern"""
        try:
            if hasattr(cache.cache, 'delete_pattern'):
                cache.cache.delete_pattern(pattern)
            else:
                # Fallback for simple cache backends
                cache.clear()
        except Exception as e:
            current_app.logger.warning(f"Cache invalidation failed: {e}")
    
    @staticmethod
    def get_cache_stats():
        """Get cache statistics if available"""
        try:
            if hasattr(cache.cache, 'info'):
                return cache.cache.info()
            return {"status": "Cache statistics not available"}
        except Exception:
            return {"status": "Error retrieving cache stats"}


# Convenience functions
def cache_faq_data():
    """Cache FAQ data"""
    @CacheService.cached_data(timeout=CacheService.LONG_CACHE, key_prefix='faq')
    def _get_faq_data():
        from services.content import ContentService
        content_service = ContentService()
        return content_service.get_faq_data()
    return _get_faq_data()


def cache_services_data():
    """Cache services data"""
    @CacheService.cached_data(timeout=CacheService.LONG_CACHE, key_prefix='services')
    def _get_services_data():
        from services.content import ContentService
        content_service = ContentService()
        return content_service.get_services_data()
    return _get_services_data()


def cache_news_data():
    """Cache news data"""
    @CacheService.cached_data(timeout=CacheService.MEDIUM_CACHE, key_prefix='news')
    def _get_news_data():
        from services.content import ContentService
        content_service = ContentService()
        return content_service.get_news()
    return _get_news_data()


def invalidate_content_cache():
    """Invalidate all content-related cache"""
    CacheService.invalidate_pattern('faq:*')
    CacheService.invalidate_pattern('services:*')
    CacheService.invalidate_pattern('news:*')
    CacheService.invalidate_pattern('route:*')