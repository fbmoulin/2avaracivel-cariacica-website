"""
Robust Integration Service for 2ª Vara Cível de Cariacica
Manages all external integrations with comprehensive error handling and security
"""

import logging
import time
import asyncio
import threading
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
import requests
import json
import hashlib
from urllib.parse import urlparse
import ssl
import certifi
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from circuitbreaker import circuit

logger = logging.getLogger(__name__)

class IntegrationError(Exception):
    """Base exception for integration errors"""
    pass

class SecurityViolationError(IntegrationError):
    """Exception for security violations in integrations"""
    pass

class RateLimitError(IntegrationError):
    """Exception for rate limit violations"""
    pass

class RobustIntegrationService:
    """
    Manages all external integrations with comprehensive error handling,
    security measures, and monitoring
    """
    
    def __init__(self):
        self.integrations = {}
        self.rate_limits = {}
        self.circuit_breakers = {}
        self.security_settings = {
            'allowed_domains': {
                'api.openai.com',
                'cdn.jsdelivr.net',
                'cdnjs.cloudflare.com',
                'fonts.googleapis.com',
                'fonts.gstatic.com'
            },
            'blocked_domains': {
                'localhost',
                '127.0.0.1',
                '0.0.0.0'
            },
            'max_request_size': 10 * 1024 * 1024,  # 10MB
            'timeout': 30,
            'verify_ssl': True
        }
        
        # Monitoring
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rate_limited_requests': 0,
            'security_violations': 0,
            'circuit_breaker_trips': 0
        }
        
        self._lock = threading.Lock()
        self.session = self._create_secure_session()

    def _create_secure_session(self) -> requests.Session:
        """Create a secure HTTP session with proper configuration"""
        session = requests.Session()
        
        # Configure SSL/TLS
        session.verify = certifi.where() if self.security_settings['verify_ssl'] else False
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': '2VaraCivelCariacica/1.0 (Security-Enhanced)',
            'Accept': 'application/json',
            'Connection': 'keep-alive'
        })
        
        return session

    def register_integration(self, name: str, config: Dict[str, Any]):
        """
        Register a new integration with configuration
        
        Args:
            name: Integration name
            config: Integration configuration including endpoints, auth, etc.
        """
        try:
            # Validate configuration
            self._validate_integration_config(name, config)
            
            # Initialize rate limiting
            if 'rate_limit' in config:
                self.rate_limits[name] = {
                    'requests': [],
                    'limit': config['rate_limit'].get('requests', 100),
                    'window': config['rate_limit'].get('window', 3600)
                }
            
            # Initialize circuit breaker
            if config.get('circuit_breaker', True):
                self.circuit_breakers[name] = {
                    'failure_count': 0,
                    'last_failure': None,
                    'state': 'closed',  # closed, open, half-open
                    'failure_threshold': config.get('failure_threshold', 5),
                    'recovery_timeout': config.get('recovery_timeout', 60)
                }
            
            self.integrations[name] = config
            logger.info(f"Integration '{name}' registered successfully")
            
        except Exception as e:
            logger.error(f"Failed to register integration '{name}': {e}")
            raise IntegrationError(f"Integration registration failed: {e}")

    def _validate_integration_config(self, name: str, config: Dict[str, Any]):
        """Validate integration configuration for security and completeness"""
        required_fields = ['base_url']
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field '{field}' in integration config")
        
        # Validate URL security
        base_url = config['base_url']
        parsed_url = urlparse(base_url)
        
        if not parsed_url.scheme in ['https', 'http']:
            raise SecurityViolationError(f"Invalid URL scheme: {parsed_url.scheme}")
        
        if parsed_url.netloc in self.security_settings['blocked_domains']:
            raise SecurityViolationError(f"Blocked domain: {parsed_url.netloc}")
        
        # Enforce HTTPS for external APIs (except localhost for development)
        if (parsed_url.netloc not in ['localhost', '127.0.0.1'] and 
            parsed_url.scheme != 'https'):
            raise SecurityViolationError("External integrations must use HTTPS")

    @circuit(failure_threshold=5, recovery_timeout=60, expected_exception=IntegrationError)
    def make_request(self, integration_name: str, method: str, endpoint: str, 
                    data: Optional[Dict] = None, headers: Optional[Dict] = None,
                    params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """
        Make a secure HTTP request to an integration
        
        Args:
            integration_name: Name of the registered integration
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data
            headers: Additional headers
            params: Query parameters
            **kwargs: Additional request arguments
            
        Returns:
            Response data as dictionary
        """
        try:
            with self._lock:
                self.metrics['total_requests'] += 1
            
            # Validate integration exists
            if integration_name not in self.integrations:
                raise IntegrationError(f"Integration '{integration_name}' not registered")
            
            config = self.integrations[integration_name]
            
            # Check circuit breaker
            if not self._check_circuit_breaker(integration_name):
                raise IntegrationError(f"Circuit breaker open for '{integration_name}'")
            
            # Check rate limiting
            if not self._check_rate_limit(integration_name):
                with self._lock:
                    self.metrics['rate_limited_requests'] += 1
                raise RateLimitError(f"Rate limit exceeded for '{integration_name}'")
            
            # Build request
            url = f"{config['base_url'].rstrip('/')}/{endpoint.lstrip('/')}"
            request_headers = self._build_headers(config, headers)
            
            # Security validation
            self._validate_request_security(url, data, request_headers)
            
            # Execute request
            start_time = time.time()
            
            response = self.session.request(
                method=method.upper(),
                url=url,
                json=data if data and method.upper() in ['POST', 'PUT', 'PATCH'] else None,
                params=params,
                headers=request_headers,
                timeout=self.security_settings['timeout'],
                **kwargs
            )
            
            execution_time = time.time() - start_time
            
            # Handle response
            self._handle_response(integration_name, response, execution_time)
            
            # Parse response
            try:
                response_data = response.json() if response.content else {}
            except json.JSONDecodeError:
                response_data = {'raw_content': response.text}
            
            with self._lock:
                self.metrics['successful_requests'] += 1
            
            return {
                'status_code': response.status_code,
                'data': response_data,
                'headers': dict(response.headers),
                'execution_time': execution_time
            }
            
        except requests.RequestException as e:
            self._handle_request_error(integration_name, e)
            raise IntegrationError(f"Request failed: {e}")
        except Exception as e:
            self._handle_request_error(integration_name, e)
            raise

    def _build_headers(self, config: Dict[str, Any], additional_headers: Optional[Dict] = None) -> Dict[str, str]:
        """Build request headers with authentication and security headers"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Add authentication
        auth_config = config.get('authentication', {})
        if auth_config.get('type') == 'bearer':
            token = auth_config.get('token')
            if token:
                headers['Authorization'] = f"Bearer {token}"
        elif auth_config.get('type') == 'api_key':
            key_header = auth_config.get('header', 'X-API-Key')
            api_key = auth_config.get('key')
            if api_key:
                headers[key_header] = api_key
        
        # Add additional headers
        if additional_headers:
            headers.update(additional_headers)
        
        return headers

    def _validate_request_security(self, url: str, data: Optional[Dict], headers: Dict[str, str]):
        """Validate request for security issues"""
        parsed_url = urlparse(url)
        
        # Check domain allowlist for external requests
        if (parsed_url.netloc not in ['localhost', '127.0.0.1'] and
            parsed_url.netloc not in self.security_settings['allowed_domains']):
            with self._lock:
                self.metrics['security_violations'] += 1
            raise SecurityViolationError(f"Domain not in allowlist: {parsed_url.netloc}")
        
        # Check request size
        if data:
            data_size = len(json.dumps(data).encode('utf-8'))
            if data_size > self.security_settings['max_request_size']:
                raise SecurityViolationError(f"Request too large: {data_size} bytes")
        
        # Validate headers for injection attempts
        for header_name, header_value in headers.items():
            if any(char in str(header_value) for char in ['\n', '\r', '\0']):
                raise SecurityViolationError(f"Invalid header value: {header_name}")

    def _check_circuit_breaker(self, integration_name: str) -> bool:
        """Check if circuit breaker allows requests"""
        if integration_name not in self.circuit_breakers:
            return True
        
        breaker = self.circuit_breakers[integration_name]
        now = time.time()
        
        if breaker['state'] == 'open':
            # Check if recovery timeout has passed
            if (breaker['last_failure'] and 
                now - breaker['last_failure'] > breaker['recovery_timeout']):
                breaker['state'] = 'half-open'
                breaker['failure_count'] = 0
                return True
            return False
        
        return True

    def _check_rate_limit(self, integration_name: str) -> bool:
        """Check if request is within rate limits"""
        if integration_name not in self.rate_limits:
            return True
        
        rate_limit = self.rate_limits[integration_name]
        now = time.time()
        
        # Clean old requests
        rate_limit['requests'] = [
            req_time for req_time in rate_limit['requests']
            if now - req_time < rate_limit['window']
        ]
        
        # Check limit
        if len(rate_limit['requests']) >= rate_limit['limit']:
            return False
        
        # Add current request
        rate_limit['requests'].append(now)
        return True

    def _handle_response(self, integration_name: str, response: requests.Response, execution_time: float):
        """Handle HTTP response and update metrics"""
        if response.status_code >= 400:
            self._handle_request_error(integration_name, 
                                     f"HTTP {response.status_code}: {response.text}")
        
        # Log slow requests
        if execution_time > 5.0:
            logger.warning(f"Slow request to {integration_name}: {execution_time:.2f}s")
        
        # Update circuit breaker on success
        if integration_name in self.circuit_breakers:
            breaker = self.circuit_breakers[integration_name]
            if breaker['state'] == 'half-open':
                breaker['state'] = 'closed'
                breaker['failure_count'] = 0

    def _handle_request_error(self, integration_name: str, error: Exception):
        """Handle request errors and update circuit breaker"""
        with self._lock:
            self.metrics['failed_requests'] += 1
        
        if integration_name in self.circuit_breakers:
            breaker = self.circuit_breakers[integration_name]
            breaker['failure_count'] += 1
            breaker['last_failure'] = time.time()
            
            if breaker['failure_count'] >= breaker['failure_threshold']:
                breaker['state'] = 'open'
                with self._lock:
                    self.metrics['circuit_breaker_trips'] += 1
                logger.warning(f"Circuit breaker opened for {integration_name}")
        
        logger.error(f"Integration error for {integration_name}: {error}")

    def get_integration_health(self, integration_name: str) -> Dict[str, Any]:
        """Get health status of an integration"""
        if integration_name not in self.integrations:
            return {'status': 'not_found'}
        
        config = self.integrations[integration_name]
        
        try:
            # Perform health check
            start_time = time.time()
            health_endpoint = config.get('health_endpoint', 'health')
            
            result = self.make_request(
                integration_name, 'GET', health_endpoint, 
                **{'timeout': 5}  # Short timeout for health checks
            )
            
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy' if result['status_code'] < 400 else 'unhealthy',
                'response_time': response_time,
                'last_check': datetime.utcnow().isoformat(),
                'circuit_breaker': self.circuit_breakers.get(integration_name, {}).get('state', 'closed')
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat(),
                'circuit_breaker': self.circuit_breakers.get(integration_name, {}).get('state', 'open')
            }

    def get_metrics(self) -> Dict[str, Any]:
        """Get integration service metrics"""
        with self._lock:
            metrics = self.metrics.copy()
        
        # Add rate limit info
        rate_limit_info = {}
        for name, limit in self.rate_limits.items():
            rate_limit_info[name] = {
                'current_requests': len(limit['requests']),
                'limit': limit['limit'],
                'window': limit['window']
            }
        
        # Add circuit breaker info
        circuit_breaker_info = {}
        for name, breaker in self.circuit_breakers.items():
            circuit_breaker_info[name] = {
                'state': breaker['state'],
                'failure_count': breaker['failure_count']
            }
        
        return {
            'metrics': metrics,
            'rate_limits': rate_limit_info,
            'circuit_breakers': circuit_breaker_info,
            'total_integrations': len(self.integrations),
            'timestamp': datetime.utcnow().isoformat()
        }

    def reset_circuit_breaker(self, integration_name: str):
        """Manually reset a circuit breaker"""
        if integration_name in self.circuit_breakers:
            breaker = self.circuit_breakers[integration_name]
            breaker['state'] = 'closed'
            breaker['failure_count'] = 0
            breaker['last_failure'] = None
            logger.info(f"Circuit breaker reset for {integration_name}")

    def update_security_settings(self, settings: Dict[str, Any]):
        """Update security settings"""
        allowed_settings = [
            'allowed_domains', 'blocked_domains', 'max_request_size', 
            'timeout', 'verify_ssl'
        ]
        
        for key, value in settings.items():
            if key in allowed_settings:
                self.security_settings[key] = value
                logger.info(f"Security setting updated: {key}")

    def cleanup(self):
        """Clean up resources"""
        try:
            if self.session:
                self.session.close()
            logger.info("Integration service cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Global integration service instance
_integration_service = None

def get_integration_service() -> RobustIntegrationService:
    """Get or create global integration service instance"""
    global _integration_service
    
    if _integration_service is None:
        _integration_service = RobustIntegrationService()
    
    return _integration_service

def init_integration_service(app) -> RobustIntegrationService:
    """Initialize integration service with Flask app"""
    service = get_integration_service()
    
    # Register OpenAI integration if configured
    openai_key = app.config.get('OPENAI_API_KEY')
    if openai_key:
        service.register_integration('openai', {
            'base_url': 'https://api.openai.com/v1',
            'authentication': {
                'type': 'bearer',
                'token': openai_key
            },
            'rate_limit': {
                'requests': 100,
                'window': 3600
            },
            'circuit_breaker': True,
            'failure_threshold': 3,
            'recovery_timeout': 300
        })
    
    # Register other integrations as needed
    
    logger.info("Integration service initialized with Flask app")
    return service