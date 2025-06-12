"""
Advanced API service for external integrations and data management
Provides standardized API interactions with rate limiting and error handling
"""
import logging
import requests
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from services.integration_service import integration_service
from services.cache_service import cache_service


class APIService:
    """Centralized API service for external integrations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CourtWebsite/2.1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Rate limiting configuration
        self.rate_limits = {}
        self.last_request_times = {}
    
    def make_request(self, method: str, url: str, service_name: str = 'external',
                    data: Dict = None, headers: Dict = None, timeout: int = 30,
                    use_cache: bool = True, cache_timeout: int = 300) -> Dict[str, Any]:
        """Make HTTP request with resilience patterns"""
        
        # Check rate limits
        if not self._check_rate_limit(service_name):
            raise Exception(f"Rate limit exceeded for service: {service_name}")
        
        # Generate cache key for GET requests
        cache_key = None
        if method.upper() == 'GET' and use_cache:
            cache_key = f"api:{service_name}:{url}"
            cached_response = cache_service.get(cache_key)
            if cached_response:
                return cached_response
        
        # Prepare request
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Execute request through integration service
        try:
            response = integration_service.call_service(
                service_name,
                self._execute_request,
                method, url, data, request_headers, timeout
            )
            
            # Cache successful GET responses
            if cache_key and response.get('success'):
                cache_service.set(cache_key, response, cache_timeout)
            
            return response
            
        except Exception as e:
            self.logger.error(f"API request failed: {method} {url} - {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'status_code': None,
                'data': None
            }
    
    def _execute_request(self, method: str, url: str, data: Dict,
                        headers: Dict, timeout: int) -> Dict[str, Any]:
        """Execute the actual HTTP request"""
        start_time = time.time()
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data if data else None,
                headers=headers,
                timeout=timeout
            )
            
            response_time = (time.time() - start_time) * 1000
            
            # Log request details
            self.logger.info(
                f"API {method} {url} - {response.status_code} - {response_time:.2f}ms"
            )
            
            # Parse response
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response_data,
                'response_time': response_time,
                'headers': dict(response.headers)
            }
            
        except requests.exceptions.Timeout:
            raise Exception(f"Request timeout after {timeout}s")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection error")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def _check_rate_limit(self, service_name: str) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        
        # Default rate limit: 100 requests per minute
        rate_limit = self.rate_limits.get(service_name, {
            'requests': 100,
            'window': 60
        })
        
        # Initialize tracking for new service
        if service_name not in self.last_request_times:
            self.last_request_times[service_name] = []
        
        # Clean old requests outside window
        window_start = current_time - rate_limit['window']
        self.last_request_times[service_name] = [
            req_time for req_time in self.last_request_times[service_name]
            if req_time > window_start
        ]
        
        # Check if under limit
        if len(self.last_request_times[service_name]) >= rate_limit['requests']:
            return False
        
        # Record current request
        self.last_request_times[service_name].append(current_time)
        return True
    
    def set_rate_limit(self, service_name: str, requests_per_minute: int):
        """Set rate limit for a specific service"""
        self.rate_limits[service_name] = {
            'requests': requests_per_minute,
            'window': 60
        }
    
    def get_api_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        current_time = time.time()
        stats = {}
        
        for service_name, request_times in self.last_request_times.items():
            # Count recent requests
            recent_requests = [
                req_time for req_time in request_times
                if req_time > current_time - 300  # Last 5 minutes
            ]
            
            stats[service_name] = {
                'recent_requests': len(recent_requests),
                'total_requests': len(request_times),
                'rate_limit': self.rate_limits.get(service_name, {'requests': 100})['requests']
            }
        
        return stats


class TJESIntegration:
    """Integration with TJ-ES (Tribunal de Justiça do Espírito Santo) systems"""
    
    def __init__(self, api_service: APIService):
        self.api_service = api_service
        self.base_url = "https://sistemas.tjes.jus.br/api"
        self.logger = logging.getLogger(__name__)
    
    def search_process(self, process_number: str) -> Dict[str, Any]:
        """Search for process information"""
        if not self._validate_process_number(process_number):
            return {
                'success': False,
                'error': 'Invalid process number format'
            }
        
        endpoint = f"{self.base_url}/processos/{process_number}"
        
        return self.api_service.make_request(
            method='GET',
            url=endpoint,
            service_name='tjes',
            use_cache=True,
            cache_timeout=1800  # 30 minutes
        )
    
    def get_hearing_schedule(self, date: str) -> Dict[str, Any]:
        """Get hearing schedule for specific date"""
        endpoint = f"{self.base_url}/audiencias"
        params = {'data': date, 'vara': '2_civel_cariacica'}
        
        return self.api_service.make_request(
            method='GET',
            url=f"{endpoint}?{'&'.join([f'{k}={v}' for k, v in params.items()])}",
            service_name='tjes',
            use_cache=True,
            cache_timeout=300  # 5 minutes
        )
    
    def _validate_process_number(self, process_number: str) -> bool:
        """Validate CNJ process number format"""
        import re
        # CNJ format: NNNNNNN-DD.AAAA.J.TR.OOOO
        pattern = r'^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$'
        return bool(re.match(pattern, process_number.replace(' ', '')))


class OpenAIService:
    """Enhanced OpenAI integration service"""
    
    def __init__(self, api_service: APIService):
        self.api_service = api_service
        self.logger = logging.getLogger(__name__)
    
    def generate_response(self, prompt: str, context: str = None) -> Dict[str, Any]:
        """Generate AI response with context"""
        try:
            from openai import OpenAI
            import os
            
            client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
            
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            return {
                'success': True,
                'response': response.choices[0].message.content,
                'usage': dict(response.usage)
            }
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Global API service instance
api_service = APIService()

# Initialize external service integrations
tjes_integration = TJESIntegration(api_service)
openai_service = OpenAIService(api_service)

# Configure rate limits
api_service.set_rate_limit('tjes', 30)  # 30 requests per minute for TJES
api_service.set_rate_limit('openai', 60)  # 60 requests per minute for OpenAI