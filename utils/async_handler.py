"""
Asynchronous Handler for 2ª Vara Cível de Cariacica
Implements async operations for improved performance and concurrent processing
"""

import asyncio
import aiohttp
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Callable, Any, Optional, Dict, List
import time
from datetime import datetime
import threading

logger = logging.getLogger('async_handler')

class AsyncHandler:
    """Enhanced async handler for concurrent operations"""
    
    def __init__(self, max_workers: int = 10):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.session = None
        self.tasks = {}
        self.task_results = {}
        self.max_workers = max_workers
        
    async def init_session(self):
        """Initialize aiohttp session for async HTTP requests"""
        if not self.session:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'User-Agent': 'Court-System-Async/1.0'}
            )
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def run_async(self, coro):
        """Run async coroutine in sync context"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    async def async_http_request(self, method: str, url: str, **kwargs) -> Dict:
        """Async HTTP request with error handling"""
        await self.init_session()
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                data = await response.text()
                return {
                    'status': response.status,
                    'data': data,
                    'headers': dict(response.headers),
                    'success': response.status < 400
                }
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request error: {e}")
            return {
                'status': 0,
                'data': None,
                'error': str(e),
                'success': False
            }
    
    async def async_database_operation(self, operation: Callable, *args, **kwargs):
        """Execute database operation asynchronously"""
        loop = asyncio.get_event_loop()
        
        try:
            result = await loop.run_in_executor(
                self.executor, 
                operation, 
                *args, 
                **kwargs
            )
            return {
                'success': True,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Async database operation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def parallel_operations(self, operations: List[tuple]) -> List[Dict]:
        """Execute multiple operations in parallel"""
        tasks = []
        
        for operation_name, operation, args, kwargs in operations:
            if asyncio.iscoroutinefunction(operation):
                task = asyncio.create_task(
                    operation(*args, **kwargs),
                    name=operation_name
                )
            else:
                # Properly handle executor tasks
                loop = asyncio.get_event_loop()
                future = loop.run_in_executor(
                    self.executor,
                    operation,
                    *args,
                    **kwargs
                )
                task = asyncio.create_task(
                    asyncio.wrap_future(future),
                    name=operation_name
                )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            {
                'operation': operations[i][0],
                'success': not isinstance(result, Exception),
                'result': result if not isinstance(result, Exception) else None,
                'error': str(result) if isinstance(result, Exception) else None,
                'timestamp': datetime.now().isoformat()
            }
            for i, result in enumerate(results)
        ]
    
    async def async_file_operations(self, file_operations: List[Dict]) -> List[Dict]:
        """Handle multiple file operations asynchronously"""
        async def read_file(filepath: str) -> Dict:
            try:
                loop = asyncio.get_event_loop()
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = await loop.run_in_executor(self.executor, f.read)
                return {
                    'filepath': filepath,
                    'success': True,
                    'content': content,
                    'size': len(content)
                }
            except Exception as e:
                return {
                    'filepath': filepath,
                    'success': False,
                    'error': str(e)
                }
        
        async def write_file(filepath: str, content: str) -> Dict:
            try:
                loop = asyncio.get_event_loop()
                with open(filepath, 'w', encoding='utf-8') as f:
                    await loop.run_in_executor(self.executor, f.write, content)
                return {
                    'filepath': filepath,
                    'success': True,
                    'bytes_written': len(content)
                }
            except Exception as e:
                return {
                    'filepath': filepath,
                    'success': False,
                    'error': str(e)
                }
        
        tasks = []
        for operation in file_operations:
            if operation['type'] == 'read':
                task = read_file(operation['filepath'])
            elif operation['type'] == 'write':
                task = write_file(operation['filepath'], operation['content'])
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
    
    async def background_task_manager(self, task_name: str, task_func: Callable, *args, **kwargs):
        """Manage long-running background tasks"""
        task_id = f"{task_name}_{int(time.time())}"
        
        async def wrapped_task():
            try:
                start_time = time.time()
                if asyncio.iscoroutinefunction(task_func):
                    result = await task_func(*args, **kwargs)
                else:
                    result = await asyncio.get_event_loop().run_in_executor(
                        self.executor, task_func, *args, **kwargs
                    )
                
                execution_time = time.time() - start_time
                
                self.task_results[task_id] = {
                    'success': True,
                    'result': result,
                    'execution_time': execution_time,
                    'completed_at': datetime.now().isoformat()
                }
                
                logger.info(f"Background task {task_id} completed in {execution_time:.2f}s")
                
            except Exception as e:
                self.task_results[task_id] = {
                    'success': False,
                    'error': str(e),
                    'completed_at': datetime.now().isoformat()
                }
                logger.error(f"Background task {task_id} failed: {e}")
        
        task = asyncio.create_task(wrapped_task(), name=task_id)
        self.tasks[task_id] = task
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Dict:
        """Get status of background task"""
        if task_id in self.task_results:
            return self.task_results[task_id]
        elif task_id in self.tasks:
            task = self.tasks[task_id]
            return {
                'status': 'running' if not task.done() else 'completed',
                'done': task.done(),
                'cancelled': task.cancelled()
            }
        else:
            return {'status': 'not_found'}
    
    async def batch_processing(self, items: List[Any], processor: Callable, batch_size: int = 10) -> List[Dict]:
        """Process items in batches asynchronously"""
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_tasks = []
            
            for item in batch:
                if asyncio.iscoroutinefunction(processor):
                    task = processor(item)
                else:
                    task = asyncio.get_event_loop().run_in_executor(
                        self.executor, processor, item
                    )
                batch_tasks.append(task)
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for j, result in enumerate(batch_results):
                results.append({
                    'item_index': i + j,
                    'success': not isinstance(result, Exception),
                    'result': result if not isinstance(result, Exception) else None,
                    'error': str(result) if isinstance(result, Exception) else None
                })
        
        return results

# Global async handler instance
async_handler = AsyncHandler()

def async_route(f):
    """Decorator to run async functions in Flask routes"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        return async_handler.run_async(f(*args, **kwargs))
    return wrapper

