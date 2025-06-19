"""
Robust OpenAI Service with Advanced Error Handling and Rate Limiting
Provides intelligent retry mechanisms, token management, and fallback responses
"""
import logging
import time
import asyncio
import threading
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from functools import wraps
import json
import os
import openai
from openai import OpenAI


@dataclass
class OpenAIConfig:
    """Advanced OpenAI service configuration"""
    api_key: str
    model: str = "gpt-4o"
    max_tokens: int = 500
    temperature: float = 0.7
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    rate_limit_requests_per_minute: int = 60
    rate_limit_tokens_per_minute: int = 40000
    fallback_enabled: bool = True
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes


class TokenManager:
    """Manage OpenAI token usage and rate limiting"""
    
    def __init__(self, config: OpenAIConfig):
        self.config = config
        self.request_history = []
        self.token_usage_history = []
        self._lock = threading.Lock()
        self.total_tokens_used = 0
        self.total_requests_made = 0
        
    def can_make_request(self, estimated_tokens: int = 0) -> tuple[bool, str]:
        """Check if request can be made within rate limits"""
        with self._lock:
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)
            
            # Clean old records
            self.request_history = [ts for ts in self.request_history if ts > minute_ago]
            self.token_usage_history = [
                (ts, tokens) for ts, tokens in self.token_usage_history 
                if ts > minute_ago
            ]
            
            # Check request rate limit
            if len(self.request_history) >= self.config.rate_limit_requests_per_minute:
                return False, f"Rate limit exceeded: {len(self.request_history)} requests in last minute"
            
            # Check token rate limit
            tokens_in_last_minute = sum(tokens for _, tokens in self.token_usage_history)
            if tokens_in_last_minute + estimated_tokens > self.config.rate_limit_tokens_per_minute:
                return False, f"Token rate limit exceeded: {tokens_in_last_minute + estimated_tokens} tokens"
            
            return True, "OK"
    
    def record_request(self, tokens_used: int):
        """Record a successful request"""
        with self._lock:
            now = datetime.now()
            self.request_history.append(now)
            self.token_usage_history.append((now, tokens_used))
            self.total_tokens_used += tokens_used
            self.total_requests_made += 1
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get token usage statistics"""
        with self._lock:
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)
            hour_ago = now - timedelta(hours=1)
            day_ago = now - timedelta(days=1)
            
            # Calculate usage for different time periods
            requests_last_minute = len([ts for ts in self.request_history if ts > minute_ago])
            requests_last_hour = len([ts for ts in self.request_history if ts > hour_ago])
            
            tokens_last_minute = sum(
                tokens for ts, tokens in self.token_usage_history if ts > minute_ago
            )
            tokens_last_hour = sum(
                tokens for ts, tokens in self.token_usage_history if ts > hour_ago
            )
            
            return {
                'total_requests': self.total_requests_made,
                'total_tokens': self.total_tokens_used,
                'requests_last_minute': requests_last_minute,
                'requests_last_hour': requests_last_hour,
                'tokens_last_minute': tokens_last_minute,
                'tokens_last_hour': tokens_last_hour,
                'rate_limit_utilization': {
                    'requests': (requests_last_minute / self.config.rate_limit_requests_per_minute) * 100,
                    'tokens': (tokens_last_minute / self.config.rate_limit_tokens_per_minute) * 100
                }
            }


class ResponseCache:
    """Cache OpenAI responses to reduce API calls"""
    
    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl
        self._lock = threading.Lock()
    
    def _generate_key(self, prompt: str, model: str, temperature: float, max_tokens: int) -> str:
        """Generate cache key from request parameters"""
        import hashlib
        key_data = f"{prompt}_{model}_{temperature}_{max_tokens}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, prompt: str, model: str, temperature: float, max_tokens: int) -> Optional[str]:
        """Get cached response if available and not expired"""
        with self._lock:
            key = self._generate_key(prompt, model, temperature, max_tokens)
            
            if key in self.cache:
                cached_data, timestamp = self.cache[key]
                if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                    return cached_data
                else:
                    del self.cache[key]
            
            return None
    
    def set(self, prompt: str, model: str, temperature: float, max_tokens: int, response: str):
        """Cache response"""
        with self._lock:
            key = self._generate_key(prompt, model, temperature, max_tokens)
            self.cache[key] = (response, datetime.now())
            
            # Clean expired entries occasionally
            if len(self.cache) % 10 == 0:
                self._clean_expired()
    
    def _clean_expired(self):
        """Remove expired cache entries"""
        now = datetime.now()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if now - timestamp >= timedelta(seconds=self.ttl)
        ]
        for key in expired_keys:
            del self.cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            return {
                'cache_size': len(self.cache),
                'cache_ttl': self.ttl
            }


class FallbackResponseGenerator:
    """Generate fallback responses when OpenAI is unavailable"""
    
    def __init__(self):
        self.fallback_responses = {
            'greeting': [
                "Olá! Como posso ajudá-lo hoje?",
                "Bem-vindo! Em que posso auxiliá-lo?",
                "Oi! Estou aqui para ajudá-lo."
            ],
            'process_info': [
                "Para informações sobre processos, recomendo consultar o sistema TJES ou entrar em contato com o cartório.",
                "Você pode verificar o andamento do seu processo através do portal oficial do TJES.",
                "Para consultas processuais, utilize nosso sistema de consulta ou contate o cartório."
            ],
            'scheduling': [
                "Para agendamentos, utilize nosso formulário online ou entre em contato durante o horário de atendimento.",
                "Você pode agendar atendimento através do nosso sistema de agendamento disponível no site.",
                "Para marcar uma reunião, acesse a seção de agendamento no menu de serviços."
            ],
            'contact': [
                "Nossa equipe está disponível durante o horário comercial. Você pode entrar em contato por telefone ou email.",
                "Para mais informações, consulte nossa página de contato ou visite presencialmente nossa sede.",
                "Estamos localizados na Rua Expedito Garcia, s/n - Centro, Cariacica - ES."
            ],
            'default': [
                "Desculpe, estou com dificuldades técnicas no momento. Tente novamente em alguns instantes ou entre em contato diretamente conosco.",
                "No momento estou indisponível. Por favor, utilize nossos outros canais de atendimento ou tente novamente mais tarde.",
                "Sistema temporariamente indisponível. Recomendo consultar nossa página de serviços ou entrar em contato presencialmente."
            ]
        }
    
    def generate_response(self, prompt: str) -> str:
        """Generate contextual fallback response"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['olá', 'oi', 'bom dia', 'boa tarde']):
            category = 'greeting'
        elif any(word in prompt_lower for word in ['processo', 'andamento', 'consulta']):
            category = 'process_info'
        elif any(word in prompt_lower for word in ['agendar', 'agendamento', 'reunião', 'horário']):
            category = 'scheduling'
        elif any(word in prompt_lower for word in ['contato', 'telefone', 'endereço', 'email']):
            category = 'contact'
        else:
            category = 'default'
        
        import random
        return random.choice(self.fallback_responses[category])


