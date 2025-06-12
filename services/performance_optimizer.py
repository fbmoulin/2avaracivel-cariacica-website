"""
Advanced Performance Optimization Service
2ª Vara Cível de Cariacica - Enterprise-grade performance tuning
"""

import time
import threading
import logging
import psutil
import gc
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from functools import wraps, lru_cache
import weakref

logger = logging.getLogger(__name__)

class PerformanceProfiler:
    """Advanced performance profiling and optimization"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.slow_operations = deque(maxlen=100)
        self.memory_snapshots = deque(maxlen=50)
        self.cpu_samples = deque(maxlen=100)
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.monitoring_active = True
        
        # Start background monitoring
        self._start_monitoring_thread()
    
    def _start_monitoring_thread(self):
        """Start background system monitoring"""
        def monitor():
            while self.monitoring_active:
                try:
                    # CPU monitoring
                    cpu_percent = psutil.cpu_percent(interval=1)
                    with self.lock:
                        self.cpu_samples.append({
                            'timestamp': time.time(),
                            'cpu_percent': cpu_percent
                        })
                    
                    # Memory monitoring
                    memory = psutil.virtual_memory()
                    with self.lock:
                        self.memory_snapshots.append({
                            'timestamp': time.time(),
                            'memory_percent': memory.percent,
                            'memory_used': memory.used,
                            'memory_available': memory.available
                        })
                    
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                
                time.sleep(5)  # Monitor every 5 seconds
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def profile_function(self, category: str = "general"):
        """Decorator for profiling function performance"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    result = None
                    success = False
                    error = str(e)
                    raise
                finally:
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss
                    execution_time = end_time - start_time
                    memory_delta = end_memory - start_memory
                    
                    # Record metrics
                    with self.lock:
                        self.metrics[category].append({
                            'function': func.__name__,
                            'execution_time': execution_time,
                            'memory_delta': memory_delta,
                            'success': success,
                            'error': error,
                            'timestamp': end_time
                        })
                        
                        # Track slow operations
                        if execution_time > 1.0:
                            self.slow_operations.append({
                                'function': func.__name__,
                                'category': category,
                                'execution_time': execution_time,
                                'timestamp': end_time
                            })
                
                return result
            return wrapper
        return decorator
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        with self.lock:
            summary = {
                'uptime': time.time() - self.start_time,
                'total_operations': sum(len(ops) for ops in self.metrics.values()),
                'categories': {},
                'system_metrics': self._get_current_system_metrics(),
                'slow_operations': list(self.slow_operations)[-10:],
                'recommendations': self._generate_recommendations()
            }
            
            # Category-specific metrics
            for category, operations in self.metrics.items():
                if operations:
                    times = [op['execution_time'] for op in operations]
                    memory_deltas = [op['memory_delta'] for op in operations]
                    success_rate = sum(1 for op in operations if op['success']) / len(operations)
                    
                    summary['categories'][category] = {
                        'total_operations': len(operations),
                        'avg_execution_time': sum(times) / len(times),
                        'min_execution_time': min(times),
                        'max_execution_time': max(times),
                        'avg_memory_delta': sum(memory_deltas) / len(memory_deltas),
                        'success_rate': success_rate,
                        'recent_operations': operations[-5:]
                    }
        
        return summary
    
    def _get_current_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / (1024**3),
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3),
                'python_memory_mb': psutil.Process().memory_info().rss / (1024**2)
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Check for slow operations
        if len(self.slow_operations) > 5:
            recommendations.append("Multiple slow operations detected - consider optimization")
        
        # Check memory usage
        try:
            memory = psutil.virtual_memory()
            if memory.percent > 80:
                recommendations.append("High memory usage detected - consider memory optimization")
        except:
            pass
        
        # Check CPU usage
        if self.cpu_samples:
            recent_cpu = [sample['cpu_percent'] for sample in list(self.cpu_samples)[-10:]]
            avg_cpu = sum(recent_cpu) / len(recent_cpu)
            if avg_cpu > 80:
                recommendations.append("High CPU usage detected - consider load balancing")
        
        # Check for memory leaks
        if len(self.memory_snapshots) > 10:
            recent_memory = [s['memory_used'] for s in list(self.memory_snapshots)[-10:]]
            if len(set(recent_memory)) == len(recent_memory) and recent_memory == sorted(recent_memory):
                recommendations.append("Potential memory leak detected - review memory management")
        
        return recommendations

