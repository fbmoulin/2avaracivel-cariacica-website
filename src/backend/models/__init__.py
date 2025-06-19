"""
Database Models - Modular Backend
Centralized model definitions for the court application
"""
from src.backend.core.database import db
from datetime import datetime
import re


class Contact(db.Model):
    """Contact form submissions model"""
    __tablename__ = 'contacts'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, name, email, phone, subject, message):
        self.name = name
        self.email = email
        self.phone = phone
        self.subject = subject
        self.message = message


class ProcessConsultation(db.Model):
    """Process consultation requests model"""
    __tablename__ = 'process_consultations'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    process_number = db.Column(db.String(50), nullable=False)
    requester_name = db.Column(db.String(100), nullable=False)
    requester_cpf = db.Column(db.String(14), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, process_number, requester_name, requester_cpf):
        self.process_number = process_number
        self.requester_name = requester_name
        self.requester_cpf = requester_cpf


class ChatMessage(db.Model):
    """Chatbot conversation history model"""
    __tablename__ = 'chat_messages'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_message, bot_response, session_id=None):
        self.user_message = user_message
        self.bot_response = bot_response
        self.session_id = session_id or f"session_{int(datetime.utcnow().timestamp())}"


class AssessorMeeting(db.Model):
    """Assessor meeting appointments model"""
    __tablename__ = 'assessor_meetings'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    requester_name = db.Column(db.String(100), nullable=False)
    requester_email = db.Column(db.String(120), nullable=False)
    requester_phone = db.Column(db.String(20), nullable=False)
    requester_cpf = db.Column(db.String(14), nullable=False)
    meeting_type = db.Column(db.String(50), nullable=False)
    meeting_date = db.Column(db.DateTime, nullable=False)
    meeting_time = db.Column(db.String(10), nullable=False)
    meeting_link = db.Column(db.String(500))
    meeting_room = db.Column(db.String(100))
    reason = db.Column(db.Text, nullable=False)
    process_number = db.Column(db.String(50))
    additional_info = db.Column(db.Text)
    status = db.Column(db.String(20), default='scheduled')
    confirmation_code = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, requester_name, requester_email, requester_phone, 
                 requester_cpf, meeting_type, meeting_date, meeting_time, 
                 reason, process_number=None, additional_info=None):
        self.requester_name = requester_name
        self.requester_email = requester_email
        self.requester_phone = requester_phone
        self.requester_cpf = requester_cpf
        self.meeting_type = meeting_type
        self.meeting_date = meeting_date
        self.meeting_time = meeting_time
        self.reason = reason
        self.process_number = process_number
        self.additional_info = additional_info
        self.confirmation_code = f"CONF{int(datetime.utcnow().timestamp())}"


# Export all models
__all__ = ['Contact', 'ProcessConsultation', 'ChatMessage', 'AssessorMeeting']