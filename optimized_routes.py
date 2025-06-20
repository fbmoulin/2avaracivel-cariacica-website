"""
Optimized Routes Module
Refactored with improved organization, caching, and performance optimizations
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, g
from database import db
from models import Contact, ProcessConsultation, AssessorMeeting, NewsItem
from utils.security import sanitize_input, validate_email
import logging
import time
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)

# Performance monitoring decorator
def monitor_route_performance(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            duration = time.time() - start_time
            if duration > 0.5:  # Log routes taking more than 500ms
                logger.warning(f"Slow route: {request.endpoint} took {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Route error: {request.endpoint} failed in {duration:.3f}s - {str(e)}")
            raise
    return decorated_function

def create_optimized_blueprints(cache, limiter):
    """Create optimized blueprints with caching and rate limiting"""
    
    # Main blueprint
    main_bp = Blueprint('main', __name__)
    
    @main_bp.route('/')
    @cache.cached(timeout=300)  # Cache for 5 minutes
    @monitor_route_performance
    def index():
        """Optimized homepage with cached content"""
        try:
            from services.content import ContentService
            content_service = ContentService()
            news = content_service.get_latest_news(limit=3)
            return render_template('index.html', news=news)
        except Exception as e:
            logger.error(f"Homepage error: {e}")
            return render_template('index.html', news=[])
    
    @main_bp.route('/sobre')
    @cache.cached(timeout=3600)  # Cache for 1 hour
    @monitor_route_performance
    def about():
        """About page with extended caching"""
        return render_template('about.html')
    
    @main_bp.route('/juiz')
    @cache.cached(timeout=3600)
    @monitor_route_performance
    def judge():
        """Judge profile page"""
        return render_template('judge.html')
    
    @main_bp.route('/faq')
    @cache.cached(timeout=1800)  # Cache for 30 minutes
    @monitor_route_performance
    def faq():
        """FAQ page with cached content"""
        try:
            from services.content import ContentService
            content_service = ContentService()
            faq_data = content_service.get_faq_data()
            return render_template('faq.html', faq_data=faq_data)
        except Exception as e:
            logger.error(f"FAQ error: {e}")
            return render_template('faq.html', faq_data={})
    
    @main_bp.route('/chatbot')
    @monitor_route_performance
    def chatbot():
        """Chatbot interface"""
        return render_template('chatbot.html')
    
    @main_bp.route('/contato', methods=['GET', 'POST'])
    @limiter.limit("5 per minute", methods=['POST'])
    @monitor_route_performance
    def contact():
        """Optimized contact form with rate limiting"""
        if request.method == 'POST':
            return handle_contact_form()
        return render_template('contact.html')
    
    def handle_contact_form():
        """Separated contact form handling for better organization"""
        try:
            # Extract and validate form data
            form_data = {
                'name': sanitize_input(request.form.get('name', '')),
                'email': sanitize_input(request.form.get('email', '')),
                'phone': sanitize_input(request.form.get('phone', '')),
                'subject': sanitize_input(request.form.get('subject', '')),
                'message': sanitize_input(request.form.get('message', ''))
            }
            
            # Validation
            if not all([form_data['name'], form_data['email'], form_data['subject'], form_data['message']]):
                flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
                return render_template('contact.html')
            
            if not validate_email(form_data['email']):
                flash('Por favor, forneça um email válido.', 'error')
                return render_template('contact.html')
            
            # Save contact
            contact = Contact(**form_data)
            db.session.add(contact)
            db.session.commit()
            
            flash('Sua mensagem foi enviada com sucesso! Retornaremos em breve.', 'success')
            return redirect(url_for('main.contact'))
            
        except Exception as e:
            logger.error(f"Contact form error: {e}")
            db.session.rollback()
            flash('Erro ao enviar mensagem. Tente novamente.', 'error')
            return render_template('contact.html')
    
    @main_bp.route('/noticias')
    @cache.cached(timeout=600)  # Cache for 10 minutes
    @monitor_route_performance
    def news():
        """Optimized news page"""
        try:
            news_items = NewsItem.query.filter_by(is_active=True).order_by(NewsItem.published_at.desc()).all()
            return render_template('news.html', news=news_items)
        except Exception as e:
            logger.error(f"News page error: {e}")
            return render_template('news.html', news=[])
    
    # Services blueprint
    services_bp = Blueprint('services', __name__, url_prefix='/servicos')
    
    @services_bp.route('/')
    @cache.cached(timeout=1800)
    @monitor_route_performance
    def services_index():
        """Services overview with caching"""
        return render_template('services/index.html')
    
    @services_bp.route('/agendamento', methods=['GET', 'POST'])
    @limiter.limit("3 per minute", methods=['POST'])
    @monitor_route_performance
    def scheduling():
        """Optimized scheduling with enhanced error handling"""
        if request.method == 'POST':
            return handle_scheduling_form()
        return render_template('services/scheduling.html')
    
    def handle_scheduling_form():
        """Separated scheduling form handling"""
        try:
            # Extract form data with validation
            meeting_data = extract_meeting_data()
            
            if not validate_meeting_data(meeting_data):
                return render_template('services/scheduling.html')
            
            # Create meeting record
            meeting = AssessorMeeting(**meeting_data)
            db.session.add(meeting)
            db.session.commit()
            
            flash('Agendamento solicitado com sucesso! Entraremos em contato.', 'success')
            return redirect(url_for('services.scheduling'))
            
        except Exception as e:
            logger.error(f"Scheduling error: {e}")
            db.session.rollback()
            flash('Erro ao processar agendamento. Tente novamente.', 'error')
            return render_template('services/scheduling.html')
    
    def extract_meeting_data():
        """Extract and sanitize meeting form data"""
        return {
            'full_name': sanitize_input(request.form.get('full_name', '')),
            'document': sanitize_input(request.form.get('document', '')),
            'email': sanitize_input(request.form.get('email', '')),
            'phone': sanitize_input(request.form.get('phone', '')),
            'meeting_type': sanitize_input(request.form.get('meeting_type', '')),
            'meeting_subject': sanitize_input(request.form.get('meeting_subject', '')),
            'preferred_date': request.form.get('preferred_date'),
            'preferred_time': sanitize_input(request.form.get('preferred_time', '09:00')),
            'process_number': sanitize_input(request.form.get('process_number', '')),
            'alternative_times': sanitize_input(request.form.get('alternative_times', ''))
        }
    
    def validate_meeting_data(data):
        """Validate meeting form data"""
        required_fields = ['full_name', 'document', 'email', 'phone', 'meeting_type', 'meeting_subject']
        
        for field in required_fields:
            if not data.get(field):
                flash(f'Campo {field} é obrigatório.', 'error')
                return False
        
        if not validate_email(data['email']):
            flash('Email inválido.', 'error')
            return False
        
        if data['preferred_date']:
            try:
                data['preferred_date'] = datetime.strptime(data['preferred_date'], '%Y-%m-%d').date()
            except ValueError:
                flash('Data inválida.', 'error')
                return False
        
        return True
    
    @services_bp.route('/consulta-processual')
    @cache.cached(timeout=1800)
    @monitor_route_performance
    def process_consultation():
        """Process consultation page"""
        return render_template('services/process_consultation.html')
    
    @services_bp.route('/balcao-virtual')
    @cache.cached(timeout=1800)
    @monitor_route_performance
    def virtual_desk():
        """Virtual desk service page"""
        return render_template('services/virtual_desk.html')
    
    @services_bp.route('/audiencias')
    @cache.cached(timeout=1800)
    @monitor_route_performance
    def hearings():
        """Hearings information page"""
        return render_template('services/hearings.html')
    
    # Chatbot blueprint
    chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')
    
    @chatbot_bp.route('/api/chat', methods=['POST'])
    @limiter.limit("30 per minute")
    @monitor_route_performance
    def chat_api():
        """Optimized chatbot API endpoint"""
        try:
            data = request.get_json()
            if not data or 'message' not in data:
                return jsonify({'error': 'Message required'}), 400
            
            try:
                from optimized_chatbot import get_optimized_chatbot
                chatbot = get_optimized_chatbot()
                response = chatbot.process_message(
                    data['message'],
                    session_id=data.get('session_id'),
                    context=data.get('context', {})
                )
            except ImportError:
                from services.chatbot_refined import get_refined_chatbot
                chatbot = get_refined_chatbot()
                response = chatbot.generate_response(
                    data['message'],
                    session_id=data.get('session_id')
                )
            
            return jsonify(response.to_dict())
            
        except Exception as e:
            logger.error(f"Chatbot API error: {e}")
            return jsonify({
                'error': 'Service temporarily unavailable',
                'response': 'Desculpe, estou temporariamente indisponível. Tente novamente em alguns minutos.'
            }), 500
    
    @chatbot_bp.route('/api/health')
    @cache.cached(timeout=60)
    @monitor_route_performance
    def chatbot_health():
        """Chatbot health status"""
        try:
            try:
                from optimized_chatbot import get_optimized_chatbot
                chatbot = get_optimized_chatbot()
                return jsonify(chatbot.get_health_status())
            except ImportError:
                from services.chatbot_refined import get_refined_chatbot
                chatbot = get_refined_chatbot()
                return jsonify({'status': 'healthy', 'service': 'chatbot_refined'})
        except Exception as e:
            logger.error(f"Chatbot health check error: {e}")
            return jsonify({'status': 'error', 'error': str(e)}), 500
    
    @chatbot_bp.route('/api/metrics')
    @limiter.limit("10 per minute")
    @monitor_route_performance
    def chatbot_metrics():
        """Chatbot performance metrics"""
        try:
            try:
                from optimized_chatbot import get_optimized_chatbot
                chatbot = get_optimized_chatbot()
                return jsonify(chatbot.get_analytics())
            except ImportError:
                from services.chatbot_refined import get_refined_chatbot
                chatbot = get_refined_chatbot()
                return jsonify({'metrics': 'available', 'service': 'chatbot_refined'})
        except Exception as e:
            logger.error(f"Chatbot metrics error: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Error handlers
    @main_bp.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @main_bp.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        db.session.rollback()
        return render_template('500.html'), 500
    
    @main_bp.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429
    
    return [main_bp, services_bp, chatbot_bp]