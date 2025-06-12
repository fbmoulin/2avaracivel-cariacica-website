"""
Optimized routes for 2ª Vara Cível de Cariacica
Refactored with advanced caching, performance optimizations, and clean architecture
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, g
from functools import wraps
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import time

# Create blueprints
main_bp = Blueprint('main', __name__)
services_bp = Blueprint('services', __name__, url_prefix='/servicos')
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

logger = logging.getLogger(__name__)


def performance_monitor(f):
    """Decorator to monitor route performance"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            if duration > 500:  # Log slow routes
                logger.warning(f"Slow route {f.__name__}: {duration:.2f}ms")
            return result
        except Exception as e:
            logger.error(f"Route {f.__name__} failed: {e}")
            raise
    return decorated_function


def cache_response(timeout: int = 300):
    """Enhanced caching decorator with conditional caching"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                from services.cache_service import cache_service
                
                # Generate cache key
                cache_key = f"route:{f.__name__}:{request.path}:{request.args.to_dict(flat=False)}"
                
                # Try to get from cache
                cached_result = cache_service.get(cache_key)
                if cached_result:
                    return cached_result
                
                # Execute function and cache result
                result = f(*args, **kwargs)
                cache_service.set(cache_key, result, timeout=timeout)
                return result
                
            except ImportError:
                # Fallback if cache service not available
                return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_form_data(required_fields: List[str]):
    """Decorator to validate form data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method == 'POST':
                missing_fields = [field for field in required_fields if not request.form.get(field)]
                if missing_fields:
                    flash(f'Campos obrigatórios faltando: {", ".join(missing_fields)}', 'error')
                    return redirect(request.url)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Main Routes
@main_bp.route('/')
@performance_monitor
@cache_response(timeout=600)  # Cache for 10 minutes
def index():
    """Optimized homepage with caching and performance monitoring"""
    try:
        # Get cached content or load fresh data
        from services.content import get_homepage_content
        content = get_homepage_content()
        
        return render_template('index.html', **content)
    except Exception as e:
        logger.error(f"Homepage error: {e}")
        return render_template('index.html', content={})


@main_bp.route('/sobre')
@performance_monitor
@cache_response(timeout=3600)  # Cache for 1 hour
def about():
    """About page with long-term caching"""
    return render_template('about.html')


@main_bp.route('/juiz')
@performance_monitor
@cache_response(timeout=3600)
def judge():
    """Judge profile page with long-term caching"""
    return render_template('judge.html')


@main_bp.route('/faq')
@performance_monitor
@cache_response(timeout=1800)  # Cache for 30 minutes
def faq():
    """FAQ page with optimized data loading"""
    try:
        from services.content import get_faq_data
        faq_data = get_faq_data()
        return render_template('faq.html', faq_data=faq_data)
    except Exception as e:
        logger.error(f"FAQ error: {e}")
        return render_template('faq.html', faq_data={})


@main_bp.route('/contato', methods=['GET', 'POST'])
@performance_monitor
@validate_form_data(['name', 'email', 'subject', 'message'])
def contact():
    """Optimized contact page with form validation"""
    if request.method == 'POST':
        try:
            from services.database_service import DatabaseService
            
            contact_data = {
                'name': request.form['name'].strip(),
                'email': request.form['email'].strip().lower(),
                'phone': request.form.get('phone', '').strip(),
                'subject': request.form['subject'],
                'message': request.form['message'].strip()
            }
            
            success, error = DatabaseService.create_contact(contact_data)
            
            if success:
                flash('Mensagem enviada com sucesso! Retornaremos em breve.', 'success')
                return redirect(url_for('main.contact'))
            else:
                flash(f'Erro ao enviar mensagem: {error}', 'error')
                
        except Exception as e:
            logger.error(f"Contact form error: {e}")
            flash('Erro interno. Tente novamente mais tarde.', 'error')
    
    return render_template('contact.html')


