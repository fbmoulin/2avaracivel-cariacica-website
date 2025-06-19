"""
Scheduling API - Modular Backend
RESTful endpoints for assessor meeting scheduling
"""
from flask import Blueprint, request, jsonify
from src.backend.models import AssessorMeeting
from src.backend.core.database import db
from src.backend.core.extensions import limiter
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
scheduling_api = Blueprint('scheduling', __name__)


@scheduling_api.route('/meeting', methods=['POST'])
@limiter.limit("5 per minute")
def schedule_meeting():
    """Schedule assessor meeting"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['requester_name', 'requester_email', 'requester_phone', 
                          'requester_cpf', 'meeting_type', 'meeting_date', 
                          'meeting_time', 'reason']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Parse meeting date
        try:
            meeting_date = datetime.fromisoformat(data['meeting_date'])
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Create new meeting
        meeting = AssessorMeeting(
            requester_name=data['requester_name'],
            requester_email=data['requester_email'],
            requester_phone=data['requester_phone'],
            requester_cpf=data['requester_cpf'],
            meeting_type=data['meeting_type'],
            meeting_date=meeting_date,
            meeting_time=data['meeting_time'],
            reason=data['reason'],
            process_number=data.get('process_number'),
            additional_info=data.get('additional_info')
        )
        
        db.session.add(meeting)
        db.session.commit()
        
        logger.info(f"Meeting scheduled: {meeting.id} for {meeting.requester_email}")
        
        return jsonify({
            'message': 'Meeting scheduled successfully',
            'meeting_id': meeting.id,
            'confirmation_code': meeting.confirmation_code,
            'status': 'scheduled'
        }), 201
        
    except Exception as e:
        logger.error(f"Meeting scheduling failed: {e}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@scheduling_api.route('/meeting/<int:meeting_id>', methods=['GET'])
@limiter.limit("100 per hour")
def get_meeting(meeting_id):
    """Get meeting details"""
    try:
        meeting = AssessorMeeting.query.get_or_404(meeting_id)
        
        return jsonify({
            'id': meeting.id,
            'requester_name': meeting.requester_name,
            'requester_email': meeting.requester_email,
            'meeting_type': meeting.meeting_type,
            'meeting_date': meeting.meeting_date.isoformat(),
            'meeting_time': meeting.meeting_time,
            'reason': meeting.reason,
            'status': meeting.status,
            'confirmation_code': meeting.confirmation_code,
            'created_at': meeting.created_at.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching meeting {meeting_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@scheduling_api.route('/availability', methods=['GET'])
@limiter.limit("50 per hour")
def check_availability():
    """Check available time slots"""
    try:
        date_str = request.args.get('date')
        if not date_str:
            return jsonify({'error': 'Date parameter is required'}), 400
        
        try:
            target_date = datetime.fromisoformat(date_str).date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Get existing meetings for the date
        existing_meetings = AssessorMeeting.query.filter(
            db.func.date(AssessorMeeting.meeting_date) == target_date
        ).all()
        
        booked_times = [meeting.meeting_time for meeting in existing_meetings]
        
        # Available time slots (court hours: 12:00-18:00)
        available_slots = [
            '12:00', '12:30', '13:00', '13:30', '14:00', '14:30',
            '15:00', '15:30', '16:00', '16:30', '17:00', '17:30'
        ]
        
        available_times = [slot for slot in available_slots if slot not in booked_times]
        
        return jsonify({
            'date': date_str,
            'available_times': available_times,
            'booked_times': booked_times
        })
        
    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        return jsonify({'error': 'Internal server error'}), 500