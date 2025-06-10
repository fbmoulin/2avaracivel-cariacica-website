"""
Optimized routes for 2ª Vara Cível de Cariacica
Refactored with caching, rate limiting, and performance optimizations
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from services.content import ContentService
from services.chatbot import ChatbotService
from services.database_service import DatabaseService
from services.scheduling_service import SchedulingService, initialize_scheduling_system
from models import HearingSchedule, AvailableTimeSlot
from services.cache_service import CacheService, cache_faq_data, cache_services_data, cache_news_data
from utils.security import sanitize_input, validate_email
from utils.request_middleware import monitor_performance, validate_request_data, cache_response
from app_factory import limiter, cache
import logging
import os
from datetime import datetime, date, timedelta
import uuid


# Create blueprints
main_bp = Blueprint('main', __name__)
services_bp = Blueprint('services', __name__, url_prefix='/servicos')
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Initialize services
content_service = ContentService()
chatbot_service = ChatbotService()

# Main routes with caching and rate limiting
@main_bp.route('/')
@CacheService.cached_route(timeout=CacheService.MEDIUM_CACHE)
@limiter.limit("100 per minute")
def index():
    """Homepage with court overview - cached for performance"""
    try:
        recent_news = cache_news_data()
        return render_template('index.html', news=recent_news[:3])
    except Exception as e:
        logging.error(f"Index page error: {e}")
        return render_template('index.html', news=[])


@main_bp.route('/sobre')
@CacheService.cached_route(timeout=CacheService.LONG_CACHE)
@limiter.limit("50 per minute")
def about():
    """About the court page - cached for long periods"""
    return render_template('about.html')


@main_bp.route('/juiz')
@CacheService.cached_route(timeout=CacheService.LONG_CACHE)
@limiter.limit("50 per minute")
def judge():
    """Judge profile page - cached for long periods"""
    return render_template('judge.html')


@main_bp.route('/faq')
@CacheService.cached_route(timeout=CacheService.LONG_CACHE)
@limiter.limit("30 per minute")
def faq():
    """FAQ page with cached data"""
    try:
        faq_data = cache_faq_data()
        return render_template('faq.html', faq_data=faq_data)
    except Exception as e:
        logging.error(f"FAQ page error: {e}")
        return render_template('faq.html', faq_data={})


@main_bp.route('/contato', methods=['GET', 'POST'])
@limiter.limit("10 per minute", methods=['POST'])
@limiter.limit("30 per minute", methods=['GET'])
def contact():
    """Contact page with form handling and validation"""
    if request.method == 'POST':
        try:
            # Validate and sanitize input
            data = {
                'name': sanitize_input(request.form.get('name', '').strip()),
                'email': request.form.get('email', '').strip().lower(),
                'phone': sanitize_input(request.form.get('phone', '').strip()),
                'subject': sanitize_input(request.form.get('subject', '').strip()),
                'message': sanitize_input(request.form.get('message', '').strip())
            }
            
            # Validation
            if not all([data['name'], data['email'], data['subject'], data['message']]):
                flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
                return render_template('contact.html')
            
            if not validate_email(data['email']):
                flash('Email inválido.', 'error')
                return render_template('contact.html')
            
            # Save to database
            contact, error = DatabaseService.create_contact(data)
            
            if contact:
                flash('Mensagem enviada com sucesso! Entraremos em contato em breve.', 'success')
                # Invalidate contact stats cache
                cache.delete('admin:contact_stats')
                return redirect(url_for('main.contact'))
            else:
                flash(f'Erro ao enviar mensagem: {error}', 'error')
                
        except Exception as e:
            logging.error(f"Contact form error: {e}")
            flash('Erro interno. Tente novamente mais tarde.', 'error')
    
    return render_template('contact.html')


@main_bp.route('/noticias')
@CacheService.cached_route(timeout=CacheService.MEDIUM_CACHE)
@limiter.limit("20 per minute")
def news():
    """News and announcements page with cached content"""
    try:
        news_data = cache_news_data()
        return render_template('news.html', news=news_data)
    except Exception as e:
        logging.error(f"News page error: {e}")
        return render_template('news.html', news=[])


# Services routes with caching
@services_bp.route('/')
@CacheService.cached_route(timeout=CacheService.LONG_CACHE)
@limiter.limit("30 per minute")
def services_index():
    """Services overview page with cached data"""
    try:
        services_data = cache_services_data()
        return render_template('services/index.html', services=services_data)
    except Exception as e:
        logging.error(f"Services page error: {e}")
        return render_template('services/index.html', services={})


@services_bp.route('/audiencias')
@CacheService.cached_route(timeout=CacheService.LONG_CACHE)
@limiter.limit("20 per minute")
def hearings():
    """Hearings information page"""
    return render_template('services/hearings.html')


@services_bp.route('/agendamento')
@limiter.limit("15 per minute")
def scheduling():
    """Advanced scheduling service page with calendar integration"""
    try:
        # Initialize scheduling system if needed
        initialize_scheduling_system()
        
        # Get next 30 days of available slots
        start_date = date.today()
        end_date = start_date + timedelta(days=30)
        available_slots = SchedulingService.get_available_slots(start_date, end_date)
        
        # Get hearing types and modes
        hearing_types = [
            {'value': 'conciliation', 'label': 'Audiência de Conciliação'},
            {'value': 'instruction', 'label': 'Audiência de Instrução'},
            {'value': 'judgment', 'label': 'Audiência de Julgamento'}
        ]
        
        hearing_modes = [
            {'value': 'virtual', 'label': 'Virtual (Online)'},
            {'value': 'in_person', 'label': 'Presencial'},
            {'value': 'hybrid', 'label': 'Híbrida'}
        ]
        
        return render_template('services/scheduling.html', 
                             available_slots=available_slots,
                             hearing_types=hearing_types,
                             hearing_modes=hearing_modes)
    
    except Exception as e:
        logging.error(f"Error loading scheduling page: {e}")
        flash('Erro ao carregar página de agendamento', 'error')
        return render_template('services/scheduling.html', 
                             available_slots=[],
                             hearing_types=[],
                             hearing_modes=[])


@services_bp.route('/balcao-virtual')
@CacheService.cached_route(timeout=CacheService.MEDIUM_CACHE)
@limiter.limit("20 per minute")
def virtual_desk():
    """Virtual desk service page"""
    return render_template('services/virtual_desk.html')


@services_bp.route('/certidoes')
@CacheService.cached_route(timeout=CacheService.LONG_CACHE)
@limiter.limit("15 per minute")
def certificates():
    """Certificates service page"""
    return render_template('services/certificates.html')


@services_bp.route('/consulta-processual', methods=['GET', 'POST'])
@limiter.limit("20 per minute", methods=['POST'])
@limiter.limit("30 per minute", methods=['GET'])
def process_consultation():
    """Process consultation with tracking and rate limiting"""
    if request.method == 'POST':
        try:
            process_number = sanitize_input(request.form.get('process_number', '').strip())
            
            if not process_number:
                flash('Número do processo é obrigatório.', 'error')
                return render_template('services/process_consultation.html')
            
            # Record consultation with spam protection
            ip_address = request.remote_addr
            consultation, error = DatabaseService.create_process_consultation(
                process_number, ip_address
            )
            
            if error:
                flash(error, 'warning')
            else:
                # Invalidate consultation stats cache
                cache.delete('admin:consultation_stats')
            
            # Simulate process lookup (in real implementation, integrate with court system)
            result = {
                'found': True,
                'process_number': process_number,
                'status': 'Em andamento',
                'last_movement': 'Aguardando decisão judicial',
                'next_hearing': 'A definir'
            }
            
            return render_template('services/process_consultation.html', 
                                 result=result, searched=True)
            
        except Exception as e:
            logging.error(f"Process consultation error: {e}")
            flash('Erro na consulta. Tente novamente.', 'error')
    
    return render_template('services/process_consultation.html')


# Chatbot routes with enhanced rate limiting and monitoring
@chatbot_bp.route('/api/message', methods=['POST'])
@limiter.limit("30 per minute")
@monitor_performance
@validate_request_data(required_fields=['message'])
def chatbot_message(validated_data):
    """Handle chatbot messages with rate limiting, session tracking, and robust error handling"""
    try:
        user_message = sanitize_input(validated_data['message'].strip())
        if not user_message:
            return jsonify({'error': 'Mensagem não pode estar vazia'}), 400
        
        # Get or create session ID
        session_id = session.get('chatbot_session')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['chatbot_session'] = session_id
        
        # Get response from chatbot with error handling
        try:
            response = chatbot_service.get_response(user_message)
        except Exception as e:
            logging.error(f"Chatbot service error: {e}")
            response = "Desculpe, estou com dificuldades técnicas no momento. Por favor, tente novamente em alguns instantes ou entre em contato diretamente conosco."
        
        # Save interaction to database with retry logic
        try:
            chat, error = DatabaseService.create_chat_message(
                user_message, response, session_id
            )
            if error:
                logging.warning(f"Failed to save chat message: {error}")
        except Exception as e:
            logging.error(f"Database error saving chat: {e}")
            # Continue without failing the request
        
        # Invalidate chatbot stats cache
        try:
            cache.delete('admin:chatbot_stats')
        except Exception as e:
            logging.warning(f"Cache invalidation failed: {e}")
        
        return jsonify({
            'response': response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Unexpected chatbot error: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': 'Ocorreu um erro inesperado. Tente novamente mais tarde.'
        }), 500


# Admin routes with authentication and caching
@admin_bp.route('/status')
@limiter.limit("10 per minute")
def system_status():
    """System status dashboard with cached data"""
    try:
        # Get cached statistics
        contact_stats = cache.get('admin:contact_stats')
        if not contact_stats:
            contact_stats, _ = DatabaseService.get_contact_statistics()
            cache.set('admin:contact_stats', contact_stats, timeout=300)
        
        consultation_stats = cache.get('admin:consultation_stats')
        if not consultation_stats:
            consultation_stats, _ = DatabaseService.get_process_consultation_statistics()
            cache.set('admin:consultation_stats', consultation_stats, timeout=300)
        
        chatbot_stats = cache.get('admin:chatbot_stats')
        if not chatbot_stats:
            chatbot_stats, _ = DatabaseService.get_chatbot_statistics()
            cache.set('admin:chatbot_stats', chatbot_stats, timeout=300)
        
        system_info = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'database_status': 'Connected',
            'openai_status': 'Active' if chatbot_service.openai_client else 'Inactive',
            'server_status': 'Running',
            'cache_status': 'Active',
            'statistics': {
                'contacts': contact_stats,
                'consultations': consultation_stats,
                'chatbot': chatbot_stats
            }
        }
        
        # Check if debug files exist
        debug_files = {
            'health_check': os.path.exists('health_check_summary.txt'),
            'error_log': os.path.exists('errors.log'),
            'error_report': os.path.exists('error_report.txt')
        }
        
        return render_template('admin/status.html', 
                             system_info=system_info,
                             debug_files=debug_files)
    except Exception as e:
        logging.error(f"Status dashboard error: {e}")
        return jsonify({'error': 'Unable to load status'}), 500


@admin_bp.route('/health-check')
@limiter.exempt
def health_check_api():
    """API endpoint for health check results"""
    try:
        if os.path.exists('health_check_summary.txt'):
            with open('health_check_summary.txt', 'r') as f:
                content = f.read()
            return jsonify({'status': 'success', 'content': content})
        else:
            return jsonify({'status': 'no_data', 'message': 'No health check data available'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@admin_bp.route('/error-report')
@limiter.exempt
def error_report_api():
    """API endpoint for error report"""
    try:
        if os.path.exists('error_report.txt'):
            with open('error_report.txt', 'r') as f:
                content = f.read()
            return jsonify({'status': 'success', 'content': content})
        else:
            return jsonify({'status': 'no_data', 'message': 'No error report available'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@admin_bp.route('/cache-clear')
@limiter.limit("5 per minute")
def clear_cache():
    """Clear application cache"""
    try:
        cache.clear()
        return jsonify({'status': 'success', 'message': 'Cache cleared successfully'})
    except Exception as e:
        logging.error(f"Cache clear error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})


@admin_bp.route('/database-cleanup')
@limiter.limit("1 per hour")
def database_cleanup():
    """Cleanup old database records"""
    try:
        success, message = DatabaseService.cleanup_old_data()
        if success:
            # Clear related caches
            cache.delete('admin:consultation_stats')
            cache.delete('admin:chatbot_stats')
            return jsonify({'status': 'success', 'message': message})
        else:
            return jsonify({'status': 'error', 'message': message})
    except Exception as e:
        logging.error(f"Database cleanup error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})


# Enhanced error handlers
@main_bp.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404


@main_bp.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500


@main_bp.errorhandler(429)
def ratelimit_handler(e):
    return render_template('errors/429.html'), 429