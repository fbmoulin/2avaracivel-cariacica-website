import os
import json
import logging
import time
import re
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional, Any
from openai import OpenAI
from services.integration_service import RetryManager, with_integration, integration_service

class ChatbotService:
    """Enhanced Service for handling chatbot interactions with debugging capabilities"""
    
    def __init__(self):
        self.openai_client = None
        self.debug_mode = os.environ.get('CHATBOT_DEBUG', 'false').lower() == 'true'
        self.performance_metrics = {
            'total_requests': 0,
            'openai_requests': 0,
            'fallback_responses': 0,
            'errors': 0,
            'average_response_time': 0,
            'last_error': None,
            'start_time': datetime.now()
        }
        self.setup_openai()
        self.predefined_responses = self.load_predefined_responses()
        self.conversation_context = []
    
    def setup_openai(self):
        """Initialize OpenAI client with robust error handling"""
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key and api_key.strip():
            try:
                self.openai_client = OpenAI(
                    api_key=api_key,
                    timeout=30.0,
                    max_retries=3
                )
                # Test connection
                self._test_openai_connection()
                logging.info("OpenAI client initialized and tested successfully")
            except Exception as e:
                logging.error(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        else:
            logging.info("OpenAI API key not available, using predefined responses")
    
    def _test_openai_connection(self):
        """Test OpenAI connection with minimal request"""
        if self.openai_client:
            try:
                self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1
                )
            except Exception as e:
                logging.warning(f"OpenAI connection test failed: {e}")
                raise
    
    def load_predefined_responses(self):
        """Load predefined responses for common questions"""
        return {
            'horario': {
                'response': 'A 2ª Vara Cível de Cariacica funciona das 12h às 18h, de segunda a sexta-feira.',
                'keywords': ['horario', 'funcionamento', 'abertura', 'fechamento', 'horário']
            },
            'endereco': {
                'response': 'A 2ª Vara Cível de Cariacica está localizada na Rua Expedito Garcia, s/n, Centro, Cariacica - ES, CEP: 29140-060.',
                'keywords': ['endereco', 'localização', 'onde', 'fica', 'endereço', 'local']
            },
            'telefone': {
                'response': 'Para contato:\n📞 Telefone: (27) 3246-8200\n📧 Email: 2varacivel.cariacica@tjes.jus.br\n💬 WhatsApp: Disponível pelo telefone principal',
                'keywords': ['telefone', 'contato', 'ligar', 'email', 'whatsapp']
            },
            'processo': {
                'response': 'Para consultar seu processo:\n1. Acesse a consulta processual em nosso site\n2. Digite o número do processo no formato CNJ\n3. Ou consulte no portal do TJES: www.tjes.jus.br\n\n📋 Tenha em mãos o número completo do processo.',
                'keywords': ['processo', 'consulta', 'andamento', 'número', 'cnj']
            },
            'audiencia': {
                'response': 'Informações sobre audiências:\n🎥 Virtuais: Realizadas pelo app Zoom, link enviado por email\n🏛️ Presenciais: Compareça no horário marcado\n📅 Reagendamento: Entre em contato conosco\n\n✉️ Instruções detalhadas são enviadas por email.',
                'keywords': ['audiencia', 'virtual', 'presencial', 'online', 'reunião']
            },
            'agendamento': {
                'response': 'Para agendar atendimento:\n🌐 Online: Acesse nossa página de agendamento\n📞 Telefone: (27) 3246-8200\n⏰ Horário: Das 12h às 18h\n\n📝 Tenha seus documentos em mãos.',
                'keywords': ['agendamento', 'agendar', 'marcar', 'atendimento', 'horário']
            },
            'documentos': {
                'response': 'Solicitação de documentos:\n📜 Certidões e documentos disponíveis\n🌐 Alguns serviços online\n🏛️ Atendimento presencial necessário para alguns casos\n\n📋 Documentos necessários: RG, CPF e comprovantes.',
                'keywords': ['documentos', 'certidão', 'certidões', 'segunda via', 'cópia']
            },
            'mediacao': {
                'response': 'Serviços de Mediação e Conciliação:\n🤝 Resolução amigável de conflitos\n📅 Agendamento disponível\n👩‍⚖️ Mediadores qualificados\n\n📞 Entre em contato para agendar.',
                'keywords': ['mediacao', 'conciliação', 'acordo', 'resolver', 'mediação']
            },
            'cumprimento': {
                'response': 'Cumprimento de Sentença:\n⚖️ Acompanhe pelo número do processo\n📋 Consulte andamentos no portal\n📞 Dúvidas: Entre em contato conosco\n\n🔍 Use a consulta processual para atualizações.',
                'keywords': ['cumprimento', 'sentença', 'execução', 'cobrança']
            },
            'prazos': {
                'response': 'Informações sobre Prazos:\n📅 Prazos processuais variam conforme o tipo\n⚖️ Consulte seu advogado para orientações específicas\n🔍 Acompanhe pelo sistema processual\n\n⏰ Fique atento aos prazos para não perder direitos.',
                'keywords': ['prazo', 'prazos', 'tempo', 'vencimento', 'data']
            },
            'agendamento': {
                'response': 'Agendamento de Atendimento:\n📅 Disponível de segunda a sexta, 12h às 18h\n📞 Telefone: (27) 3246-8200\n💻 Também pelo nosso portal online\n\n📝 Tenha em mãos documentos necessários para o atendimento.',
                'keywords': ['agendamento', 'agendar', 'marcar', 'atendimento', 'horario']
            },
            'documentos': {
                'response': 'Documentos e Certidões:\n📋 Certidões de objeto e pé\n📄 Cartas de sentença\n🏛️ Documentos processuais\n📞 Solicite pelo telefone (27) 3246-8200\n\n💰 Consulte taxas e prazos no atendimento.',
                'keywords': ['documento', 'documentos', 'certidao', 'certidão', 'papel', 'carta']
            },
            'reuniao_assessor': {
                'response': 'Agendamento de Reunião com Assessores:\n👥 Reuniões disponíveis com assessores judiciais\n📅 Horários: 12h às 18h, segunda a sexta\n⏰ Duração típica: 30-60 minutos\n🎥 Atendimento presencial ou virtual pelo app Zoom\n📋 Necessário: dados do processo e identificação\n\n🔗 Para agendar, clique aqui: [AGENDAR_REUNIAO_ASSESSOR]',
                'keywords': ['reuniao', 'reunião', 'assessor', 'assessores', 'conversar', 'falar', 'encontro', 'atendimento']
            },
            'reuniao_juiz': {
                'response': 'Solicitação de Audiência com o Juiz:\n⚖️ Audiências com o juiz são formais e processuais\n📋 Necessário: petição através de advogado\n📅 Agendamento através do sistema oficial\n💼 Requer representação legal\n\n📞 Para orientações: (27) 3246-8200',
                'keywords': ['juiz', 'juíz', 'magistrado', 'audiencia', 'encontrar', 'reunião', 'falar']
            },
            'agendamento_geral': {
                'response': 'Tipos de Agendamento Disponíveis:\n\n👥 **Reunião com Assessores**\n• Esclarecimentos sobre processos\n• Orientações gerais\n• Informações sobre andamentos\n• Presencial ou virtual pelo app Zoom\n\n⚖️ **Audiência com o Juiz**\n• Apenas através de petição\n• Representação obrigatória por advogado\n\n📅 **Atendimento Presencial**\n• Protocolo de documentos\n• Certidões e informações\n\n🔗 [AGENDAR_REUNIAO_ASSESSOR] para reunião com assessores',
                'keywords': ['agendar', 'agendamento', 'marcar', 'reunião', 'encontro', 'conversa', 'falar']
            }
        }
    
    def find_predefined_response(self, user_message):
        """Find matching predefined response based on keywords"""
        normalized_message = user_message.lower().strip()
        
        # Score each predefined response based on keyword matches
        best_match = None
        best_score = 0
        
        for category, data in self.predefined_responses.items():
            score = 0
            for keyword in data['keywords']:
                if keyword in normalized_message:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = data['response']
        
        return best_match if best_score > 0 else None
    
    def get_response(self, user_message, session_id=None):
        """Get chatbot response with comprehensive error handling"""
        if not user_message or not user_message.strip():
            return "Por favor, digite sua pergunta para que eu possa ajudá-lo."
        
        try:
            # Sanitize input
            user_message = user_message.strip()[:500]  # Limit message length
            
            # Check for meeting scheduling requests first
            meeting_response = self.handle_meeting_requests(user_message)
            if meeting_response:
                return meeting_response
            
            # Check for predefined responses
            predefined_response = self.find_predefined_response(user_message)
            if predefined_response:
                return self.process_special_actions(predefined_response)
            
            # Use OpenAI if available
            if self.openai_client:
                try:
                    return self.get_openai_response(user_message)
                except Exception as openai_error:
                    logging.error(f"OpenAI API error: {openai_error}")
                    # Fall back to default response if OpenAI fails
                    return self.get_default_response()
            
            # Default response when no OpenAI
            return self.get_default_response()
            
        except Exception as e:
            logging.error(f"Critical error in chatbot response: {e}")
            return "Desculpe, ocorreu um erro temporário. Por favor, tente novamente ou entre em contato pelo telefone (27) 3246-8200."
    
    @RetryManager.with_retry(max_attempts=2, backoff_factor=1.2, initial_delay=0.5)
    def get_openai_response(self, user_message):
        """Get response from OpenAI API optimized for production deployment"""
        try:
            start_time = time.time()
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """Você é o assistente virtual da 2ª Vara Cível de Cariacica do Tribunal de Justiça do Espírito Santo.

INFORMAÇÕES BÁSICAS:
• Horário: 12h às 18h, segunda a sexta-feira
• Endereço: Rua Expedito Garcia, s/n, Centro, Cariacica-ES, CEP: 29140-060
• Telefone: (27) 3246-8200
• Email: 2varacivel.cariacica@tjes.jus.br

COMPETÊNCIAS DA VARA:
• Ações cíveis em geral
• Execuções de título extrajudicial
• Cumprimento de sentença
• Ações de cobrança
• Contratos e responsabilidade civil
• Mediação e conciliação

SERVIÇOS DISPONÍVEIS:
• Consulta processual online
• Agendamento de reuniões com assessores
• Audiências presenciais e virtuais
• Solicitação de certidões
• Balcão virtual
• Serviços de mediação

AGENDAMENTO DE REUNIÕES:
• ASSESSORES: Reuniões diretas disponíveis para esclarecimentos, orientações sobre processos
• MODALIDADES: Presencial ou virtual pelo app Zoom
• JUIZ: Apenas por petição formal através de advogado, não agendamento direto
• Para reunião com assessor, ofereça: [AGENDAR_REUNIAO_ASSESSOR]

INSTRUÇÕES:
• Seja sempre cordial e profissional
• Para solicitações de reunião com assessores, forneça opção de agendamento direto
• Para solicitações de reunião com juiz, explique o processo formal necessário
• Forneça informações precisas e atualizadas
• Para dúvidas específicas sobre processos, oriente consulta pelo número CNJ
• Em caso de urgência, indique contato telefônico
• Use formatação clara com emojis quando apropriado
• Mantenha respostas concisas mas completas"""
                    },
                    {"role": "user", "content": user_message[:500]}
                ],
                max_tokens=300,  # Increased for more complete responses
                temperature=0.7,
                timeout=25,      # Balanced timeout for quality responses
                stream=False     # Ensure deployment compatibility
            )
            
            response_time = time.time() - start_time
            logging.info(f"OpenAI API response time: {response_time:.2f}s")
            
            # Validate response
            if response.choices and response.choices[0].message.content:
                ai_response = response.choices[0].message.content.strip()
                return self.process_special_actions(ai_response)
            else:
                logging.warning("Empty OpenAI response, using fallback")
                return self.get_fallback_response(user_message)
            
        except Exception as e:
            logging.error(f"OpenAI deployment error: {e}")
            return self.get_fallback_response(user_message)
    
    def get_fallback_response(self, user_message):
        """Fallback response when OpenAI is not available"""
        normalized_message = user_message.lower()
        
        # More comprehensive keyword matching
        if any(word in normalized_message for word in ['horario', 'hora', 'funcionamento', 'aberto']):
            return self.predefined_responses['horario']['response']
        elif any(word in normalized_message for word in ['endereco', 'endereço', 'localização', 'onde', 'local']):
            return self.predefined_responses['endereco']['response']
        elif any(word in normalized_message for word in ['telefone', 'contato', 'falar', 'ligar']):
            return self.predefined_responses['telefone']['response']
        elif any(word in normalized_message for word in ['processo', 'consulta', 'numero', 'cnj']):
            return self.predefined_responses['processo']['response']
        elif any(word in normalized_message for word in ['audiencia', 'audiência', 'zoom', 'virtual']):
            return self.predefined_responses['audiencia']['response']
        
        return self.get_default_response()
    
    def handle_meeting_requests(self, user_message):
        """Handle specific meeting scheduling requests"""
        normalized_message = user_message.lower().strip()
        
        # Check for specific meeting requests with assessors
        assessor_patterns = [
            r'.*quero.*reunião.*assessor.*',
            r'.*agendar.*encontro.*assessor.*',
            r'.*marcar.*conversa.*assessor.*',
            r'.*falar.*assessor.*',
            r'.*reunir.*assessor.*'
        ]
        
        # Check for judge meeting requests
        judge_patterns = [
            r'.*quero.*reunião.*juiz.*',
            r'.*agendar.*encontro.*juiz.*',
            r'.*marcar.*conversa.*juiz.*',
            r'.*falar.*juiz.*',
            r'.*reunir.*juiz.*',
            r'.*audiência.*juiz.*'
        ]
        
        for pattern in assessor_patterns:
            if re.search(pattern, normalized_message):
                return self.get_assessor_meeting_response()
        
        for pattern in judge_patterns:
            if re.search(pattern, normalized_message):
                return self.get_judge_meeting_response()
        
        return None
    
    def get_assessor_meeting_response(self):
        """Response for assessor meeting requests"""
        return """🤝 **Agendamento de Reunião com Assessores**

📋 **Informações Necessárias:**
• Nome completo
• CPF ou documento de identificação
• Número do processo (se houver)
• Assunto da reunião

📅 **Horários Disponíveis:**
• Segunda a sexta-feira: 12h às 18h
• Duração: 30 a 60 minutos
• Presencial ou virtual pelo app Zoom

⚡ **Para agendar agora:**
Clique no botão abaixo para iniciar o agendamento online

[INICIAR_AGENDAMENTO_ASSESSOR]

📞 **Ou ligue:** (27) 3246-8200"""
    
    def get_judge_meeting_response(self):
        """Response for judge meeting requests"""
        return """⚖️ **Audiência com o Juiz**

📋 **Processo Formal Obrigatório:**
• Requer petição através de advogado
• Não é possível agendamento direto
• Deve seguir procedimento judicial

💼 **Como Proceder:**
1. Consulte seu advogado
2. Advogado deve protocolar petição
3. Agendamento através do sistema oficial

📞 **Para orientações:**
• Telefone: (27) 3246-8200
• Email: 2varacivel.cariacica@tjes.jus.br

💡 **Alternativa:**
Para esclarecimentos gerais, posso agendar uma reunião com nossos assessores judiciais.

[AGENDAR_REUNIAO_ASSESSOR]"""
    
    def process_special_actions(self, response):
        """Process special action tokens in responses"""
        # Convert action tokens to interactive buttons/links
        if '[AGENDAR_REUNIAO_ASSESSOR]' in response:
            response = response.replace('[AGENDAR_REUNIAO_ASSESSOR]', 
                '🔗 **[Clique aqui para agendar reunião com assessores](/servicos/agendamento-assessor)**')
        
        if '[INICIAR_AGENDAMENTO_ASSESSOR]' in response:
            response = response.replace('[INICIAR_AGENDAMENTO_ASSESSOR]', 
                '🔗 **[AGENDAR REUNIÃO COM ASSESSOR](/servicos/agendamento-assessor)**')
        
        return response
    
    def get_default_response(self):
        """Default response when no specific match is found"""
        return """Olá! Sou o assistente virtual da 2ª Vara Cível de Cariacica. 
        Posso ajudar com informações sobre:
        • Horário de funcionamento
        • Localização e contato
        • Consulta processual
        • Agendamento de atendimento
        • Audiências
        • Documentos e certidões
        
        Como posso ajudá-lo hoje?"""


def get_chatbot_response(message: str, session_id: str = None) -> str:
    """
    Public function to get chatbot response
    Used by routes and external modules
    """
    try:
        chatbot = ChatbotService()
        return chatbot.get_response(message, session_id)
    except Exception as e:
        logging.error(f"Error in get_chatbot_response: {e}")
        return "Desculpe, ocorreu um erro temporário. Tente novamente em alguns momentos."
