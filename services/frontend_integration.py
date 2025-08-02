"""
Frontend Integration Service
Manages frontend-backend communication and real-time updates
"""
import json
import logging
from datetime import datetime
from flask import jsonify
import hashlib

logger = logging.getLogger(__name__)

class FrontendIntegrationService:
    """Handles frontend integration and communication patterns"""
    
    def __init__(self):
        self.response_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    def create_response(self, data=None, success=True, message=None, metadata=None):
        """Create standardized API response"""
        response = {
            'success': success,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        if message:
            response['message'] = message
            
        if metadata:
            response['metadata'] = metadata
            
        return jsonify(response)
    
    def create_error_response(self, error_message, error_code=None, status_code=400):
        """Create standardized error response"""
        response = {
            'success': False,
            'timestamp': datetime.utcnow().isoformat(),
            'error': {
                'message': error_message,
                'code': error_code or 'UNKNOWN_ERROR'
            }
        }
        
        return jsonify(response), status_code
    
    def create_paginated_response(self, items, page=1, per_page=20, total=None):
        """Create paginated response for lists"""
        if total is None:
            total = len(items)
            
        total_pages = (total + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        return self.create_response(
            data=items,
            metadata={
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': total_pages,
                    'has_next': has_next,
                    'has_prev': has_prev
                }
            }
        )
    
    def cache_response(self, key, data, ttl=None):
        """Cache response data with TTL"""
        if ttl is None:
            ttl = self.cache_ttl
            
        cache_entry = {
            'data': data,
            'expires_at': datetime.utcnow().timestamp() + ttl
        }
        
        # Create hash of key for storage
        cache_key = hashlib.md5(key.encode()).hexdigest()
        self.response_cache[cache_key] = cache_entry
        
        # Cleanup expired entries
        self._cleanup_cache()
        
        return data
    
    def get_cached_response(self, key):
        """Get cached response if available and not expired"""
        cache_key = hashlib.md5(key.encode()).hexdigest()
        
        if cache_key in self.response_cache:
            entry = self.response_cache[cache_key]
            if entry['expires_at'] > datetime.utcnow().timestamp():
                return entry['data']
            else:
                # Remove expired entry
                del self.response_cache[cache_key]
                
        return None
    
    def _cleanup_cache(self):
        """Remove expired cache entries"""
        current_time = datetime.utcnow().timestamp()
        expired_keys = [
            key for key, entry in self.response_cache.items()
            if entry['expires_at'] <= current_time
        ]
        
        for key in expired_keys:
            del self.response_cache[key]
    
    def validate_request_data(self, data, required_fields, optional_fields=None):
        """Validate request data structure"""
        errors = []
        
        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate field types if specified
        if optional_fields:
            for field, field_type in optional_fields.items():
                if field in data and data[field] is not None:
                    if not isinstance(data[field], field_type):
                        errors.append(f"Invalid type for field {field}: expected {field_type.__name__}")
        
        return errors
    
    def create_websocket_message(self, event_type, data, target=None):
        """Create WebSocket message format"""
        message = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if target:
            message['target'] = target
            
        return json.dumps(message)
    
    def create_sse_event(self, event_type, data, event_id=None):
        """Create Server-Sent Event format"""
        event_lines = []
        
        if event_id:
            event_lines.append(f"id: {event_id}")
            
        event_lines.append(f"event: {event_type}")
        event_lines.append(f"data: {json.dumps(data)}")
        event_lines.append("")  # Empty line to end event
        
        return "\n".join(event_lines)
    
    def create_notification(self, title, message, notification_type='info', action=None):
        """Create notification object for frontend"""
        notification = {
            'id': hashlib.md5(f"{title}{message}{datetime.utcnow()}".encode()).hexdigest()[:8],
            'title': title,
            'message': message,
            'type': notification_type,
            'timestamp': datetime.utcnow().isoformat(),
            'read': False
        }
        
        if action:
            notification['action'] = action
            
        return notification
    
    def create_progress_update(self, task_id, progress, status='in_progress', message=None):
        """Create progress update for long-running tasks"""
        update = {
            'task_id': task_id,
            'progress': max(0, min(100, progress)),  # Ensure 0-100 range
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if message:
            update['message'] = message
            
        return update
    
    def create_form_validation_response(self, field_errors):
        """Create form validation error response"""
        return self.create_error_response(
            error_message="Validation failed",
            error_code="VALIDATION_ERROR",
            status_code=422
        ), {
            'field_errors': field_errors
        }

# Create singleton instance
frontend_integration = FrontendIntegrationService()