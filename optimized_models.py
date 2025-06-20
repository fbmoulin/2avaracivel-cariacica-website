"""
Optimized Database Models
Enhanced with indexes, validation, and performance optimizations
"""
from database import db
from datetime import datetime, timedelta
from sqlalchemy import Index, event
from sqlalchemy.ext.hybrid import hybrid_property
import uuid
import hashlib
import re

class OptimizedBaseModel:
    """Base model with common functionality and optimizations"""
    
    def to_dict(self):
        """Enhanced serialization with type checking"""
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif hasattr(value, 'to_dict'):
                    result[key] = value.to_dict()
                else:
                    result[key] = value
        return result
    
    def update_from_dict(self, data):
        """Update model from dictionary with validation"""
        for key, value in data.items():
            if hasattr(self, key) and not key.startswith('_'):
                setattr(self, key, value)
    
    @classmethod
    def create(cls, **kwargs):
        """Factory method for creating instances"""
        instance = cls(**kwargs)
        db.session.add(instance)
        return instance

class Contact(db.Model, OptimizedBaseModel):
    """Optimized contact model with enhanced validation"""
    __tablename__ = 'contact'
    __table_args__ = (
        {'extend_existing': True},
        Index('idx_contact_created_at', 'created_at'),
        Index('idx_contact_email', 'email'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, read, responded
    priority = db.Column(db.String(10), default='normal', nullable=False)  # low, normal, high
    
    def __init__(self, name, email, phone, subject, message, **kwargs):
        self.name = name
        self.email = email
        self.phone = phone
        self.subject = subject
        self.message = message
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @hybrid_property
    def is_recent(self):
        """Check if contact is from last 24 hours"""
        return self.created_at > datetime.utcnow() - timedelta(days=1)
    
    @classmethod
    def get_recent_contacts(cls, days=7):
        """Get recent contacts efficiently"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return cls.query.filter(cls.created_at >= cutoff_date).order_by(cls.created_at.desc())
    
    def __repr__(self):
        return f'<Contact {self.name} - {self.subject[:30]}>'

class NewsItem(db.Model, OptimizedBaseModel):
    """Optimized news model with content management features"""
    __tablename__ = 'news_item'
    __table_args__ = (
        {'extend_existing': True},
        Index('idx_news_published_active', 'published_at', 'is_active'),
        Index('idx_news_featured', 'is_featured'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500), nullable=True)
    published_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    author = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(50), default='geral', nullable=False)
    view_count = db.Column(db.Integer, default=0, nullable=False)
    
    @hybrid_property
    def is_recent(self):
        """Check if news is from last 30 days"""
        return self.published_at > datetime.utcnow() - timedelta(days=30)
    
    @classmethod
    def get_featured_news(cls, limit=3):
        """Get featured news efficiently"""
        return cls.query.filter_by(is_active=True, is_featured=True)\
                      .order_by(cls.published_at.desc()).limit(limit)
    
    @classmethod
    def get_latest_news(cls, limit=5):
        """Get latest active news"""
        return cls.query.filter_by(is_active=True)\
                      .order_by(cls.published_at.desc()).limit(limit)
    
    def increment_views(self):
        """Increment view count efficiently"""
        self.view_count = (self.view_count or 0) + 1
        db.session.commit()
    
    def __repr__(self):
        return f'<NewsItem {self.title[:50]}>'

class ProcessConsultation(db.Model, OptimizedBaseModel):
    """Optimized process consultation model"""
    __tablename__ = 'process_consultation'
    __table_args__ = (
        {'extend_existing': True},
        Index('idx_process_number', 'process_number'),
        Index('idx_consultation_date', 'consulted_at'),
        Index('idx_requester_cpf', 'requester_cpf'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    process_number = db.Column(db.String(50), nullable=False, index=True)
    requester_name = db.Column(db.String(100), nullable=False)
    requester_cpf = db.Column(db.String(14), nullable=False, index=True)
    consulted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    consultation_type = db.Column(db.String(20), default='public', nullable=False)  # public, authenticated
    
    def __init__(self, process_number, requester_name, requester_cpf, **kwargs):
        self.process_number = process_number
        self.requester_name = requester_name
        self.requester_cpf = requester_cpf
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @staticmethod
    def validate_process_number(process_number):
        """Validate CNJ process number format"""
        pattern = r'^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$'
        return re.match(pattern, process_number) is not None
    
    @staticmethod
    def validate_cpf(cpf):
        """Validate CPF format and checksum"""
        cpf = re.sub(r'[^0-9]', '', cpf)
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False
        
        # Calculate verification digits
        def calculate_digit(cpf_digits, multiplier_start):
            total = sum(int(cpf_digits[i]) * (multiplier_start - i) for i in range(len(cpf_digits)))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder
        
        first_digit = calculate_digit(cpf[:9], 10)
        second_digit = calculate_digit(cpf[:10], 11)
        
        return cpf[-2:] == f"{first_digit}{second_digit}"
    
    @classmethod
    def get_consultation_stats(cls, days=30):
        """Get consultation statistics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return {
            'total': cls.query.filter(cls.consulted_at >= cutoff_date).count(),
            'today': cls.query.filter(cls.consulted_at >= datetime.utcnow().date()).count(),
            'unique_processes': db.session.query(cls.process_number).filter(
                cls.consulted_at >= cutoff_date
            ).distinct().count()
        }
    
    def __repr__(self):
        return f'<ProcessConsultation {self.process_number}>'

class AssessorMeeting(db.Model, OptimizedBaseModel):
    """Optimized assessor meeting model with enhanced scheduling"""
    __tablename__ = 'assessor_meeting'
    __table_args__ = (
        {'extend_existing': True},
        Index('idx_meeting_date_status', 'preferred_date', 'status'),
        Index('idx_meeting_email', 'email'),
        Index('idx_meeting_type', 'meeting_type'),
        Index('idx_confirmation_token', 'confirmation_token'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Personal Information
    full_name = db.Column(db.String(100), nullable=False, index=True)
    document = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    
    # Meeting Details
    process_number = db.Column(db.String(50), nullable=True)
    meeting_type = db.Column(db.String(30), nullable=False, index=True)
    meeting_subject = db.Column(db.Text, nullable=False)
    
    # Scheduling
    preferred_date = db.Column(db.Date, nullable=False, index=True)
    preferred_time = db.Column(db.String(10), nullable=False)
    alternative_times = db.Column(db.Text, nullable=True)
    
    # Meeting Information
    scheduled_date = db.Column(db.DateTime, nullable=True)
    assessor_name = db.Column(db.String(100), nullable=True)
    meeting_room = db.Column(db.String(50), nullable=True)
    meeting_link = db.Column(db.String(500), nullable=True)
    
    # Status and Metadata
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Administrative
    confirmation_token = db.Column(db.String(100), nullable=True, unique=True, index=True)
    reminder_sent = db.Column(db.Boolean, default=False, nullable=False)
    priority = db.Column(db.String(10), default='normal', nullable=False)
    
    def __init__(self, full_name, document, email, phone, meeting_type, meeting_subject, 
                 preferred_date, preferred_time, **kwargs):
        self.full_name = full_name
        self.document = document
        self.email = email
        self.phone = phone
        self.meeting_type = meeting_type
        self.meeting_subject = meeting_subject
        self.preferred_date = preferred_date
        self.preferred_time = preferred_time
        self.confirmation_token = str(uuid.uuid4())
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @hybrid_property
    def is_confirmed(self):
        """Check if meeting is confirmed"""
        return self.status in ['confirmed', 'scheduled']
    
    @hybrid_property
    def is_upcoming(self):
        """Check if meeting is in the future"""
        if self.scheduled_date:
            return self.scheduled_date > datetime.utcnow()
        return self.preferred_date >= datetime.utcnow().date()
    
    def generate_confirmation_token(self):
        """Generate unique confirmation token"""
        self.confirmation_token = str(uuid.uuid4())
        return self.confirmation_token
    
    @classmethod
    def get_pending_meetings(cls):
        """Get all pending meetings efficiently"""
        return cls.query.filter_by(status='pending').order_by(cls.created_at.desc())
    
    @classmethod
    def get_scheduled_meetings(cls, date_from=None, date_to=None):
        """Get scheduled meetings within date range"""
        query = cls.query.filter(cls.status.in_(['scheduled', 'confirmed']))
        
        if date_from:
            query = query.filter(cls.scheduled_date >= date_from)
        if date_to:
            query = query.filter(cls.scheduled_date <= date_to)
        
        return query.order_by(cls.scheduled_date.asc())
    
    def to_calendar_event(self):
        """Convert to calendar event format"""
        return {
            'id': self.id,
            'title': f'Reunião - {self.full_name}',
            'description': f'Tipo: {self.meeting_type}\nAssunto: {self.meeting_subject}',
            'start': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'location': self.meeting_room if self.meeting_type == 'presencial' else self.meeting_link,
            'attendees': [self.email],
            'status': self.status
        }
    
    def __repr__(self):
        return f'<AssessorMeeting {self.full_name} - {self.meeting_type}>'

class ChatMessage(db.Model, OptimizedBaseModel):
    """Optimized chat message model with analytics"""
    __tablename__ = 'chat_message'
    __table_args__ = (
        {'extend_existing': True},
        Index('idx_chat_session_time', 'session_id', 'created_at'),
        Index('idx_chat_created_at', 'created_at'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    session_id = db.Column(db.String(100), nullable=True, index=True)
    response_time = db.Column(db.Float, nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)
    response_type = db.Column(db.String(20), default='openai', nullable=False)
    
    def __init__(self, user_message, bot_response, session_id=None, **kwargs):
        self.user_message = user_message
        self.bot_response = bot_response
        self.session_id = session_id or str(uuid.uuid4())
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def get_session_messages(cls, session_id, limit=10):
        """Get messages for a session efficiently"""
        return cls.query.filter_by(session_id=session_id)\
                      .order_by(cls.created_at.desc()).limit(limit)
    
    @classmethod
    def get_analytics_data(cls, days=30):
        """Get chat analytics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return {
            'total_messages': cls.query.filter(cls.created_at >= cutoff_date).count(),
            'unique_sessions': db.session.query(cls.session_id).filter(
                cls.created_at >= cutoff_date
            ).distinct().count(),
            'avg_response_time': db.session.query(db.func.avg(cls.response_time)).filter(
                cls.created_at >= cutoff_date
            ).scalar() or 0
        }
    
    def __repr__(self):
        return f'<ChatMessage {self.id} - {self.session_id}>'

# Event listeners for automatic optimizations
@event.listens_for(Contact, 'before_insert')
def contact_before_insert(mapper, connection, target):
    """Auto-populate contact fields"""
    if not target.created_at:
        target.created_at = datetime.utcnow()

@event.listens_for(NewsItem, 'before_update')
def news_before_update(mapper, connection, target):
    """Update timestamp on news updates"""
    target.updated_at = datetime.utcnow()

@event.listens_for(AssessorMeeting, 'before_insert')
def meeting_before_insert(mapper, connection, target):
    """Generate confirmation token if not present"""
    if not target.confirmation_token:
        target.confirmation_token = str(uuid.uuid4())