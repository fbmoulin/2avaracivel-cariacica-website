"""
Optimized Chatbot Service for 2ª Vara Cível de Cariacica
Enhanced with advanced conversation management and performance optimization
"""
import os
import time
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
import openai

logger = logging.getLogger(__name__)

class ConversationContext:
    """Enhanced conversation context management"""
    
    def __init__(self, session_id: str, max_history: int = 10):
        self.session_id = session_id
        self.max_history = max_history
        self.messages: List[Dict] = []
        self.metadata = {
            'created_at': datetime.now(timezone.utc),
            'last_activity': datetime.now(timezone.utc),
            'message_count': 0,
            'topics_discussed': set(),
            'user_preferences': {}
        }
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add message to conversation history"""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metadata': metadata or {}
        }
        
        self.messages.append(message)
        self.metadata['message_count'] += 1
        self.metadata['last_activity'] = datetime.now(timezone.utc)
        
        # Keep only recent messages
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def get_context_summary(self) -> str:
        """Generate context summary for AI"""
        if not self.messages:
            return "Nova conversa iniciada."
        
        recent_topics = list(self.metadata['topics_discussed'])[-3:]
        return f"Conversa em andamento. Tópicos recentes: {', '.join(recent_topics) if recent_topics else 'geral'}"
    
    def extract_topics(self, message: str):
        """Extract discussion topics from message"""
        topics_keywords = {
            'processo': ['processo', 'processual', 'número'],
            'agendamento': ['agendamento', 'marcar', 'reunião', 'encontro'],
            'contato': ['contato', 'telefone', 'email', 'endereço'],
            'horario': ['horário', 'funcionamento', 'atendimento'],
            'documentos': ['documento', 'certidão', 'comprovante'],
            'informacoes': ['informação', 'dúvida', 'esclarecimento']
        }
        
        message_lower = message.lower()
        for topic, keywords in topics_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                self.metadata['topics_discussed'].add(topic)

class ResponseStrategy:
    """Base class for response strategies"""
    
    def __init__(self, name: str, confidence_threshold: float = 0.7):
        self.name = name
        self.confidence_threshold = confidence_threshold
    
    def can_handle(self, message: str, context: ConversationContext) -> float:
        """Return confidence score (0-1) for handling this message"""
        raise NotImplementedError
    
    def generate_response(self, message: str, context: ConversationContext) -> Tuple[str, Dict]:
        """Generate response with metadata"""
        raise NotImplementedError

class PredefinedResponseStrategy(ResponseStrategy):
    """Handle predefined responses for common questions"""
    
    def __init__(self):
        super().__init__("predefined", 0.8)
        self.responses = {
            'horario': {
                'keywords': ['horário', 'funcionamento', 'aberto', 'fechado', 'atendimento'],
                'response': '''🕐 **Horário de Funcionamento da 2ª Vara Cível de Cariacica:**

**Segunda a Sexta-feira:** 12h às 19h
**Sábados, Domingos e Feriados:** Fechado

📍 **Localização:** Fórum de Cariacica
📞 **Telefone:** (27) 3636-9500
📧 **Email:** 2civelcariacica@tjes.jus.br

Posso ajudar com mais informações sobre nossos serviços?'''
            },
            'contato': {
                'keywords': ['contato', 'telefone', 'email', 'endereço', 'localização'],
                'response': '''📞 **Informações de Contato - 2ª Vara Cível de Cariacica:**

📍 **Endereço:** Fórum de Cariacica - ES
📞 **Telefone:** (27) 3636-9500
📧 **Email:** 2civelcariacica@tjes.jus.br
🌐 **Site:** Portal do TJES

**Horário de Atendimento:**
Segunda a Sexta: 12h às 19h

Como posso ajudar com mais informações?'''
            },
            'processo': {
                'keywords': ['processo', 'consultar', 'número', 'andamento'],
                'response': '''⚖️ **Consulta de Processos:**

Para consultar o andamento do seu processo, você pode:

1. **Consulta Online:** Use nosso sistema de consulta processual
2. **TJES:** Acesse o portal do Tribunal de Justiça do ES
3. **Presencial:** Venha ao Fórum nos horários de atendimento

**Informações necessárias:**
- Número do processo
- Nome das partes
- CPF/CNPJ

Precisa de ajuda para localizar um processo específico?'''
            },
            'agendamento': {
                'keywords': ['agendar', 'marcar', 'reunião', 'atendimento', 'assessor'],
                'response': '''📅 **Agendamento com Assessor:**

Você pode agendar atendimento conosco através de:

**Tipos de Atendimento Disponíveis:**
🏛️ **Presencial** - No Fórum de Cariacica
💻 **Videoconferência** - Reunião online
📋 **Gabinete** - Atendimento especializado
📄 **Cartório** - Serviços documentais

**Para agendar:** Use nossa página de agendamento ou entre em contato.

Gostaria que eu ajude você a agendar um atendimento?'''
            },
            'servicos': {
                'keywords': ['serviços', 'oferece', 'disponível', 'fazer'],
                'response': '''🏛️ **Serviços da 2ª Vara Cível de Cariacica:**

**Principais Serviços:**
• Consulta de processos cíveis
• Agendamento com assessores
• Balcão virtual (TJES)
• Informações processuais
• Orientações jurídicas básicas

**Áreas de Atuação:**
• Direito Civil em geral
• Contratos e obrigações
• Responsabilidade civil
• Direitos reais

Em que posso ajudar especificamente?'''
            }
        }
    
    def can_handle(self, message: str, context: ConversationContext) -> float:
        message_lower = message.lower()
        max_confidence = 0.0
        
        for category, data in self.responses.items():
            keyword_matches = sum(1 for keyword in data['keywords'] if keyword in message_lower)
            if keyword_matches > 0:
                confidence = min(0.9, keyword_matches / len(data['keywords']) + 0.3)
                max_confidence = max(max_confidence, confidence)
        
        return max_confidence
    
    def generate_response(self, message: str, context: ConversationContext) -> Tuple[str, Dict]:
        message_lower = message.lower()
        best_response = ""
        best_category = ""
        best_score = 0.0
        
        for category, data in self.responses.items():
            keyword_matches = sum(1 for keyword in data['keywords'] if keyword in message_lower)
            if keyword_matches > 0:
                score = keyword_matches / len(data['keywords'])
                if score > best_score:
                    best_score = score
                    best_response = data['response']
                    best_category = category
        
        metadata = {
            'strategy': self.name,
            'category': best_category,
            'confidence_score': 'high' if best_score > 0.7 else 'medium',
            'keywords_matched': best_score
        }
        
        return best_response, metadata

class OpenAIResponseStrategy(ResponseStrategy):
    """Handle complex queries using OpenAI"""
    
    def __init__(self):
        super().__init__("openai", 0.6)
        self.client = None
        self.api_available = False
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                openai.api_key = api_key
                self.client = openai
                self.api_available = True
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.api_available = False
        else:
            logger.warning("OpenAI API key not found")
    
    def can_handle(self, message: str, context: ConversationContext) -> float:
        if not self.api_available:
            return 0.0
        
        # Handle complex legal questions, specific cases, or when other strategies fail
        complex_indicators = [
            len(message.split()) > 15,  # Longer messages
            any(word in message.lower() for word in ['como', 'quando', 'onde', 'porque', 'qual']),
            'específico' in message.lower(),
            'detalhes' in message.lower()
        ]
        
        return 0.7 if any(complex_indicators) else 0.4
    
    def generate_response(self, message: str, context: ConversationContext) -> Tuple[str, Dict]:
        if not self.api_available:
            return self._fallback_response(), {'strategy': 'openai_fallback', 'error': 'API not available'}
        
        try:
            start_time = time.time()
            
            system_prompt = """Você é um assistente virtual da 2ª Vara Cível de Cariacica, Espírito Santo.

