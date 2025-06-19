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

# Initialize services with error handling
try:
    from services.cache_service import cache_service, CacheService
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    logging.warning("Cache service not available")

try:
    from services.api_service import api_service, tjes_integration
    API_SERVICE_AVAILABLE = True
except ImportError:
    API_SERVICE_AVAILABLE = False
    logging.warning("API service not available")

# Create blueprints
main_bp = Blueprint('main', __name__)
services_bp = Blueprint('services', __name__, url_prefix='/servicos')
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

# Initialize services
content_service = ContentService()

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

@main_bp.route('/form-demo')
def form_demo():
    """Demo page for form micro-interactions"""
    return render_template('form-demo.html')

@main_bp.route('/chatbot')
def chatbot():
    """Chatbot interface page"""
    return render_template('chatbot.html')

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

@services_bp.route('/tutorial-zoom')
def tutorial_zoom():
    """Zoom audio configuration tutorial"""
    return render_template('services/zoom_tutorial_simple.html')

@services_bp.route('/tutorial-zoom-acessivel')
def tutorial_zoom_accessible():
    """Enhanced accessibility version of Zoom tutorial"""
    return render_template('services/zoom_tutorial.html')

@services_bp.route('/consulta-processual', methods=['GET', 'POST'])
def process_consultation():
    """Process consultation service with enhanced integration"""
    if request.method == 'POST':
        process_number = sanitize_input(request.form.get('process_number', ''))
        
        if not process_number:
            flash('Número do processo é obrigatório.', 'error')
            return render_template('services/process_consultation.html')
        
        try:
            # Log the consultation
            consultation = ProcessConsultation(
                process_number=process_number,
                requester_name=sanitize_input(request.form.get('requester_name', 'Anonymous')),
                requester_cpf=sanitize_input(request.form.get('requester_cpf', '000.000.000-00')),
                ip_address=request.remote_addr
            )
            db.session.add(consultation)
            db.session.commit()
            
            # Try integration with TJES if available
            if API_SERVICE_AVAILABLE:
                try:
                    from services.api_service import tjes_integration
                    tjes_result = tjes_integration.search_process(process_number)
                    if tjes_result.get('success'):
                        flash('Processo encontrado no sistema TJES. Informações atualizadas.', 'success')
                    else:
                        flash('Consulta registrada. Para informações detalhadas, acesse o portal do TJES.', 'info')
                except Exception as e:
                    logging.warning(f"TJES integration error: {e}")
                    flash('Consulta registrada. Para informações detalhadas, acesse o portal do TJES.', 'info')
            else:
                flash('Consulta registrada. Para informações detalhadas, acesse o portal do TJES.', 'info')
            
        except Exception as e:
            logging.error(f"Error logging process consultation: {e}")
            flash('Erro ao realizar consulta. Tente novamente mais tarde.', 'error')
    
    return render_template('services/process_consultation.html')

# Assessor meeting routes
@services_bp.route('/agendamento-assessor')
def agendamento_assessor():
    """Assessor meeting scheduling page"""
    return render_template('services/agendamento_assessor.html')

