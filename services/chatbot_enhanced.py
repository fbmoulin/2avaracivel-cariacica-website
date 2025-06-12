"""
Enhanced Chatbot Service with Comprehensive Error Handling and Performance Optimizations
Robust implementation with advanced validation, caching, and fallback mechanisms
"""
import os
import json
import logging
import re
import time
import hashlib
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from functools import lru_cache
from openai import OpenAI
import sqlite3
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class ChatbotCache:
    """Thread-safe in-memory cache with TTL and intelligent invalidation"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache = {}
        self.timestamps = {}
        self.access_count = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.lock = threading.RLock()
        self.stats = {'hits': 0, 'misses': 0, 'evictions': 0}
    
    def _normalize_key(self, message: str) -> str:
        """Normalize message for consistent cache keys"""
        # Remove extra whitespace, convert to lowercase, remove punctuation
        normalized = re.sub(r'\s+', ' ', message.lower().strip())
        normalized = re.sub(r'[^\w\s]', '', normalized)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get(self, message: str) -> Optional[str]:
        """Thread-safe cache retrieval with TTL validation"""
        with self.lock:
            key = self._normalize_key(message)
            
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            # Check TTL
            if time.time() - self.timestamps[key] > self.default_ttl:
                self._remove_key(key)
                self.stats['misses'] += 1
                return None
            
            # Update access stats
            self.access_count[key] = self.access_count.get(key, 0) + 1
            self.stats['hits'] += 1
            
            return self.cache[key]
    
    def set(self, message: str, response: str, ttl: Optional[int] = None) -> None:
        """Thread-safe cache storage with automatic eviction"""
        with self.lock:
            key = self._normalize_key(message)
            
            # Evict if at capacity
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            self.cache[key] = response
            self.timestamps[key] = time.time()
            self.access_count[key] = 1
    
    def _evict_lru(self) -> None:
        """Evict least recently used entries"""
        if not self.cache:
            return
        
        # Find oldest entry
        oldest_key = min(self.timestamps.keys(), key=lambda k: self.timestamps[k])
        self._remove_key(oldest_key)
        self.stats['evictions'] += 1
    
    def _remove_key(self, key: str) -> None:
        """Remove key from all tracking structures"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)
        self.access_count.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache data"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
            self.access_count.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'entries': len(self.cache),
                'max_size': self.max_size,
                'hit_rate': round(hit_rate, 2),
                'total_hits': self.stats['hits'],
                'total_misses': self.stats['misses'],
                'total_evictions': self.stats['evictions']
            }


class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    @staticmethod
    def validate_message(message: Any) -> Tuple[bool, str, Optional[str]]:
        """Validate and sanitize user message"""
        
        # Type validation
        if not isinstance(message, str):
            return False, "Mensagem deve ser texto", None
        
        # Basic sanitization
        message = message.strip()
        
        # Length validation
        if not message:
            return False, "Mensagem não pode estar vazia", None
        
        if len(message) > 2000:
            return False, "Mensagem muito longa (máximo 2000 caracteres)", None
        
        # Content validation - basic HTML/script injection prevention
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return False, "Conteúdo não permitido na mensagem", None
        
        # Advanced sanitization
        sanitized = InputValidator._sanitize_text(message)
        
        return True, "", sanitized
    
    @staticmethod
    def _sanitize_text(text: str) -> str:
        """Advanced text sanitization"""
        # Remove potentially dangerous characters but preserve readability
        text = re.sub(r'[<>"\']', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


class RateLimiter:
    """Advanced rate limiting with multiple strategies"""
    
    def __init__(self):
        self.requests = {}
        self.blocked_ips = {}
        self.lock = threading.RLock()
    
    def is_allowed(self, identifier: str, max_requests: int = 30, window_seconds: int = 60) -> Tuple[bool, Optional[str]]:
        """Check if request is allowed based on rate limits"""
        with self.lock:
            current_time = time.time()
            
            # Check if IP is temporarily blocked
            if identifier in self.blocked_ips:
                if current_time - self.blocked_ips[identifier] < 300:  # 5 minute block
                    return False, "IP temporariamente bloqueado devido a excesso de requisições"
                else:
                    del self.blocked_ips[identifier]
            
            # Initialize or clean old requests
            if identifier not in self.requests:
                self.requests[identifier] = []
            
            # Remove old requests outside the window
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier] 
                if current_time - req_time < window_seconds
            ]
            
            # Check rate limit
            if len(self.requests[identifier]) >= max_requests:
                # Block IP for repeated violations
                violation_count = len(self.requests[identifier])
                if violation_count > max_requests * 1.5:
                    self.blocked_ips[identifier] = current_time
                
                return False, f"Limite de requisições excedido. Máximo {max_requests} por {window_seconds} segundos"
            
            # Record this request
            self.requests[identifier].append(current_time)
            return True, None


