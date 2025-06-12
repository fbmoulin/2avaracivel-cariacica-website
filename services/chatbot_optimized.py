"""
Optimized chatbot service with intelligent response caching and performance enhancements
Advanced OpenAI integration with fallback strategies and response optimization
"""
import os
import logging
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from functools import lru_cache
import hashlib
import re

logger = logging.getLogger(__name__)


class ResponseCache:
    """Intelligent response caching with semantic similarity"""
    
    def __init__(self, max_size: int = 500):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def _normalize_message(self, message: str) -> str:
        """Normalize message for better cache hits"""
        # Convert to lowercase and remove extra whitespace
        normalized = re.sub(r'\s+', ' ', message.lower().strip())
        # Remove punctuation
        normalized = re.sub(r'[^\w\s]', '', normalized)
        return normalized
    
    def _generate_key(self, message: str) -> str:
        """Generate cache key from normalized message"""
        normalized = self._normalize_message(message)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get(self, message: str) -> Optional[str]:
        """Get cached response if available"""
        key = self._generate_key(message)
        
        if key in self.cache:
            self.access_times[key] = time.time()
            self.hits += 1
            return self.cache[key]['response']
        
        self.misses += 1
        return None
    
    def set(self, message: str, response: str):
        """Cache response with LRU eviction"""
        key = self._generate_key(message)
        
        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = {
            'response': response,
            'created_at': time.time(),
            'original_message': message
        }
        self.access_times[key] = time.time()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            'total_entries': len(self.cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'max_size': self.max_size
        }


