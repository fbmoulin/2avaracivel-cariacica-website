"""
Chatbot Service - Modular Backend
AI-powered conversation management with OpenAI integration
"""
import openai
from flask import current_app
import logging
from typing import Dict, List, Any
import json

logger = logging.getLogger(__name__)


class ChatbotService:
    """Centralized chatbot service with OpenAI integration"""
    
    def __init__(self):
        self.predefined_responses = {
            'horario': 'O horário de funcionamento da 2ª Vara Cível de Cariacica é de segunda a sexta-feira, das 12h às 18h.',
            'endereco': 'A 2ª Vara Cível de Cariacica está localizada na Av. Meridional, 211 - Alto Lage, Cariacica/ES.',
            'telefone': 'O telefone para contato é (27) 3246-8200.',
            'servicos': 'Oferecemos serviços de consulta processual, agendamento de audiências, balcão virtual e atendimento presencial.',
            'agendamento': 'Para agendar um atendimento, utilize nosso sistema de agendamento online ou compareça presencialmente.',
            'processos': 'Para consultar processos, utilize nosso sistema de consulta processual com número do processo e CPF.',
            'audiencias': 'Informações sobre audiências podem ser consultadas no sistema do TJES ou presencialmente no cartório.'
        }
    
    def get_response(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """Get chatbot response for user message"""
        try:
            # Check for predefined responses first
            predefined_response = self._check_predefined_responses(message)
            if predefined_response:
                return {
                    'message': predefined_response,
                    'response_type': 'predefined',
                    'confidence': 0.9,
                    'suggestions': self._get_suggestions(message)
                }
            
            # Use OpenAI for complex queries
            if current_app.config.get('OPENAI_API_KEY'):
                openai_response = self._get_openai_response(message)
                if openai_response:
                    return openai_response
            
            # Fallback response
            return {
                'message': 'Desculpe, não consegui entender sua pergunta. Posso ajudá-lo com informações sobre horários, endereço, serviços ou agendamentos.',
                'response_type': 'fallback',
                'confidence': 0.3,
                'suggestions': ['Horário de funcionamento', 'Endereço', 'Telefone', 'Serviços disponíveis']
            }
            
        except Exception as e:
            logger.error(f"Chatbot service error: {e}")
            return {
                'message': 'Ocorreu um erro temporário. Tente novamente em alguns instantes.',
                'response_type': 'error',
                'confidence': 0.1,
                'suggestions': []
            }
    
    def _check_predefined_responses(self, message: str) -> str:
        """Check if message matches predefined responses"""
        message_lower = message.lower()
        
        keywords_map = {
            'horario': ['horario', 'horário', 'funcionamento', 'aberto', 'fecha', 'abre'],
            'endereco': ['endereco', 'endereço', 'localização', 'onde', 'local', 'localizado'],
            'telefone': ['telefone', 'contato', 'fone', 'ligar', 'número'],
            'servicos': ['serviços', 'servicos', 'atendimento', 'o que fazem'],
            'agendamento': ['agendar', 'agendamento', 'marcar', 'horário'],
            'processos': ['processo', 'processos', 'consultar', 'andamento'],
            'audiencias': ['audiência', 'audiencias', 'audiencia', 'julgamento']
        }
        
        for key, keywords in keywords_map.items():
            if any(keyword in message_lower for keyword in keywords):
                return self.predefined_responses.get(key)
        
        return None
    
    def _get_openai_response(self, message: str) -> Dict[str, Any]:
        """Get response from OpenAI API"""
        try:
            openai.api_key = current_app.config.get('OPENAI_API_KEY')
            
            system_prompt = """Você é um assistente virtual da 2ª Vara Cível de Cariacica. 
            Forneça informações precisas e úteis sobre:
            - Horário: Segunda a sexta, 12h às 18h
            - Endereço: Av. Meridional, 211 - Alto Lage, Cariacica/ES
            - Telefone: (27) 3246-8200
            - Serviços: consulta processual, agendamentos, balcão virtual
            
            Seja conciso, profissional e útil. Limite respostas a 100 palavras."""
            
            response = openai.ChatCompletion.create(
                model=current_app.config.get('OPENAI_MODEL', 'gpt-4'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=current_app.config.get('OPENAI_MAX_TOKENS', 150),
                temperature=current_app.config.get('OPENAI_TEMPERATURE', 0.7)
            )
            
            return {
                'message': response.choices[0].message.content.strip(),
                'response_type': 'openai',
                'confidence': 0.8,
                'suggestions': self._get_suggestions(message)
            }
            
        except Exception as e:
            logger.warning(f"OpenAI API error: {e}")
            return None
    
    def _get_suggestions(self, message: str) -> List[str]:
        """Get contextual suggestions based on message"""
        suggestions = [
            'Horário de funcionamento',
            'Como chegar ao fórum',
            'Agendar atendimento',
            'Consultar processo'
        ]
        
        message_lower = message.lower()
        
        if 'horario' in message_lower or 'funcionamento' in message_lower:
            return ['Endereço do fórum', 'Telefone para contato', 'Serviços disponíveis']
        elif 'endereco' in message_lower or 'onde' in message_lower:
            return ['Horário de funcionamento', 'Como chegar', 'Telefone']
        elif 'processo' in message_lower:
            return ['Como consultar processo', 'Agendar atendimento', 'Status processual']
        
        return suggestions[:3]