class MemoryOptimizer:
    """Memory usage optimization and garbage collection management"""
    
    def __init__(self):
        self.object_counts = {}
        self.weak_refs = weakref.WeakSet()
        self.last_gc_time = time.time()
        self.gc_interval = 300  # 5 minutes
    
    @lru_cache(maxsize=1000)
    def cached_computation(self, key: str, computation_func):
        """LRU cached computation with automatic memory management"""
        return computation_func()
    
    def track_object(self, obj):
        """Track object for memory monitoring"""
        obj_type = type(obj).__name__
        self.object_counts[obj_type] = self.object_counts.get(obj_type, 0) + 1
        self.weak_refs.add(obj)
        return obj
    
    def optimize_memory(self) -> Dict[str, Any]:
        """Perform memory optimization operations"""
        start_memory = psutil.Process().memory_info().rss
        
        # Force garbage collection
        collected = gc.collect()
        
        # Clear function caches if memory usage is high
        memory = psutil.virtual_memory()
        if memory.percent > 70:
            self.cached_computation.cache_clear()
        
        # Update last GC time
        self.last_gc_time = time.time()
        
        end_memory = psutil.Process().memory_info().rss
        memory_freed = start_memory - end_memory
        
        return {
            'objects_collected': collected,
            'memory_freed_mb': memory_freed / (1024**2),
            'current_memory_mb': end_memory / (1024**2),
            'object_counts': self.object_counts.copy(),
            'cache_info': self.cached_computation.cache_info()._asdict()
        }
    
    def should_run_gc(self) -> bool:
        """Determine if garbage collection should be run"""
        return time.time() - self.last_gc_time > self.gc_interval

