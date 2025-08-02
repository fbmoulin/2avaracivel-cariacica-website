"""
API Routes for robust backend-frontend integration
Provides stable endpoints with proper error handling
"""
from flask import Blueprint, request, jsonify
from database import db
from models import Contact, ProcessConsultation, ChatMessage, AssessorMeeting
from services.chatbot_refined import get_refined_chatbot
from utils.security import sanitize_input, validate_email
import logging
from datetime import datetime
from functools import wraps
import time

logger = logging.getLogger(__name__)

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

def handle_errors(f):
    """Decorator for consistent error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': str(e), 'type': 'validation_error'}), 400
        except KeyError as e:
            return jsonify({'error': f'Missing field: {str(e)}', 'type': 'missing_field'}), 400
        except Exception as e:
            logger.error(f"API error in {f.__name__}: {str(e)}")
            return jsonify({'error': 'Internal server error', 'type': 'server_error'}), 500
    return decorated_function

def rate_limit(max_requests=60, window=60):
    """Simple rate limiting decorator"""
    requests = {}
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            now = time.time()
            # Clean old entries
            for ip in list(requests.keys()):
                requests[ip] = [t for t in requests[ip] if now - t < window]
                if not requests[ip]:
                    del requests[ip]
            
            # Check rate limit
            client_ip = request.remote_addr
            if client_ip in requests:
                if len(requests[client_ip]) >= max_requests:
                    return jsonify({'error': 'Rate limit exceeded', 'type': 'rate_limit'}), 429
            
            # Record request
            if client_ip not in requests:
                requests[client_ip] = []
            requests[client_ip].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Chat API endpoint
@api_bp.route('/chat', methods=['POST'])
@handle_errors
@rate_limit(max_requests=30, window=60)
def chat():
    """Handle chat messages with the AI chatbot"""
    data = request.get_json()
    
    if not data or 'message' not in data:
        raise ValueError("Message is required")
    
    message = sanitize_input(data['message'])
    if not message:
        raise ValueError("Message cannot be empty")
    
    # Get session ID or create new one
    session_id = data.get('session_id', request.headers.get('X-Session-ID', 'default'))
    
    # Get chatbot response
    chatbot = get_refined_chatbot()
    response = chatbot.get_response(message, session_id)
    
    # Save to database
    try:
        chat_msg = ChatMessage(
            session_id=session_id,
            user_message=message,
            bot_response=response
        )
        db.session.add(chat_msg)
        db.session.commit()
    except Exception as e:
        logger.error(f"Failed to save chat message: {e}")
        # Continue anyway - don't fail the request
    
    return jsonify({
        'response': response,
        'session_id': session_id,
        'timestamp': datetime.utcnow().isoformat()
    })

# Search API endpoint
@api_bp.route('/search', methods=['GET'])
@handle_errors
@rate_limit(max_requests=60, window=60)
def search():
    """Search for processes or content"""
    query = request.args.get('query', '').strip()
    search_type = request.args.get('type', 'all')
    
    if not query:
        raise ValueError("Query parameter is required")
    
    if len(query) > 200:
        raise ValueError("Query too long (max 200 characters)")
    
    results = {
        'query': query,
        'type': search_type,
        'results': [],
        'count': 0
    }
    
    # Search processes
    if search_type in ['all', 'process']:
        try:
            processes = db.session.query(ProcessConsultation).filter(
                ProcessConsultation.process_number.contains(query)
            ).limit(10).all()
            
            for proc in processes:
                results['results'].append({
                    'type': 'process',
                    'number': proc.process_number,
                    'consulted_at': proc.consulted_at.isoformat() if proc.consulted_at else None
                })
        except Exception as e:
            logger.error(f"Process search error: {e}")
    
    # Search contacts
    if search_type in ['all', 'contact']:
        try:
            contacts = db.session.query(Contact).filter(
                db.or_(
                    Contact.name.contains(query),
                    Contact.email.contains(query)
                )
            ).limit(5).all()
            
            for contact in contacts:
                results['results'].append({
                    'type': 'contact',
                    'name': contact.name,
                    'created_at': contact.created_at.isoformat() if contact.created_at else None
                })
        except Exception as e:
            logger.error(f"Contact search error: {e}")
    
    results['count'] = len(results['results'])
    return jsonify(results)

# Schedule availability API
@api_bp.route('/schedule', methods=['GET'])
@handle_errors
@rate_limit(max_requests=60, window=60)
def get_schedule():
    """Get available scheduling slots"""
    date_str = request.args.get('date')
    service_type = request.args.get('service_type', 'presencial')
    
    if not date_str:
        # Default to today
        date_obj = datetime.now().date()
    else:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
    
    # Get existing appointments for the date
    try:
        existing = AssessorMeeting.query.filter(
            db.func.date(AssessorMeeting.scheduled_date) == date_obj
        ).all()
        
        # Generate available slots (9:00 to 17:00, 30 min slots)
        all_slots = []
        for hour in range(9, 17):
            for minute in [0, 30]:
                slot_time = f"{hour:02d}:{minute:02d}"
                all_slots.append(slot_time)
        
        # Mark occupied slots
        occupied_times = [
            meeting.scheduled_date.strftime('%H:%M') 
            for meeting in existing 
            if meeting.scheduled_date
        ]
        
        available_slots = [
            {
                'time': slot,
                'available': slot not in occupied_times
            }
            for slot in all_slots
        ]
        
        return jsonify({
            'date': date_str,
            'service_type': service_type,
            'slots': available_slots,
            'total_available': sum(1 for s in available_slots if s['available'])
        })
        
    except Exception as e:
        logger.error(f"Schedule query error: {e}")
        raise

# Chatbot message API (alternative endpoint)
@api_bp.route('/chatbot/message', methods=['POST'])
@handle_errors
@rate_limit(max_requests=30, window=60)
def chatbot_message():
    """Alternative chatbot endpoint for compatibility"""
    return chat()

# Process consultation API
@api_bp.route('/process/consult', methods=['POST'])
@handle_errors
@rate_limit(max_requests=20, window=60)
def consult_process():
    """Record a process consultation"""
    data = request.get_json()
    
    if not data or 'process_number' not in data:
        raise ValueError("Process number is required")
    
    process_number = sanitize_input(data['process_number'])
    
    # Validate process number format
    import re
    if not re.match(r'^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$', process_number):
        raise ValueError("Invalid process number format")
    
    # Record consultation
    try:
        consultation = ProcessConsultation(
            process_number=process_number,
            requester_name="API User",  # Default for API calls
            requester_cpf="000.000.000-00",  # Default for API calls
            ip_address=request.remote_addr
        )
        db.session.add(consultation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'process_number': process_number,
            'message': 'Consultation recorded successfully'
        })
    except Exception as e:
        logger.error(f"Failed to record consultation: {e}")
        raise

# Health check for API
@api_bp.route('/health', methods=['GET'])
def api_health():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': [
            '/api/chat',
            '/api/search',
            '/api/schedule',
            '/api/chatbot/message',
            '/api/process/consult'
        ]
    })

# Test transaction endpoint for integration testing
@api_bp.route('/test-transaction', methods=['POST'])
@handle_errors
def test_transaction():
    """Test endpoint for database transaction handling"""
    try:
        # Simulate a complex transaction
        with db.session.begin():
            # Create a test record
            test_contact = Contact(
                name="Transaction Test",
                email="test@transaction.com",
                phone="(00) 0000-0000",
                subject="Test Transaction",
                message="Testing transaction handling"
            )
            db.session.add(test_contact)
            
            # Immediately delete it (rollback test)
            db.session.delete(test_contact)
        
        return jsonify({
            'status': 'success',
            'message': 'Transaction test completed'
        })
    except Exception as e:
        logger.error(f"Transaction test failed: {e}")
        raise

# Error handlers for API
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found', 'type': 'not_found'}), 404

@api_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed', 'type': 'method_not_allowed'}), 405

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'type': 'server_error'}), 500