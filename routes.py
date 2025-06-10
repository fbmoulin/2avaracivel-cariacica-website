from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from services.content import ContentService
from services.chatbot import ChatbotService
from models import Contact, ProcessConsultation, db
from utils.security import sanitize_input, validate_email
import logging
import os
from datetime import datetime

# Create blueprints
main_bp = Blueprint('main', __name__)
services_bp = Blueprint('services', __name__, url_prefix='/servicos')
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

# Initialize services
content_service = ContentService()
chatbot_service = ChatbotService()

# Main routes
@main_bp.route('/')
def index():
    """Homepage with court overview"""
    news = content_service.get_latest_news(limit=3)
    return render_template('index.html', news=news)

@main_bp.route('/sobre')
def about():
    """About the court page"""
    return render_template('about.html')

@main_bp.route('/juiz')
def judge():
    """Judge profile page"""
    return render_template('judge.html')

@main_bp.route('/faq')
def faq():
    """FAQ page with categorized questions"""
    faq_data = content_service.get_faq_data()
    return render_template('faq.html', faq_data=faq_data)

@main_bp.route('/contato', methods=['GET', 'POST'])
def contact():
    """Contact page with form"""
    if request.method == 'POST':
        # Get form data
        name = sanitize_input(request.form.get('name', ''))
        email = sanitize_input(request.form.get('email', ''))
        phone = sanitize_input(request.form.get('phone', ''))
        subject = sanitize_input(request.form.get('subject', ''))
        message = sanitize_input(request.form.get('message', ''))
        
        # Basic validation
        if not all([name, email, subject, message]):
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
            return render_template('contact.html')
        
        if not validate_email(email):
            flash('Por favor, forneça um email válido.', 'error')
            return render_template('contact.html')
        
        try:
            # Save contact form submission
            contact = Contact(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            db.session.add(contact)
            db.session.commit()
            
            flash('Sua mensagem foi enviada com sucesso! Retornaremos em breve.', 'success')
            return redirect(url_for('main.contact'))
            
        except Exception as e:
            logging.error(f"Error saving contact form: {e}")
            flash('Erro ao enviar mensagem. Tente novamente mais tarde.', 'error')
    
    return render_template('contact.html')

@main_bp.route('/noticias')
def news():
    """News and announcements page"""
    news_items = content_service.get_news()
    return render_template('news.html', news=news_items)

# Services routes
@services_bp.route('/')
def services_index():
    """Services overview page"""
    services_data = content_service.get_services_data()
    return render_template('services/index.html', services=services_data)

@services_bp.route('/audiencias')
def hearings():
    """Hearings information page"""
    return render_template('services/hearings.html')

@services_bp.route('/agendamento')
def scheduling():
    """Scheduling service page"""
    return render_template('services/scheduling.html')

@services_bp.route('/balcao-virtual')
def virtual_desk():
    """Virtual desk service page"""
    return render_template('services/virtual_desk.html')

@services_bp.route('/certidoes')
def certificates():
    """Certificates service page"""
    return render_template('services/certificates.html')

@services_bp.route('/consulta-processual', methods=['GET', 'POST'])
def process_consultation():
    """Process consultation service"""
    if request.method == 'POST':
        process_number = sanitize_input(request.form.get('process_number', ''))
        
        if not process_number:
            flash('Número do processo é obrigatório.', 'error')
            return render_template('services/process_consultation.html')
        
        try:
            # Log the consultation
            consultation = ProcessConsultation(
                process_number=process_number,
                ip_address=request.remote_addr
            )
            db.session.add(consultation)
            db.session.commit()
            
            # In a real implementation, this would query the actual court system
            flash('Consulta realizada. Para informações detalhadas, acesse o portal do TJES.', 'info')
            
        except Exception as e:
            logging.error(f"Error logging process consultation: {e}")
            flash('Erro ao realizar consulta. Tente novamente mais tarde.', 'error')
    
    return render_template('services/process_consultation.html')

# Chatbot routes
@chatbot_bp.route('/api/message', methods=['POST'])
def chatbot_message():
    """Handle chatbot messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Mensagem não pode estar vazia'}), 400
        
        # Get bot response
        response = chatbot_service.get_response(user_message)
        
        return jsonify({'response': response})
        
    except Exception as e:
        logging.error(f"Chatbot error: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# System monitoring routes
@main_bp.route('/admin/status')
def system_status():
    """System status dashboard - restricted access"""
    try:
        # Basic system information
        system_info = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'database_status': 'Connected',
            'openai_status': 'Active' if chatbot_service.openai_client else 'Inactive',
            'server_status': 'Running'
        }
        
        # Check if debug files exist
        debug_files = {
            'health_check': os.path.exists('health_check_summary.txt'),
            'error_log': os.path.exists('errors.log'),
            'error_report': os.path.exists('error_report.txt')
        }
        
        # Get recent logs if available
        recent_errors = []
        if os.path.exists('errors.log'):
            try:
                with open('errors.log', 'r') as f:
                    lines = f.readlines()
                    recent_errors = lines[-10:]  # Last 10 lines
            except:
                pass
        
        return render_template('admin/status.html', 
                             system_info=system_info,
                             debug_files=debug_files,
                             recent_errors=recent_errors)
    except Exception as e:
        logging.error(f"Status dashboard error: {e}")
        return jsonify({'error': 'Unable to load status'}), 500

@main_bp.route('/admin/health-check')
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

@main_bp.route('/admin/error-report')
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

# Error handlers
@main_bp.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@main_bp.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