class OptimizedChatbotService:
    """Advanced chatbot service with OpenAI integration and intelligent fallbacks"""
    
    def __init__(self):
        self.openai_client = None
        self.response_cache = ResponseCache(max_size=500)
        self.predefined_responses = self._load_predefined_responses()
        self.conversation_context = {}
        self.rate_limit_tracker = {}
        
        self._initialize_openai()
    
    def _initialize_openai(self):
        """Initialize OpenAI client with error handling"""
        try:
            api_key = os.environ.get('OPENAI_API_KEY')
            if api_key:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully")
            else:
                logger.warning("OpenAI API key not found, using fallback responses only")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
    
    def _load_predefined_responses(self) -> Dict[str, Dict[str, Any]]:
        """Load optimized predefined responses with enhanced keywords"""
        return {
            'saudacao': {
                'keywords': ['ola', 'oi', 'bom dia', 'boa tarde', 'boa noite', 'hello', 'hi'],
                'response': """Olá! Bem-vindo à 2ª Vara Cível de Cariacica! 👋

Sou seu assistente virtual e posso ajudar com:
• 📋 Consulta processual
• 📅 Agendamento de atendimento  
• 🎥 Informações sobre audiências
• 📄 Solicitação de documentos
• 📞 Contatos e localização
• ⚖️ Serviços da vara cível

Como posso ajudá-lo hoje?""",
                'priority': 10
            },
            
            'horario': {
                'keywords': ['horario', 'horário', 'funcionamento', 'atendimento', 'aberto', 'fechado', 'quando'],
                'response': """⏰ **Horário de Funcionamento**

📅 **Segunda a Sexta-feira: 12h às 18h**
🚫 **Fechado**: Fins de semana e feriados

**Atendimento Presencial:**
• Rua Expedito Garcia, s/n, Centro
• Cariacica - ES, CEP: 29140-060

**Contato:**
• ☎️ Telefone: (27) 3246-8200
• 📧 Email: 2varacivel.cariacica@tjes.jus.br""",
                'priority': 9
            },
            
            'localizacao': {
                'keywords': ['endereco', 'endereço', 'localização', 'onde', 'como chegar', 'local'],
                'response': """📍 **Localização da 2ª Vara Cível**

🏛️ **Endereço Completo:**
Rua Expedito Garcia, s/n
Centro, Cariacica - ES
CEP: 29140-060

🚗 **Como Chegar:**
• Próximo ao centro de Cariacica
• Acesso por transporte público
• Estacionamento disponível

📞 **Contato:** (27) 3246-8200
⏰ **Horário:** 12h às 18h (Seg-Sex)""",
                'priority': 8
            },
            
            'processo': {
                'keywords': ['processo', 'consulta', 'andamento', 'numero', 'cnj', 'processual'],
                'response': """🔍 **Consulta Processual**

Para consultar seu processo:

1️⃣ **Em nosso site:**
• Acesse a seção "Consulta Processual"
• Digite o número completo no formato CNJ
• Visualize andamentos e decisões

2️⃣ **Portal do TJES:**
• www.tjes.jus.br
• Seção "Consulta Processual"

📋 **Importante:** Tenha em mãos o número completo do processo no formato NNNNNNN-DD.AAAA.J.TR.OOOO

❓ Precisa de ajuda com o número do processo?""",
                'priority': 9
            },
            
            'audiencia': {
                'keywords': ['audiencia', 'audiência', 'virtual', 'presencial', 'zoom', 'reunião', 'videoconferencia'],
                'response': """🎥 **Audiências - Informações Completas**

**🎯 Tipos de Audiência:**
• Conciliação
• Instrução e Julgamento
• Mediação

**💻 Audiências Virtuais (Zoom):**
• Link enviado por email 48h antes
• Tutorial de configuração disponível
• Teste sua conexão antecipadamente

**🏛️ Audiências Presenciais:**
• Compareça 15 minutos antes
• Traga documentos originais
• Use vestimenta adequada

**📧 Instruções detalhadas são sempre enviadas por email**

🆘 Problemas técnicos? Entre em contato: (27) 3246-8200""",
                'priority': 9
            },
            
            'agendamento': {
                'keywords': ['agendamento', 'agendar', 'marcar', 'atendimento', 'horário'],
                'response': """📅 **Agendamento de Atendimento**

**🌐 Online (Recomendado):**
• Acesse nossa página de agendamento
• Escolha data e horário disponível
• Receba confirmação por email

**📞 Por Telefone:**
• (27) 3246-8200
• Segunda a Sexta: 12h às 18h

**📋 Documentos Necessários:**
• RG ou CNH
• CPF
• Comprovantes relacionados ao assunto

**⏰ Horários Disponíveis:**
• 12h às 18h (Segunda a Sexta)
• Consulte disponibilidade online

💡 **Dica:** Agendamento online é mais rápido!""",
                'priority': 8
            },
            
            'documentos': {
                'keywords': ['documentos', 'certidão', 'certidões', 'segunda via', 'cópia', 'papel'],
                'response': """📄 **Solicitação de Documentos**

**📜 Documentos Disponíveis:**
• Certidões de processos
• Cópias de petições
• Atas de audiência
• Sentenças e decisões

**🌐 Alguns Serviços Online:**
• Consulta de documentos
• Download de decisões públicas

**🏛️ Atendimento Presencial:**
• Documentos específicos
• Autenticação de cópias
• Certidões com carimbo oficial

**📋 Leve Sempre:**
• RG ou CNH original
• CPF
• Comprovantes necessários

📞 Dúvidas? Ligue: (27) 3246-8200""",
                'priority': 7
            },
            
            'despedida': {
                'keywords': ['tchau', 'obrigado', 'obrigada', 'valeu', 'bye', 'adeus', 'até logo'],
                'response': """Muito obrigado por usar nossos serviços! 😊

Se precisar de mais alguma coisa, estarei aqui para ajudar.

**Lembre-se:**
• 📞 Telefone: (27) 3246-8200
• ⏰ Horário: 12h às 18h (Seg-Sex)
• 🌐 Site: Sempre disponível

Tenha um ótimo dia! ⚖️✨""",
                'priority': 5
            }
        }
    
    def _find_best_predefined_response(self, user_message: str) -> Optional[Tuple[str, int]]:
        """Find best matching predefined response with scoring"""
        normalized_message = user_message.lower().strip()
        best_match = None
        best_score = 0
        
        for category, data in self.predefined_responses.items():
            score = 0
            
            # Calculate keyword matches
            for keyword in data['keywords']:
                if keyword in normalized_message:
                    score += data.get('priority', 1)
            
            # Bonus for exact phrase matches
            for keyword in data['keywords']:
                if len(keyword.split()) > 1 and keyword in normalized_message:
                    score += 5
            
            if score > best_score:
                best_score = score
                best_match = data['response']
        
        return (best_match, best_score) if best_score > 0 else (None, 0)
    
    def _check_rate_limit(self, session_id: str) -> bool:
        """Check if session is within rate limits"""
        now = time.time()
        session_data = self.rate_limit_tracker.get(session_id, {'requests': [], 'last_request': 0})
        
        # Remove old requests (older than 1 minute)
        session_data['requests'] = [req_time for req_time in session_data['requests'] if now - req_time < 60]
        
        # Check rate limit (max 10 requests per minute)
        if len(session_data['requests']) >= 10:
            return False
        
        # Add current request
        session_data['requests'].append(now)
        session_data['last_request'] = now
        self.rate_limit_tracker[session_id] = session_data
        
        return True
    
    def _get_openai_response(self, user_message: str, context: List[Dict] = None) -> str:
        """Get response from OpenAI with context awareness"""
        try:
            if not self.openai_client:
                return None
            
            # Build conversation context
            messages = [
                {
                    "role": "system",
                    "content": """Você é o assistente virtual da 2ª Vara Cível de Cariacica do TJES.

INFORMAÇÕES IMPORTANTES:
• Horário: Segunda a Sexta, 12h às 18h
• Endereço: Rua Expedito Garcia, s/n, Centro, Cariacica-ES
• Telefone: (27) 3246-8200
• Email: 2varacivel.cariacica@tjes.jus.br

COMPETÊNCIAS:
• Ações cíveis em geral
• Execuções de título extrajudicial
• Cumprimento de sentença
• Ações de cobrança
• Contratos e responsabilidade civil

SERVIÇOS:
• Consulta processual online
• Agendamento de atendimento
• Audiências presenciais e virtuais
• Solicitação de certidões
• Balcão virtual

INSTRUÇÕES:
• Seja cordial e profissional
• Forneça informações precisas
• Use formatação clara
• Mantenha respostas concisas
• Para processos específicos, oriente consulta pelo número CNJ
• Em urgências, indique contato telefônico"""
                }
            ]
            
            # Add context if provided
            if context:
                messages.extend(context[-3:])  # Last 3 exchanges for context
            
            # Add current user message
            messages.append({"role": "user", "content": user_message[:500]})
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=400,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    def _update_conversation_context(self, session_id: str, user_message: str, response: str):
        """Update conversation context for better continuity"""
        if session_id not in self.conversation_context:
            self.conversation_context[session_id] = []
        
        context = self.conversation_context[session_id]
        context.append({"role": "user", "content": user_message})
        context.append({"role": "assistant", "content": response})
        
        # Keep only last 6 messages (3 exchanges)
        if len(context) > 6:
            context = context[-6:]
        
        self.conversation_context[session_id] = context
    
    def get_response(self, user_message: str, session_id: str = None) -> str:
        """Get optimized chatbot response with multiple strategies"""
        try:
            # Validate input
            if not user_message or not user_message.strip():
                return "Por favor, digite uma mensagem para que eu possa ajudá-lo."
            
            user_message = user_message.strip()
            if len(user_message) > 1000:
                return "Mensagem muito longa. Por favor, seja mais conciso para que eu possa ajudá-lo melhor."
            
            # Check rate limiting
            if session_id and not self._check_rate_limit(session_id):
                return "Muitas mensagens em pouco tempo. Aguarde um momento antes de enviar outra mensagem."
            
            # Try cache first
            cached_response = self.response_cache.get(user_message)
            if cached_response:
                logger.debug(f"Cache hit for message: {user_message[:50]}...")
                return cached_response
            
            # Try predefined responses
            predefined_response, score = self._find_best_predefined_response(user_message)
            if predefined_response and score >= 3:  # High confidence threshold
                self.response_cache.set(user_message, predefined_response)
                return predefined_response
            
            # Try OpenAI with context
            context = self.conversation_context.get(session_id, []) if session_id else []
            openai_response = self._get_openai_response(user_message, context)
            
            if openai_response:
                # Cache successful OpenAI responses
                self.response_cache.set(user_message, openai_response)
                
                # Update conversation context
                if session_id:
                    self._update_conversation_context(session_id, user_message, openai_response)
                
                return openai_response
            
            # Fallback to default response or best predefined match
            if predefined_response:
                self.response_cache.set(user_message, predefined_response)
                return predefined_response
            
            # Ultimate fallback
            default_response = self._get_default_response()
            self.response_cache.set(user_message, default_response)
            return default_response
            
        except Exception as e:
            logger.error(f"Chatbot error: {e}")
            return "Desculpe, ocorreu um erro temporário. Tente novamente em alguns momentos ou entre em contato pelo telefone (27) 3246-8200."
    
    def _get_default_response(self) -> str:
        """Enhanced default response with helpful information"""
        return """Olá! Sou o assistente virtual da 2ª Vara Cível de Cariacica.

🔍 **Principais Serviços:**
• Consulta processual
• Agendamento de atendimento
• Informações sobre audiências
• Solicitação de documentos

📞 **Contato Direto:**
• Telefone: (27) 3246-8200
• Horário: 12h às 18h (Segunda a Sexta)

💡 **Dica:** Digite palavras-chave como "processo", "audiência" ou "agendamento" para obter informações específicas.

Como posso ajudá-lo hoje?"""
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive chatbot statistics"""
        cache_stats = self.response_cache.get_stats()
        
        return {
            'cache_statistics': cache_stats,
            'active_sessions': len(self.conversation_context),
            'predefined_responses': len(self.predefined_responses),
            'openai_available': bool(self.openai_client),
            'rate_limited_sessions': len(self.rate_limit_tracker)
        }


# Global chatbot service instance
chatbot_service = OptimizedChatbotService()


def get_chatbot_response(message: str, session_id: str = None) -> str:
    """Public function to get optimized chatbot response"""
    return chatbot_service.get_response(message, session_id)