INSTRUÇÕES IMPORTANTES:
- Forneça informações precisas e úteis sobre processos cíveis
- Seja profissional, educado e acessível
- Use linguagem clara e evite jargões excessivos
- Quando não souber algo específico, oriente o usuário a entrar em contato
- Mantenha respostas concisas mas completas
- Use emojis moderadamente para melhor apresentação

INFORMAÇÕES DA VARA:
- Horário: Segunda a Sexta, 12h às 19h
- Telefone: (27) 3636-9500
- Email: 2civelcariacica@tjes.jus.br
- Localização: Fórum de Cariacica - ES

Responda sempre em português brasileiro."""
            
            # Prepare conversation context
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add recent conversation history
            for msg in context.messages[-3:]:  # Last 3 messages for context
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
            
            # Add current user message
            messages.append({"role": "user", "content": message})
            
            response = self.client.ChatCompletion.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                timeout=10
            )
            
            processing_time = time.time() - start_time
            
            ai_response = response.choices[0].message.content.strip()
            
            metadata = {
                'strategy': self.name,
                'processing_time': f"{processing_time:.2f}s",
                'confidence_score': 'high',
                'model': 'gpt-4o',
                'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else 'unknown'
            }
            
            return ai_response, metadata
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._fallback_response(), {
                'strategy': 'openai_fallback',
                'error': str(e),
                'confidence_score': 'low'
            }
    
    def _fallback_response(self) -> str:
        return """Obrigado pela sua pergunta! Para melhor atendimento sobre questões específicas, recomendo:

📞 **Contato direto:** (27) 3636-9500
📧 **Email:** 2civelcariacica@tjes.jus.br
🕐 **Horário:** Segunda a Sexta, 12h às 19h

Nossa equipe terá prazer em ajudar com informações detalhadas sobre seu caso.

Posso ajudar com outras informações gerais sobre nossos serviços?"""

class FallbackResponseStrategy(ResponseStrategy):
    """Handle cases when no other strategy applies"""
    
    def __init__(self):
        super().__init__("fallback", 0.1)
    
    def can_handle(self, message: str, context: ConversationContext) -> float:
        return 0.1  # Always available as last resort
    
    def generate_response(self, message: str, context: ConversationContext) -> Tuple[str, Dict]:
        responses = [
            """Obrigado por entrar em contato! Para melhor atendimento, posso ajudar com:

