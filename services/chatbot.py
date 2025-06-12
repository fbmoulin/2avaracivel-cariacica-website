import os
import json
import logging
from openai import OpenAI
from services.integration_service import RetryManager, with_integration
import time

class ChatbotService:
    """Service for handling chatbot interactions"""
    
    def __init__(self):
        self.openai_client = None
        self.setup_openai()
        self.predefined_responses = self.load_predefined_responses()
    
    def setup_openai(self):
        """Initialize OpenAI client if API key is available"""
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            try:
                self.openai_client = OpenAI(api_key=api_key)
                logging.info("OpenAI client initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        else:
            logging.info("OpenAI API key not found, using predefined responses")
    
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
                'response': 'Informações sobre audiências:\n🎥 Virtuais: Link enviado por email\n🏛️ Presenciais: Compareça no horário marcado\n📅 Reagendamento: Entre em contato conosco\n\n✉️ Instruções detalhadas são enviadas por email.',
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
    
    def get_response(self, user_message):
        """Get chatbot response for user message"""
        try:
            # Check for predefined responses first
            predefined_response = self.find_predefined_response(user_message)
            if predefined_response:
                return predefined_response
            
            # Use OpenAI if available
            if self.openai_client:
                return self.get_openai_response(user_message)
            
            # Default response
            return self.get_default_response()
            
        except Exception as e:
            logging.error(f"Error getting chatbot response: {e}")
            return "Desculpe, ocorreu um erro. Tente novamente ou entre em contato conosco diretamente."
    
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
• Agendamento de atendimento
• Audiências presenciais e virtuais
• Solicitação de certidões
• Balcão virtual
• Serviços de mediação

INSTRUÇÕES:
• Seja sempre cordial e profissional
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
                return response.choices[0].message.content.strip()
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
