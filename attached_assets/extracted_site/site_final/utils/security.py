import re
import html
from urllib.parse import quote

def sanitize_input(input_string):
    """Sanitize user input to prevent XSS attacks"""
    if not input_string:
        return ""
    
    # Remove HTML tags and escape special characters
    cleaned = html.escape(str(input_string).strip())
    
    # Remove potentially dangerous characters
    cleaned = re.sub(r'[<>"\']', '', cleaned)
    
    return cleaned

def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format (Brazilian)"""
    if not phone:
        return True  # Phone is optional
    
    # Remove non-numeric characters
    clean_phone = re.sub(r'\D', '', phone)
    
    # Check if it's a valid Brazilian phone number
    return len(clean_phone) >= 10 and len(clean_phone) <= 11

def validate_process_number(process_number):
    """Validate CNJ process number format"""
    if not process_number:
        return False
    
    # Remove non-numeric characters
    clean_number = re.sub(r'\D', '', process_number)
    
    # CNJ format: 20 digits
    return len(clean_number) == 20

def secure_filename(filename):
    """Make filename secure for storage"""
    if not filename:
        return ""
    
    # Remove directory traversal attempts
    filename = filename.replace('..', '')
    filename = filename.replace('/', '')
    filename = filename.replace('\\', '')
    
    # Keep only alphanumeric characters, dots, and hyphens
    filename = re.sub(r'[^a-zA-Z0-9.-]', '_', filename)
    
    return filename

def rate_limit_key(request):
    """Generate rate limiting key based on IP address"""
    return f"rate_limit_{request.remote_addr}"
