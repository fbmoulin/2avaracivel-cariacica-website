"""
Refined Chatbot Service for 2ª Vara Cível de Cariacica
Advanced architecture with modular design, enhanced AI integration, and comprehensive analytics
"""

import os
import json
import logging
import time
import re
import hashlib
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI library not available")

from services.integration_service import RetryManager


class ResponseType(Enum):
    """Response type enumeration for better categorization"""
    OPENAI = "openai"
    PREDEFINED = "predefined"
    FALLBACK = "fallback"
    CONTEXT_AWARE = "context_aware"
    MEETING_SCHEDULING = "meeting_scheduling"


class MessageRole(Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ChatMessage:
    """Structured chat message representation"""
    content: str
    role: MessageRole
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    message_id: Optional[str] = None

    def __post_init__(self):
        if not self.message_id:
            self.message_id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique message ID"""
        content_hash = hashlib.md5(self.content.encode()).hexdigest()[:8]
        timestamp_str = self.timestamp.strftime("%Y%m%d%H%M%S")
        return f"{self.role.value}_{timestamp_str}_{content_hash}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'content': self.content,
            'role': self.role.value,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata or {},
            'message_id': self.message_id
        }


@dataclass
class ChatResponse:
    """Structured chat response with comprehensive metadata"""
    content: str
    response_type: ResponseType
    response_time: float
    confidence_score: float
    context_used: bool = False
    openai_tokens_used: int = 0
    fallback_reason: Optional[str] = None
    suggestions: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
        if self.metadata is None:
            self.metadata = {}


class ResponseStrategy(ABC):
    """Abstract base class for response strategies"""
    
    @abstractmethod
    def can_handle(self, message: str, context: List[ChatMessage]) -> bool:
        """Check if this strategy can handle the message"""
        pass
    
    @abstractmethod
    def generate_response(self, message: str, context: List[ChatMessage]) -> ChatResponse:
        """Generate response using this strategy"""
        pass
    
    @property
    @abstractmethod
    def priority(self) -> int:
        """Strategy priority (lower number = higher priority)"""
        pass


class MeetingSchedulingStrategy(ResponseStrategy):
    """Strategy for handling meeting scheduling requests"""
    
    def __init__(self):
        self.meeting_keywords = [
            'agendar', 'reunião', 'encontro', 'marcar', 'horário',
            'disponibilidade', 'assessor', 'juiz', 'audiência'
        ]
    
    @property
    def priority(self) -> int:
        return 1
    
    def can_handle(self, message: str, context: List[ChatMessage]) -> bool:
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.meeting_keywords)
    
    def generate_response(self, message: str, context: List[ChatMessage]) -> ChatResponse:
        start_time = time.time()
        
        # Analyze message for specific meeting type
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['juiz', 'magistrado']):
            response_content = """📋 **Reunião com o Juiz**

Para reuniões com o magistrado:
• ⚖️ Requer petição formal através de advogado
• 📄 Processo oficial via sistema judicial
• 🏛️ Não há agendamento direto disponível

📞 **Orientações**: (27) 3246-8200
📧 **Email**: 2varacivel.cariacica@tjes.jus.br

**[INFORMACAO_FORMAL_JUIZ]**"""
        
        elif any(word in message_lower for word in ['assessor', 'orientação', 'esclarecimento']):
            response_content = """📅 **Agendamento com Assessor**

Disponível para esclarecimentos e orientações:
• 🏛️ **Presencial**: Atendimento no fórum
• 💻 **Virtual**: Videoconferência via Zoom
• 📋 **Gabinete**: Consultas sobre processos
• 📄 **Cartório**: Serviços de documentação

🌐 **Agendar Online**: Acesse nossa página de agendamento
📞 **Telefone**: (27) 3246-8200
⏰ **Horário**: Segunda a Sexta, 12h às 18h

**[AGENDAR_REUNIAO_ASSESSOR]**"""
        
        else:
            response_content = """📅 **Serviços de Agendamento**

**🏛️ Reunião com Assessor:**
• Orientações sobre processos
• Esclarecimentos jurídicos
• Modalidades: presencial ou virtual

**⚖️ Audiência com Juiz:**
• Requer processo formal
• Via petição de advogado

🌐 **Agende online** ou ligue (27) 3246-8200
⏰ **Horário**: Segunda a Sexta, 12h às 18h

**[OPCOES_AGENDAMENTO]**"""
        
        response_time = time.time() - start_time
        
        return ChatResponse(
            content=response_content,
            response_type=ResponseType.MEETING_SCHEDULING,
            response_time=response_time,
            confidence_score=0.95,
            context_used=len(context) > 0,
            suggestions=["Informações de contato", "Horários de funcionamento", "Consulta processual"],
            metadata={"strategy": "meeting_scheduling", "detected_keywords": self.meeting_keywords}
        )


class PredefinedResponseStrategy(ResponseStrategy):
    """Strategy for predefined responses using keyword matching"""
    
    def __init__(self):
        self.responses = self._load_responses()
    
    @property
    def priority(self) -> int:
        return 2
    
    def _load_responses(self) -> Dict[str, Dict[str, Any]]:
        """Load optimized predefined responses"""
        return {
            'horario': {
                'response': '🕐 **Horário de Funcionamento**\n\n⏰ **Segunda a Sexta**: 12h às 18h\n🚫 **Finais de semana**: Fechado\n📅 **Feriados**: Consulte nosso calendário\n\n📞 **Contato**: (27) 3246-8200',
                'keywords': ['horario', 'funcionamento', 'abertura', 'fechamento', 'horário', 'aberto', 'fecha'],
                'confidence': 0.9
            },
            'endereco': {
                'response': '📍 **Localização da 2ª Vara Cível**\n\n🏛️ **Endereço**: Rua Expedito Garcia, s/n\n🏘️ **Bairro**: Centro, Cariacica - ES\n📮 **CEP**: 29140-060\n\n🚗 **Como chegar**: Próximo ao centro de Cariacica\n🚌 **Transporte público**: Linhas municipais disponíveis',
                'keywords': ['endereco', 'localização', 'onde', 'fica', 'endereço', 'local', 'chegar'],
                'confidence': 0.9
            },
            'contato': {
                'response': '📞 **Informações de Contato**\n\n☎️ **Telefone**: (27) 3246-8200\n📧 **Email**: 2varacivel.cariacica@tjes.jus.br\n💬 **WhatsApp**: Disponível pelo telefone principal\n\n⏰ **Atendimento**: 12h às 18h (segunda a sexta)\n🏛️ **Presencial**: Rua Expedito Garcia, s/n - Centro',
                'keywords': ['telefone', 'contato', 'ligar', 'email', 'whatsapp', 'comunicação'],
                'confidence': 0.9
            },
            'processo': {
                'response': '🔍 **Consulta Processual**\n\n**🌐 Online:**\n• Portal do TJES: www.tjes.jus.br\n• Nossa página de consulta\n\n**📋 Você precisará:**\n• Número do processo (formato CNJ)\n• CPF do interessado\n\n**🏛️ Presencial:**\n• Atendimento das 12h às 18h\n• Traga documentos de identificação\n\n**[CONSULTAR_PROCESSO]**',
                'keywords': ['processo', 'consulta', 'andamento', 'número', 'cnj', 'tramitação'],
                'confidence': 0.95
            },
            'audiencia': {
                'response': '🎥 **Informações sobre Audiências**\n\n**💻 Audiências Virtuais:**\n• Plataforma: Zoom\n• Link enviado por email\n• Teste de conexão recomendado\n\n**🏛️ Audiências Presenciais:**\n• Compareça no horário exato\n• Documentos de identificação\n• Chegue com 15 min de antecedência\n\n📧 **Instruções detalhadas** são enviadas previamente\n📞 **Dúvidas**: (27) 3246-8200',
                'keywords': ['audiencia', 'virtual', 'presencial', 'online', 'reunião', 'zoom'],
                'confidence': 0.9
            },
            'documentos': {
                'response': '📄 **Documentos e Certidões**\n\n**📜 Disponíveis:**\n• Certidões de objeto e pé\n• Cartas de sentença\n• Documentos processuais\n• Cópias autenticadas\n\n**🌐 Alguns serviços online**\n**🏛️ Atendimento presencial** para casos específicos\n\n📞 **Solicitar**: (27) 3246-8200\n💰 **Taxas**: Consulte valores no atendimento',
                'keywords': ['documento', 'documentos', 'certidao', 'certidão', 'papel', 'carta', 'cópia'],
                'confidence': 0.85
            },
            'mediacao': {
                'response': '🤝 **Mediação e Conciliação**\n\n**🎯 Objetivo:**\n• Resolução amigável de conflitos\n• Acordo entre as partes\n• Processo mais rápido\n\n**👩‍⚖️ Equipe qualificada** de mediadores\n**📅 Agendamento disponível**\n**💼 Casos cíveis** em geral\n\n📞 **Agendar**: (27) 3246-8200\n🌐 **Mais informações** em nosso site',
                'keywords': ['mediacao', 'conciliação', 'acordo', 'resolver', 'mediação', 'conciliar'],
                'confidence': 0.85
            }
        }
    
    def can_handle(self, message: str, context: List[ChatMessage]) -> bool:
        message_lower = message.lower()
        for response_data in self.responses.values():
            if any(keyword in message_lower for keyword in response_data['keywords']):
                return True
        return False
    
    def generate_response(self, message: str, context: List[ChatMessage]) -> ChatResponse:
        start_time = time.time()
        message_lower = message.lower()
        
        best_match = None
        best_score = 0
        
        for key, response_data in self.responses.items():
            matches = sum(1 for keyword in response_data['keywords'] if keyword in message_lower)
            score = matches / len(response_data['keywords'])
            
            if score > best_score:
                best_score = score
                best_match = response_data
        
        if best_match:
            response_time = time.time() - start_time
            return ChatResponse(
                content=best_match['response'],
                response_type=ResponseType.PREDEFINED,
                response_time=response_time,
                confidence_score=best_match['confidence'] * best_score,
                context_used=False,
                suggestions=self._generate_suggestions(message_lower),
                metadata={"strategy": "predefined", "match_score": best_score}
            )
        
        return None
    
    def _generate_suggestions(self, message: str) -> List[str]:
        """Generate contextual suggestions based on the message"""
        suggestions = []
        
        if 'processo' in message:
            suggestions.extend(["Agendamento de atendimento", "Documentos necessários"])
        elif 'horario' in message:
            suggestions.extend(["Informações de contato", "Localização"])
        elif 'contato' in message:
            suggestions.extend(["Horário de funcionamento", "Agendamento"])
        
        return suggestions[:3]  # Limit to 3 suggestions


class OpenAIStrategy(ResponseStrategy):
    """Strategy for OpenAI-powered responses with advanced prompt engineering"""
    
    def __init__(self, openai_client: Optional[OpenAI]):
        self.client = openai_client
        self.system_prompt = self._build_system_prompt()
    
    @property
    def priority(self) -> int:
        return 3
    
    def can_handle(self, message: str, context: List[ChatMessage]) -> bool:
        return self.client is not None
    
    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt for OpenAI"""
        return """Você é o assistente virtual especializado da 2ª Vara Cível de Cariacica do TJES.

IDENTIDADE E CONTEXTO:
• Assistente oficial da 2ª Vara Cível de Cariacica
• Especialista em direito civil e processos judiciais
• Comunicação profissional, acessível e empática

INFORMAÇÕES INSTITUCIONAIS:
📍 Endereço: Rua Expedito Garcia, s/n, Centro, Cariacica-ES, CEP: 29140-060
📞 Telefone: (27) 3246-8200
📧 Email: 2varacivel.cariacica@tjes.jus.br
⏰ Funcionamento: 12h às 18h, segunda a sexta-feira

COMPETÊNCIAS DA VARA:
• Ações cíveis (contratos, responsabilidade civil, direitos reais)
• Execuções de título extrajudicial
• Cumprimento de sentença
• Ações de cobrança e indenização
• Inventários e partilhas
• Interdições e tutelas
• Mediação e conciliação

SERVIÇOS PRIORITÁRIOS:
🔍 Consulta processual (online via TJES ou presencial)
📅 Agendamento com assessores (presencial/virtual)
📄 Solicitação de certidões e documentos
🤝 Serviços de mediação e conciliação
💻 Balcão virtual e atendimento online

DIRETRIZES DE ATENDIMENTO:
1. Seja sempre cordial, profissional e empático
2. Forneça informações precisas e atualizadas
3. Use formatação clara com emojis quando apropriado
4. Oriente sobre processos formais quando necessário
5. Sugira agendamento para questões complexas
6. Mantenha respostas concisas mas completas
7. Para urgências, indique contato telefônico imediato

AGENDAMENTOS ESPECÍFICOS:
• ASSESSORES: Disponível agendamento direto para orientações
• JUIZ: Apenas via petição formal através de advogado
• Para reunião com assessor, use: **[AGENDAR_REUNIAO_ASSESSOR]**

ORIENTAÇÕES ESPECIAIS:
• Dúvidas processuais específicas: consulta pelo número CNJ
• Prazos processuais: orientação com advogado
• Urgências: contato telefônico prioritário
• Documentação: verificar requisitos no atendimento

Mantenha sempre tom respeitoso e institucional, demonstrando conhecimento jurídico adequado."""

    def generate_response(self, message: str, context: List[ChatMessage]) -> ChatResponse:
        start_time = time.time()
        
        try:
            # Build conversation context
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add recent context (last 4 messages for efficiency)
            for msg in context[-4:]:
                messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
            
            # Add current user message
            messages.append({"role": "user", "content": message[:500]})  # Limit length
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=400,
                temperature=0.7,
                timeout=25,
                stream=False
            )
            
            response_time = time.time() - start_time
            
            if response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content.strip()
                tokens_used = response.usage.total_tokens if response.usage else 0
                
                return ChatResponse(
                    content=content,
                    response_type=ResponseType.OPENAI,
                    response_time=response_time,
                    confidence_score=0.85,  # OpenAI responses generally high confidence
                    context_used=len(context) > 0,
                    openai_tokens_used=tokens_used,
                    suggestions=self._extract_suggestions(content),
                    metadata={
                        "strategy": "openai",
                        "model": "gpt-4o",
                        "context_messages": len(context),
                        "tokens_used": tokens_used
                    }
                )
            
            return None
            
        except Exception as e:
            logging.error(f"OpenAI strategy error: {e}")
            return None
    
    def _extract_suggestions(self, content: str) -> List[str]:
        """Extract actionable suggestions from OpenAI response"""
        suggestions = []
        
        # Look for action markers in response
        if "[AGENDAR_REUNIAO_ASSESSOR]" in content:
            suggestions.append("Agendar reunião com assessor")
        if "[CONSULTAR_PROCESSO]" in content:
            suggestions.append("Consultar processo online")
        if "telefone" in content.lower():
            suggestions.append("Entrar em contato por telefone")
        
        return suggestions