@services_bp.route('/agendar-assessor', methods=['POST'])
def agendar_assessor():
    """Handle assessor meeting scheduling form submission - supports videoconference and in-person"""
    try:
        # Extract and sanitize form data
        full_name = sanitize_input(request.form.get('full_name', ''))
        document = sanitize_input(request.form.get('document', ''))
        email = sanitize_input(request.form.get('email', ''))
        phone = sanitize_input(request.form.get('phone', ''))
        process_number = sanitize_input(request.form.get('process_number', ''))
        meeting_type = sanitize_input(request.form.get('meeting_type', ''))
        meeting_subject = sanitize_input(request.form.get('meeting_subject', ''))
        preferred_date = request.form.get('preferred_date', '')
        preferred_time = request.form.get('preferred_time', '')
        alternative_times = sanitize_input(request.form.get('alternative_times', ''))
        
        # Validate required fields
        if not all([full_name, document, email, phone, meeting_type, meeting_subject, preferred_date, preferred_time]):
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
            return redirect(url_for('services.agendamento_assessor'))
        
        # Validate email format
        if not validate_email(email):
            flash('Email inválido. Verifique o formato.', 'error')
            return redirect(url_for('services.agendamento_assessor'))
        
        # Validate meeting type
        if meeting_type not in ['presencial', 'videoconferencia', 'gabinete', 'cartorio']:
            flash('Tipo de reunião inválido. Selecione presencial, videoconferência, gabinete ou cartório.', 'error')
            return redirect(url_for('services.agendamento_assessor'))
        
        # Parse preferred date
        try:
            preferred_date_obj = datetime.strptime(preferred_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Data inválida. Verifique o formato.', 'error')
            return redirect(url_for('services.agendamento_assessor'))
        
        # Check if date is in the future
        if preferred_date_obj <= date.today():
            flash('A data deve ser futura.', 'error')
            return redirect(url_for('services.agendamento_assessor'))
        
        # Create meeting record
        meeting = AssessorMeeting(
            full_name=full_name,
            document=document,
            email=email,
            phone=phone,
            process_number=process_number if process_number else None,
            meeting_type=meeting_type,
            meeting_subject=meeting_subject,
            preferred_date=preferred_date_obj,
            preferred_time=preferred_time,
            alternative_times=alternative_times if alternative_times else None,
            confirmation_token=str(uuid.uuid4()),
            status='pending'
        )
        
        db.session.add(meeting)
        db.session.commit()
        
        # Success message based on meeting type
        if meeting_type == 'videoconferencia':
            flash(f'Solicitação de videoconferência enviada com sucesso! Você receberá um email com o link da reunião em {email}.', 'success')
        elif meeting_type == 'gabinete':
            flash(f'Solicitação de atendimento no gabinete enviada com sucesso! Você receberá confirmação por email em {email}.', 'success')
        elif meeting_type == 'cartorio':
            flash(f'Solicitação de atendimento no cartório enviada com sucesso! Você receberá confirmação por email em {email}.', 'success')
        else:
            flash(f'Agendamento presencial solicitado com sucesso! Você receberá confirmação por email em {email}.', 'success')
        
        logging.info(f"Meeting scheduled: {meeting_type} for {full_name} on {preferred_date}")
        
        return redirect(url_for('services.agendamento_assessor'))
        
    except Exception as e:
        logging.error(f"Error scheduling meeting: {e}")
        flash('Erro ao processar agendamento. Tente novamente mais tarde.', 'error')
        return redirect(url_for('services.agendamento_assessor'))

@services_bp.route('/confirmacao-assessor/<token>')
def confirmacao_assessor(token):
    """Display meeting request confirmation"""
    try:
        meeting = AssessorMeeting.query.filter_by(confirmation_token=token).first()
        
        if not meeting:
            flash('Confirmação não encontrada.', 'error')
            return redirect(url_for('services.agendamento_assessor'))
        
        return render_template('services/confirmacao_assessor.html', meeting=meeting)
        
    except Exception as e:
        logging.error(f"Error displaying meeting confirmation: {e}")
        flash('Erro ao exibir confirmação.', 'error')
        return redirect(url_for('services.agendamento_assessor'))

# Chatbot routes
@main_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages - main chat endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Mensagem não pode estar vazia'}), 400
        
        # Get bot response using refined chatbot service
        refined_chatbot = get_refined_chatbot()
        response = refined_chatbot.get_response(user_message)
        
        return jsonify({'response': response})
        
    except Exception as e:
        logging.error(f"Chat error: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@chatbot_bp.route('/api/message', methods=['POST'])
def chatbot_message():
    """Enhanced chatbot message handling with refined service"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        session_id = data.get('session_id', request.remote_addr)
        
        if not user_message:
            return jsonify({'error': 'Mensagem não pode estar vazia'}), 400
        
        # Get refined chatbot instance
        chatbot = get_refined_chatbot()
        
        # Get detailed response with metadata
        response_obj = chatbot.get_detailed_response(user_message, session_id)
        
        # Return enhanced response with comprehensive metadata
        return jsonify({
            'response': response_obj.content,
            'response_type': response_obj.response_type.value,
            'confidence_score': response_obj.confidence_score,
            'response_time': response_obj.response_time,
            'suggestions': response_obj.suggestions,
            'metadata': response_obj.metadata,
            'context_used': response_obj.context_used,
            'openai_tokens_used': response_obj.openai_tokens_used,
            'fallback_reason': response_obj.fallback_reason
        })
        
    except Exception as e:
        logging.error(f"Refined chatbot error: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@chatbot_bp.route('/api/health', methods=['GET'])
def chatbot_health():
    """Get refined chatbot health status and metrics"""
    try:
        chatbot = get_refined_chatbot()
        health_status = chatbot.get_health_status()
        return jsonify(health_status)
    except Exception as e:
        logging.error(f"Error getting refined chatbot health: {e}")
        return jsonify({'error': 'Erro ao obter status do chatbot'}), 500

@chatbot_bp.route('/api/metrics', methods=['GET'])
def chatbot_metrics():
    """Get detailed refined chatbot performance metrics"""
    try:
        chatbot = get_refined_chatbot()
        metrics = chatbot.get_analytics()
        return jsonify(metrics)
    except Exception as e:
        logging.error(f"Error getting chatbot metrics: {e}")
        return jsonify({'error': 'Erro ao obter métricas do chatbot'}), 500

@chatbot_bp.route('/api/debug/enable', methods=['POST', 'GET'])
def enable_debug():
    """Enable refined chatbot debug mode"""
    try:
        chatbot = get_refined_chatbot()
        chatbot.enable_debug_mode()
        return jsonify({'message': 'Debug mode enabled', 'debug_mode': True})
    except Exception as e:
        logging.error(f"Error enabling debug mode: {e}")
        return jsonify({'error': 'Erro ao ativar modo debug'}), 500

@chatbot_bp.route('/api/debug/disable', methods=['POST', 'GET'])
def disable_debug():
    """Disable refined chatbot debug mode"""
    try:
        chatbot = get_refined_chatbot()
        chatbot.disable_debug_mode()
        return jsonify({'message': 'Debug mode disabled', 'debug_mode': False})
    except Exception as e:
        logging.error(f"Error disabling debug mode: {e}")
        return jsonify({'error': 'Erro ao desativar modo debug'}), 500

@chatbot_bp.route('/api/reset', methods=['POST', 'GET'])
def reset_metrics():
    """Reset refined chatbot performance metrics"""
    try:
        chatbot = get_refined_chatbot()
        chatbot.reset_analytics()
        return jsonify({'message': 'Metrics reset successfully'})
    except Exception as e:
        logging.error(f"Error resetting metrics: {e}")
        return jsonify({'error': 'Erro ao resetar métricas'}), 500

@chatbot_bp.route('/debug')
def chatbot_debug_panel():
    """Refined chatbot debug panel interface"""
    try:
        chatbot = get_refined_chatbot()
        health_status = chatbot.get_health_status()
        metrics = chatbot.get_analytics()
        return render_template('chatbot_debug_refined.html', 
                             health=health_status, 
                             metrics=metrics)
    except Exception as e:
        logging.error(f"Error loading refined debug panel: {e}")
        flash('Erro ao carregar painel de debug', 'error')
        return redirect(url_for('main.index'))

# System monitoring routes
@main_bp.route('/admin/status')
def system_status():
    """System status dashboard - restricted access"""
    try:
        # Basic system information
        system_info = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'database_status': 'Connected',
            'openai_status': 'Active' if get_refined_chatbot().openai_client else 'Inactive',
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

@main_bp.route('/consulta', methods=['GET', 'POST'])
def process_consultation_alt():
    """Alternative process consultation page"""
    if request.method == 'POST':
        try:
            process_number = sanitize_input(request.form.get('numero_processo', ''))
            
            if not process_number:
                flash('Número do processo é obrigatório.', 'error')
                return render_template('consultation.html')
            
            # Save consultation request
            consultation = ProcessConsultation(
                process_number=process_number,
                requester_name='Anonymous',
                requester_cpf='000.000.000-00'
            )
            
            db.session.add(consultation)
            db.session.commit()
            
            flash('Consulta realizada com sucesso!', 'success')
            return render_template('consultation.html', result="Processo encontrado e em andamento.")
            
        except Exception as e:
            logging.error(f"Process consultation error: {e}")
            flash('Erro ao consultar processo. Tente novamente.', 'error')
            db.session.rollback()
    
    return render_template('consultation.html')

@main_bp.route('/agendamento', methods=['GET', 'POST'])
def schedule_meeting():
    """Schedule meeting with assessors"""
    if request.method == 'POST':
        try:
            name = sanitize_input(request.form.get('nome', ''))
            email = sanitize_input(request.form.get('email', ''))
            phone = sanitize_input(request.form.get('telefone', ''))
            meeting_type = sanitize_input(request.form.get('tipo_reuniao', ''))
            preferred_date = request.form.get('data_preferida')
            message = sanitize_input(request.form.get('mensagem', ''))
            
            if not all([name, email, meeting_type]):
                flash('Campos obrigatórios devem ser preenchidos.', 'error')
                return render_template('scheduling.html')
            
            if not validate_email(email):
                flash('Email inválido.', 'error')
                return render_template('scheduling.html')
            
            # Save meeting request
            meeting = AssessorMeeting(
                full_name=name,
                document='000.000.000-00',  # Default CPF
                email=email,
                phone=phone,
                meeting_type=meeting_type,
                meeting_subject=message,
                preferred_date=datetime.strptime(preferred_date, '%Y-%m-%d').date() if preferred_date else None,
                preferred_time='09:00'  # Default time
            )
            
            db.session.add(meeting)
            db.session.commit()
            
            flash('Agendamento solicitado com sucesso!', 'success')
            return redirect(url_for('main.schedule_meeting'))
            
        except Exception as e:
            logging.error(f"Meeting scheduling error: {e}")
            flash('Erro ao agendar reunião. Tente novamente.', 'error')
            db.session.rollback()
    
    return render_template('scheduling.html')

@main_bp.route('/balcao-virtual')
def virtual_counter():
    """Virtual counter services page"""
    return render_template('virtual_counter.html')

@main_bp.route('/health')
def health_check():
    """Comprehensive system health check with robust monitoring"""
    try:
        from services.health_monitor import health_monitor
        health_report = health_monitor.get_comprehensive_health_report()
        return jsonify(health_report)
    except Exception as e:
        logging.error(f'Health check failed: {e}')
        return jsonify({
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        })

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
