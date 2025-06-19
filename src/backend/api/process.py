"""
Process Consultation API - Modular Backend
RESTful endpoints for process consultation management
"""
from flask import Blueprint, request, jsonify
from src.backend.models import ProcessConsultation
from src.backend.core.database import db
from src.backend.core.extensions import limiter
import logging
import re

logger = logging.getLogger(__name__)
process_api = Blueprint('process', __name__)


def validate_cpf(cpf):
    """Validate CPF format and checksum"""
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    
    # Calculate first digit
    sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digit1 = (sum1 * 10) % 11
    if digit1 == 10:
        digit1 = 0
    
    # Calculate second digit
    sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digit2 = (sum2 * 10) % 11
    if digit2 == 10:
        digit2 = 0
    
    return int(cpf[9]) == digit1 and int(cpf[10]) == digit2


@process_api.route('/consultation', methods=['POST'])
@limiter.limit("5 per minute")
def submit_consultation():
    """Submit process consultation request"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['process_number', 'requester_name', 'requester_cpf']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate CPF
        if not validate_cpf(data['requester_cpf']):
            return jsonify({'error': 'Invalid CPF format'}), 400
        
        # Create new consultation request
        consultation = ProcessConsultation(
            process_number=data['process_number'],
            requester_name=data['requester_name'],
            requester_cpf=data['requester_cpf']
        )
        
        db.session.add(consultation)
        db.session.commit()
        
        logger.info(f"Process consultation submitted: {consultation.process_number}")
        
        return jsonify({
            'message': 'Process consultation submitted successfully',
            'consultation_id': consultation.id,
            'status': 'pending_review'
        }), 201
        
    except Exception as e:
        logger.error(f"Process consultation submission failed: {e}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@process_api.route('/consultation/<int:consultation_id>', methods=['GET'])
@limiter.limit("100 per hour")
def get_consultation(consultation_id):
    """Get consultation details"""
    try:
        consultation = ProcessConsultation.query.get_or_404(consultation_id)
        
        return jsonify({
            'id': consultation.id,
            'process_number': consultation.process_number,
            'requester_name': consultation.requester_name,
            'created_at': consultation.created_at.isoformat(),
            'status': 'processed'
        })
        
    except Exception as e:
        logger.error(f"Error fetching consultation {consultation_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@process_api.route('/search', methods=['GET'])
@limiter.limit("20 per hour")
def search_process():
    """Search for process information"""
    try:
        process_number = request.args.get('number')
        if not process_number:
            return jsonify({'error': 'Process number is required'}), 400
        
        # In a real system, this would integrate with court database
        # For now, return simulated response
        return jsonify({
            'process_number': process_number,
            'status': 'active',
            'court': '2ª Vara Cível de Cariacica',
            'last_movement': 'Processo em tramitação',
            'next_hearing': None,
            'message': 'Consulte o sistema oficial do TJES para informações detalhadas'
        })
        
    except Exception as e:
        logger.error(f"Process search failed: {e}")
        return jsonify({'error': 'Internal server error'}), 500