class FallbackStrategy(ResponseStrategy):
    """Fallback strategy for unhandled messages"""
    
    @property
    def priority(self) -> int:
        return 10  # Lowest priority
    
    def can_handle(self, message: str, context: List[ChatMessage]) -> bool:
        return True  # Always can handle as fallback
    
    def generate_response(self, message: str, context: List[ChatMessage]) -> ChatResponse:
        start_time = time.time()
        
        fallback_content = """👋 **Olá! Sou o assistente virtual da 2ª Vara Cível de Cariacica.**

🔍 **Posso ajudar com:**
• Horário de funcionamento e localização
• Informações de contato
• Consulta processual
• Agendamento de atendimentos
• Audiências e procedimentos
• Documentos e certidões
• Mediação e conciliação

📞 **Para atendimento especializado**: (27) 3246-8200
📧 **Email**: 2varacivel.cariacica@tjes.jus.br
⏰ **Horário**: Segunda a Sexta, 12h às 18h

🤔 **Poderia reformular sua pergunta?** Isso me ajudará a fornecer informações mais precisas."""
        
        response_time = time.time() - start_time
        
        return ChatResponse(
            content=fallback_content,
            response_type=ResponseType.FALLBACK,
            response_time=response_time,
            confidence_score=0.5,
            context_used=False,
            fallback_reason="No specific strategy matched",
            suggestions=[
                "Horário de funcionamento",
                "Consulta processual",
                "Informações de contato",
                "Agendar atendimento"
            ],
            metadata={"strategy": "fallback"}
        )