class RobustOpenAIService:
    """Enhanced OpenAI service with comprehensive reliability features"""
    
    def __init__(self, config: OpenAIConfig):
        self.config = config
        self.client = None
        self.token_manager = TokenManager(config)
        self.cache = ResponseCache(config.cache_ttl) if config.cache_enabled else None
        self.fallback_generator = FallbackResponseGenerator() if config.fallback_enabled else None
        self.logger = logging.getLogger(__name__)
        self._initialized = False
        self._health_status = 'unknown'
        self._performance_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'fallback_responses': 0,
            'average_response_time': 0.0
        }
        self._lock = threading.Lock()
    
    def initialize(self):
        """Initialize robust OpenAI service"""
        if self._initialized:
            return
        
        try:
            if not self.config.api_key:
                raise ValueError("OpenAI API key not provided")
            
            self.client = OpenAI(
                api_key=self.config.api_key,
                timeout=self.config.timeout
            )
            
            # Test connection
            self._test_connection()
            
            self._health_status = 'healthy'
            self._initialized = True
            self.logger.info("Robust OpenAI service initialized successfully")
            
        except Exception as e:
            self._health_status = 'failed'
            self.logger.error(f"Failed to initialize OpenAI service: {str(e)}")
            raise
    
    def _test_connection(self):
        """Test OpenAI API connection"""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10,
                timeout=10
            )
            self.logger.info("OpenAI API connection test successful")
        except Exception as e:
            raise Exception(f"OpenAI API connection test failed: {str(e)}")
    
    def generate_response(self, prompt: str, context: str = None, **kwargs) -> Dict[str, Any]:
        """Generate response with comprehensive error handling and optimization"""
        start_time = time.time()
        
        with self._lock:
            self._performance_metrics['total_requests'] += 1
        
        try:
            # Prepare messages
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})
            
            # Override config with kwargs
            model = kwargs.get('model', self.config.model)
            max_tokens = kwargs.get('max_tokens', self.config.max_tokens)
            temperature = kwargs.get('temperature', self.config.temperature)
            
            # Check cache first
            if self.cache:
                cached_response = self.cache.get(prompt, model, temperature, max_tokens)
                if cached_response:
                    with self._lock:
                        self._performance_metrics['cache_hits'] += 1
                        self._performance_metrics['successful_requests'] += 1
                    
                    return {
                        'response': cached_response,
                        'source': 'cache',
                        'tokens_used': 0,
                        'response_time': time.time() - start_time,
                        'model': model
                    }
            
            # Check rate limits
            estimated_tokens = len(prompt.split()) * 1.3  # Rough estimation
            can_proceed, limit_message = self.token_manager.can_make_request(int(estimated_tokens))
            
            if not can_proceed:
                self.logger.warning(f"Rate limit check failed: {limit_message}")
                if self.fallback_generator:
                    fallback_response = self.fallback_generator.generate_response(prompt)
                    with self._lock:
                        self._performance_metrics['fallback_responses'] += 1
                    
                    return {
                        'response': fallback_response,
                        'source': 'fallback_rate_limit',
                        'tokens_used': 0,
                        'response_time': time.time() - start_time,
                        'warning': limit_message
                    }
                else:
                    raise Exception(limit_message)
            
            # Make API call with retry logic
            response_data = self._make_api_call_with_retry(messages, model, max_tokens, temperature)
            
            # Extract response text
            response_text = response_data.choices[0].message.content.strip()
            tokens_used = response_data.usage.total_tokens
            
            # Record usage
            self.token_manager.record_request(tokens_used)
            
            # Cache response
            if self.cache:
                self.cache.set(prompt, model, temperature, max_tokens, response_text)
            
            # Update metrics
            response_time = time.time() - start_time
            with self._lock:
                self._performance_metrics['successful_requests'] += 1
                self._update_response_time(response_time)
            
            return {
                'response': response_text,
                'source': 'openai_api',
                'tokens_used': tokens_used,
                'response_time': response_time,
                'model': model
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            
            with self._lock:
                self._performance_metrics['failed_requests'] += 1
                self._update_response_time(response_time)
            
            self.logger.error(f"OpenAI API call failed: {str(e)}")
            
            # Use fallback if available
            if self.fallback_generator:
                fallback_response = self.fallback_generator.generate_response(prompt)
                with self._lock:
                    self._performance_metrics['fallback_responses'] += 1
                
                return {
                    'response': fallback_response,
                    'source': 'fallback_error',
                    'tokens_used': 0,
                    'response_time': response_time,
                    'error': str(e)
                }
            else:
                raise
    
    def _make_api_call_with_retry(self, messages: List[Dict], model: str, max_tokens: int, temperature: float):
        """Make API call with exponential backoff retry logic"""
        last_error = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout=self.config.timeout
                )
                return response
                
            except openai.RateLimitError as e:
                last_error = e
                if attempt < self.config.max_retries:
                    delay = self._calculate_retry_delay(attempt, base_delay=60)  # Longer delay for rate limits
                    self.logger.warning(f"Rate limit hit, retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise
                    
            except (openai.APITimeoutError, openai.APIConnectionError) as e:
                last_error = e
                if attempt < self.config.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    self.logger.warning(f"API timeout/connection error, retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise
                    
            except Exception as e:
                last_error = e
                self.logger.error(f"Unexpected OpenAI error: {str(e)}")
                raise
        
        if last_error:
            raise last_error
    
    def _calculate_retry_delay(self, attempt: int, base_delay: float = None) -> float:
        """Calculate retry delay with exponential backoff"""
        if base_delay is None:
            base_delay = self.config.retry_delay
            
        if self.config.exponential_backoff:
            return min(base_delay * (2 ** attempt), 300)  # Max 5 minutes
        return base_delay
    
    def _update_response_time(self, response_time: float):
        """Update average response time using exponential moving average"""
        if self._performance_metrics['average_response_time'] == 0:
            self._performance_metrics['average_response_time'] = response_time
        else:
            self._performance_metrics['average_response_time'] = (
                self._performance_metrics['average_response_time'] * 0.9 + response_time * 0.1
            )
    
    def check_health(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health_data = {
            'status': 'unknown',
            'timestamp': datetime.now().isoformat(),
            'api_connectivity': {},
            'performance': {},
            'rate_limits': {},
            'errors': []
        }
        
        try:
            # Test API connectivity
            start_time = time.time()
            test_response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "Health check"}],
                max_tokens=10,
                timeout=10
            )
            api_response_time = time.time() - start_time
            
            # Get usage statistics
            usage_stats = self.token_manager.get_usage_stats()
            cache_stats = self.cache.get_stats() if self.cache else {}
            
            health_data.update({
                'status': 'healthy',
                'api_connectivity': {
                    'response_time_ms': round(api_response_time * 1000, 2),
                    'model': self.config.model,
                    'api_key_configured': bool(self.config.api_key)
                },
                'performance': {
                    **self._performance_metrics,
                    'average_response_time_ms': round(self._performance_metrics['average_response_time'] * 1000, 2),
                    'success_rate': round(
                        (self._performance_metrics['successful_requests'] / 
                         max(1, self._performance_metrics['total_requests'])) * 100, 2
                    )
                },
                'rate_limits': usage_stats,
                'cache': cache_stats
            })
            
            # Add warnings for performance issues
            if usage_stats['rate_limit_utilization']['requests'] > 80:
                health_data['errors'].append("High request rate limit utilization")
            
            if usage_stats['rate_limit_utilization']['tokens'] > 80:
                health_data['errors'].append("High token rate limit utilization")
            
            if self._performance_metrics['average_response_time'] > 10:
                health_data['errors'].append("High average response time")
            
            self._health_status = 'healthy'
            
        except Exception as e:
            health_data.update({
                'status': 'unhealthy',
                'error': str(e),
                'errors': [f"Health check failed: {str(e)}"]
            })
            self._health_status = 'unhealthy'
            self.logger.error(f"OpenAI health check failed: {str(e)}")
        
        return health_data
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        usage_stats = self.token_manager.get_usage_stats()
        cache_stats = self.cache.get_stats() if self.cache else {}
        
        return {
            'openai_metrics': self._performance_metrics.copy(),
            'token_usage': usage_stats,
            'cache_performance': cache_stats,
            'configuration': {
                'model': self.config.model,
                'max_tokens': self.config.max_tokens,
                'temperature': self.config.temperature,
                'timeout': self.config.timeout,
                'max_retries': self.config.max_retries,
                'rate_limits': {
                    'requests_per_minute': self.config.rate_limit_requests_per_minute,
                    'tokens_per_minute': self.config.rate_limit_tokens_per_minute
                }
            },
            'recommendations': self._get_performance_recommendations()
        }
    
    def _get_performance_recommendations(self) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        success_rate = (self._performance_metrics['successful_requests'] / 
                       max(1, self._performance_metrics['total_requests'])) * 100
        
        if success_rate < 95:
            recommendations.append("Low success rate - consider reviewing error handling")
        
        if self._performance_metrics['average_response_time'] > 5:
            recommendations.append("High response times - consider reducing max_tokens or optimizing prompts")
        
        usage_stats = self.token_manager.get_usage_stats()
        if usage_stats['rate_limit_utilization']['tokens'] > 80:
            recommendations.append("High token usage - consider implementing more aggressive caching")
        
        if self._performance_metrics['fallback_responses'] > self._performance_metrics['successful_requests'] * 0.1:
            recommendations.append("High fallback usage - check API connectivity and rate limits")
        
        return recommendations


