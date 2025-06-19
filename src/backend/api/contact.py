"""
Contact API - Modular Backend
RESTful endpoints for contact form management
"""
from flask import Blueprint, request, jsonify
from src.backend.models import Contact
from src.backend.core.database import db
from src.backend.core.extensions import limiter
import logging

logger = logging.getLogger(__name__)
contact_api = Blueprint('contact', __name__)


@contact_api.route('/', methods=['POST'])
@limiter.limit("10 per minute")
def submit_contact():
    """Submit contact form"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create new contact
        contact = Contact(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', ''),
            subject=data['subject'],
            message=data['message']
        )
        
        db.session.add(contact)
        db.session.commit()
        
        logger.info(f"New contact form submitted: {contact.email}")
        
        return jsonify({
            'message': 'Contact form submitted successfully',
            'contact_id': contact.id
        }), 201
        
    except Exception as e:
        logger.error(f"Contact form submission failed: {e}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@contact_api.route('/', methods=['GET'])
@limiter.limit("100 per hour")
def get_contacts():
    """Get contact submissions (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        contacts = Contact.query.order_by(Contact.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'contacts': [{
                'id': contact.id,
                'name': contact.name,
                'email': contact.email,
                'phone': contact.phone,
                'subject': contact.subject,
                'message': contact.message,
                'created_at': contact.created_at.isoformat()
            } for contact in contacts.items],
            'total': contacts.total,
            'pages': contacts.pages,
            'current_page': page
        })
        
    except Exception as e:
        logger.error(f"Error fetching contacts: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@contact_api.route('/<int:contact_id>', methods=['GET'])
@limiter.limit("100 per hour")
def get_contact(contact_id):
    """Get specific contact by ID"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        
        return jsonify({
            'id': contact.id,
            'name': contact.name,
            'email': contact.email,
            'phone': contact.phone,
            'subject': contact.subject,
            'message': contact.message,
            'created_at': contact.created_at.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching contact {contact_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500