class ConversationManager:
    """Manages conversation context and message history"""
    
    def __init__(self, max_context_messages: int = 10):
        self.conversations: Dict[str, List[ChatMessage]] = {}
        self.max_context_messages = max_context_messages
    
    def add_message(self, session_id: str, message: ChatMessage) -> None:
        """Add message to conversation context"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append(message)
        
        # Trim context if too long
        if len(self.conversations[session_id]) > self.max_context_messages:
            self.conversations[session_id] = self.conversations[session_id][-self.max_context_messages:]
    
    def get_context(self, session_id: str) -> List[ChatMessage]:
        """Get conversation context for session"""
        return self.conversations.get(session_id, [])
    
    def clear_context(self, session_id: str) -> None:
        """Clear conversation context for session"""
        if session_id in self.conversations:
            del self.conversations[session_id]
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a conversation session"""
        messages = self.conversations.get(session_id, [])
        
        if not messages:
            return {"message_count": 0, "duration": 0, "first_message": None, "last_message": None}
        
        first_msg = messages[0]
        last_msg = messages[-1]
        duration = (last_msg.timestamp - first_msg.timestamp).total_seconds()
        
        return {
            "message_count": len(messages),
            "duration": duration,
            "first_message": first_msg.timestamp.isoformat(),
            "last_message": last_msg.timestamp.isoformat(),
            "user_messages": len([m for m in messages if m.role == MessageRole.USER]),
            "assistant_messages": len([m for m in messages if m.role == MessageRole.ASSISTANT])
        }


