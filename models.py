from database import db
from datetime import datetime, timedelta

class Contact(db.Model):
    """Model for contact form submissions"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Contact {self.name} - {self.subject}>'

class NewsItem(db.Model):
    """Model for news and announcements"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500), nullable=True)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<NewsItem {self.title}>'

class ProcessConsultation(db.Model):
    """Model for process consultation requests"""
    id = db.Column(db.Integer, primary_key=True)
    process_number = db.Column(db.String(50), nullable=False)
    consulted_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)
    
    def __repr__(self):
        return f'<ProcessConsultation {self.process_number}>'

class ChatMessage(db.Model):
    """Model for chatbot interactions"""
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return f'<ChatMessage {self.id}>'


class HearingSchedule(db.Model):
    """Model for hearing scheduling"""
    id = db.Column(db.Integer, primary_key=True)
    process_number = db.Column(db.String(50), nullable=False)
    hearing_type = db.Column(db.String(50), nullable=False)  # 'conciliation', 'instruction', 'judgment'
    hearing_mode = db.Column(db.String(20), nullable=False)  # 'virtual', 'in_person', 'hybrid'
    scheduled_date = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    
    # Participant information
    lawyer_name = db.Column(db.String(100), nullable=False)
    lawyer_email = db.Column(db.String(120), nullable=False)
    lawyer_phone = db.Column(db.String(20), nullable=True)
    client_name = db.Column(db.String(100), nullable=False)
    
    # Virtual meeting details
    meeting_link = db.Column(db.String(500), nullable=True)
    meeting_id = db.Column(db.String(50), nullable=True)
    meeting_password = db.Column(db.String(20), nullable=True)
    
    # Status and metadata
    status = db.Column(db.String(20), default='scheduled')  # 'scheduled', 'confirmed', 'rescheduled', 'cancelled', 'completed'
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Calendar integration
    calendar_event_id = db.Column(db.String(100), nullable=True)
    reminder_sent = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<HearingSchedule {self.process_number} - {self.scheduled_date}>'

    def to_calendar_event(self):
        """Convert to calendar event format"""
        return {
            'summary': f'Audiência - Processo {self.process_number}',
            'description': f'Tipo: {self.hearing_type}\nModo: {self.hearing_mode}\nAdvogado: {self.lawyer_name}\nCliente: {self.client_name}',
            'start': self.scheduled_date.isoformat(),
            'end': (self.scheduled_date + timedelta(minutes=self.duration_minutes)).isoformat(),
            'location': self.meeting_link if self.hearing_mode == 'virtual' else '2ª Vara Cível de Cariacica'
        }


class AvailableTimeSlot(db.Model):
    """Model for available time slots"""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    max_hearings = db.Column(db.Integer, default=1)
    current_bookings = db.Column(db.Integer, default=0)
    hearing_type = db.Column(db.String(50), nullable=True)
    
    def __repr__(self):
        return f'<TimeSlot {self.date} {self.start_time}-{self.end_time}>'

    @property
    def datetime_start(self):
        return datetime.combine(self.date, self.start_time)
    
    @property
    def datetime_end(self):
        return datetime.combine(self.date, self.end_time)
    
    @property
    def is_bookable(self):
        return self.is_available and self.current_bookings < self.max_hearings


class AssessorMeeting(db.Model):
    """Model for assessor meeting requests"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Personal Information
    full_name = db.Column(db.String(100), nullable=False)
    document = db.Column(db.String(20), nullable=False)  # CPF or RG
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    
    # Meeting Details
    process_number = db.Column(db.String(50), nullable=True)
    meeting_type = db.Column(db.String(20), nullable=False)  # 'presencial', 'virtual'
    meeting_subject = db.Column(db.Text, nullable=False)
    
    # Scheduling
    preferred_date = db.Column(db.Date, nullable=False)
    preferred_time = db.Column(db.String(10), nullable=False)
    alternative_times = db.Column(db.Text, nullable=True)
    
    # Meeting Information (when scheduled)
    scheduled_date = db.Column(db.DateTime, nullable=True)
    assessor_name = db.Column(db.String(100), nullable=True)
    meeting_room = db.Column(db.String(50), nullable=True)
    meeting_link = db.Column(db.String(500), nullable=True)
    
    # Status and Metadata
    status = db.Column(db.String(20), default='pending')  # 'pending', 'scheduled', 'confirmed', 'completed', 'cancelled'
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Administrative
    confirmation_token = db.Column(db.String(100), nullable=True)
    reminder_sent = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<AssessorMeeting {self.full_name} - {self.preferred_date}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'process_number': self.process_number,
            'meeting_type': self.meeting_type,
            'meeting_subject': self.meeting_subject,
            'preferred_date': self.preferred_date.strftime('%d/%m/%Y') if self.preferred_date else None,
            'preferred_time': self.preferred_time,
            'scheduled_date': self.scheduled_date.strftime('%d/%m/%Y às %H:%M') if self.scheduled_date else None,
            'status': self.status,
            'created_at': self.created_at.strftime('%d/%m/%Y às %H:%M')
        }