# OpenAI decorator for easy integration
def with_robust_openai(context: str = None, **openai_kwargs):
    """Decorator to add robust OpenAI integration to functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract prompt from function arguments or return value
            result = func(*args, **kwargs)
            if isinstance(result, str):
                return robust_openai_service.generate_response(result, context, **openai_kwargs)
            return result
        return wrapper
    return decorator


# Global robust OpenAI service instance
robust_openai_service = None


def initialize_robust_openai(api_key: str = None):
    """Initialize robust OpenAI service"""
    global robust_openai_service
    
    if not api_key:
        api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        raise ValueError("OpenAI API key not provided")
    
    config = OpenAIConfig(api_key=api_key)
    robust_openai_service = RobustOpenAIService(config)
    robust_openai_service.initialize()
    
    logging.info("Robust OpenAI service initialized successfully")


def get_openai_health() -> Dict[str, Any]:
    """Get comprehensive OpenAI service health status"""
    if not robust_openai_service:
        return {'status': 'not_initialized', 'error': 'Service not initialized'}
    
    return robust_openai_service.check_health()


def get_openai_performance_report() -> Dict[str, Any]:
    """Get detailed OpenAI performance report"""
    if not robust_openai_service:
        return {'error': 'Service not initialized'}
    
    return robust_openai_service.get_performance_metrics()