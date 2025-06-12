import json
import os
from datetime import datetime
from models import NewsItem, db
from functools import lru_cache
import time

class ContentService:
    """Service for managing static content"""
    
    def __init__(self):
        self.data_path = 'data'
    
    def get_faq_data(self):
        """Load FAQ data from JSON file"""
        try:
            faq_file = os.path.join(self.data_path, 'faq.json')
            with open(faq_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_faq()
        except Exception as e:
            print(f"Error loading FAQ data: {e}")
            return self.get_default_faq()
    
    def get_default_faq(self):
        """Return default FAQ data"""
        return {
            "Horário e Funcionamento": [
                {
                    "pergunta": "Qual o horário de funcionamento da 2ª Vara Cível?",
                    "resposta": "A 2ª Vara Cível de Cariacica funciona das 12h às 18h, de segunda a sexta-feira."
                },
                {
                    "pergunta": "A vara funciona aos sábados?",
                    "resposta": "Não, a vara funciona apenas em dias úteis, de segunda a sexta-feira."
                }
            ],
            "Processos e Consultas": [
                {
                    "pergunta": "Como consultar um processo?",
                    "resposta": "Você pode consultar seu processo através do número CNJ no portal do TJES ou em nossa seção de consulta processual."
                },
                {
                    "pergunta": "Preciso de advogado para todas as ações?",
                    "resposta": "Não. Para ações de até 20 salários mínimos, você pode ingressar sem advogado. Acima desse valor, a representação por advogado é obrigatória."
                }
            ],
            "Audiências": [
                {
                    "pergunta": "Como participar de audiência virtual?",
                    "resposta": "Você receberá um link por email para participar via Zoom. Certifique-se de ter boa conexão de internet e ambiente adequado."
                },
                {
                    "pergunta": "Posso remarcar uma audiência?",
                    "resposta": "Remarcações devem ser solicitadas com antecedência mínima de 48 horas, através de peticionamento ou contato direto."
                }
            ]
        }
    
    def get_services_data(self):
        """Load services data from JSON file"""
        try:
            services_file = os.path.join(self.data_path, 'services.json')
            with open(services_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_services()
        except Exception as e:
            print(f"Error loading services data: {e}")
            return self.get_default_services()
    
    def get_default_services(self):
        """Return default services data"""
        return [
            {
                "nome": "Consulta Processual",
                "descricao": "Consulte o andamento de seus processos online",
                "icon": "search",
                "url": "/servicos/consulta-processual"
            },
            {
                "nome": "Agendamento",
                "descricao": "Agende seu atendimento presencial",
                "icon": "calendar",
                "url": "/servicos/agendamento"
            },
            {
                "nome": "Audiências",
                "descricao": "Informações sobre audiências presenciais e virtuais",
                "icon": "users",
                "url": "/servicos/audiencias"
            },
            {
                "nome": "Balcão Virtual",
                "descricao": "Atendimento online para dúvidas e solicitações",
                "icon": "monitor",
                "url": "/servicos/balcao-virtual"
            },
            {
                "nome": "Certidões",
                "descricao": "Solicite certidões e documentos oficiais",
                "icon": "file-text",
                "url": "/servicos/certidoes"
            }
        ]
    
    def get_news(self):
        """Get news from database or fallback to JSON"""
        from flask import has_app_context
        
        # Only try database if we have app context
        if has_app_context():
            try:
                # Try to get from database first
                news_items = NewsItem.query.filter_by(is_active=True).order_by(NewsItem.published_at.desc()).all()
                if news_items:
                    return [
                        {
                            'id': item.id,
                            'title': item.title,
                            'content': item.content,
                            'summary': item.summary,
                            'published_at': item.published_at.strftime('%d/%m/%Y')
                        }
                        for item in news_items
                    ]
            except Exception as e:
                print(f"Error loading news from database: {e}")
        
        # Fallback to JSON file
        try:
            news_file = os.path.join(self.data_path, 'news.json')
            with open(news_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_news()
        except Exception as e:
            print(f"Error loading news from JSON: {e}")
            return self.get_default_news()
    
    def get_latest_news(self, limit=3):
        """Get latest news items"""
        news = self.get_news()
        return news[:limit]
    
    def get_default_news(self):
        """Return default news data"""
        return [
            {
                'id': 1,
                'title': 'Funcionamento da 2ª Vara Cível de Cariacica',
                'summary': 'A vara está funcionando normalmente com atendimento presencial e virtual.',
                'content': 'A 2ª Vara Cível de Cariacica continua funcionando normalmente, oferecendo atendimento presencial das 12h às 18h e serviços virtuais através de nosso portal.',
                'published_at': '01/01/2024'
            },
            {
                'id': 2,
                'title': 'Audiências Virtuais Disponíveis',
                'summary': 'Participe de audiências de forma virtual através do Zoom.',
                'content': 'As audiências virtuais estão disponíveis para maior comodidade dos usuários. Você receberá instruções por email para participar.',
                'published_at': '15/12/2023'
            }
        ]
