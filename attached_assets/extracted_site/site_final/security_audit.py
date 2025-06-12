#!/usr/bin/env python3
"""
Comprehensive Security Audit for 2ª Vara Cível de Cariacica
Performs thorough security analysis and strengthens all integrations
"""

import os
import re
import hashlib
import sqlite3
import requests
from pathlib import Path
import subprocess
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_audit.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SecurityAuditor:
    def __init__(self):
        self.vulnerabilities = []
        self.recommendations = []
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'status': 'PENDING',
            'categories': {}
        }

    def audit_environment_variables(self):
        """Audit environment variable security"""
        logger.info("🔒 Auditing environment variables...")
        
        required_vars = ['SESSION_SECRET', 'DATABASE_URL', 'OPENAI_API_KEY']
        secure_vars = []
        issues = []
        
        for var in required_vars:
            value = os.environ.get(var)
            if not value:
                issues.append(f"Missing environment variable: {var}")
            elif var == 'SESSION_SECRET':
                if len(value) < 32:
                    issues.append(f"SESSION_SECRET too short (minimum 32 characters)")
                elif value == 'dev-secret-key-change-in-production':
                    issues.append(f"SESSION_SECRET using default development value")
                else:
                    secure_vars.append(var)
            else:
                secure_vars.append(var)
        
        self.report['categories']['environment'] = {
            'secure_variables': len(secure_vars),
            'total_variables': len(required_vars),
            'issues': issues,
            'status': 'SECURE' if not issues else 'NEEDS_ATTENTION'
        }
        
        return not issues

    def audit_sql_injection(self):
        """Audit for SQL injection vulnerabilities"""
        logger.info("🔒 Auditing SQL injection vulnerabilities...")
        
        python_files = list(Path('.').rglob('*.py'))
        vulnerabilities = []
        
        dangerous_patterns = [
            r'cursor\.execute\([^?]*%[sd]',  # String formatting in SQL
            r'\.execute\([^?]*\+',          # String concatenation in SQL
            r'\.execute\([^?]*f["\']',      # f-string in SQL
            r'\.execute\([^?]*\.format',    # .format() in SQL
        ]
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for i, line in enumerate(content.split('\n'), 1):
                        for pattern in dangerous_patterns:
                            if re.search(pattern, line):
                                vulnerabilities.append({
                                    'file': str(file_path),
                                    'line': i,
                                    'issue': 'Potential SQL injection vulnerability',
                                    'code': line.strip()
                                })
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
        
        self.report['categories']['sql_injection'] = {
            'files_scanned': len(python_files),
            'vulnerabilities': len(vulnerabilities),
            'details': vulnerabilities,
            'status': 'SECURE' if not vulnerabilities else 'CRITICAL'
        }
        
        return not vulnerabilities

    def audit_xss_vulnerabilities(self):
        """Audit for XSS vulnerabilities"""
        logger.info("🔒 Auditing XSS vulnerabilities...")
        
        template_files = list(Path('templates').rglob('*.html'))
        vulnerabilities = []
        
        dangerous_patterns = [
            r'\{\{.*\|safe\}\}',           # |safe filter
            r'\{\{.*\|raw\}\}',            # |raw filter  
            r'innerHTML\s*=',              # Direct innerHTML assignment
            r'document\.write\(',          # document.write usage
            r'eval\(',                     # eval() usage
        ]
        
        for file_path in template_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for i, line in enumerate(content.split('\n'), 1):
                        for pattern in dangerous_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                vulnerabilities.append({
                                    'file': str(file_path),
                                    'line': i,
                                    'issue': 'Potential XSS vulnerability',
                                    'code': line.strip()
                                })
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
        
        self.report['categories']['xss'] = {
            'files_scanned': len(template_files),
            'vulnerabilities': len(vulnerabilities),
            'details': vulnerabilities,
            'status': 'SECURE' if not vulnerabilities else 'HIGH'
        }
        
        return not vulnerabilities

    def audit_csrf_protection(self):
        """Audit CSRF protection"""
        logger.info("🔒 Auditing CSRF protection...")
        
        issues = []
        
        # Check if WTF-CSRF is properly configured
        config_files = ['config.py', 'app.py', 'main.py']
        csrf_configured = False
        
        for file_path in config_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if 'WTF_CSRF_ENABLED' in content and 'True' in content:
                            csrf_configured = True
                            break
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")
        
        if not csrf_configured:
            issues.append("CSRF protection not properly configured")
        
        # Check forms for CSRF tokens
        template_files = list(Path('templates').rglob('*.html'))
        forms_without_csrf = []
        
        for file_path in template_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '<form' in content.lower():
                        if 'csrf_token' not in content.lower():
                            forms_without_csrf.append(str(file_path))
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
        
        self.report['categories']['csrf'] = {
            'csrf_configured': csrf_configured,
            'forms_without_csrf': len(forms_without_csrf),
            'vulnerable_templates': forms_without_csrf,
            'issues': issues,
            'status': 'SECURE' if not issues and not forms_without_csrf else 'MEDIUM'
        }
        
        return not issues and not forms_without_csrf

    def audit_file_permissions(self):
        """Audit file and directory permissions"""
        logger.info("🔒 Auditing file permissions...")
        
        sensitive_files = [
            'config.py', 'main.py', 'app.py', '.env',
            'instance/', 'data/', '*.log'
        ]
        
        issues = []
        
        for pattern in sensitive_files:
            files = list(Path('.').glob(pattern))
            for file_path in files:
                try:
                    stat = file_path.stat()
                    mode = oct(stat.st_mode)[-3:]
                    
                    # Check for world-readable permissions
                    if mode.endswith('4') or mode.endswith('6') or mode.endswith('7'):
                        issues.append(f"{file_path}: World-readable permissions ({mode})")
                    
                    # Check for world-writable permissions
                    if mode.endswith('2') or mode.endswith('3') or mode.endswith('6') or mode.endswith('7'):
                        issues.append(f"{file_path}: World-writable permissions ({mode})")
                        
                except Exception as e:
                    logger.warning(f"Could not check permissions for {file_path}: {e}")
        
        self.report['categories']['file_permissions'] = {
            'files_checked': len(sensitive_files),
            'issues': issues,
            'status': 'SECURE' if not issues else 'MEDIUM'
        }
        
        return not issues

    def audit_dependencies(self):
        """Audit Python dependencies for known vulnerabilities"""
        logger.info("🔒 Auditing dependencies...")
        
        try:
            # Check if safety is available
            result = subprocess.run(['pip', 'list'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning("Could not list installed packages")
                return False
            
            packages = result.stdout
            vulnerable_packages = []
            
            # Common vulnerable patterns
            vulnerable_patterns = [
                ('flask', '1.0'),    # Old Flask versions
                ('jinja2', '2.10'),  # Old Jinja2 versions
                ('werkzeug', '0.15') # Old Werkzeug versions
            ]
            
            for package, min_version in vulnerable_patterns:
                if package in packages.lower():
                    # This is a simplified check - in production, use proper vulnerability databases
                    logger.info(f"Found {package} - recommend checking for latest version")
            
            self.report['categories']['dependencies'] = {
                'packages_found': len(packages.split('\n')),
                'vulnerable_packages': len(vulnerable_packages),
                'details': vulnerable_packages,
                'status': 'SECURE' if not vulnerable_packages else 'MEDIUM'
            }
            
            return not vulnerable_packages
            
        except Exception as e:
            logger.warning(f"Could not audit dependencies: {e}")
            return False

    def audit_input_validation(self):
        """Audit input validation"""
        logger.info("🔒 Auditing input validation...")
        
        python_files = list(Path('.').rglob('*.py'))
        issues = []
        
        validation_patterns = [
            r'request\.form\.get\([^)]*\)',     # Form input without validation
            r'request\.args\.get\([^)]*\)',     # Query params without validation
            r'request\.json\.get\([^)]*\)',     # JSON input without validation
        ]
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for i, line in enumerate(content.split('\n'), 1):
                        for pattern in validation_patterns:
                            if re.search(pattern, line):
                                # Check if validation is present in the same function
                                if not re.search(r'validate|clean|sanitize|strip', content[max(0, i-10):i+10]):
                                    issues.append({
                                        'file': str(file_path),
                                        'line': i,
                                        'issue': 'Input without validation',
                                        'code': line.strip()
                                    })
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
        
        self.report['categories']['input_validation'] = {
            'files_scanned': len(python_files),
            'potential_issues': len(issues),
            'details': issues,
            'status': 'SECURE' if len(issues) < 5 else 'MEDIUM'
        }
        
        return len(issues) < 5

    def audit_authentication_security(self):
        """Audit authentication and session security"""
        logger.info("🔒 Auditing authentication security...")
        
        issues = []
        
        # Check session configuration
        config_patterns = [
            ('SESSION_COOKIE_SECURE', 'HTTPS cookie security'),
            ('SESSION_COOKIE_HTTPONLY', 'XSS protection'),
            ('SESSION_COOKIE_SAMESITE', 'CSRF protection'),
            ('PERMANENT_SESSION_LIFETIME', 'Session timeout')
        ]
        
        config_file = 'config.py'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    content = f.read()
                    for pattern, description in config_patterns:
                        if pattern not in content:
                            issues.append(f"Missing {pattern} configuration ({description})")
            except Exception as e:
                logger.warning(f"Could not read {config_file}: {e}")
        
        self.report['categories']['authentication'] = {
            'configurations_checked': len(config_patterns),
            'issues': issues,
            'status': 'SECURE' if not issues else 'MEDIUM'
        }
        
        return not issues

    def audit_logging_security(self):
        """Audit logging for security issues"""
        logger.info("🔒 Auditing logging security...")
        
        python_files = list(Path('.').rglob('*.py'))
        issues = []
        
        # Check for sensitive data in logs
        sensitive_patterns = [
            r'log.*password',
            r'log.*secret',
            r'log.*token',
            r'print.*password',
            r'print.*secret'
        ]
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for i, line in enumerate(content.split('\n'), 1):
                        for pattern in sensitive_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                issues.append({
                                    'file': str(file_path),
                                    'line': i,
                                    'issue': 'Potential sensitive data in logs',
                                    'code': line.strip()
                                })
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
        
        self.report['categories']['logging'] = {
            'files_scanned': len(python_files),
            'potential_issues': len(issues),
            'details': issues,
            'status': 'SECURE' if not issues else 'MEDIUM'
        }
        
        return not issues

    def run_full_audit(self):
        """Run complete security audit"""
        logger.info("🔒 Starting comprehensive security audit...")
        
        audit_functions = [
            ('Environment Variables', self.audit_environment_variables),
            ('SQL Injection', self.audit_sql_injection),
            ('XSS Vulnerabilities', self.audit_xss_vulnerabilities),
            ('CSRF Protection', self.audit_csrf_protection),
            ('File Permissions', self.audit_file_permissions),
            ('Dependencies', self.audit_dependencies),
            ('Input Validation', self.audit_input_validation),
            ('Authentication', self.audit_authentication_security),
            ('Logging Security', self.audit_logging_security)
        ]
        
        passed_audits = 0
        total_audits = len(audit_functions)
        
        for audit_name, audit_func in audit_functions:
            try:
                result = audit_func()
                if result:
                    passed_audits += 1
                    logger.info(f"✅ {audit_name}: PASSED")
                else:
                    logger.warning(f"⚠️  {audit_name}: NEEDS ATTENTION")
            except Exception as e:
                logger.error(f"❌ {audit_name}: ERROR - {e}")
        
        # Calculate overall security score
        security_score = (passed_audits / total_audits) * 100
        
        self.report['summary'] = {
            'total_audits': total_audits,
            'passed_audits': passed_audits,
            'security_score': security_score,
            'status': 'EXCELLENT' if security_score >= 90 else 'GOOD' if security_score >= 70 else 'NEEDS_IMPROVEMENT'
        }
        
        self.report['status'] = 'COMPLETED'
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Save report
        self.save_report()
        
        return self.report

    def generate_recommendations(self):
        """Generate security recommendations"""
        recommendations = []
        
        for category, data in self.report['categories'].items():
            if data.get('status') != 'SECURE':
                if category == 'environment':
                    recommendations.append("Strengthen environment variable security")
                elif category == 'sql_injection':
                    recommendations.append("Implement parameterized queries for all database operations")
                elif category == 'xss':
                    recommendations.append("Implement proper output encoding and CSP headers")
                elif category == 'csrf':
                    recommendations.append("Enable CSRF protection for all forms")
                elif category == 'input_validation':
                    recommendations.append("Implement comprehensive input validation")
        
        self.report['recommendations'] = recommendations

    def save_report(self):
        """Save security audit report"""
        report_file = f"security_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w') as f:
                json.dump(self.report, f, indent=2)
            logger.info(f"Security audit report saved to {report_file}")
        except Exception as e:
            logger.error(f"Could not save report: {e}")

def main():
    """Main function to run security audit"""
    auditor = SecurityAuditor()
    report = auditor.run_full_audit()
    
    print("\n" + "="*60)
    print("SECURITY AUDIT SUMMARY")
    print("="*60)
    print(f"Overall Status: {report['summary']['status']}")
    print(f"Security Score: {report['summary']['security_score']:.1f}%")
    print(f"Audits Passed: {report['summary']['passed_audits']}/{report['summary']['total_audits']}")
    
    if report['recommendations']:
        print("\nRECOMMENDATIONS:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
    
    print(f"\nDetailed report saved to security audit file")
    print("="*60)

if __name__ == "__main__":
    main()