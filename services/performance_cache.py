"""
Advanced Performance Caching System
2ª Vara Cível de Cariacica - Production-grade caching implementation
"""

import os
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

class PerformanceCache:
    """Advanced caching system for optimal performance"""
    
    def __init__(self):
        self.memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'last_cleanup': time.time()
        }
        self.max_cache_size = 1000
        self.default_ttl = 300  # 5 minutes
        
    def _generate_cache_key(self, key: str, params: Dict = None) -> str:
        """Generate consistent cache key"""
        if params:
            param_string = json.dumps(params, sort_keys=True)
            key_data = f"{key}:{param_string}"
        else:
            key_data = key
            
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_expired(self, cache_entry: Dict) -> bool:
        """Check if cache entry has expired"""
        return time.time() > cache_entry.get('expires_at', 0)
    
    def _cleanup_expired(self):
        """Remove expired cache entries"""
        current_time = time.time()
        
        # Only cleanup every 5 minutes
        if current_time - self.cache_stats['last_cleanup'] < 300:
            return
            
        expired_keys = []
        for key, entry in self.memory_cache.items():
            if self._is_expired(entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
            self.cache_stats['evictions'] += 1
        
        self.cache_stats['last_cleanup'] = current_time
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _evict_lru(self):
        """Evict least recently used entries if cache is full"""
        if len(self.memory_cache) >= self.max_cache_size:
            # Sort by last_accessed time and remove oldest
            sorted_entries = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].get('last_accessed', 0)
            )
            
            # Remove oldest 10% of entries
            evict_count = max(1, len(sorted_entries) // 10)
            for i in range(evict_count):
                key = sorted_entries[i][0]
                del self.memory_cache[key]
                self.cache_stats['evictions'] += 1
    
    def get(self, key: str, params: Dict = None) -> Optional[Any]:
        """Get value from cache"""
        cache_key = self._generate_cache_key(key, params)
        
        # Cleanup expired entries periodically
        self._cleanup_expired()
        
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            
            if not self._is_expired(entry):
                # Update access time
                entry['last_accessed'] = time.time()
                entry['access_count'] = entry.get('access_count', 0) + 1
                
                self.cache_stats['hits'] += 1
                logger.debug(f"Cache hit for key: {key}")
                return entry['value']
            else:
                # Remove expired entry
                del self.memory_cache[cache_key]
                self.cache_stats['evictions'] += 1
        
        self.cache_stats['misses'] += 1
        logger.debug(f"Cache miss for key: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = None, params: Dict = None):
        """Set value in cache"""
        cache_key = self._generate_cache_key(key, params)
        ttl = ttl or self.default_ttl
        
        # Evict LRU entries if cache is full
        self._evict_lru()
        
        current_time = time.time()
        self.memory_cache[cache_key] = {
            'value': value,
            'created_at': current_time,
            'last_accessed': current_time,
            'expires_at': current_time + ttl,
            'access_count': 0,
            'ttl': ttl
        }
        
        logger.debug(f"Cached value for key: {key} (TTL: {ttl}s)")
    
    def delete(self, key: str, params: Dict = None):
        """Delete value from cache"""
        cache_key = self._generate_cache_key(key, params)
        
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
            logger.debug(f"Deleted cache entry for key: {key}")
    
    def clear(self):
        """Clear all cache entries"""
        self.memory_cache.clear()
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'last_cleanup': time.time()
        }
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': len(self.memory_cache),
            'max_cache_size': self.max_cache_size,
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'evictions': self.cache_stats['evictions'],
            'hit_rate_percent': round(hit_rate, 2),
            'total_requests': total_requests,
            'memory_usage_percent': round(len(self.memory_cache) / self.max_cache_size * 100, 2)
        }

class ChatbotResponseCache:
    """Specialized cache for chatbot responses"""
    
    def __init__(self, cache_instance: PerformanceCache):
        self.cache = cache_instance
        self.response_ttl = 300  # 5 minutes for chatbot responses
    
    def get_response(self, message: str) -> Optional[str]:
        """Get cached chatbot response"""
        # Normalize message for consistent caching
        normalized_message = message.lower().strip()
        return self.cache.get('chatbot_response', {'message': normalized_message})
    
    def cache_response(self, message: str, response: str):
        """Cache chatbot response"""
        normalized_message = message.lower().strip()
        self.cache.set(
            'chatbot_response', 
            response, 
            ttl=self.response_ttl,
            params={'message': normalized_message}
        )

class StaticFileCache:
    """Cache for static file metadata and headers"""
    
    def __init__(self, cache_instance: PerformanceCache):
        self.cache = cache_instance
        self.file_ttl = 3600  # 1 hour for file metadata
    
    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """Get cached file information"""
        return self.cache.get('static_file_info', {'path': file_path})
    
    def cache_file_info(self, file_path: str, file_info: Dict):
        """Cache static file information"""
        self.cache.set(
            'static_file_info',
            file_info,
            ttl=self.file_ttl,
            params={'path': file_path}
        )

class DatabaseQueryCache:
    """Cache for database query results"""
    
    def __init__(self, cache_instance: PerformanceCache):
        self.cache = cache_instance
        self.query_ttl = 600  # 10 minutes for database queries
    
    def get_query_result(self, query_hash: str) -> Optional[Any]:
        """Get cached query result"""
        return self.cache.get('db_query', {'hash': query_hash})
    
    def cache_query_result(self, query_hash: str, result: Any, ttl: int = None):
        """Cache database query result"""
        ttl = ttl or self.query_ttl
        self.cache.set(
            'db_query',
            result,
            ttl=ttl,
            params={'hash': query_hash}
        )

class CacheManager:
    """Centralized cache management"""
    
    def __init__(self):
        self.performance_cache = PerformanceCache()
        self.chatbot_cache = ChatbotResponseCache(self.performance_cache)
        self.static_cache = StaticFileCache(self.performance_cache)
        self.db_cache = DatabaseQueryCache(self.performance_cache)
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive caching statistics"""
        base_stats = self.performance_cache.get_stats()
        
        return {
            **base_stats,
            'cache_types': {
                'chatbot_responses': 'Active',
                'static_files': 'Active',
                'database_queries': 'Active',
                'general_cache': 'Active'
            },
            'performance_impact': {
                'memory_efficient': True,
                'automatic_cleanup': True,
                'lru_eviction': True,
                'ttl_expiration': True
            }
        }
    
    def optimize_cache_settings(self, max_size: int = None, default_ttl: int = None):
        """Optimize cache settings for production"""
        if max_size:
            self.performance_cache.max_cache_size = max_size
        
        if default_ttl:
            self.performance_cache.default_ttl = default_ttl
    
    def health_check(self) -> Dict[str, Any]:
        """Perform cache health check"""
        stats = self.performance_cache.get_stats()
        
        health_status = {
            'status': 'healthy',
            'issues': []
        }
        
        # Check for potential issues
        if stats['hit_rate_percent'] < 30:
            health_status['issues'].append('Low cache hit rate - consider optimizing cache keys')
        
        if stats['memory_usage_percent'] > 90:
            health_status['issues'].append('High memory usage - consider increasing max cache size')
        
        if stats['evictions'] > stats['hits']:
            health_status['issues'].append('High eviction rate - consider increasing TTL values')
        
        if health_status['issues']:
            health_status['status'] = 'warning'
        
        return {
            'cache_health': health_status,
            'statistics': stats,
            'timestamp': datetime.now().isoformat()
        }

# Global cache manager instance
cache_manager = CacheManager()