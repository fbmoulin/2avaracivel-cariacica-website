"""
Advanced caching service with Redis support and intelligent cache management
Provides distributed caching, cache warming, and automatic invalidation
"""
import os
import json
import logging
import time
from typing import Any, Optional, Dict, List
from functools import wraps
from datetime import datetime, timedelta
import hashlib


class CacheService:
    """Advanced caching service with multiple backends"""
    
    # Cache timeout constants
    SHORT_CACHE = 60          # 1 minute
    MEDIUM_CACHE = 300        # 5 minutes
    LONG_CACHE = 1800         # 30 minutes
    EXTENDED_CACHE = 7200     # 2 hours
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache_backend = self._initialize_cache_backend()
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    def _initialize_cache_backend(self):
        """Initialize cache backend with robust fallback"""
        try:
            # Try Redis first for production
            import redis
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
            client = redis.from_url(
                redis_url, 
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            client.ping()  # Test connection
            self.logger.info("Redis cache backend initialized successfully")
            return RedisCache(client)
        except Exception as e:
            # Fallback to memory cache with logging
            self.logger.info(f"Redis not available ({e}), using memory cache backend")
            return MemoryCache()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.cache_backend.get(key)
            if value is not None:
                self._cache_stats['hits'] += 1
                return value
            else:
                self._cache_stats['misses'] += 1
                return None
        except Exception as e:
            self.logger.error(f"Cache get error: {e}")
            self._cache_stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any, timeout: int = MEDIUM_CACHE) -> bool:
        """Set value in cache"""
        try:
            success = self.cache_backend.set(key, value, timeout)
            if success:
                self._cache_stats['sets'] += 1
            return success
        except Exception as e:
            self.logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            success = self.cache_backend.delete(key)
            if success:
                self._cache_stats['deletes'] += 1
            return success
        except Exception as e:
            self.logger.error(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            count = self.cache_backend.clear_pattern(pattern)
            self._cache_stats['deletes'] += count
            return count
        except Exception as e:
            self.logger.error(f"Cache clear pattern error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._cache_stats['hits'] + self._cache_stats['misses']
        hit_rate = (self._cache_stats['hits'] / max(total_requests, 1)) * 100
        
        return {
            'hits': self._cache_stats['hits'],
            'misses': self._cache_stats['misses'],
            'sets': self._cache_stats['sets'],
            'deletes': self._cache_stats['deletes'],
            'hit_rate': round(hit_rate, 2),
            'backend': type(self.cache_backend).__name__
        }
    
    @staticmethod
    def cached_route(timeout: int = MEDIUM_CACHE, key_prefix: str = None):
        """Decorator for caching Flask route responses"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                from flask import request
                
                # Generate cache key
                if key_prefix:
                    cache_key = f"{key_prefix}:{request.path}:{request.query_string.decode()}"
                else:
                    cache_key = f"route:{request.path}:{request.query_string.decode()}"
                
                # Hash long keys
                if len(cache_key) > 200:
                    cache_key = hashlib.md5(cache_key.encode()).hexdigest()
                
                # Try to get from cache
                cached_result = cache_service.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                cache_service.set(cache_key, result, timeout)
                return result
            
            return wrapper
        return decorator


class MemoryCache:
    """Simple in-memory cache implementation"""
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            if key in self._expiry and time.time() > self._expiry[key]:
                del self._cache[key]
                del self._expiry[key]
                return None
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any, timeout: int) -> bool:
        self._cache[key] = value
        self._expiry[key] = time.time() + timeout
        return True
    
    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
            return True
        return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern (simple implementation)"""
        import fnmatch
        keys_to_delete = [key for key in self._cache.keys() if fnmatch.fnmatch(key, pattern)]
        for key in keys_to_delete:
            self.delete(key)
        return len(keys_to_delete)


class RedisCache:
    """Redis-based cache implementation"""
    
    def __init__(self, client):
        self.client = client
    
    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None
    
    def set(self, key: str, value: Any, timeout: int) -> bool:
        try:
            serialized = json.dumps(value, default=str)
            return self.client.setex(key, timeout, serialized)
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        try:
            return bool(self.client.delete(key))
        except Exception:
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception:
            return 0


# Global cache service instance
cache_service = CacheService()