🏛️ **Informações sobre a 2ª Vara Cível**
📞 **Contatos e horários de funcionamento**
⚖️ **Orientações sobre consulta de processos**
📅 **Agendamento de atendimentos**

Como posso ajudar você hoje?""",
            
            """Estou aqui para ajudar! Posso fornecer informações sobre:

• Horários de funcionamento
• Contatos da vara
• Consulta de processos
• Agendamento com assessores
• Serviços disponíveis

Digite sua dúvida ou escolha um dos tópicos acima.""",
            
            """Para atendimento personalizado sobre sua questão específica:

📞 **Telefone:** (27) 3636-9500
📧 **Email:** 2civelcariacica@tjes.jus.br
🕐 **Horário:** Segunda a Sexta, 12h às 19h

Ou posso ajudar com informações gerais sobre nossos serviços. O que você gostaria de saber?"""
        ]
        
        # Simple rotation based on message count
        response_index = context.metadata['message_count'] % len(responses)
        
        metadata = {
            'strategy': self.name,
            'confidence_score': 'low',
            'response_type': 'general_help'
        }
        
        return responses[response_index], metadata

class OptimizedChatbotService:
    """Enhanced chatbot service with multiple response strategies"""
    
    def __init__(self):
        self.strategies = [
            PredefinedResponseStrategy(),
            OpenAIResponseStrategy(),
            FallbackResponseStrategy()
        ]
        self.conversations: Dict[str, ConversationContext] = {}
        self.analytics = {
            'total_messages': 0,
            'strategy_usage': {},
            'session_count': 0,
            'avg_response_time': 0.0
        }
        
        logger.info("Optimized Chatbot Service initialized with %d strategies", len(self.strategies))
    
    def get_or_create_conversation(self, session_id: str) -> ConversationContext:
        """Get existing conversation or create new one"""
        if session_id not in self.conversations:
            self.conversations[session_id] = ConversationContext(session_id)
            self.analytics['session_count'] += 1
            
            # Clean up old conversations (keep last 100)
            if len(self.conversations) > 100:
                oldest_sessions = sorted(
                    self.conversations.keys(),
                    key=lambda x: self.conversations[x].metadata['last_activity']
                )[:50]
                for old_session in oldest_sessions:
                    del self.conversations[old_session]
        
        return self.conversations[session_id]
    
    def process_message(self, message: str, session_id: str = None) -> Dict:
        """Process user message and return response with metadata"""
        start_time = time.time()
        
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
        
        # Get conversation context
        conversation = self.get_or_create_conversation(session_id)
        conversation.extract_topics(message)
        
        # Find best strategy
        best_strategy = None
        best_confidence = 0.0
        
        for strategy in self.strategies:
            confidence = strategy.can_handle(message, conversation)
            if confidence > best_confidence:
                best_confidence = confidence
                best_strategy = strategy
        
        # Generate response
        if best_strategy:
            response_text, response_metadata = best_strategy.generate_response(message, conversation)
        else:
            # Fallback to last strategy
            response_text, response_metadata = self.strategies[-1].generate_response(message, conversation)
            response_metadata['fallback_used'] = True
        
        # Update conversation
        conversation.add_message('user', message)
        conversation.add_message('assistant', response_text, response_metadata)
        
        processing_time = time.time() - start_time
        
        # Update analytics
        self.analytics['total_messages'] += 1
        strategy_name = response_metadata.get('strategy', 'unknown')
        self.analytics['strategy_usage'][strategy_name] = self.analytics['strategy_usage'].get(strategy_name, 0) + 1
        
        # Update average response time
        prev_avg = self.analytics['avg_response_time']
        total_msgs = self.analytics['total_messages']
        self.analytics['avg_response_time'] = (prev_avg * (total_msgs - 1) + processing_time) / total_msgs
        
        return {
            'response': response_text,
            'session_id': session_id,
            'processing_time': f"{processing_time:.3f}s",
            'metadata': {
                **response_metadata,
                'conversation_length': len(conversation.messages),
                'topics_discussed': list(conversation.metadata['topics_discussed'])
            }
        }
    
    def get_analytics(self) -> Dict:
        """Get service analytics"""
        return {
            'service_stats': self.analytics,
            'active_conversations': len(self.conversations),
            'strategies_available': len(self.strategies),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def cleanup_old_conversations(self, max_age_hours: int = 24):
        """Clean up old conversations"""
        cutoff_time = datetime.now(timezone.utc).timestamp() - (max_age_hours * 3600)
        
        old_sessions = [
            session_id for session_id, conv in self.conversations.items()
            if conv.metadata['last_activity'].timestamp() < cutoff_time
        ]
        
        for session_id in old_sessions:
            del self.conversations[session_id]
        
        logger.info(f"Cleaned up {len(old_sessions)} old conversations")

# Global service instance
chatbot_service = OptimizedChatbotService()

def get_chatbot_response(message: str, session_id: str = None) -> Dict:
    """Main function to get chatbot response"""
    return chatbot_service.process_message(message, session_id)

def get_chatbot_analytics() -> Dict:
    """Get chatbot analytics"""
    return chatbot_service.get_analytics()