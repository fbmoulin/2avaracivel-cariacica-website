"""
Optimized Database Models for 2ª Vara Cível de Cariacica
Enhanced with performance optimizations, validation, and better relationships
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
import re

Base = declarative_base()

class TimestampMixin:
    """Mixin for common timestamp fields"""
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)

class Contact(Base, TimestampMixin):
    """Enhanced Contact model with validation and indexing"""
    __tablename__ = 'contacts'
    __table_args__ = (
        Index('idx_contact_email', 'email'),
        Index('idx_contact_created', 'created_at'),
        Index('idx_contact_status', 'status'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    phone = Column(String(20))
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), default='pending', nullable=False)  # pending, read, responded
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(String(500))
    
    def __init__(self, name, email, phone, subject, message, ip_address=None, user_agent=None):
        self.name = name.strip()
        self.email = email.lower().strip()
        self.phone = phone.strip() if phone else None
        self.subject = subject.strip()
        self.message = message.strip()
        self.ip_address = ip_address
        self.user_agent = user_agent[:500] if user_agent else None
    
    @validates('email')
    def validate_email(self, key, address):
        """Validate email format"""
        if not address:
            raise ValueError("Email é obrigatório")
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, address):
            raise ValueError("Formato de email inválido")
        
        return address.lower().strip()
    
    @validates('phone')
    def validate_phone(self, key, phone):
        """Validate Brazilian phone format"""
        if not phone:
            return None
            
        # Remove all non-digits
        phone_digits = re.sub(r'\D', '', phone)
        
        # Brazilian phone: 10 or 11 digits
        if len(phone_digits) not in [10, 11]:
            raise ValueError("Telefone deve ter 10 ou 11 dígitos")
            
        return phone_digits
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'subject': self.subject,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ProcessConsultation(Base, TimestampMixin):
    """Enhanced Process Consultation model with validation"""
    __tablename__ = 'process_consultations'
    __table_args__ = (
        Index('idx_process_number', 'process_number'),
        Index('idx_requester_cpf', 'requester_cpf'),
        Index('idx_consultation_created', 'created_at'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True)
    process_number = Column(String(50), nullable=False)
    requester_name = Column(String(100), nullable=False)
    requester_cpf = Column(String(14), nullable=False)
    consultation_type = Column(String(30), default='general', nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    def __init__(self, process_number, requester_name, requester_cpf, 
                 consultation_type='general', ip_address=None, user_agent=None):
        self.process_number = process_number.strip()
        self.requester_name = requester_name.strip()
        self.requester_cpf = self.format_cpf(requester_cpf)
        self.consultation_type = consultation_type
        self.ip_address = ip_address
        self.user_agent = user_agent[:500] if user_agent else None
    
    @staticmethod
    def format_cpf(cpf):
        """Format and validate CPF"""
        if not cpf:
            raise ValueError("CPF é obrigatório")
        
        # Remove all non-digits
        cpf_digits = re.sub(r'\D', '', cpf)
        
        if len(cpf_digits) != 11:
            raise ValueError("CPF deve ter 11 dígitos")
        
        # Format CPF: 000.000.000-00
        return f"{cpf_digits[:3]}.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:]}"
    
    @validates('process_number')
    def validate_process_number(self, key, process_number):
        """Validate process number format"""
        if not process_number:
            raise ValueError("Número do processo é obrigatório")
        
        # Remove spaces and special characters
        clean_number = re.sub(r'[^\d-]', '', process_number.strip())
        
        if len(clean_number) < 10:
            raise ValueError("Número do processo inválido")
        
        return clean_number
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'process_number': self.process_number,
            'requester_name': self.requester_name,
            'requester_cpf': self.requester_cpf,
            'consultation_type': self.consultation_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ChatMessage(Base, TimestampMixin):
    """Enhanced Chat Message model with conversation management"""
    __tablename__ = 'chat_messages'
    __table_args__ = (
        Index('idx_chat_session', 'session_id'),
        Index('idx_chat_created', 'created_at'),
        Index('idx_chat_response_type', 'response_type'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), nullable=False)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    response_type = Column(String(30), default='general')  # predefined, openai, fallback, meeting
    confidence_score = Column(String(10))  # low, medium, high
    processing_time = Column(String(20))  # in milliseconds
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    def __init__(self, user_message, bot_response, session_id=None, response_type='general',
                 confidence_score=None, processing_time=None, ip_address=None, user_agent=None):
        self.user_message = user_message.strip()
        self.bot_response = bot_response.strip()
        self.session_id = session_id or self.generate_session_id()
        self.response_type = response_type
        self.confidence_score = confidence_score
        self.processing_time = processing_time
        self.ip_address = ip_address
        self.user_agent = user_agent[:500] if user_agent else None
    
    @staticmethod
    def generate_session_id():
        """Generate unique session ID"""
        import uuid
        return str(uuid.uuid4())
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_message': self.user_message,
            'bot_response': self.bot_response,
            'response_type': self.response_type,
            'confidence_score': self.confidence_score,
            'processing_time': self.processing_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AssessorMeeting(Base, TimestampMixin):
    """Enhanced Assessor Meeting model with comprehensive service types"""
    __tablename__ = 'assessor_meetings'
    __table_args__ = (
        Index('idx_meeting_date', 'preferred_date'),
        Index('idx_meeting_type', 'meeting_type'),
        Index('idx_meeting_status', 'status'),
        Index('idx_meeting_created', 'created_at'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True)
    
    # Personal Information
    full_name = Column(String(100), nullable=False)
    cpf = Column(String(14), nullable=False)
    email = Column(String(120), nullable=False)
    phone = Column(String(20), nullable=False)
    
    # Meeting Details
    meeting_type = Column(String(30), nullable=False)  # presencial, videoconferencia, gabinete, cartorio
    preferred_date = Column(String(20), nullable=False)
    preferred_time = Column(String(20), nullable=False)
    alternative_date = Column(String(20))
    alternative_time = Column(String(20))
    
    # Service Information
    service_description = Column(Text, nullable=False)
    process_number = Column(String(50))
    urgency_level = Column(String(20), default='normal')  # low, normal, high, urgent
    
    # Meeting Configuration
    meeting_link = Column(String(500))  # For video conferences
    meeting_room = Column(String(50))   # For in-person meetings
    meeting_notes = Column(Text)
    
    # Status and Tracking
    status = Column(String(20), default='pending')  # pending, scheduled, confirmed, completed, cancelled
    confirmation_code = Column(String(20))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Administrative
    assigned_to = Column(String(100))
    scheduled_datetime = Column(DateTime)
    completed_at = Column(DateTime)
    
    def __init__(self, full_name, cpf, email, phone, meeting_type, preferred_date, 
                 preferred_time, service_description, process_number=None, 
                 alternative_date=None, alternative_time=None, urgency_level='normal',
                 ip_address=None, user_agent=None):
        self.full_name = full_name.strip()
        self.cpf = ProcessConsultation.format_cpf(cpf)  # Reuse CPF validation
        self.email = email.lower().strip()
        self.phone = re.sub(r'\D', '', phone)  # Store only digits
        self.meeting_type = meeting_type
        self.preferred_date = preferred_date
        self.preferred_time = preferred_time
        self.alternative_date = alternative_date
        self.alternative_time = alternative_time
        self.service_description = service_description.strip()
        self.process_number = process_number.strip() if process_number else None
        self.urgency_level = urgency_level
        self.ip_address = ip_address
        self.user_agent = user_agent[:500] if user_agent else None
        self.confirmation_code = self.generate_confirmation_code()
    
    @staticmethod
    def generate_confirmation_code():
        """Generate unique confirmation code"""
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    @validates('email')
    def validate_email(self, key, address):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, address):
            raise ValueError("Formato de email inválido")
        return address.lower().strip()
    
    @validates('meeting_type')
    def validate_meeting_type(self, key, meeting_type):
        """Validate meeting type"""
        valid_types = ['presencial', 'videoconferencia', 'gabinete', 'cartorio']
        if meeting_type not in valid_types:
            raise ValueError(f"Tipo de reunião deve ser um de: {', '.join(valid_types)}")
        return meeting_type
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'cpf': self.cpf,
            'email': self.email,
            'phone': self.phone,
            'meeting_type': self.meeting_type,
            'preferred_date': self.preferred_date,
            'preferred_time': self.preferred_time,
            'alternative_date': self.alternative_date,
            'alternative_time': self.alternative_time,
            'service_description': self.service_description,
            'process_number': self.process_number,
            'urgency_level': self.urgency_level,
            'status': self.status,
            'confirmation_code': self.confirmation_code,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SystemLog(Base, TimestampMixin):
    """System logging model for monitoring and debugging"""
    __tablename__ = 'system_logs'
    __table_args__ = (
        Index('idx_log_level', 'log_level'),
        Index('idx_log_source', 'source'),
        Index('idx_log_created', 'created_at'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True)
    log_level = Column(String(20), nullable=False)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    source = Column(String(50), nullable=False)     # chatbot, contact, process, meeting, system
    message = Column(Text, nullable=False)
    details = Column(Text)  # JSON or additional details
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    session_id = Column(String(100))
    
    def __init__(self, log_level, source, message, details=None, ip_address=None, 
                 user_agent=None, session_id=None):
        self.log_level = log_level.upper()
        self.source = source
        self.message = message
        self.details = details
        self.ip_address = ip_address
        self.user_agent = user_agent[:500] if user_agent else None
        self.session_id = session_id
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'log_level': self.log_level,
            'source': self.source,
            'message': self.message,
            'details': self.details,
            'ip_address': self.ip_address,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserSession(Base, TimestampMixin):
    """Enhanced user session tracking"""
    __tablename__ = 'user_sessions'
    __table_args__ = (
        Index('idx_session_id', 'session_id'),
        Index('idx_session_ip', 'ip_address'),
        Index('idx_session_created', 'created_at'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), unique=True, nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(500))
    last_activity = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    page_views = Column(Integer, default=1)
    chat_messages = Column(Integer, default=0)
    forms_submitted = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    def __init__(self, session_id, ip_address, user_agent=None):
        self.session_id = session_id
        self.ip_address = ip_address
        self.user_agent = user_agent[:500] if user_agent else None
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now(timezone.utc)
    
    def increment_page_views(self):
        """Increment page view counter"""
        self.page_views += 1
        self.update_activity()
    
    def increment_chat_messages(self):
        """Increment chat message counter"""
        self.chat_messages += 1
        self.update_activity()
    
    def increment_forms_submitted(self):
        """Increment forms submitted counter"""
        self.forms_submitted += 1
        self.update_activity()
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'ip_address': self.ip_address,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'page_views': self.page_views,
            'chat_messages': self.chat_messages,
            'forms_submitted': self.forms_submitted,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }