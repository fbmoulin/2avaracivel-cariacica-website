"""
Optimized cache service with Redis fallback and intelligent caching strategies
High-performance caching layer with compression and TTL management
"""
import logging
import pickle
import time
import hashlib
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
from functools import wraps
import json
import gzip

logger = logging.getLogger(__name__)


class CacheBackend:
    """Abstract base class for cache backends"""
    
    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError
    
    def set(self, key: str, value: Any, timeout: int = 300) -> bool:
        raise NotImplementedError
    
    def delete(self, key: str) -> bool:
        raise NotImplementedError
    
    def clear(self) -> bool:
        raise NotImplementedError
    
    def get_stats(self) -> Dict[str, Any]:
        raise NotImplementedError


class MemoryCacheBackend(CacheBackend):
    """Optimized in-memory cache with LRU eviction"""
    
    def __init__(self, max_size: int = 1000, default_timeout: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        self.max_size = max_size
        self.default_timeout = default_timeout
        self.hits = 0
        self.misses = 0
        self.sets = 0
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self.cache:
            return True
        
        expires_at = self.cache[key].get('expires_at')
        if expires_at is None:
            return False
        
        return time.time() > expires_at
    
    def _evict_expired(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, data in self.cache.items()
            if data.get('expires_at') and current_time > data['expires_at']
        ]
        
        for key in expired_keys:
            self.delete(key)
    
    def _evict_lru(self):
        """Evict least recently used entries if over capacity"""
        if len(self.cache) <= self.max_size:
            return
        
        # Sort by access time and remove oldest
        sorted_keys = sorted(self.access_times.items(), key=lambda x: x[1])
        keys_to_remove = sorted_keys[:len(self.cache) - self.max_size + 1]
        
        for key, _ in keys_to_remove:
            self.delete(key)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with LRU tracking"""
        self._evict_expired()
        
        if key not in self.cache or self._is_expired(key):
            self.misses += 1
            return None
        
        self.hits += 1
        self.access_times[key] = time.time()
        return self.cache[key]['value']
    
    def set(self, key: str, value: Any, timeout: int = None) -> bool:
        """Set value in cache with optional timeout"""
        try:
            if timeout is None:
                timeout = self.default_timeout
            
            expires_at = time.time() + timeout if timeout > 0 else None
            
            self.cache[key] = {
                'value': value,
                'created_at': time.time(),
                'expires_at': expires_at
            }
            self.access_times[key] = time.time()
            self.sets += 1
            
            self._evict_lru()
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        removed = key in self.cache
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
        return removed
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        self.cache.clear()
        self.access_times.clear()
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'backend': 'MemoryCache',
            'total_keys': len(self.cache),
            'hits': self.hits,
            'misses': self.misses,
            'sets': self.sets,
            'hit_rate': hit_rate,
            'miss_rate': 100 - hit_rate,
            'max_size': self.max_size
        }


class RedisCacheBackend(CacheBackend):
    """Redis cache backend with compression and serialization"""
    
    def __init__(self, redis_url: str = 'redis://localhost:6379', 
                 compress_threshold: int = 1024):
        self.redis_url = redis_url
        self.compress_threshold = compress_threshold
        self.redis_client = None
        self.hits = 0
        self.misses = 0
        self.sets = 0
        
        self._connect()
    
    def _connect(self):
        """Initialize Redis connection"""
        try:
            import redis
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=False,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache backend connected")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize and optionally compress value"""
        try:
            # Serialize with pickle
            data = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Compress if over threshold
            if len(data) > self.compress_threshold:
                data = gzip.compress(data)
                return b'compressed:' + data
            
            return b'raw:' + data
            
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            raise
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize and decompress value"""
        try:
            if data.startswith(b'compressed:'):
                data = gzip.decompress(data[11:])
            elif data.startswith(b'raw:'):
                data = data[4:]
            
            return pickle.loads(data)
            
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            raise
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        if not self.redis_client:
            return None
        
        try:
            data = self.redis_client.get(f"cache:{key}")
            if data is None:
                self.misses += 1
                return None
            
            self.hits += 1
            return self._deserialize(data)
            
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            self.misses += 1
            return None
    
    def set(self, key: str, value: Any, timeout: int = 300) -> bool:
        """Set value in Redis cache"""
        if not self.redis_client:
            return False
        
        try:
            data = self._serialize(value)
            result = self.redis_client.setex(f"cache:{key}", timeout, data)
            
            if result:
                self.sets += 1
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis cache"""
        if not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.delete(f"cache:{key}"))
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        if not self.redis_client:
            return False
        
        try:
            keys = self.redis_client.keys("cache:*")
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        stats = {
            'backend': 'RedisCache',
            'connected': bool(self.redis_client),
            'hits': self.hits,
            'misses': self.misses,
            'sets': self.sets,
            'hit_rate': hit_rate,
            'miss_rate': 100 - hit_rate
        }
        
        if self.redis_client:
            try:
                info = self.redis_client.info('memory')
                stats.update({
                    'memory_used': info.get('used_memory_human', 'unknown'),
                    'total_keys': self.redis_client.dbsize()
                })
            except Exception as e:
                logger.warning(f"Could not get Redis info: {e}")
        
        return stats


class OptimizedCacheService:
    """High-performance cache service with multiple backends and intelligent strategies"""
    
    def __init__(self):
        self.primary_backend: Optional[CacheBackend] = None
        self.fallback_backend: Optional[CacheBackend] = None
        self.enable_fallback = True
        self.key_prefix = "court_app"
        
        self._initialize_backends()
    
    def _initialize_backends(self):
        """Initialize cache backends with fallback"""
        try:
            # Try Redis first
            import os
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
            self.primary_backend = RedisCacheBackend(redis_url)
            logger.info("Primary cache backend: Redis")
        except Exception as e:
            logger.warning(f"Redis backend failed: {e}")
        
        # Always have memory cache as fallback
        self.fallback_backend = MemoryCacheBackend(max_size=1000, default_timeout=300)
        
        if not self.primary_backend:
            self.primary_backend = self.fallback_backend
            self.fallback_backend = None
            logger.info("Primary cache backend: Memory")
    
    def _make_key(self, key: str) -> str:
        """Generate prefixed cache key"""
        return f"{self.key_prefix}:{key}"
    
    def _hash_key(self, key: str) -> str:
        """Hash long keys to avoid length limits"""
        if len(key) > 200:
            return hashlib.md5(key.encode()).hexdigest()
        return key
    
    def get(self, key: str) -> Optional[Any]:
        """Get value with fallback support"""
        cache_key = self._make_key(self._hash_key(key))
        
        # Try primary backend
        try:
            value = self.primary_backend.get(cache_key)
            if value is not None:
                return value
        except Exception as e:
            logger.warning(f"Primary cache get failed: {e}")
        
        # Try fallback backend
        if self.fallback_backend and self.enable_fallback:
            try:
                return self.fallback_backend.get(cache_key)
            except Exception as e:
                logger.warning(f"Fallback cache get failed: {e}")
        
        return None
    
    def set(self, key: str, value: Any, timeout: int = 300) -> bool:
        """Set value with dual backend support"""
        cache_key = self._make_key(self._hash_key(key))
        success = False
        
        # Set in primary backend
        try:
            if self.primary_backend.set(cache_key, value, timeout):
                success = True
        except Exception as e:
            logger.warning(f"Primary cache set failed: {e}")
        
        # Set in fallback backend
        if self.fallback_backend and self.enable_fallback:
            try:
                self.fallback_backend.set(cache_key, value, timeout)
            except Exception as e:
                logger.warning(f"Fallback cache set failed: {e}")
        
        return success
    
    def delete(self, key: str) -> bool:
        """Delete from all backends"""
        cache_key = self._make_key(self._hash_key(key))
        success = False
        
        try:
            if self.primary_backend.delete(cache_key):
                success = True
        except Exception as e:
            logger.warning(f"Primary cache delete failed: {e}")
        
        if self.fallback_backend:
            try:
                self.fallback_backend.delete(cache_key)
            except Exception as e:
                logger.warning(f"Fallback cache delete failed: {e}")
        
        return success
    
    def clear(self) -> bool:
        """Clear all backends"""
        success = True
        
        try:
            self.primary_backend.clear()
        except Exception as e:
            logger.error(f"Primary cache clear failed: {e}")
            success = False
        
        if self.fallback_backend:
            try:
                self.fallback_backend.clear()
            except Exception as e:
                logger.error(f"Fallback cache clear failed: {e}")
        
        return success
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = {
            'timestamp': datetime.utcnow().isoformat(),
            'primary_backend': {},
            'fallback_backend': {}
        }
        
        try:
            stats['primary_backend'] = self.primary_backend.get_stats()
        except Exception as e:
            logger.error(f"Failed to get primary backend stats: {e}")
        
        if self.fallback_backend:
            try:
                stats['fallback_backend'] = self.fallback_backend.get_stats()
            except Exception as e:
                logger.error(f"Failed to get fallback backend stats: {e}")
        
        return stats
    
    def cache_function(self, timeout: int = 300, key_func: Optional[callable] = None):
        """Decorator to cache function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = f"func:{func.__name__}:{key_func(*args, **kwargs)}"
                else:
                    cache_key = f"func:{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
                
                # Try to get cached result
                result = self.get(cache_key)
                if result is not None:
                    return result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, timeout)
                return result
            
            return wrapper
        return decorator


# Global cache service instance
cache_service = OptimizedCacheService()


def cached(timeout: int = 300, key: Optional[str] = None):
    """Convenient decorator for caching function results"""
    return cache_service.cache_function(timeout=timeout, key_func=key)