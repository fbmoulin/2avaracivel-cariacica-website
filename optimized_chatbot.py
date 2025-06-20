"""
Optimized Chatbot Service
Streamlined architecture with improved performance and reduced complexity
"""
import os
import json
import logging
import time
import re
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI library not available")

logger = logging.getLogger(__name__)

class ResponseType(Enum):
    """Response type categories"""
    OPENAI = "openai"
    PREDEFINED = "predefined"
    FALLBACK = "fallback"
    CACHED = "cached"

@dataclass
class ChatResponse:
    """Optimized chat response structure"""
    response: str
    response_type: ResponseType
    confidence: float
    session_id: str
    timestamp: datetime
    response_time: float
    cached: bool = False
    suggestions: Optional[List[str]] = None
    
    def to_dict(self):
        return {
            'response': self.response,
            'response_type': self.response_type.value,
            'confidence': self.confidence,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'response_time': self.response_time,
            'cached': self.cached,
            'suggestions': self.suggestions or []
        }

class OptimizedChatbot:
    """Streamlined chatbot with improved performance"""
    
    def __init__(self):
        self.client = None
        self.initialize_openai()
        
        # Performance optimization
        self.response_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Analytics (simplified)
        self.metrics = {
            'total_requests': 0,
            'response_types': {rt.value: 0 for rt in ResponseType},
            'cache_hits': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        # Load predefined responses
        self.predefined_responses = self.load_predefined_responses()
        
        logger.info("Optimized chatbot initialized")
    
    def initialize_openai(self):
        """Initialize OpenAI client with error handling"""
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI not available, using fallback responses only")
            return
        
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OpenAI API key not found")
            return
        
        try:
            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
    
    @lru_cache(maxsize=128)
    def load_predefined_responses(self):
        """Load predefined responses with caching"""
        return {
            'horario': {
                'keywords': ['horario', 'funcionamento', 'atendimento', 'hora'],
                'response': 'A 2ª Vara Cível de Cariacica funciona de segunda a sexta-feira, das 12h às 18h.',
                'confidence': 0.95
            },
            'endereco': {
                'keywords': ['endereco', 'endereço', 'localização', 'localização', 'onde fica'],
                'response': 'Estamos localizados na Av. Meridional, 211 - Alto Lage, Cariacica/ES.',
                'confidence': 0.95
            },
            'contato': {
                'keywords': ['telefone', 'contato', 'falar', 'ligar'],
                'response': 'Nosso telefone é (27) 3246-8200. Você também pode nos contatar através do formulário no site.',
                'confidence': 0.9
            },
            'processo': {
                'keywords': ['consultar processo', 'numero processo', 'andamento'],
                'response': 'Para consultar seu processo, use o número CNJ no portal do TJES ou em nossa seção de consulta processual.',
                'confidence': 0.9
            },
            'agendamento': {
                'keywords': ['agendar', 'agendamento', 'marcar', 'atendimento'],
                'response': 'Você pode agendar atendimento através da nossa seção de agendamento ou pelo telefone (27) 3246-8200.',
                'confidence': 0.9
            }
        }
    
    def process_message(self, message: str, session_id: str = None, context: Dict = None) -> ChatResponse:
        """Optimized message processing"""
        start_time = time.time()
        self.metrics['total_requests'] += 1
        
        if not session_id:
            session_id = f"session_{int(time.time())}"
        
        try:
            # Check cache first
            cache_key = self.get_cache_key(message)
            cached_response = self.get_cached_response(cache_key)
            
            if cached_response:
                self.metrics['cache_hits'] += 1
                self.metrics['response_types'][ResponseType.CACHED.value] += 1
                
                response_time = time.time() - start_time
                return ChatResponse(
                    response=cached_response['response'],
                    response_type=ResponseType.CACHED,
                    confidence=cached_response['confidence'],
                    session_id=session_id,
                    timestamp=datetime.now(),
                    response_time=response_time,
                    cached=True,
                    suggestions=cached_response.get('suggestions', [])
                )
            
            # Try predefined responses
            predefined_response = self.get_predefined_response(message)
            if predefined_response:
                response_time = time.time() - start_time
                self.metrics['response_types'][ResponseType.PREDEFINED.value] += 1
                
                # Cache the response
                self.cache_response(cache_key, predefined_response)
                
                return ChatResponse(
                    response=predefined_response['response'],
                    response_type=ResponseType.PREDEFINED,
                    confidence=predefined_response['confidence'],
                    session_id=session_id,
                    timestamp=datetime.now(),
                    response_time=response_time,
                    suggestions=predefined_response.get('suggestions', [])
                )
            
            # Try OpenAI if available
            if self.client:
                openai_response = self.get_openai_response(message, context)
                if openai_response:
                    response_time = time.time() - start_time
                    self.metrics['response_types'][ResponseType.OPENAI.value] += 1
                    
                    # Cache the response
                    self.cache_response(cache_key, openai_response)
                    
                    return ChatResponse(
                        response=openai_response['response'],
                        response_type=ResponseType.OPENAI,
                        confidence=openai_response['confidence'],
                        session_id=session_id,
                        timestamp=datetime.now(),
                        response_time=response_time,
                        suggestions=openai_response.get('suggestions', [])
                    )
            
            # Fallback response
            fallback_response = self.get_fallback_response()
            response_time = time.time() - start_time
            self.metrics['response_types'][ResponseType.FALLBACK.value] += 1
            
            return ChatResponse(
                response=fallback_response['response'],
                response_type=ResponseType.FALLBACK,
                confidence=fallback_response['confidence'],
                session_id=session_id,
                timestamp=datetime.now(),
                response_time=response_time
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.metrics['errors'] += 1
            
            response_time = time.time() - start_time
            return ChatResponse(
                response="Desculpe, ocorreu um erro. Tente novamente em alguns minutos.",
                response_type=ResponseType.FALLBACK,
                confidence=0.0,
                session_id=session_id,
                timestamp=datetime.now(),
                response_time=response_time
            )
    
    def get_cache_key(self, message: str) -> str:
        """Generate cache key from message"""
        normalized = re.sub(r'[^\w\s]', '', message.lower().strip())
        return str(hash(normalized))
    
    def get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached response if valid"""
        if cache_key in self.response_cache:
            cached_data = self.response_cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['data']
            else:
                del self.response_cache[cache_key]
        return None
    
    def cache_response(self, cache_key: str, response_data: Dict):
        """Cache response with TTL"""
        self.response_cache[cache_key] = {
            'data': response_data,
            'timestamp': time.time()
        }
        
        # Simple cache cleanup (keep last 100 items)
        if len(self.response_cache) > 100:
            oldest_key = min(self.response_cache.keys(), 
                           key=lambda k: self.response_cache[k]['timestamp'])
            del self.response_cache[oldest_key]
    
    def get_predefined_response(self, message: str) -> Optional[Dict]:
        """Get predefined response based on keywords"""
        message_lower = message.lower()
        
        for category, data in self.predefined_responses.items():
            for keyword in data['keywords']:
                if keyword in message_lower:
                    return {
                        'response': data['response'],
                        'confidence': data['confidence'],
                        'category': category,
                        'suggestions': self.get_related_suggestions(category)
                    }
        
        return None
    
    def get_related_suggestions(self, category: str) -> List[str]:
        """Get related suggestions for a category"""
        suggestions_map = {
            'horario': ['Qual o telefone?', 'Como chegar?'],
            'endereco': ['Qual o horário?', 'Como agendar?'],
            'contato': ['Horário de funcionamento', 'Localização'],
            'processo': ['Agendar atendimento', 'Contato'],
            'agendamento': ['Horário de funcionamento', 'Telefone']
        }
        return suggestions_map.get(category, [])
    
    def get_openai_response(self, message: str, context: Dict = None) -> Optional[Dict]:
        """Get response from OpenAI with optimized prompt"""
        try:
            system_prompt = """Você é um assistente da 2ª Vara Cível de Cariacica.
Seja conciso, útil e profissional. Forneça informações sobre:
- Horário: Segunda a sexta, 12h às 18h
- Endereço: Av. Meridional, 211 - Alto Lage, Cariacica/ES
- Telefone: (27) 3246-8200
- Consulta processual via portal TJES
- Agendamento de atendimento disponível"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=200,
                temperature=0.7,
                timeout=10
            )
            
            if response.choices:
                return {
                    'response': response.choices[0].message.content.strip(),
                    'confidence': 0.8,
                    'tokens_used': response.usage.total_tokens if response.usage else 0
                }
        
        except Exception as e:
            logger.error(f"OpenAI request failed: {e}")
        
        return None
    
    def get_fallback_response(self) -> Dict:
        """Get fallback response"""
        fallback_messages = [
            "Posso ajudá-lo com informações sobre horário, localização, contato ou agendamento.",
            "Para informações específicas, entre em contato pelo telefone (27) 3246-8200.",
            "Visite nossa seção de serviços para consultar processos ou agendar atendimento."
        ]
        
        import random
        return {
            'response': random.choice(fallback_messages),
            'confidence': 0.5,
            'suggestions': ['Horário de funcionamento', 'Telefone', 'Localização']
        }
    
    def get_health_status(self) -> Dict:
        """Get chatbot health status"""
        return {
            'status': 'healthy' if self.client else 'limited',
            'openai_available': self.client is not None,
            'cache_size': len(self.response_cache),
            'uptime_minutes': (datetime.now() - self.metrics['start_time']).total_seconds() / 60,
            'total_requests': self.metrics['total_requests'],
            'error_rate': self.metrics['errors'] / max(self.metrics['total_requests'], 1)
        }
    
    def get_analytics(self) -> Dict:
        """Get simplified analytics"""
        total_requests = max(self.metrics['total_requests'], 1)
        
        return {
            'total_requests': self.metrics['total_requests'],
            'response_types': self.metrics['response_types'],
            'cache_hit_rate': self.metrics['cache_hits'] / total_requests,
            'error_rate': self.metrics['errors'] / total_requests,
            'uptime_hours': (datetime.now() - self.metrics['start_time']).total_seconds() / 3600,
            'cache_size': len(self.response_cache)
        }
    
    def clear_cache(self):
        """Clear response cache"""
        self.response_cache.clear()
        logger.info("Response cache cleared")
    
    def reset_metrics(self):
        """Reset analytics metrics"""
        self.metrics = {
            'total_requests': 0,
            'response_types': {rt.value: 0 for rt in ResponseType},
            'cache_hits': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        logger.info("Metrics reset")

# Global chatbot instance
_chatbot_instance = None

def get_optimized_chatbot():
    """Get singleton chatbot instance"""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = OptimizedChatbot()
    return _chatbot_instance