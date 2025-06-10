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
            'horario': 'A 2ª Vara Cível de Cariacica funciona das 12h às 18h, de segunda a sexta-feira.',
            'endereco': 'A 2ª Vara Cível de Cariacica está localizada na Rua Expedito Garcia, s/n, Centro, Cariacica - ES.',
            'telefone': 'Para contato, ligue: (27) 3246-8200 ou envie um email para 2varacivel.cariacica@tjes.jus.br',
            'processo': 'Para consultar seu processo, você precisa do número no formato CNJ. Acesse a consulta processual em nosso site ou no portal do TJES.',
            'audiencia': 'As audiências podem ser realizadas presencialmente ou virtualmente. Você receberá as instruções por email ou pode consultar no portal do TJES.',
            'agendamento': 'Para agendar atendimento, acesse nossa página de agendamento ou ligue para (27) 3246-8200.',
            'documentos': 'Para solicitar certidões e outros documentos, acesse nossa seção de serviços ou compareça presencialmente com os documentos necessários.',
            'mediacao': 'Oferecemos serviços de mediação e conciliação. Entre em contato para mais informações sobre agendamento.',
            'cumprimento': 'Para questões sobre cumprimento de sentença, consulte o andamento do seu processo ou entre em contato conosco.',
            'execucao': 'Para informações sobre execução de título, acesse nossos serviços online ou consulte presencialmente.'
        }
    
    def get_response(self, user_message):
        """Get chatbot response for user message"""
        try:
            # Clean and normalize user message
            normalized_message = user_message.lower().strip()
            
            # Check for predefined responses first
            for keyword, response in self.predefined_responses.items():
                if keyword in normalized_message:
                    return response
            
            # Use OpenAI if available
            if self.openai_client:
                return self.get_openai_response(user_message)
            
            # Default response
            return self.get_default_response()
            
        except Exception as e:
            logging.error(f"Error getting chatbot response: {e}")
            return "Desculpe, ocorreu um erro. Tente novamente ou entre em contato conosco diretamente."
    
    @RetryManager.with_retry(max_attempts=3, backoff_factor=1.5, initial_delay=1.0)
    def get_openai_response(self, user_message):
        """Get response from OpenAI API with retry logic and error handling"""
        try:
            start_time = time.time()
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """Você é um assistente virtual da 2ª Vara Cível de Cariacica. 
                        Responda de forma educada, profissional e precisa sobre:
                        - Horário de funcionamento: 12h às 18h, segunda a sexta
                        - Endereço: Rua Expedito Garcia, s/n, Centro, Cariacica - ES
                        - Telefone: (27) 3246-8200
                        - Email: 2varacivel.cariacica@tjes.jus.br
                        - Serviços: consulta processual, agendamento, audiências, certidões, mediação
                        - Sempre mantenha um tom respeitoso e oficial
                        - Se não souber algo específico, direcione para contato direto
                        - Respostas devem ser concisas e úteis"""
                    },
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200,
                temperature=0.7,
                timeout=30  # 30 second timeout
            )
            
            response_time = time.time() - start_time
            logging.info(f"OpenAI API response time: {response_time:.2f}s")
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            return self.get_fallback_response(user_message)
    
    def get_fallback_response(self, user_message):
        """Fallback response when OpenAI is not available"""
        normalized_message = user_message.lower()
        
        # More comprehensive keyword matching
        if any(word in normalized_message for word in ['horario', 'hora', 'funcionamento', 'aberto']):
            return self.predefined_responses['horario']
        elif any(word in normalized_message for word in ['endereco', 'endereço', 'localização', 'onde', 'local']):
            return self.predefined_responses['endereco']
        elif any(word in normalized_message for word in ['telefone', 'contato', 'falar', 'ligar']):
            return self.predefined_responses['telefone']
        elif any(word in normalized_message for word in ['processo', 'consulta', 'numero', 'cnj']):
            return self.predefined_responses['processo']
        elif any(word in normalized_message for word in ['audiencia', 'audiência', 'zoom', 'virtual']):
            return self.predefined_responses['audiencia']
        elif any(word in normalized_message for word in ['agendamento', 'agendar', 'marcar']):
            return self.predefined_responses['agendamento']
        elif any(word in normalized_message for word in ['documento', 'certidao', 'certidão', 'papel']):
            return self.predefined_responses['documentos']
        elif any(word in normalized_message for word in ['mediacao', 'mediação', 'conciliacao', 'conciliação']):
            return self.predefined_responses['mediacao']
        
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