class RequestOptimizer:
    """HTTP request and response optimization"""
    
    def __init__(self):
        self.request_stats = defaultdict(list)
        self.response_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.lock = threading.Lock()
    
    def optimize_request(self, request_path: str, method: str):
        """Decorator for optimizing HTTP requests"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                # Check cache for GET requests
                if method == 'GET':
                    cache_key = f"{request_path}_{hash(str(args) + str(kwargs))}"
                    with self.lock:
                        if cache_key in self.response_cache:
                            cached_response, cache_time = self.response_cache[cache_key]
                            if time.time() - cache_time < 300:  # 5 minute cache
                                self.cache_hits += 1
                                return cached_response
                            else:
                                del self.response_cache[cache_key]
                        self.cache_misses += 1
                
                # Execute function
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Cache GET responses
                if method == 'GET' and execution_time < 5.0:  # Don't cache slow responses
                    with self.lock:
                        self.response_cache[cache_key] = (result, time.time())
                
                # Record stats
                with self.lock:
                    self.request_stats[request_path].append({
                        'method': method,
                        'execution_time': execution_time,
                        'timestamp': time.time()
                    })
                
                return result
            return wrapper
        return decorator
    
    def get_request_stats(self) -> Dict[str, Any]:
        """Get request performance statistics"""
        with self.lock:
            stats = {
                'cache_hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses) * 100 if (self.cache_hits + self.cache_misses) > 0 else 0,
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'cached_responses': len(self.response_cache),
                'endpoints': {}
            }
            
            for endpoint, requests in self.request_stats.items():
                if requests:
                    times = [req['execution_time'] for req in requests]
                    stats['endpoints'][endpoint] = {
                        'total_requests': len(requests),
                        'avg_response_time': sum(times) / len(times),
                        'min_response_time': min(times),
                        'max_response_time': max(times),
                        'recent_requests': requests[-5:]
                    }
        
        return stats

class DatabaseQueryOptimizer:
    """Database query performance optimization"""
    
    def __init__(self):
        self.query_stats = defaultdict(list)
        self.slow_queries = deque(maxlen=50)
        self.query_cache = {}
        self.lock = threading.Lock()
    
    def optimize_query(self, query_type: str = "select"):
        """Decorator for optimizing database queries"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                # Generate cache key for SELECT queries
                if query_type.lower() == 'select':
                    cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
                    with self.lock:
                        if cache_key in self.query_cache:
                            cached_result, cache_time = self.query_cache[cache_key]
                            if time.time() - cache_time < 600:  # 10 minute cache
                                return cached_result
                
                # Execute query
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Cache SELECT results
                if query_type.lower() == 'select' and execution_time < 2.0:
                    with self.lock:
                        self.query_cache[cache_key] = (result, time.time())
                
                # Record statistics
                with self.lock:
                    self.query_stats[func.__name__].append({
                        'query_type': query_type,
                        'execution_time': execution_time,
                        'timestamp': time.time()
                    })
                    
                    # Track slow queries
                    if execution_time > 0.5:
                        self.slow_queries.append({
                            'function': func.__name__,
                            'query_type': query_type,
                            'execution_time': execution_time,
                            'timestamp': time.time()
                        })
                
                return result
            return wrapper
        return decorator
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get database query performance statistics"""
        with self.lock:
            stats = {
                'total_queries': sum(len(queries) for queries in self.query_stats.values()),
                'cached_queries': len(self.query_cache),
                'slow_queries': list(self.slow_queries)[-10:],
                'query_functions': {}
            }
            
            for func_name, queries in self.query_stats.items():
                if queries:
                    times = [q['execution_time'] for q in queries]
                    stats['query_functions'][func_name] = {
                        'total_queries': len(queries),
                        'avg_execution_time': sum(times) / len(times),
                        'min_execution_time': min(times),
                        'max_execution_time': max(times),
                        'slow_query_count': sum(1 for t in times if t > 0.5)
                    }
        
        return stats

class PerformanceManager:
    """Centralized performance management system"""
    
    def __init__(self):
        self.profiler = PerformanceProfiler()
        self.memory_optimizer = MemoryOptimizer()
        self.request_optimizer = RequestOptimizer()
        self.query_optimizer = DatabaseQueryOptimizer()
        self.optimization_history = deque(maxlen=100)
    
    def run_optimization_cycle(self) -> Dict[str, Any]:
        """Run complete optimization cycle"""
        start_time = time.time()
        results = {}
        
        # Memory optimization
        if self.memory_optimizer.should_run_gc():
            results['memory_optimization'] = self.memory_optimizer.optimize_memory()
        
        # Get performance summary
        results['performance_summary'] = self.profiler.get_performance_summary()
        results['request_stats'] = self.request_optimizer.get_request_stats()
        results['query_stats'] = self.query_optimizer.get_query_stats()
        
        # Record optimization
        optimization_record = {
            'timestamp': time.time(),
            'duration': time.time() - start_time,
            'results': results
        }
        
        self.optimization_history.append(optimization_record)
        
        return results
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        return {
            'current_performance': self.run_optimization_cycle(),
            'optimization_history': list(self.optimization_history)[-10:],
            'recommendations': self._generate_system_recommendations(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_system_recommendations(self) -> List[str]:
        """Generate system-wide optimization recommendations"""
        recommendations = []
        
        # Analyze optimization history
        if len(self.optimization_history) > 5:
            recent_optimizations = list(self.optimization_history)[-5:]
            memory_trends = []
            
            for opt in recent_optimizations:
                if 'memory_optimization' in opt['results']:
                    memory_trends.append(opt['results']['memory_optimization']['current_memory_mb'])
            
            if memory_trends and len(set(memory_trends)) == len(memory_trends):
                if memory_trends == sorted(memory_trends):
                    recommendations.append("Memory usage consistently increasing - investigate memory leaks")
        
        # Check request performance
        request_stats = self.request_optimizer.get_request_stats()
        if request_stats['cache_hit_rate'] < 50:
            recommendations.append("Low cache hit rate - consider caching strategy optimization")
        
        # Check query performance
        query_stats = self.query_optimizer.get_query_stats()
        if query_stats['slow_queries']:
            recommendations.append("Slow database queries detected - consider query optimization")
        
        return recommendations

# Global performance manager
performance_manager = PerformanceManager()

def optimize_performance():
    """Run performance optimization"""
    return performance_manager.run_optimization_cycle()

def get_performance_report():
    """Get comprehensive performance report"""
    return performance_manager.get_optimization_report()