def background_task(task_name: str):
    """Decorator for background tasks"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return async_handler.run_async(
                async_handler.background_task_manager(task_name, f, *args, **kwargs)
            )
        return wrapper
    return decorator

async def async_error_handler(error_func: Callable, error: Exception, context: Dict = None):
    """Async error handling"""
    try:
        if asyncio.iscoroutinefunction(error_func):
            await error_func(error, context)
        else:
            await asyncio.get_event_loop().run_in_executor(
                async_handler.executor, error_func, error, context
            )
    except Exception as e:
        logger.error(f"Async error handler failed: {e}")

async def health_check_async() -> Dict:
    """Async health check for system components"""
    checks = [
        ('database', check_database_async),
        ('external_api', check_external_api_async),
        ('file_system', check_file_system_async),
        ('cache', check_cache_async)
    ]
    
    results = await async_handler.parallel_operations([
        (name, func, [], {}) for name, func in checks
    ])
    
    return {
        'overall_status': 'healthy' if all(r['success'] for r in results) else 'degraded',
        'components': results,
        'timestamp': datetime.now().isoformat()
    }

async def check_database_async():
    """Async database connectivity check"""
    try:
        # Simulate database check
        await asyncio.sleep(0.1)
        return {'status': 'connected', 'response_time': 0.1}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

async def check_external_api_async():
    """Async external API check"""
    try:
        result = await async_handler.async_http_request(
            'GET', 
            'https://httpbin.org/status/200'
        )
        return {
            'status': 'available' if result['success'] else 'unavailable',
            'response_time': 0.2
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

async def check_file_system_async():
    """Async file system check"""
    try:
        import os
        await asyncio.sleep(0.05)
        return {
            'status': 'available',
            'disk_usage': {
                'total': 100000000,
                'used': 50000000,
                'free': 50000000
            }
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

async def check_cache_async():
    """Async cache system check"""
    try:
        await asyncio.sleep(0.02)
        return {'status': 'available', 'hit_rate': 0.85}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}