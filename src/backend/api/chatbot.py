"""
Chatbot API - Modular Backend
RESTful endpoints for AI-powered chatbot interaction
"""
from flask import Blueprint, request, jsonify, current_app
from src.backend.models import ChatMessage
from src.backend.core.database import db
from src.backend.core.extensions import limiter
from src.backend.services.chatbot_service import ChatbotService
import logging
import uuid

logger = logging.getLogger(__name__)
chatbot_api = Blueprint('chatbot', __name__)

# Initialize chatbot service
chatbot_service = ChatbotService()


@chatbot_api.route('/chat', methods=['POST'])
@limiter.limit("30 per minute")
def chat():
    """Process chatbot conversation"""
    try:
        data = request.get_json()
        
        if not data.get('message'):
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message']
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Get bot response
        bot_response = chatbot_service.get_response(user_message, session_id)
        
        # Save conversation to database
        chat_message = ChatMessage(
            user_message=user_message,
            bot_response=bot_response['message'],
            session_id=session_id
        )
        
        db.session.add(chat_message)
        db.session.commit()
        
        return jsonify({
            'message': bot_response['message'],
            'session_id': session_id,
            'response_type': bot_response.get('response_type', 'general'),
            'confidence': bot_response.get('confidence', 0.8),
            'suggestions': bot_response.get('suggestions', [])
        })
        
    except Exception as e:
        logger.error(f"Chatbot conversation failed: {e}")
        db.session.rollback()
        return jsonify({
            'error': 'Internal server error',
            'message': 'Desculpe, ocorreu um erro. Tente novamente em alguns instantes.'
        }), 500


@chatbot_api.route('/history/<session_id>', methods=['GET'])
@limiter.limit("100 per hour")
def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        messages = ChatMessage.query.filter_by(session_id=session_id)\
                                  .order_by(ChatMessage.created_at.asc()).all()
        
        return jsonify({
            'session_id': session_id,
            'messages': [{
                'id': msg.id,
                'user_message': msg.user_message,
                'bot_response': msg.bot_response,
                'timestamp': msg.created_at.isoformat()
            } for msg in messages]
        })
        
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@chatbot_api.route('/analytics', methods=['GET'])
@limiter.limit("50 per hour")
def get_analytics():
    """Get chatbot usage analytics"""
    try:
        # Basic analytics
        total_conversations = db.session.query(ChatMessage.session_id).distinct().count()
        total_messages = ChatMessage.query.count()
        
        return jsonify({
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'average_messages_per_session': round(total_messages / max(total_conversations, 1), 2)
        })
        
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        return jsonify({'error': 'Internal server error'}), 500