@main_bp.route('/noticias')
@performance_monitor
@cache_response(timeout=900)  # Cache for 15 minutes
def news():
    """News page with optimized loading"""
    try:
        from services.content import get_news_data
        news_data = get_news_data()
        return render_template('news.html', news_data=news_data)
    except Exception as e:
        logger.error(f"News error: {e}")
        return render_template('news.html', news_data=[])


# Services Routes
@services_bp.route('/')
@performance_monitor
@cache_response(timeout=1800)
def services_index():
    """Services overview with caching"""
    return render_template('services/index.html')


@services_bp.route('/audiencias')
@performance_monitor
@cache_response(timeout=1800)
def hearings():
    """Hearings page with tutorial content"""
    return render_template('services/hearings.html')


@services_bp.route('/agendamento')
@performance_monitor
def scheduling():
    """Scheduling service page"""
    return render_template('services/scheduling.html')


@services_bp.route('/balcao-virtual')
@performance_monitor
@cache_response(timeout=3600)
def virtual_desk():
    """Virtual desk service page"""
    return render_template('services/virtual_desk.html')


@services_bp.route('/certidoes')
@performance_monitor
@cache_response(timeout=3600)
def certificates():
    """Certificates service page"""
    return render_template('services/certificates.html')


@services_bp.route('/consulta-processual', methods=['GET', 'POST'])
@performance_monitor
def process_consultation():
    """Process consultation with rate limiting and optimization"""
    if request.method == 'POST':
        try:
            process_number = request.form.get('process_number', '').strip()
            
            if not process_number:
                flash('Número do processo é obrigatório', 'error')
                return render_template('services/process_consultation.html')
            
            # Validate CNJ format
            if not validate_cnj_format(process_number):
                flash('Formato de número de processo inválido', 'error')
                return render_template('services/process_consultation.html')
            
            # Try to get process information
            from services.api_service import get_process_info
            process_info = get_process_info(process_number)
            
            # Log consultation
            from services.database_service import DatabaseService
            DatabaseService.log_process_consultation(process_number, request.remote_addr)
            
            return render_template('services/process_consultation.html', 
                                 process_info=process_info, 
                                 process_number=process_number)
            
        except Exception as e:
            logger.error(f"Process consultation error: {e}")
            flash('Erro ao consultar processo. Tente novamente.', 'error')
    
    return render_template('services/process_consultation.html')


# Chatbot Routes
@chatbot_bp.route('/api/message', methods=['POST'])
@performance_monitor
def chatbot_message():
    """Optimized chatbot endpoint with rate limiting"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Mensagem é obrigatória'}), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({'error': 'Mensagem não pode estar vazia'}), 400
        
        # Get session ID for conversation tracking
        session_id = data.get('session_id', request.remote_addr)
        
        # Get chatbot response
        from services.chatbot import get_chatbot_response
        response = get_chatbot_response(user_message, session_id)
        
        # Log interaction
        try:
            from services.database_service import DatabaseService
            DatabaseService.log_chatbot_interaction(user_message, response, session_id)
        except Exception as e:
            logger.warning(f"Failed to log chatbot interaction: {e}")
        
        return jsonify({
            'response': response,
            'timestamp': datetime.utcnow().isoformat(),
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        return jsonify({
            'response': 'Desculpe, ocorreu um erro temporário. Tente novamente em alguns momentos.',
            'error': True
        }), 500


# Utility Functions
def validate_cnj_format(process_number: str) -> bool:
    """Validate CNJ process number format"""
    import re
    # CNJ format: NNNNNNN-DD.AAAA.J.TR.OOOO
    pattern = r'^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$'
    return bool(re.match(pattern, process_number))


def get_client_ip() -> str:
    """Get client IP address with proxy support"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr


# Error handlers for blueprints
@main_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors for main blueprint"""
    return render_template('errors/404.html'), 404


@main_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors for main blueprint"""
    logger.error(f"Internal error: {error}")
    return render_template('errors/500.html'), 500


# Health check endpoint
@main_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Quick database check
        from models import db
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.1.0'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500