class AnalyticsEngine:
    """Advanced analytics and performance tracking"""
    
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'response_types': {rt.value: 0 for rt in ResponseType},
            'average_response_time': 0.0,
            'confidence_scores': [],
            'errors': 0,
            'start_time': datetime.now(),
            'last_reset': datetime.now(),
            'session_count': 0,
            'openai_tokens_total': 0
        }
        self.daily_stats = {}
    
    def record_response(self, response: ChatResponse, session_id: str) -> None:
        """Record response metrics"""
        self.metrics['total_requests'] += 1
        self.metrics['response_types'][response.response_type.value] += 1
        self.metrics['confidence_scores'].append(response.confidence_score)
        self.metrics['openai_tokens_total'] += response.openai_tokens_used
        
        # Update average response time
        current_avg = self.metrics['average_response_time']
        total_requests = self.metrics['total_requests']
        self.metrics['average_response_time'] = (
            (current_avg * (total_requests - 1) + response.response_time) / total_requests
        )
        
        # Daily statistics
        today = datetime.now().date().isoformat()
        if today not in self.daily_stats:
            self.daily_stats[today] = {
                'requests': 0,
                'avg_confidence': 0.0,
                'response_types': {rt.value: 0 for rt in ResponseType}
            }
        
        self.daily_stats[today]['requests'] += 1
        self.daily_stats[today]['response_types'][response.response_type.value] += 1
    
    def record_error(self, error: str) -> None:
        """Record error occurrence"""
        self.metrics['errors'] += 1
        logging.error(f"Chatbot error recorded: {error}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        uptime = (datetime.now() - self.metrics['start_time']).total_seconds()
        avg_confidence = sum(self.metrics['confidence_scores']) / max(1, len(self.metrics['confidence_scores']))
        
        return {
            'total_requests': self.metrics['total_requests'],
            'uptime_seconds': uptime,
            'average_response_time': round(self.metrics['average_response_time'], 3),
            'average_confidence': round(avg_confidence, 3),
            'error_rate': self.metrics['errors'] / max(1, self.metrics['total_requests']),
            'success_rate': 1 - (self.metrics['errors'] / max(1, self.metrics['total_requests'])),
            'response_type_distribution': self.metrics['response_types'],
            'openai_tokens_used': self.metrics['openai_tokens_total'],
            'daily_stats': self.daily_stats
        }
    
    def reset_metrics(self) -> None:
        """Reset all metrics"""
        self.metrics = {
            'total_requests': 0,
            'response_types': {rt.value: 0 for rt in ResponseType},
            'average_response_time': 0.0,
            'confidence_scores': [],
            'errors': 0,
            'start_time': datetime.now(),
            'last_reset': datetime.now(),
            'session_count': 0,
            'openai_tokens_total': 0
        }
        self.daily_stats = {}


class RefinedChatbotService:
    """
    Refined Chatbot Service with advanced architecture
    Features: Strategy pattern, conversation management, analytics, and comprehensive error handling
    """
    
    def __init__(self):
        self.openai_client = self._initialize_openai()
        self.strategies = self._initialize_strategies()
        self.conversation_manager = ConversationManager()
        self.analytics = AnalyticsEngine()
        self.debug_mode = os.environ.get('CHATBOT_DEBUG', 'false').lower() == 'true'
        
        logging.info("Refined Chatbot Service initialized successfully")
    
    def _initialize_openai(self) -> Optional[OpenAI]:
        """Initialize OpenAI client with comprehensive error handling"""
        if not OPENAI_AVAILABLE:
            logging.warning("OpenAI library not available")
            return None
        
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key or not api_key.strip():
            logging.info("OpenAI API key not configured, using fallback responses")
            return None
        
        try:
            client = OpenAI(
                api_key=api_key,
                timeout=30.0,
                max_retries=2
            )
            
            # Test connection with minimal request
            test_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            
            logging.info("OpenAI client initialized and tested successfully")
            return client
            
        except Exception as e:
            logging.error(f"Failed to initialize OpenAI client: {e}")
            return None
    
    def _initialize_strategies(self) -> List[ResponseStrategy]:
        """Initialize response strategies in priority order"""
        strategies = [
            MeetingSchedulingStrategy(),
            PredefinedResponseStrategy(),
            FallbackStrategy()  # Always include fallback
        ]
        
        # Add OpenAI strategy if available
        if self.openai_client:
            strategies.insert(-1, OpenAIStrategy(self.openai_client))  # Before fallback
        
        # Sort by priority
        strategies.sort(key=lambda s: s.priority)
        
        logging.info(f"Initialized {len(strategies)} response strategies")
        return strategies
    
    def get_response(self, message: str, session_id: str = "default") -> str:
        """
        Main method to get chatbot response
        Returns the response content as string for backward compatibility
        """
        response = self.get_detailed_response(message, session_id)
        return response.content
    
    def get_detailed_response(self, message: str, session_id: str = "default") -> ChatResponse:
        """
        Get detailed chatbot response with full metadata
        """
        start_time = time.time()
        
        if not message or not message.strip():
            return ChatResponse(
                content="Por favor, digite sua pergunta para que eu possa ajudá-lo.",
                response_type=ResponseType.FALLBACK,
                response_time=time.time() - start_time,
                confidence_score=1.0,
                fallback_reason="Empty message"
            )
        
        try:
            # Sanitize and prepare message
            clean_message = message.strip()[:1000]  # Reasonable limit
            
            # Get conversation context
            context = self.conversation_manager.get_context(session_id)
            
            # Add user message to context
            user_message = ChatMessage(
                content=clean_message,
                role=MessageRole.USER,
                timestamp=datetime.now()
            )
            self.conversation_manager.add_message(session_id, user_message)
            
            # Try strategies in priority order
            response = None
            for strategy in self.strategies:
                if strategy.can_handle(clean_message, context):
                    if self.debug_mode:
                        logging.info(f"Using strategy: {strategy.__class__.__name__}")
                    
                    response = strategy.generate_response(clean_message, context)
                    if response:
                        break
            
            # Fallback should never fail, but just in case
            if not response:
                response = ChatResponse(
                    content="Desculpe, ocorreu um erro temporário. Tente novamente ou entre em contato pelo telefone (27) 3246-8200.",
                    response_type=ResponseType.FALLBACK,
                    response_time=time.time() - start_time,
                    confidence_score=0.5,
                    fallback_reason="All strategies failed"
                )
            
            # Add assistant response to context
            assistant_message = ChatMessage(
                content=response.content,
                role=MessageRole.ASSISTANT,
                timestamp=datetime.now(),
                metadata=response.metadata
            )
            self.conversation_manager.add_message(session_id, assistant_message)
            
            # Record analytics
            self.analytics.record_response(response, session_id)
            
            return response
            
        except Exception as e:
            error_msg = f"Critical error in chatbot: {str(e)}"
            logging.error(error_msg)
            self.analytics.record_error(error_msg)
            
            return ChatResponse(
                content="Desculpe, ocorreu um erro temporário. Por favor, tente novamente ou entre em contato pelo telefone (27) 3246-8200.",
                response_type=ResponseType.FALLBACK,
                response_time=time.time() - start_time,
                confidence_score=0.3,
                fallback_reason=f"Exception: {str(e)}"
            )
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        messages = self.conversation_manager.get_context(session_id)
        return [msg.to_dict() for msg in messages]
    
    def clear_conversation(self, session_id: str) -> None:
        """Clear conversation history for a session"""
        self.conversation_manager.clear_context(session_id)
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics data"""
        return self.analytics.get_performance_summary()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        analytics = self.get_analytics()
        
        # Determine health status
        if analytics['error_rate'] == 0:
            status = 'excellent'
        elif analytics['success_rate'] > 0.95:
            status = 'good'
        elif analytics['success_rate'] > 0.8:
            status = 'fair'
        else:
            status = 'poor'
        
        return {
            'status': status,
            'openai_available': self.openai_client is not None,
            'strategies_count': len(self.strategies),
            'debug_mode': self.debug_mode,
            'analytics': analytics,
            'recommendations': self._generate_health_recommendations(analytics)
        }
    
    def _generate_health_recommendations(self, analytics: Dict[str, Any]) -> List[str]:
        """Generate health recommendations based on analytics"""
        recommendations = []
        
        if analytics['error_rate'] > 0.1:
            recommendations.append("High error rate detected - review system logs")
        
        if analytics['average_response_time'] > 3.0:
            recommendations.append("Response times are slower than optimal")
        
        if not self.openai_client:
            recommendations.append("OpenAI integration unavailable - using fallback responses")
        
        if analytics['total_requests'] == 0:
            recommendations.append("No requests processed yet - system ready")
        
        if analytics['average_confidence'] < 0.7:
            recommendations.append("Low confidence scores - review response strategies")
        
        if not recommendations:
            recommendations.append("System performing optimally")
        
        return recommendations
    
    def enable_debug_mode(self) -> None:
        """Enable debug mode"""
        self.debug_mode = True
        logging.info("Debug mode enabled for refined chatbot")
    
    def disable_debug_mode(self) -> None:
        """Disable debug mode"""
        self.debug_mode = False
        logging.info("Debug mode disabled for refined chatbot")
    
    def reset_analytics(self) -> None:
        """Reset analytics data"""
        self.analytics.reset_metrics()
        logging.info("Analytics data reset")


# Singleton instance for global access
_refined_chatbot_instance = None

def get_refined_chatbot() -> RefinedChatbotService:
    """Get singleton instance of refined chatbot service"""
    global _refined_chatbot_instance
    if _refined_chatbot_instance is None:
        _refined_chatbot_instance = RefinedChatbotService()
    return _refined_chatbot_instance


# Backward compatibility function
def get_chatbot_response(message: str, session_id: str = "default") -> str:
    """
    Backward compatible function for getting chatbot responses
    """
    try:
        chatbot = get_refined_chatbot()
        return chatbot.get_response(message, session_id)
    except Exception as e:
        logging.error(f"Error in get_chatbot_response: {e}")
        return "Desculpe, ocorreu um erro temporário. Tente novamente em alguns momentos."