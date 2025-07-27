"""
Refactored Routes Module for 2ª Vara Cível de Cariacica
Improved code organization, error handling, and performance
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from database import db
from services.content import ContentService
from services.chatbot_refined import get_refined_chatbot
from models import Contact, ProcessConsultation, AssessorMeeting
from utils.security import sanitize_input, validate_email
import logging
import os
from datetime import datetime, date
import uuid
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)

# Initialize services with error handling
try:
    from services.cache_service import cache_service
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    logger.warning("Cache service not available")

try:
    from services.api_service import tjes_integration
    API_SERVICE_AVAILABLE = True
except ImportError:
    API_SERVICE_AVAILABLE = False
    logger.warning("API service not available")

# Create blueprints
main_bp = Blueprint('main', __name__)
services_bp = Blueprint('services', __name__, url_prefix='/servicos')
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

# Initialize services
content_service = ContentService()

# Cache decorator
def cache_route(timeout=300):
    """Cache decorator for routes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if CACHE_AVAILABLE:
                cache_key = f"{request.path}:{request.query_string}"
                cached = cache_service.get(cache_key)
                if cached:
                    return cached
                result = f(*args, **kwargs)
                cache_service.set(cache_key, result, timeout=timeout)
                return result
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Error handler decorator
def handle_errors(f):
    """Decorator to handle errors in routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {e}")
            flash('Ocorreu um erro. Por favor, tente novamente.', 'error')
            return redirect(url_for('main.index'))
    return decorated_function

# Main routes
@main_bp.route('/')
@cache_route(timeout=600)
def index():
    """Homepage with court overview"""
    news = content_service.get_latest_news(limit=3)
    return render_template('index.html', news=news)

@main_bp.route('/sobre')
@cache_route(timeout=3600)
def about():
    """About the court page"""
    return render_template('about.html')

@main_bp.route('/juiz')
@cache_route(timeout=3600)
def judge():
    """Judge profile page"""
    return render_template('judge.html')

@main_bp.route('/faq')
@cache_route(timeout=1800)
def faq():
    """FAQ page with categorized questions"""
    faq_data = content_service.get_faq_data()
    return render_template('faq.html', faq_data=faq_data)

@main_bp.route('/form-demo')
def form_demo():
    """Demo page for form micro-interactions"""
    return render_template('form-demo.html')

@main_bp.route('/chatbot')
def chatbot():
    """Chatbot interface page"""
    return render_template('chatbot.html')

@main_bp.route('/contato', methods=['GET', 'POST'])
@handle_errors
def contact():
    """Contact page with form submission handling"""
    if request.method == 'POST':
        # Validate and sanitize form data
        form_data = {
            'name': sanitize_input(request.form.get('name', '')),
            'email': sanitize_input(request.form.get('email', '')),
            'phone': sanitize_input(request.form.get('phone', '')),
            'subject': sanitize_input(request.form.get('subject', '')),
            'message': sanitize_input(request.form.get('message', ''))
        }
        
        # Validate required fields
        required_fields = ['name', 'email', 'subject', 'message']
        if not all(form_data.get(field) for field in required_fields):
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
            return render_template('contact.html')
        
        # Validate email format
        if not validate_email(form_data['email']):
            flash('Por favor, forneça um email válido.', 'error')
            return render_template('contact.html')
        
        # Save contact submission
        contact = Contact(**form_data)
        db.session.add(contact)
        db.session.commit()
        
        flash('Sua mensagem foi enviada com sucesso! Retornaremos em breve.', 'success')
        logger.info(f"Contact form submitted by {form_data['email']}")
        
        return redirect(url_for('main.contact'))
    
    return render_template('contact.html')

@main_bp.route('/noticias')
@cache_route(timeout=600)
def news():
    """News and announcements page"""
    news_items = content_service.get_news()
    return render_template('news.html', news=news_items)

@main_bp.route('/consulta-processual', methods=['GET', 'POST'])
def process_consultation_main():
    """Process consultation service - main route redirect"""
    return redirect(url_for('services.process_consultation'))

@main_bp.route('/agendamento', methods=['GET', 'POST'])
def scheduling_main():
    """Scheduling service - main route redirect"""
    return redirect(url_for('services.scheduling'))

# Services routes
@services_bp.route('/')
@cache_route(timeout=1800)
def services_index():
    """Services overview page"""
    services = content_service.get_services_data()
    return render_template('services/index.html', services=services)

@services_bp.route('/consulta-processual', methods=['GET', 'POST'])
@handle_errors
def process_consultation():
    """Process consultation service"""
    if request.method == 'POST':
        process_number = sanitize_input(request.form.get('process_number', ''))
        
        if not process_number:
            flash('Por favor, informe o número do processo.', 'error')
            return render_template('services/consulta_processual.html')
        
        # Log consultation request
        consultation = ProcessConsultation(
            process_number=process_number,
            requester_name=sanitize_input(request.form.get('name', 'Anonymous')),
            requester_cpf=sanitize_input(request.form.get('cpf', '000.000.000-00')),
            ip_address=request.remote_addr
        )
        db.session.add(consultation)
        db.session.commit()
        
        logger.info(f"Process consultation for: {process_number}")
        
        # Redirect to TJES portal
        tjes_url = (
            "https://pje.tjes.jus.br/pje2g/ConsultaPublica/"
            f"listView.seam?numeroProcesso={process_number}"
        )
        return redirect(tjes_url)
    
    return render_template('services/consulta_processual.html')

@services_bp.route('/agendamento', methods=['GET', 'POST'])
@handle_errors
def scheduling():
    """Scheduling service for meetings and appointments"""
    if request.method == 'POST':
        # Collect and validate form data
        form_data = {
            'full_name': sanitize_input(request.form.get('full_name', '')),
            'document': sanitize_input(request.form.get('document', '')),
            'email': sanitize_input(request.form.get('email', '')),
            'phone': sanitize_input(request.form.get('phone', '')),
            'process_number': sanitize_input(request.form.get('process_number', '')),
            'meeting_type': request.form.get('meeting_type', ''),
            'meeting_subject': sanitize_input(request.form.get('meeting_subject', '')),
            'preferred_date': request.form.get('preferred_date', ''),
            'preferred_time': request.form.get('preferred_time', ''),
            'alternative_times': sanitize_input(request.form.get('alternative_times', ''))
        }
        
        # Validate required fields
        required = ['full_name', 'document', 'email', 'phone', 
                   'meeting_type', 'meeting_subject', 'preferred_date', 
                   'preferred_time']
        
        if not all(form_data.get(field) for field in required):
            flash('Por favor, preencha todos os campos obrigatórios.', 'error')
            return render_template('services/agendamento.html')
        
        # Validate email
        if not validate_email(form_data['email']):
            flash('Por favor, forneça um email válido.', 'error')
            return render_template('services/agendamento.html')
        
        # Parse and validate date
        try:
            preferred_date = datetime.strptime(
                form_data['preferred_date'], 
                '%Y-%m-%d'
            ).date()
            
            if preferred_date < date.today():
                flash('A data não pode ser no passado.', 'error')
                return render_template('services/agendamento.html')
        except ValueError:
            flash('Data inválida.', 'error')
            return render_template('services/agendamento.html')
        
        # Create meeting record
        meeting = AssessorMeeting(
            full_name=form_data['full_name'],
            document=form_data['document'],
            email=form_data['email'],
            phone=form_data['phone'],
            process_number=form_data['process_number'] or None,
            meeting_type=form_data['meeting_type'],
            meeting_subject=form_data['meeting_subject'],
            preferred_date=preferred_date,
            preferred_time=form_data['preferred_time'],
            alternative_times=form_data['alternative_times'] or None,
            confirmation_token=str(uuid.uuid4())
        )
        
        db.session.add(meeting)
        db.session.commit()
        
        flash('Solicitação de agendamento enviada com sucesso!', 'success')
        logger.info(f"Meeting scheduled for {form_data['email']}")
        
        return redirect(url_for('services.scheduling'))
    
    return render_template('services/agendamento.html')

@services_bp.route('/balcao-virtual')
@cache_route(timeout=3600)
def virtual_desk():
    """Virtual desk information page"""
    return render_template('services/balcao_virtual.html')

# Chatbot routes
@chatbot_bp.route('/message', methods=['POST'])
@handle_errors
def chatbot_message():
    """Handle chatbot messages"""
    data = request.get_json()
    user_message = data.get('message', '')
    session_id = data.get('session_id', str(uuid.uuid4()))
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Get chatbot response
    chatbot = get_refined_chatbot()
    response = chatbot.get_response(user_message, session_id)
    
    return jsonify({
        'response': response.message,
        'session_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'metadata': {
            'response_type': response.response_type,
            'confidence_score': response.confidence_score,
            'suggestions': response.suggestions
        }
    })

@chatbot_bp.route('/health')
def chatbot_health():
    """Chatbot health check endpoint"""
    chatbot = get_refined_chatbot()
    is_healthy = chatbot.check_health()
    
    return jsonify({
        'status': 'healthy' if is_healthy else 'unhealthy',
        'timestamp': datetime.now().isoformat()
    })

# API endpoints for AJAX calls
@main_bp.route('/api/validate-email', methods=['POST'])
def validate_email_api():
    """API endpoint for email validation"""
    email = request.get_json().get('email', '')
    is_valid = validate_email(email)
    
    return jsonify({'valid': is_valid})

@main_bp.route('/api/check-process', methods=['POST'])
def check_process_api():
    """API endpoint for process number validation"""
    process_number = request.get_json().get('process_number', '')
    
    # Basic format validation
    is_valid = bool(process_number and len(process_number) >= 10)
    
    return jsonify({
        'valid': is_valid,
        'message': 'Número de processo válido' if is_valid else 'Número inválido'
    })

# Error handlers
@main_bp.errorhandler(404)
def not_found(error):
    """Custom 404 page"""
    return render_template('errors/404.html'), 404

@main_bp.errorhandler(500)
def internal_error(error):
    """Custom 500 page"""
    logger.error(f"Internal error: {error}")
    return render_template('errors/500.html'), 500