"""
Security Validation System for 2ª Vara Cível de Cariacica
Comprehensive input validation, output encoding, and security checks
"""

import re
import html
import json
import hashlib
import secrets
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Comprehensive security validation system"""
    
    # XSS prevention patterns
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
        r'<applet[^>]*>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        r'<form[^>]*>',
        r'vbscript:',
        r'data:text/html',
        r'expression\s*\(',
        r'url\s*\(',
        r'@import',
        r'behavior\s*:',
        r'-moz-binding',
        r'mocha:',
        r'livescript:'
    ]
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r'\bunion\b.*\bselect\b',
        r'\bselect\b.*\bfrom\b.*\bwhere\b.*\bor\b.*[\'\"]\s*=\s*[\'\"]\s*',
        r'\bdrop\b.*\btable\b',
        r'\bdelete\b.*\bfrom\b',
        r'\binsert\b.*\binto\b',
        r'\bupdate\b.*\bset\b',
        r'\bexec\b\s*\(',
        r'\bexecute\b\s*\(',
        r'\bsp_\w+',
        r'\bxp_\w+',
        r';\s*(drop|delete|insert|update|create|alter|grant|revoke)',
        r'--\s*$',
        r'/\*.*\*/',
        r'\bchar\b\s*\(\s*\d+\s*\)',
        r'\bwaitfor\b.*\bdelay\b'
    ]
    
    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r'[;&|`$()]',
        r'\b(cat|ls|pwd|whoami|id|ps|netstat|ifconfig|ping|wget|curl|nc|sh|bash|zsh|fish)\b',
        r'\.{2,}[/\\]',
        r'[/\\](etc|proc|sys|dev|var|tmp)[/\\]',
        r'\$\{[^}]*\}',
        r'\$\([^)]*\)',
        r'`[^`]*`'
    ]
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r'\.{2,}[/\\]',
        r'[/\\]\.{2,}',
        r'%2e%2e%2f',
        r'%2e%2e%5c',
        r'\.\.%2f',
        r'\.\.%5c',
        r'%252e%252e%252f',
        r'%c0%ae%c0%ae%c0%af'
    ]

    @staticmethod
    def validate_input(value: Any, input_type: str = 'general', 
                      max_length: int = 5000, allow_html: bool = False) -> Dict[str, Any]:
        """
        Comprehensive input validation
        
        Args:
            value: Input value to validate
            input_type: Type of input (email, phone, url, etc.)
            max_length: Maximum allowed length
            allow_html: Whether to allow HTML content
            
        Returns:
            Dictionary with validation results
        """
        if value is None:
            return {'valid': True, 'sanitized': None, 'warnings': []}
        
        # Convert to string for validation
        str_value = str(value)
        warnings = []
        
        # Length validation
        if len(str_value) > max_length:
            return {
                'valid': False, 
                'error': f'Input too long (max {max_length} characters)',
                'sanitized': str_value[:max_length]
            }
        
        # Null byte detection
        if '\x00' in str_value:
            return {
                'valid': False,
                'error': 'Null bytes not allowed',
                'sanitized': str_value.replace('\x00', '')
            }
        
        # Type-specific validation
        if input_type == 'email':
            return SecurityValidator._validate_email(str_value)
        elif input_type == 'phone':
            return SecurityValidator._validate_phone(str_value)
        elif input_type == 'url':
            return SecurityValidator._validate_url(str_value)
        elif input_type == 'number':
            return SecurityValidator._validate_number(str_value)
        elif input_type == 'cpf':
            return SecurityValidator._validate_cpf(str_value)
        elif input_type == 'cnpj':
            return SecurityValidator._validate_cnpj(str_value)
        
        # General validation
        sanitized_value = SecurityValidator.sanitize_input(str_value, allow_html)
        
        # Security pattern detection
        if SecurityValidator._detect_xss(str_value):
            warnings.append('Potential XSS content detected')
        
        if SecurityValidator._detect_sql_injection(str_value):
            warnings.append('Potential SQL injection detected')
        
        if SecurityValidator._detect_command_injection(str_value):
            warnings.append('Potential command injection detected')
        
        if SecurityValidator._detect_path_traversal(str_value):
            warnings.append('Potential path traversal detected')
        
        return {
            'valid': len(warnings) == 0,
            'sanitized': sanitized_value,
            'warnings': warnings,
            'original_length': len(str_value),
            'sanitized_length': len(sanitized_value)
        }

    @staticmethod
    def sanitize_input(value: str, allow_html: bool = False) -> str:
        """Sanitize input string"""
        if not value:
            return value
        
        # Remove control characters except newlines and tabs
        sanitized = ''.join(char for char in value if ord(char) >= 32 or char in '\n\t')
        
        # HTML encoding if HTML is not allowed
        if not allow_html:
            sanitized = html.escape(sanitized, quote=True)
        
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        return sanitized

    @staticmethod
    def _validate_email(email: str) -> Dict[str, Any]:
        """Validate email address"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return {'valid': False, 'error': 'Invalid email format'}
        
        # Check for dangerous patterns
        if any(pattern in email.lower() for pattern in ['script', 'javascript', 'vbscript']):
            return {'valid': False, 'error': 'Suspicious email content'}
        
        return {'valid': True, 'sanitized': email.lower().strip()}

    @staticmethod
    def _validate_phone(phone: str) -> Dict[str, Any]:
        """Validate Brazilian phone number"""
        # Remove non-digits
        digits_only = re.sub(r'\D', '', phone)
        
        # Brazilian phone patterns
        if len(digits_only) == 10:  # Landline
            if not digits_only.startswith(('11', '12', '13', '14', '15', '16', '17', '18', '19',
                                         '21', '22', '24', '27', '28', '31', '32', '33', '34',
                                         '35', '37', '38', '41', '42', '43', '44', '45', '46',
                                         '47', '48', '49', '51', '53', '54', '55', '61', '62',
                                         '63', '64', '65', '66', '67', '68', '69', '71', '73',
                                         '74', '75', '77', '79', '81', '82', '83', '84', '85',
                                         '86', '87', '88', '89', '91', '92', '93', '94', '95',
                                         '96', '97', '98', '99')):
                return {'valid': False, 'error': 'Invalid area code'}
        elif len(digits_only) == 11:  # Mobile
            if not digits_only.startswith(('11', '12', '13', '14', '15', '16', '17', '18', '19',
                                         '21', '22', '24', '27', '28', '31', '32', '33', '34',
                                         '35', '37', '38', '41', '42', '43', '44', '45', '46',
                                         '47', '48', '49', '51', '53', '54', '55', '61', '62',
                                         '63', '64', '65', '66', '67', '68', '69', '71', '73',
                                         '74', '75', '77', '79', '81', '82', '83', '84', '85',
                                         '86', '87', '88', '89', '91', '92', '93', '94', '95',
                                         '96', '97', '98', '99')):
                return {'valid': False, 'error': 'Invalid area code'}
            if not digits_only[2] == '9':
                return {'valid': False, 'error': 'Invalid mobile number format'}
        else:
            return {'valid': False, 'error': 'Invalid phone number length'}
        
        return {'valid': True, 'sanitized': digits_only}

    @staticmethod
    def _validate_url(url: str) -> Dict[str, Any]:
        """Validate URL"""
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in ['http', 'https']:
                return {'valid': False, 'error': 'Invalid URL scheme'}
            
            # Check for suspicious patterns
            if any(pattern in url.lower() for pattern in ['javascript:', 'data:', 'vbscript:']):
                return {'valid': False, 'error': 'Suspicious URL scheme'}
            
            # Check domain
            if not parsed.netloc:
                return {'valid': False, 'error': 'Missing domain'}
            
            return {'valid': True, 'sanitized': url}
            
        except Exception:
            return {'valid': False, 'error': 'Invalid URL format'}

    @staticmethod
    def _validate_number(value: str) -> Dict[str, Any]:
        """Validate numeric input"""
        try:
            # Remove common formatting
            cleaned = re.sub(r'[,.\s]', '', value)
            
            if not cleaned.replace('-', '').isdigit():
                return {'valid': False, 'error': 'Not a valid number'}
            
            num = float(value.replace(',', '.'))
            
            # Check for reasonable ranges
            if abs(num) > 1e15:
                return {'valid': False, 'error': 'Number too large'}
            
            return {'valid': True, 'sanitized': str(num)}
            
        except (ValueError, OverflowError):
            return {'valid': False, 'error': 'Invalid number format'}

    @staticmethod
    def _validate_cpf(cpf: str) -> Dict[str, Any]:
        """Validate Brazilian CPF"""
        # Remove formatting
        digits = re.sub(r'\D', '', cpf)
        
        if len(digits) != 11:
            return {'valid': False, 'error': 'CPF must have 11 digits'}
        
        # Check for known invalid patterns
        if digits == digits[0] * 11:
            return {'valid': False, 'error': 'Invalid CPF pattern'}
        
        # Calculate verification digits
        def calculate_digit(digits, weights):
            sum_value = sum(int(digit) * weight for digit, weight in zip(digits, weights))
            remainder = sum_value % 11
            return 0 if remainder < 2 else 11 - remainder
        
        first_digit = calculate_digit(digits[:9], range(10, 1, -1))
        second_digit = calculate_digit(digits[:10], range(11, 1, -1))
        
        if digits[9] != str(first_digit) or digits[10] != str(second_digit):
            return {'valid': False, 'error': 'Invalid CPF checksum'}
        
        return {'valid': True, 'sanitized': digits}

    @staticmethod
    def _validate_cnpj(cnpj: str) -> Dict[str, Any]:
        """Validate Brazilian CNPJ"""
        # Remove formatting
        digits = re.sub(r'\D', '', cnpj)
        
        if len(digits) != 14:
            return {'valid': False, 'error': 'CNPJ must have 14 digits'}
        
        # Check for known invalid patterns
        if digits == digits[0] * 14:
            return {'valid': False, 'error': 'Invalid CNPJ pattern'}
        
        # Calculate verification digits
        def calculate_digit(digits, weights):
            sum_value = sum(int(digit) * weight for digit, weight in zip(digits, weights))
            remainder = sum_value % 11
            return 0 if remainder < 2 else 11 - remainder
        
        first_weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        second_weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        
        first_digit = calculate_digit(digits[:12], first_weights)
        second_digit = calculate_digit(digits[:13], second_weights)
        
        if digits[12] != str(first_digit) or digits[13] != str(second_digit):
            return {'valid': False, 'error': 'Invalid CNPJ checksum'}
        
        return {'valid': True, 'sanitized': digits}

    @staticmethod
    def _detect_xss(value: str) -> bool:
        """Detect XSS patterns"""
        value_lower = value.lower()
        return any(re.search(pattern, value_lower, re.IGNORECASE) 
                  for pattern in SecurityValidator.XSS_PATTERNS)

    @staticmethod
    def _detect_sql_injection(value: str) -> bool:
        """Detect SQL injection patterns"""
        value_lower = value.lower()
        return any(re.search(pattern, value_lower, re.IGNORECASE) 
                  for pattern in SecurityValidator.SQL_INJECTION_PATTERNS)

    @staticmethod
    def _detect_command_injection(value: str) -> bool:
        """Detect command injection patterns"""
        return any(re.search(pattern, value, re.IGNORECASE) 
                  for pattern in SecurityValidator.COMMAND_INJECTION_PATTERNS)

    @staticmethod
    def _detect_path_traversal(value: str) -> bool:
        """Detect path traversal patterns"""
        return any(re.search(pattern, value, re.IGNORECASE) 
                  for pattern in SecurityValidator.PATH_TRAVERSAL_PATTERNS)

    @staticmethod
    def generate_csrf_token() -> str:
        """Generate secure CSRF token"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def verify_csrf_token(token: str, session_token: str) -> bool:
        """Verify CSRF token"""
        if not token or not session_token:
            return False
        return secrets.compare_digest(token, session_token)

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash password securely"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        pwd_hash = hashlib.pbkdf2_hmac('sha256', 
                                      password.encode('utf-8'), 
                                      salt.encode('utf-8'), 
                                      100000)
        
        return pwd_hash.hex(), salt

    @staticmethod
    def verify_password(password: str, pwd_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        try:
            computed_hash = hashlib.pbkdf2_hmac('sha256',
                                              password.encode('utf-8'),
                                              salt.encode('utf-8'),
                                              100000)
            return secrets.compare_digest(pwd_hash, computed_hash.hex())
        except Exception:
            return False

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove path components
        filename = filename.split('/')[-1].split('\\')[-1]
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove control characters
        filename = ''.join(char for char in filename if ord(char) >= 32)
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        return filename or 'unnamed_file'

    @staticmethod
    def validate_file_upload(file_data: bytes, filename: str, 
                           allowed_types: List[str] = None,
                           max_size: int = 10 * 1024 * 1024) -> Dict[str, Any]:
        """Validate file upload"""
        if not file_data:
            return {'valid': False, 'error': 'No file data provided'}
        
        if len(file_data) > max_size:
            return {'valid': False, 'error': f'File too large (max {max_size} bytes)'}
        
        # Sanitize filename
        safe_filename = SecurityValidator.sanitize_filename(filename)
        
        if allowed_types:
            file_ext = safe_filename.split('.')[-1].lower() if '.' in safe_filename else ''
            if file_ext not in allowed_types:
                return {'valid': False, 'error': f'File type not allowed: {file_ext}'}
        
        # Check for executable content
        dangerous_signatures = [
            b'\x4d\x5a',  # PE executable
            b'\x7f\x45\x4c\x46',  # ELF executable
            b'#!/bin/',  # Shell script
            b'<?php',  # PHP script
        ]
        
        for signature in dangerous_signatures:
            if file_data.startswith(signature):
                return {'valid': False, 'error': 'Executable content detected'}
        
        return {
            'valid': True,
            'sanitized_filename': safe_filename,
            'file_size': len(file_data)
        }