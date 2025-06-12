"""
Hearing Scheduling Service
Handles online hearing scheduling with calendar integration
"""
import uuid
import logging
from datetime import datetime, timedelta, time, date
from typing import List, Dict, Optional, Tuple
from models import db
from services.database_service import DatabaseService
import json
import secrets
import string

class SchedulingService:
    """Service for managing hearing schedules"""

    @staticmethod
    def get_available_slots(start_date: date, end_date: date, hearing_type: str = None) -> List[Dict]:
        """Get available time slots for scheduling"""
        try:
            query = AvailableTimeSlot.query.filter(
                AvailableTimeSlot.date >= start_date,
                AvailableTimeSlot.date <= end_date,
                AvailableTimeSlot.is_available == True
            )
            
            if hearing_type:
                query = query.filter(
                    (AvailableTimeSlot.hearing_type == hearing_type) |
                    (AvailableTimeSlot.hearing_type.is_(None))
                )
            
            slots = query.filter(
                AvailableTimeSlot.current_bookings < AvailableTimeSlot.max_hearings
            ).order_by(AvailableTimeSlot.date, AvailableTimeSlot.start_time).all()
            
            return [
                {
                    'id': slot.id,
                    'date': slot.date.strftime('%Y-%m-%d'),
                    'start_time': slot.start_time.strftime('%H:%M'),
                    'end_time': slot.end_time.strftime('%H:%M'),
                    'available_spots': slot.max_hearings - slot.current_bookings,
                    'hearing_type': slot.hearing_type
                }
                for slot in slots
            ]
        except Exception as e:
            logging.error(f"Error getting available slots: {e}")
            return []

    @staticmethod
    def create_hearing_schedule(schedule_data: Dict) -> Tuple[Optional[HearingSchedule], Optional[str]]:
        """Create a new hearing schedule"""
        try:
            # Validate required fields
            required_fields = ['process_number', 'hearing_type', 'hearing_mode', 
                             'scheduled_date', 'lawyer_name', 'lawyer_email', 'client_name']
            
            for field in required_fields:
                if not schedule_data.get(field):
                    return None, f"Campo obrigatório ausente: {field}"
            
            # Parse scheduled date
            if isinstance(schedule_data['scheduled_date'], str):
                scheduled_date = datetime.fromisoformat(schedule_data['scheduled_date'])
            else:
                scheduled_date = schedule_data['scheduled_date']
            
            # Check if slot is available
            slot_id = schedule_data.get('slot_id')
            if slot_id:
                slot = AvailableTimeSlot.query.get(slot_id)
                if not slot or not slot.is_bookable:
                    return None, "Horário não disponível"
                
                # Update slot booking count
                slot.current_bookings += 1
                if slot.current_bookings >= slot.max_hearings:
                    slot.is_available = False
            
            # Generate meeting details for virtual hearings
            meeting_details = {}
            if schedule_data['hearing_mode'] in ['virtual', 'hybrid']:
                meeting_details = SchedulingService._generate_meeting_details()
            
            # Create hearing schedule
            hearing = HearingSchedule(
                process_number=schedule_data['process_number'],
                hearing_type=schedule_data['hearing_type'],
                hearing_mode=schedule_data['hearing_mode'],
                scheduled_date=scheduled_date,
                duration_minutes=schedule_data.get('duration_minutes', 60),
                lawyer_name=schedule_data['lawyer_name'],
                lawyer_email=schedule_data['lawyer_email'],
                lawyer_phone=schedule_data.get('lawyer_phone'),
                client_name=schedule_data['client_name'],
                meeting_link=meeting_details.get('meeting_link'),
                meeting_id=meeting_details.get('meeting_id'),
                meeting_password=meeting_details.get('meeting_password'),
                notes=schedule_data.get('notes')
            )
            
            db.session.add(hearing)
            DatabaseService.safe_commit()
            
            logging.info(f"Hearing scheduled successfully: {hearing.id}")
            return hearing, None
            
        except Exception as e:
            logging.error(f"Error creating hearing schedule: {e}")
            db.session.rollback()
            return None, f"Erro ao agendar audiência: {str(e)}"

    @staticmethod
    def _generate_meeting_details() -> Dict[str, str]:
        """Generate virtual meeting details"""
        meeting_id = ''.join(secrets.choice(string.digits) for _ in range(11))
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
        
        # In a real implementation, this would integrate with Zoom/Teams API
        meeting_link = f"https://meet.varacivel.jus.br/j/{meeting_id}?pwd={password}"
        
        return {
            'meeting_link': meeting_link,
            'meeting_id': meeting_id,
            'meeting_password': password
        }

    @staticmethod
    def get_hearing_schedule(hearing_id: int) -> Optional[HearingSchedule]:
        """Get a specific hearing schedule"""
        try:
            return HearingSchedule.query.get(hearing_id)
        except Exception as e:
            logging.error(f"Error getting hearing schedule: {e}")
            return None

    @staticmethod
    def update_hearing_status(hearing_id: int, status: str, notes: str = None) -> bool:
        """Update hearing status"""
        try:
            hearing = HearingSchedule.query.get(hearing_id)
            if not hearing:
                return False
            
            hearing.status = status
            hearing.updated_at = datetime.utcnow()
            if notes:
                hearing.notes = notes
            
            DatabaseService.safe_commit()
            return True
            
        except Exception as e:
            logging.error(f"Error updating hearing status: {e}")
            return False

    @staticmethod
    def reschedule_hearing(hearing_id: int, new_slot_id: int) -> Tuple[bool, Optional[str]]:
        """Reschedule a hearing to a new time slot"""
        try:
            hearing = HearingSchedule.query.get(hearing_id)
            if not hearing:
                return False, "Audiência não encontrada"
            
            new_slot = AvailableTimeSlot.query.get(new_slot_id)
            if not new_slot or not new_slot.is_bookable:
                return False, "Novo horário não disponível"
            
            # Free up the old slot
            old_date = hearing.scheduled_date.date()
            old_time = hearing.scheduled_date.time()
            old_slot = AvailableTimeSlot.query.filter(
                AvailableTimeSlot.date == old_date,
                AvailableTimeSlot.start_time <= old_time,
                AvailableTimeSlot.end_time > old_time
            ).first()
            
            if old_slot:
                old_slot.current_bookings = max(0, old_slot.current_bookings - 1)
                old_slot.is_available = True
            
            # Book the new slot
            new_slot.current_bookings += 1
            if new_slot.current_bookings >= new_slot.max_hearings:
                new_slot.is_available = False
            
            # Update hearing
            hearing.scheduled_date = new_slot.datetime_start
            hearing.status = 'rescheduled'
            hearing.updated_at = datetime.utcnow()
            
            DatabaseService.safe_commit()
            return True, None
            
        except Exception as e:
            logging.error(f"Error rescheduling hearing: {e}")
            return False, f"Erro ao reagendar: {str(e)}"

    @staticmethod
    def cancel_hearing(hearing_id: int, reason: str = None) -> bool:
        """Cancel a hearing and free up the time slot"""
        try:
            hearing = HearingSchedule.query.get(hearing_id)
            if not hearing:
                return False
            
            # Free up the time slot
            hearing_date = hearing.scheduled_date.date()
            hearing_time = hearing.scheduled_date.time()
            slot = AvailableTimeSlot.query.filter(
                AvailableTimeSlot.date == hearing_date,
                AvailableTimeSlot.start_time <= hearing_time,
                AvailableTimeSlot.end_time > hearing_time
            ).first()
            
            if slot:
                slot.current_bookings = max(0, slot.current_bookings - 1)
                slot.is_available = True
            
            # Update hearing status
            hearing.status = 'cancelled'
            hearing.updated_at = datetime.utcnow()
            if reason:
                hearing.notes = f"Cancelada: {reason}"
            
            DatabaseService.safe_commit()
            return True
            
        except Exception as e:
            logging.error(f"Error cancelling hearing: {e}")
            return False

    @staticmethod
    def get_hearings_by_date_range(start_date: date, end_date: date, status: str = None) -> List[HearingSchedule]:
        """Get hearings within a date range"""
        try:
            query = HearingSchedule.query.filter(
                HearingSchedule.scheduled_date >= datetime.combine(start_date, time.min),
                HearingSchedule.scheduled_date <= datetime.combine(end_date, time.max)
            )
            
            if status:
                query = query.filter(HearingSchedule.status == status)
            
            return query.order_by(HearingSchedule.scheduled_date).all()
            
        except Exception as e:
            logging.error(f"Error getting hearings by date range: {e}")
            return []

    @staticmethod
    def create_default_time_slots(start_date: date, end_date: date) -> bool:
        """Create default time slots for court schedule"""
        try:
            current_date = start_date
            
            while current_date <= end_date:
                # Skip weekends
                if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                    # Create morning slots (14:00 - 16:00)
                    morning_slots = [
                        (time(14, 0), time(15, 0)),
                        (time(15, 0), time(16, 0))
                    ]
                    
                    # Create afternoon slots (16:30 - 18:00)
                    afternoon_slots = [
                        (time(16, 30), time(17, 30)),
                        (time(17, 30), time(18, 30))
                    ]
                    
                    all_slots = morning_slots + afternoon_slots
                    
                    for start_time, end_time in all_slots:
                        # Check if slot already exists
                        existing_slot = AvailableTimeSlot.query.filter(
                            AvailableTimeSlot.date == current_date,
                            AvailableTimeSlot.start_time == start_time
                        ).first()
                        
                        if not existing_slot:
                            slot = AvailableTimeSlot(
                                date=current_date,
                                start_time=start_time,
                                end_time=end_time,
                                max_hearings=2,  # Allow 2 hearings per slot
                                current_bookings=0
                            )
                            db.session.add(slot)
                
                current_date += timedelta(days=1)
            
            DatabaseService.safe_commit()
            return True
            
        except Exception as e:
            logging.error(f"Error creating default time slots: {e}")
            return False

    @staticmethod
    def get_hearing_statistics(start_date: date, end_date: date) -> Dict:
        """Get hearing statistics for a date range"""
        try:
            hearings = SchedulingService.get_hearings_by_date_range(start_date, end_date)
            
            stats = {
                'total_hearings': len(hearings),
                'by_status': {},
                'by_type': {},
                'by_mode': {},
                'virtual_percentage': 0
            }
            
            for hearing in hearings:
                # Count by status
                status = hearing.status
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                
                # Count by type
                h_type = hearing.hearing_type
                stats['by_type'][h_type] = stats['by_type'].get(h_type, 0) + 1
                
                # Count by mode
                mode = hearing.hearing_mode
                stats['by_mode'][mode] = stats['by_mode'].get(mode, 0) + 1
            
            # Calculate virtual percentage
            virtual_count = stats['by_mode'].get('virtual', 0)
            if stats['total_hearings'] > 0:
                stats['virtual_percentage'] = round((virtual_count / stats['total_hearings']) * 100, 1)
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting hearing statistics: {e}")
            return {}

# Initialize default slots for the next 30 days
def initialize_scheduling_system():
    """Initialize the scheduling system with default time slots"""
    try:
        start_date = date.today()
        end_date = start_date + timedelta(days=30)
        return SchedulingService.create_default_time_slots(start_date, end_date)
    except Exception as e:
        logging.error(f"Error initializing scheduling system: {e}")
        return False