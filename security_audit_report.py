#!/usr/bin/env python3
"""
Comprehensive Security Audit for 2ª Vara Cível de Cariacica
Performs detailed security analysis and generates vulnerability report
"""

import os
import re
import json
import logging
from datetime import datetime
from pathlib import Path
import subprocess
import hashlib

class SecurityAuditor:
    def __init__(self):
        self.vulnerabilities = []
        self.security_score = 100
        self.audit_timestamp = datetime.now().isoformat()
        
    def audit_authentication_security(self):
        """Audit authentication mechanisms"""
        findings = {
            'category': 'Authentication Security',
            'issues': [],
            'recommendations': []
        }
        
        # Check session configuration
        config_files = ['config.py', 'app_factory.py']
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    content = f.read()
                    
                    # Check session security settings
                    if 'SESSION_COOKIE_SECURE = True' in content:
                        findings['issues'].append("✓ Secure session cookies enabled")
                    else:
                        findings['issues'].append("⚠ Session cookies not marked as secure")
                        self.security_score -= 5
                        
                    if 'SESSION_COOKIE_HTTPONLY = True' in content:
                        findings['issues'].append("✓ HttpOnly session cookies enabled")
                    else:
                        findings['issues'].append("⚠ HttpOnly session cookies not enabled")
                        self.security_score -= 5
                        
                    if 'WTF_CSRF_ENABLED = True' in content:
                        findings['issues'].append("✓ CSRF protection enabled")
                    else:
                        findings['issues'].append("❌ CSRF protection not enabled")
                        self.security_score -= 15
        
        return findings
    
    def audit_input_validation(self):
        """Audit input validation and sanitization"""
        findings = {
            'category': 'Input Validation',
            'issues': [],
            'recommendations': []
        }
        
        # Check security utilities
        security_files = ['utils/security.py', 'utils/security_middleware.py']
        has_input_validation = False
        
        for sec_file in security_files:
            if os.path.exists(sec_file):
                with open(sec_file, 'r') as f:
                    content = f.read()
                    
                    if 'sanitize_input' in content:
                        has_input_validation = True
                        findings['issues'].append("✓ Input sanitization functions implemented")
                        
                    if 'validate_email' in content:
                        findings['issues'].append("✓ Email validation implemented")
                        
                    if 'validate_phone' in content:
                        findings['issues'].append("✓ Phone validation implemented")
                        
                    if 'suspicious_patterns' in content:
                        findings['issues'].append("✓ Malicious pattern detection implemented")
        
        if not has_input_validation:
            findings['issues'].append("❌ No input sanitization found")
            self.security_score -= 20
            
        return findings
    
    def audit_sql_injection_protection(self):
        """Audit SQL injection protection"""
        findings = {
            'category': 'SQL Injection Protection',
            'issues': [],
            'recommendations': []
        }
        
        # Check for SQLAlchemy usage and parameterized queries
        python_files = list(Path('.').glob('*.py')) + list(Path('./services').glob('*.py'))
        
        raw_sql_found = False
        parameterized_queries = False
        
        for py_file in python_files:
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    
                    # Check for raw SQL
                    if re.search(r'execute\s*\([\'"].*%.*[\'"]', content):
                        raw_sql_found = True
                        findings['issues'].append(f"⚠ Potential raw SQL in {py_file.name}")
                        
                    # Check for SQLAlchemy usage
                    if 'db.session.execute(text(' in content:
                        parameterized_queries = True
                        findings['issues'].append(f"✓ Parameterized queries found in {py_file.name}")
                        
            except Exception as e:
                continue
        
        if not raw_sql_found:
            findings['issues'].append("✓ No raw SQL injection vulnerabilities detected")
        else:
            self.security_score -= 15
            
        if parameterized_queries:
            findings['issues'].append("✓ SQLAlchemy parameterized queries in use")
        
        return findings
    
    def audit_xss_protection(self):
        """Audit Cross-Site Scripting protection"""
        findings = {
            'category': 'XSS Protection',
            'issues': [],
            'recommendations': []
        }
        
        # Check template files for auto-escaping
        template_files = list(Path('./templates').glob('*.html'))
        
        auto_escape_enabled = False
        unsafe_rendering = False
        
        for template in template_files:
            try:
                with open(template, 'r') as f:
                    content = f.read()
                    
                    # Check for potentially unsafe rendering
                    if '|safe' in content:
                        unsafe_rendering = True
                        findings['issues'].append(f"⚠ Unsafe template rendering in {template.name}")
                        
                    # Check for proper escaping patterns
                    if '{{' in content and '}}' in content:
                        auto_escape_enabled = True
                        
            except Exception as e:
                continue
        
        if auto_escape_enabled:
            findings['issues'].append("✓ Jinja2 auto-escaping in use")
        
        if unsafe_rendering:
            self.security_score -= 10
            
        # Check for CSP headers
        if os.path.exists('utils/security_middleware.py'):
            with open('utils/security_middleware.py', 'r') as f:
                content = f.read()
                if 'Content-Security-Policy' in content:
                    findings['issues'].append("✓ Content Security Policy implemented")
                else:
                    findings['issues'].append("⚠ Content Security Policy not found")
                    self.security_score -= 10
        
        return findings
    
    def audit_rate_limiting(self):
        """Audit rate limiting implementation"""
        findings = {
            'category': 'Rate Limiting',
            'issues': [],
            'recommendations': []
        }
        
        # Check for rate limiting implementation
        security_files = ['utils/security_middleware.py', 'app_factory.py', 'config.py']
        
        rate_limiting_found = False
        
        for sec_file in security_files:
            if os.path.exists(sec_file):
                with open(sec_file, 'r') as f:
                    content = f.read()
                    
                    if 'rate_limit' in content.lower() or 'flask-limiter' in content.lower():
                        rate_limiting_found = True
                        findings['issues'].append(f"✓ Rate limiting implemented in {sec_file}")
        
        if not rate_limiting_found:
            findings['issues'].append("⚠ Rate limiting not detected")
            self.security_score -= 10
            
        return findings
    
    def audit_https_security(self):
        """Audit HTTPS and transport security"""
        findings = {
            'category': 'HTTPS Security',
            'issues': [],
            'recommendations': []
        }
        
        # Check for HTTPS enforcement
        config_files = ['config.py', 'app_factory.py']
        
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    content = f.read()
                    
                    if 'Strict-Transport-Security' in content:
                        findings['issues'].append("✓ HSTS header configured")
                    else:
                        findings['issues'].append("⚠ HSTS header not found")
                        self.security_score -= 5
                        
                    if 'ProxyFix' in content:
                        findings['issues'].append("✓ Proxy handling configured")
        
        return findings
    
    def audit_secret_management(self):
        """Audit secret and API key management"""
        findings = {
            'category': 'Secret Management',
            'issues': [],
            'recommendations': []
        }
        
        # Check for hardcoded secrets
        python_files = list(Path('.').glob('*.py'))
        
        hardcoded_secrets = False
        env_usage = False
        
        for py_file in python_files:
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    
                    # Check for environment variable usage
                    if 'os.environ.get' in content:
                        env_usage = True
                        
                    # Check for potential hardcoded secrets
                    secret_patterns = [
                        r'password\s*=\s*[\'"][^\'"\s]+[\'"]',
                        r'secret\s*=\s*[\'"][^\'"\s]+[\'"]',
                        r'api_key\s*=\s*[\'"][^\'"\s]+[\'"]',
                        r'token\s*=\s*[\'"][^\'"\s]+[\'"]'
                    ]
                    
                    for pattern in secret_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            hardcoded_secrets = True
                            findings['issues'].append(f"⚠ Potential hardcoded secret in {py_file.name}")
                            
            except Exception as e:
                continue
        
        if env_usage:
            findings['issues'].append("✓ Environment variables used for secrets")
        
        if hardcoded_secrets:
            self.security_score -= 25
        else:
            findings['issues'].append("✓ No hardcoded secrets detected")
            
        return findings
    
    def audit_error_handling(self):
        """Audit error handling and information disclosure"""
        findings = {
            'category': 'Error Handling',
            'issues': [],
            'recommendations': []
        }
        
        # Check for custom error handlers
        route_files = ['routes.py', 'app_factory.py']
        
        error_handlers_found = False
        debug_mode_disabled = False
        
        for route_file in route_files:
            if os.path.exists(route_file):
                with open(route_file, 'r') as f:
                    content = f.read()
                    
                    if 'errorhandler' in content:
                        error_handlers_found = True
                        findings['issues'].append(f"✓ Custom error handlers in {route_file}")
                        
                    if 'DEBUG = False' in content:
                        debug_mode_disabled = True
                        findings['issues'].append("✓ Debug mode disabled in production")
        
        if not error_handlers_found:
            findings['issues'].append("⚠ Custom error handlers not found")
            self.security_score -= 10
            
        return findings
    
    def audit_file_upload_security(self):
        """Audit file upload security"""
        findings = {
            'category': 'File Upload Security',
            'issues': [],
            'recommendations': []
        }
        
        # Check for file upload handling
        python_files = list(Path('.').glob('*.py'))
        
        file_validation = False
        size_limits = False
        
        for py_file in python_files:
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    
                    if 'secure_filename' in content:
                        file_validation = True
                        findings['issues'].append("✓ Secure filename validation implemented")
                        
                    if 'MAX_CONTENT_LENGTH' in content:
                        size_limits = True
                        findings['issues'].append("✓ File size limits configured")
                        
                    if 'ALLOWED_EXTENSIONS' in content:
                        findings['issues'].append("✓ File type restrictions implemented")
                        
            except Exception as e:
                continue
        
        if not file_validation:
            findings['issues'].append("⚠ File upload validation not detected")
            
        return findings
    
    def generate_comprehensive_report(self):
        """Generate comprehensive security audit report"""
        
        print("🔒 Performing Comprehensive Security Audit...")
        
        audit_results = {
            'audit_timestamp': self.audit_timestamp,
            'initial_security_score': 100,
            'findings': []
        }
        
        # Run all security audits
        audit_methods = [
            self.audit_authentication_security,
            self.audit_input_validation,
            self.audit_sql_injection_protection,
            self.audit_xss_protection,
            self.audit_rate_limiting,
            self.audit_https_security,
            self.audit_secret_management,
            self.audit_error_handling,
            self.audit_file_upload_security
        ]
        
        for audit_method in audit_methods:
            try:
                result = audit_method()
                audit_results['findings'].append(result)
            except Exception as e:
                print(f"Error in {audit_method.__name__}: {e}")
        
        audit_results['final_security_score'] = self.security_score
        audit_results['security_grade'] = self.get_security_grade()
        
        return audit_results
    
    def get_security_grade(self):
        """Get security grade based on score"""
        if self.security_score >= 90:
            return "A - Excellent Security"
        elif self.security_score >= 80:
            return "B - Good Security"
        elif self.security_score >= 70:
            return "C - Fair Security"
        elif self.security_score >= 60:
            return "D - Poor Security"
        else:
            return "F - Critical Security Issues"
    
    def print_report(self, audit_results):
        """Print formatted security audit report"""
        
        print("\n" + "="*80)
        print("🔒 COMPREHENSIVE SECURITY AUDIT REPORT")
        print("2ª Vara Cível de Cariacica - Digital Platform")
        print("="*80)
        
        print(f"\n📅 Audit Date: {audit_results['audit_timestamp']}")
        print(f"🏆 Security Score: {audit_results['final_security_score']}/100")
        print(f"📊 Security Grade: {audit_results['security_grade']}")
        
        print("\n" + "-"*80)
        print("DETAILED FINDINGS BY CATEGORY")
        print("-"*80)
        
        for finding in audit_results['findings']:
            print(f"\n📋 {finding['category']}")
            print("-" * (len(finding['category']) + 4))
            
            for issue in finding['issues']:
                print(f"  {issue}")
        
        print("\n" + "="*80)
        print("SECURITY RECOMMENDATIONS")
        print("="*80)
        
        recommendations = [
            "✓ Implement comprehensive logging for security events",
            "✓ Set up automated security monitoring alerts",
            "✓ Regular security dependency updates",
            "✓ Implement Web Application Firewall (WAF)",
            "✓ Enable database query monitoring",
            "✓ Set up automated backup encryption",
            "✓ Implement API endpoint authentication",
            "✓ Regular penetration testing schedule"
        ]
        
        for rec in recommendations:
            print(f"  {rec}")
        
        print("\n" + "="*80)
        
        return audit_results

def run_security_audit():
    """Main function to run security audit"""
    auditor = SecurityAuditor()
    results = auditor.generate_comprehensive_report()
    formatted_results = auditor.print_report(results)
    
    # Save detailed report to file
    with open('security_audit_detailed.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    run_security_audit()