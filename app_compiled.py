"""
Compiled Production Application - 2ª Vara Cível de Cariacica
Optimized single-file deployment with essential components only
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import time
import threading
from datetime import datetime

# Optimized logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Global extensions
db = SQLAlchemy(model_class=Base)
cache = Cache()
limiter = Limiter(key_func=get_remote_address, default_limits=["1000 per hour"])

# Performance monitoring
request_count = 0
start_time = time.time()

class ProductionConfig:
    SECRET_KEY = os.environ.get("SESSION_SECRET", "production-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///court.db")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 1800,
        "pool_pre_ping": True,
        "pool_timeout": 30,
        "max_overflow": 20,
        "pool_size": 10
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

# Models
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProcessConsultation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_number = db.Column(db.String(50), nullable=False)
    requester_name = db.Column(db.String(100), nullable=False)
    requester_cpf = db.Column(db.String(14), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def create_app():
    app = Flask(__name__)
    app.config.from_object(ProductionConfig)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize extensions
    db.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    
    # Performance monitoring
    @app.before_request
    def before_request():
        g.start_time = time.time()
        global request_count
        request_count += 1
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            response_time = time.time() - g.start_time
            response.headers['X-Response-Time'] = f"{response_time:.3f}s"
        return response
    
    # Routes
    @app.route('/')
    @cache.cached(timeout=600)
    def index():
        return render_template('index.html')
    
    @app.route('/sobre')
    @cache.cached(timeout=600)
    def about():
        return render_template('about.html')
    
    @app.route('/contato', methods=['GET', 'POST'])
    def contact():
        if request.method == 'POST':
            contact = Contact(
                name=request.form.get('name', '').strip(),
                email=request.form.get('email', '').strip(),
                phone=request.form.get('phone', '').strip(),
                message=request.form.get('message', '').strip()
            )
            db.session.add(contact)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Mensagem enviada com sucesso!'})
        
        return render_template('contact.html')
    
    @app.route('/consulta', methods=['GET', 'POST'])
    def process_consultation():
        if request.method == 'POST':
            consultation = ProcessConsultation(
                process_number=request.form.get('process_number', '').strip(),
                requester_name=request.form.get('name', '').strip(),
                requester_cpf=request.form.get('cpf', '').strip()
            )
            db.session.add(consultation)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Consulta registrada com sucesso!'})
        
        return render_template('services/consulta_processual.html')
    
    @app.route('/faq')
    @cache.cached(timeout=3600)
    def faq():
        return render_template('faq.html')
    
    @app.route('/noticias')
    @cache.cached(timeout=1800)
    def news():
        return render_template('news.html')
    
    @app.route('/juiz')
    @cache.cached(timeout=3600)
    def judge():
        return render_template('judge.html')
    
    @app.route('/servicos/')
    @cache.cached(timeout=600)
    def services():
        return render_template('services/index.html')
    
    @app.route('/servicos/balcao-virtual')
    @cache.cached(timeout=600)
    def virtual_counter():
        return render_template('services/balcao_virtual.html')
    
    @app.route('/servicos/agendamento')
    def scheduling():
        return render_template('services/agendamento.html')
    
    @app.route('/servicos/audiencias')
    @cache.cached(timeout=600)
    def hearings():
        return render_template('services/audiencias.html')
    
    @app.route('/servicos/certidoes')
    @cache.cached(timeout=600)
    def certificates():
        return render_template('services/certidoes.html')
    
    @app.route('/balcao-virtual')
    def virtual_counter_redirect():
        return render_template('services/balcao_virtual.html')
    
    @app.route('/agendamento')
    def scheduling_redirect():
        return render_template('services/agendamento.html')
    
    @app.route('/chatbot')
    def chatbot():
        return render_template('chatbot.html')
    
    @app.route('/chat', methods=['POST'])
    @limiter.limit("10 per minute")
    def chat():
        message = request.json.get('message', '').strip()
        if not message:
            return jsonify({'error': 'Mensagem vazia'}), 400
        
        # Simple chatbot responses
        responses = {
            'horario': 'O atendimento é de segunda a sexta, das 12h às 19h.',
            'endereco': 'Rua Expedito Garcia, s/n - Centro, Cariacica - ES.',
            'telefone': 'Telefone: (27) 3136-3600',
            'processo': 'Para consultar processos, use o serviço de Consulta Processual.',
            'agendamento': 'Para agendar atendimento, acesse o serviço de Agendamento.',
            'certidao': 'Para solicitar certidões, acesse o serviço correspondente.'
        }
        
        response = "Como posso ajudá-lo? Posso fornecer informações sobre horários, endereço, telefone e serviços disponíveis."
        
        for key, value in responses.items():
            if key in message.lower():
                response = value
                break
        
        # Save chat message
        try:
            chat_msg = ChatMessage(
                session_id=request.remote_addr,
                message=message,
                response=response
            )
            db.session.add(chat_msg)
            db.session.commit()
        except:
            pass
        
        return jsonify({'response': response})
    
    @app.route('/health')
    def health():
        uptime = time.time() - start_time
        return jsonify({
            'status': 'healthy',
            'uptime': f"{uptime:.1f}s",
            'requests': request_count,
            'timestamp': datetime.now().isoformat()
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({'error': 'Muitas requisições. Tente novamente em alguns minutos.'}), 429
    
    # Create tables
    with app.app_context():
        db.create_all()
        logger.info("Application initialized successfully")
    
    return app

# Application factory
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)