class EnhancedChatbotService:
    """Enhanced chatbot service with comprehensive error handling and performance optimization"""
    
    def __init__(self):
        self.openai_client = None
        self.cache = ChatbotCache(max_size=1000, default_ttl=3600)
        self.rate_limiter = RateLimiter()
        self.conversation_contexts = {}
        self.performance_metrics = {
            'total_requests': 0,
            'openai_requests': 0,
            'cache_hits': 0,
            'errors': 0,
            'avg_response_time': 0
        }
        
        self._initialize_openai()
        self.predefined_responses = self._load_enhanced_responses()
    
    def _initialize_openai(self) -> None:
        """Initialize OpenAI client with comprehensive error handling"""
        try:
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                logger.warning("OpenAI API key not found. Using fallback responses only.")
                return
            
            if not api_key.startswith('sk-'):
                logger.error("Invalid OpenAI API key format")
                return
            
            self.openai_client = OpenAI(
                api_key=api_key,
                timeout=30.0,
                max_retries=2
            )
            
            # Test connection
            self._test_openai_connection()
            logger.info("OpenAI client initialized and tested successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.openai_client = None
    
    def _test_openai_connection(self) -> None:
        """Test OpenAI connection with minimal request"""
        if not self.openai_client:
            return
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5,
                timeout=10
            )
            if not response.choices:
                raise Exception("Empty response from OpenAI")
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            self.openai_client = None
    
    def _load_enhanced_responses(self) -> Dict[str, Dict[str, Any]]:
        """Load enhanced predefined responses with weighted keywords and context awareness"""
        return {
            'saudacao': {
                'response': """Olá! Bem-vindo à 2ª Vara Cível de Cariacica! 👋

Sou seu assistente virtual e posso ajudar com:
• 📋 Consulta processual online
• 📅 Agendamento de atendimento
• 🎥 Informações sobre audiências
• 📄 Solicitação de documentos
• 📞 Contatos e localização
• ⚖️ Mediação e conciliação

Como posso ajudá-lo hoje?""",
                'keywords': [
                    ('ola', 3), ('oi', 3), ('olá', 3),
                    ('bom dia', 4), ('boa tarde', 4), ('boa noite', 4),
                    ('hello', 2), ('hi', 2)
                ],
                'context_tags': ['greeting', 'welcome']
            },
            
            'horario': {
                'response': """⏰ **Horário de Funcionamento**

📅 **Segunda a Sexta-feira: 12h às 18h**
🚫 **Fechado**: Fins de semana e feriados

**Serviços Online:** Disponíveis 24h
**Atendimento Presencial:** Apenas no horário de funcionamento

📞 **Contato de Emergência:** (27) 3246-8200
📧 **Email:** 2varacivel.cariacica@tjes.jus.br""",
                'keywords': [
                    ('horario', 5), ('horário', 5), ('funcionamento', 4),
                    ('aberto', 3), ('fechado', 3), ('quando', 2),
                    ('que horas', 4), ('abre', 3), ('fecha', 3)
                ],
                'context_tags': ['schedule', 'hours']
            },
            
            'localizacao': {
                'response': """📍 **Localização da 2ª Vara Cível**

🏛️ **Endereço Completo:**
Rua Expedito Garcia, s/n
Centro, Cariacica - ES
CEP: 29140-060

🚗 **Como Chegar:**
• Próximo ao centro comercial de Cariacica
• Acesso por transporte público (linhas urbanas)
• Estacionamento disponível na rua
• Ponto de referência: Próximo à Prefeitura Municipal

🕐 **Horário de Atendimento:** 12h às 18h (Seg-Sex)
📞 **Telefone:** (27) 3246-8200""",
                'keywords': [
                    ('endereco', 5), ('endereço', 5), ('localização', 5),
                    ('onde', 4), ('como chegar', 5), ('local', 3),
                    ('fica', 3), ('localiza', 4)
                ],
                'context_tags': ['location', 'address']
            },
            
            'processo_consulta': {
                'response': """🔍 **Consulta Processual Completa**

**💻 Em Nosso Site:**
1. Acesse a seção "Consulta Processual"
2. Digite o número no formato CNJ (NNNNNNN-DD.AAAA.J.TR.OOOO)
3. Visualize andamentos, decisões e documentos

**🌐 Portal do TJES:**
• Site: www.tjes.jus.br
• Seção "Consulta Processual"
• Acesso a todos os tribunais do ES

**📱 App do TJES:**
• Download gratuito na App Store/Google Play
• Consultas offline
• Notificações push

**❓ Não tem o número do processo?**
Entre em contato conosco com seus dados pessoais.

📞 **Ajuda:** (27) 3246-8200""",
                'keywords': [
                    ('processo', 5), ('consulta', 5), ('andamento', 4),
                    ('numero', 4), ('número', 4), ('cnj', 5),
                    ('processual', 5), ('tramitação', 3)
                ],
                'context_tags': ['process', 'consultation']
            },
            
            'audiencia_info': {
                'response': """🎥 **Audiências - Guia Completo**

**💻 Audiências Virtuais (Zoom):**
• Link enviado por email 48h antes
• Tutorial de configuração no nosso site
• Teste sua conexão 1 dia antes
• Suporte técnico: (27) 3246-8200

**🏛️ Audiências Presenciais:**
• Compareça 15 minutos antes do horário
• Traga documentos originais
• Use vestimenta adequada (social)
• Localização: Rua Expedito Garcia, s/n

**📋 Tipos de Audiência:**
• Conciliação (tentativa de acordo)
• Instrução e Julgamento (testemunhas/provas)
• Mediação (resolução consensual)

**🆘 Problemas Técnicos ou Dúvidas:**
Entre em contato imediatamente: (27) 3246-8200

**📧 Todas as instruções são enviadas por email**""",
                'keywords': [
                    ('audiencia', 5), ('audiência', 5), ('virtual', 4),
                    ('presencial', 4), ('zoom', 4), ('reunião', 3),
                    ('videoconferencia', 4), ('online', 3)
                ],
                'context_tags': ['hearing', 'virtual', 'presential']
            },
            
            'agendamento_completo': {
                'response': """📅 **Agendamento de Atendimento Completo**

**🌐 Agendamento Online (Recomendado):**
• Acesse nossa página de agendamento
• Escolha data e horário disponível
• Confirmação automática por email
• Cancelamento/reagendamento online

**📞 Agendamento por Telefone:**
• (27) 3246-8200
• Horário: 12h às 18h (Segunda a Sexta)
• Confirmação na mesma ligação

**📋 Documentos Necessários:**
• RG, CNH ou documento oficial com foto
• CPF
• Comprovantes relacionados ao assunto
• Procuração (se representando terceiros)

**⏰ Horários Disponíveis:**
• Segunda a Sexta: 12h às 18h
• Atendimentos de 30 minutos
• Intervalos de 30 em 30 minutos

**💡 Dica:** Agendamento online é mais rápido e você recebe confirmação imediata!""",
                'keywords': [
                    ('agendamento', 5), ('agendar', 5), ('marcar', 4),
                    ('atendimento', 5), ('horário', 3), ('consulta', 3),
                    ('reunião', 3)
                ],
                'context_tags': ['scheduling', 'appointment']
            }
        }
    
    def get_response(self, message: str, session_id: Optional[str] = None, 
                    client_ip: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced response generation with comprehensive error handling"""
        start_time = time.time()
        
        try:
            # Update metrics
            self.performance_metrics['total_requests'] += 1
            
            # Rate limiting
            if client_ip:
                allowed, error_msg = self.rate_limiter.is_allowed(client_ip)
                if not allowed:
                    return {
                        'success': False,
                        'error': error_msg,
                        'error_type': 'rate_limit'
                    }
            
            # Input validation
            is_valid, error_msg, sanitized_message = InputValidator.validate_message(message)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_msg,
                    'error_type': 'validation'
                }
            
            # Try cache first
            cached_response = self.cache.get(sanitized_message)
            if cached_response:
                self.performance_metrics['cache_hits'] += 1
                return {
                    'success': True,
                    'response': cached_response,
                    'source': 'cache',
                    'response_time': round((time.time() - start_time) * 1000, 2)
                }
            
            # Try predefined responses
            predefined_response = self._find_best_predefined_response(sanitized_message)
            if predefined_response:
                processed_response = self._process_special_actions(predefined_response)
                self.cache.set(sanitized_message, processed_response)
                return {
                    'success': True,
                    'response': processed_response,
                    'source': 'predefined',
                    'response_time': round((time.time() - start_time) * 1000, 2)
                }
            
            # Try OpenAI
            if self.openai_client:
                try:
                    openai_response = self._get_openai_response(sanitized_message, session_id)
                    if openai_response:
                        self.performance_metrics['openai_requests'] += 1
                        processed_response = self._process_special_actions(openai_response)
                        self.cache.set(sanitized_message, processed_response)
                        return {
                            'success': True,
                            'response': processed_response,
                            'source': 'openai',
                            'response_time': round((time.time() - start_time) * 1000, 2)
                        }
                except Exception as e:
                    logger.error(f"OpenAI request failed: {e}")
                    # Continue to fallback
            
            # Fallback response
            fallback_response = self._get_smart_fallback(sanitized_message)
            self.cache.set(sanitized_message, fallback_response)
            
            return {
                'success': True,
                'response': fallback_response,
                'source': 'fallback',
                'response_time': round((time.time() - start_time) * 1000, 2)
            }
            
        except Exception as e:
            logger.error(f"Chatbot service error: {e}")
            self.performance_metrics['errors'] += 1
            
            return {
                'success': False,
                'error': "Erro interno do sistema. Tente novamente ou entre em contato conosco.",
                'error_type': 'internal_error'
            }
        finally:
            # Update average response time
            response_time = time.time() - start_time
            current_avg = self.performance_metrics['avg_response_time']
            total_requests = self.performance_metrics['total_requests']
            self.performance_metrics['avg_response_time'] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
    
    def _find_best_predefined_response(self, message: str) -> Optional[str]:
        """Enhanced predefined response matching with weighted keywords"""
        normalized_message = message.lower().strip()
        best_match = None
        best_score = 0
        
        for category, data in self.predefined_responses.items():
            score = 0
            
            # Calculate weighted keyword matches
            for keyword, weight in data['keywords']:
                if keyword in normalized_message:
                    score += weight
                    
                    # Bonus for exact phrase matches
                    if len(keyword.split()) > 1:
                        score += weight * 0.5
            
            # Context bonus
            if score > 0 and 'context_tags' in data:
                for tag in data['context_tags']:
                    if tag.lower() in normalized_message:
                        score += 2
            
            if score > best_score:
                best_score = score
                best_match = data['response']
        
        return best_match if best_score >= 3 else None
    
    def _get_openai_response(self, message: str, session_id: Optional[str]) -> Optional[str]:
        """Enhanced OpenAI integration with context and error handling"""
        try:
            # Build context-aware messages
            messages = [
                {
                    "role": "system",
                    "content": """Você é o assistente virtual da 2ª Vara Cível de Cariacica do TJES.

INFORMAÇÕES BÁSICAS:
• Horário: 12h às 18h, segunda a sexta-feira
• Endereço: Rua Expedito Garcia, s/n, Centro, Cariacica-ES, CEP: 29140-060
• Telefone: (27) 3246-8200
• Email: 2varacivel.cariacica@tjes.jus.br

COMPETÊNCIAS:
• Ações cíveis em geral, execuções, cumprimento de sentença
• Contratos e responsabilidade civil
• Mediação e conciliação

SERVIÇOS:
• Consulta processual online
• Agendamento de atendimento
• Audiências presenciais e virtuais
• Solicitação de certidões

INSTRUÇÕES:
• Seja cordial, preciso e profissional
• Use formatação clara e emojis quando apropriado
• Para dúvidas específicas sobre processos, oriente consulta pelo número CNJ
• Em urgências, indique contato telefônico
• Mantenha respostas concisas mas completas (máximo 300 palavras)"""
                }
            ]
            
            # Add conversation context if available
            if session_id and session_id in self.conversation_contexts:
                context = self.conversation_contexts[session_id]
                messages.extend(context[-4:])  # Last 2 exchanges
            
            # Add current message
            messages.append({"role": "user", "content": message[:500]})
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=400,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1,
                timeout=25
            )
            
            if response.choices and response.choices[0].message.content:
                ai_response = response.choices[0].message.content.strip()
                
                # Update conversation context
                if session_id:
                    self._update_conversation_context(session_id, message, ai_response)
                
                return ai_response
            
            return None
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    def _update_conversation_context(self, session_id: str, user_message: str, bot_response: str) -> None:
        """Update conversation context for continuity"""
        if session_id not in self.conversation_contexts:
            self.conversation_contexts[session_id] = []
        
        context = self.conversation_contexts[session_id]
        context.extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": bot_response}
        ])
        
        # Keep only last 6 messages (3 exchanges)
        if len(context) > 6:
            self.conversation_contexts[session_id] = context[-6:]
    
    def _get_smart_fallback(self, message: str) -> str:
        """Intelligent fallback response based on message analysis"""
        normalized = message.lower()
        
        # Keyword-based intelligent fallback
        if any(word in normalized for word in ['horario', 'hora', 'funcionamento', 'aberto']):
            return self.predefined_responses['horario']['response']
        elif any(word in normalized for word in ['endereco', 'endereço', 'onde', 'localização']):
            return self.predefined_responses['localizacao']['response']
        elif any(word in normalized for word in ['processo', 'consulta', 'numero', 'cnj']):
            return self.predefined_responses['processo_consulta']['response']
        elif any(word in normalized for word in ['audiencia', 'audiência', 'zoom', 'virtual']):
            return self.predefined_responses['audiencia_info']['response']
        elif any(word in normalized for word in ['agendar', 'agendamento', 'marcar']):
            return self.predefined_responses['agendamento_completo']['response']
        
        return """Olá! Sou o assistente virtual da 2ª Vara Cível de Cariacica.

🔍 **Principais Serviços:**
• Consulta processual online
• Agendamento de atendimento
• Informações sobre audiências
• Solicitação de documentos
• Contatos e localização

📞 **Contato Direto:**
• Telefone: (27) 3246-8200
• Horário: 12h às 18h (Segunda a Sexta)
• Email: 2varacivel.cariacica@tjes.jus.br

💡 **Dica:** Digite palavras-chave como "processo", "horário", "agendamento" ou "audiência" para informações específicas.

Como posso ajudá-lo hoje?"""
    
    def _process_special_actions(self, response: str) -> str:
        """Process special action tokens in responses"""
        # Convert action tokens to interactive elements
        action_replacements = {
            '[AGENDAR_REUNIAO_ASSESSOR]': '**[Agendar Reunião com Assessores](/servicos/agendamento-assessor)**',
            '[CONSULTAR_PROCESSO]': '**[Consultar Processo](/servicos/consulta-processual)**',
            '[AGENDAR_ATENDIMENTO]': '**[Agendar Atendimento](/servicos/agendamento)**',
            '[CONTATO_DIRETO]': '**[Entrar em Contato](/contato)**'
        }
        
        for token, replacement in action_replacements.items():
            response = response.replace(token, replacement)
        
        return response
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        cache_stats = self.cache.get_stats()
        
        return {
            'requests': {
                'total': self.performance_metrics['total_requests'],
                'openai': self.performance_metrics['openai_requests'],
                'cache_hits': self.performance_metrics['cache_hits'],
                'errors': self.performance_metrics['errors']
            },
            'performance': {
                'avg_response_time_ms': round(self.performance_metrics['avg_response_time'] * 1000, 2),
                'cache_hit_rate': cache_stats['hit_rate']
            },
            'cache': cache_stats,
            'openai_status': 'available' if self.openai_client else 'unavailable'
        }
    
    def clear_cache(self) -> None:
        """Clear all cached responses"""
        self.cache.clear()
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'cache': 'healthy',
                'rate_limiter': 'healthy',
                'openai': 'unavailable' if not self.openai_client else 'healthy'
            },
            'metrics': self.get_performance_stats()
        }
        
        # Test OpenAI connection if available
        if self.openai_client:
            try:
                self._test_openai_connection()
                health_status['components']['openai'] = 'healthy'
            except Exception:
                health_status['components']['openai'] = 'degraded'
                health_status['status'] = 'degraded'
        
        return health_status


# Global instance
enhanced_chatbot_service = EnhancedChatbotService()