#!/usr/bin/env python3
"""
Advanced Penetration Testing Suite for 2ª Vara Cível de Cariacica
Tests for common web application vulnerabilities and attack vectors
"""

import requests
import json
import time
import urllib.parse
from datetime import datetime
import subprocess
import sys

class PenetrationTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.vulnerabilities = []
        self.test_results = []
        
    def test_sql_injection(self):
        """Test for SQL injection vulnerabilities"""
        print("Testing SQL Injection vulnerabilities...")
        
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT NULL,NULL,NULL--",
            "admin'--",
            "' OR 1=1#",
            "') OR ('1'='1",
            "1' AND SLEEP(5)--"
        ]
        
        # Test contact form
        contact_endpoint = f"{self.base_url}/contato"
        
        for payload in sql_payloads:
            try:
                data = {
                    'nome': payload,
                    'email': 'test@example.com',
                    'telefone': '11999999999',
                    'assunto': 'Test',
                    'mensagem': 'Test message'
                }
                
                start_time = time.time()
                response = self.session.post(contact_endpoint, data=data, timeout=10)
                response_time = time.time() - start_time
                
                # Check for SQL injection indicators
                if response_time > 4 or 'error' in response.text.lower() or 'sql' in response.text.lower():
                    self.vulnerabilities.append({
                        'type': 'SQL Injection',
                        'endpoint': '/contato',
                        'payload': payload,
                        'response_time': response_time,
                        'status_code': response.status_code
                    })
                    
            except Exception as e:
                if 'timeout' in str(e).lower():
                    self.vulnerabilities.append({
                        'type': 'SQL Injection (Time-based)',
                        'endpoint': '/contato',
                        'payload': payload,
                        'error': str(e)
                    })
    
    def test_xss_vulnerabilities(self):
        """Test for Cross-Site Scripting vulnerabilities"""
        print("Testing XSS vulnerabilities...")
        
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            'javascript:alert("XSS")',
            '<svg onload=alert("XSS")>',
            '"><script>alert("XSS")</script>',
            '<iframe src="javascript:alert(\'XSS\')"></iframe>',
            '<body onload=alert("XSS")>'
        ]
        
        # Test chatbot endpoint
        chat_endpoint = f"{self.base_url}/chat"
        
        for payload in xss_payloads:
            try:
                data = {'message': payload}
                response = self.session.post(
                    chat_endpoint, 
                    json=data, 
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                # Check if payload is reflected without proper escaping
                if payload in response.text or 'script' in response.text.lower():
                    self.vulnerabilities.append({
                        'type': 'XSS (Reflected)',
                        'endpoint': '/chat',
                        'payload': payload,
                        'response_contains_payload': payload in response.text
                    })
                    
            except Exception as e:
                continue
    
    def test_csrf_protection(self):
        """Test CSRF protection implementation"""
        print("Testing CSRF protection...")
        
        # Test form submissions without CSRF token
        test_endpoints = [
            ('/contato', {
                'nome': 'Test User',
                'email': 'test@example.com',
                'telefone': '11999999999',
                'assunto': 'CSRF Test',
                'mensagem': 'Testing CSRF protection'
            }),
            ('/consulta', {
                'numero_processo': '12345678901234567890'
            })
        ]
        
        for endpoint, data in test_endpoints:
            try:
                # First request without CSRF token
                response = self.session.post(f"{self.base_url}{endpoint}", data=data, timeout=10)
                
                if response.status_code == 200:
                    self.vulnerabilities.append({
                        'type': 'CSRF Protection Missing',
                        'endpoint': endpoint,
                        'status_code': response.status_code,
                        'note': 'Form submitted without CSRF token'
                    })
                    
            except Exception as e:
                continue
    
    def test_authentication_bypass(self):
        """Test for authentication bypass vulnerabilities"""
        print("Testing authentication bypass...")
        
        # Test admin endpoints without authentication
        admin_endpoints = [
            '/admin',
            '/admin/dashboard',
            '/admin/logs',
            '/admin/health-check'
        ]
        
        for endpoint in admin_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                
                if response.status_code == 200 and 'login' not in response.text.lower():
                    self.vulnerabilities.append({
                        'type': 'Authentication Bypass',
                        'endpoint': endpoint,
                        'status_code': response.status_code,
                        'note': 'Admin endpoint accessible without authentication'
                    })
                    
            except Exception as e:
                continue
    
    def test_rate_limiting(self):
        """Test rate limiting implementation"""
        print("Testing rate limiting...")
        
        # Send rapid requests to test rate limiting
        test_endpoint = f"{self.base_url}/chat"
        
        request_count = 0
        blocked = False
        
        for i in range(20):  # Send 20 rapid requests
            try:
                data = {'message': f'Rate limit test {i}'}
                response = self.session.post(
                    test_endpoint, 
                    json=data,
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
                
                request_count += 1
                
                if response.status_code == 429:  # Too Many Requests
                    blocked = True
                    break
                    
            except Exception as e:
                break
        
        if not blocked and request_count >= 15:
            self.vulnerabilities.append({
                'type': 'Rate Limiting Insufficient',
                'endpoint': '/chat',
                'requests_sent': request_count,
                'note': 'Rate limiting not triggered after multiple requests'
            })
    
    def test_information_disclosure(self):
        """Test for information disclosure vulnerabilities"""
        print("Testing information disclosure...")
        
        # Test for debug information exposure
        test_endpoints = [
            '/nonexistent-page',
            '/admin/nonexistent',
            '/debug',
            '/test',
            '/.env',
            '/config',
            '/backup'
        ]
        
        for endpoint in test_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                
                # Check for debug information in responses
                debug_indicators = [
                    'traceback', 'exception', 'debug', 'error', 
                    'stack trace', 'python', 'flask', 'werkzeug'
                ]
                
                response_lower = response.text.lower()
                
                for indicator in debug_indicators:
                    if indicator in response_lower and response.status_code != 404:
                        self.vulnerabilities.append({
                            'type': 'Information Disclosure',
                            'endpoint': endpoint,
                            'status_code': response.status_code,
                            'indicator': indicator,
                            'note': 'Debug information exposed'
                        })
                        break
                        
            except Exception as e:
                continue
    
    def test_security_headers(self):
        """Test security headers implementation"""
        print("Testing security headers...")
        
        try:
            response = self.session.get(self.base_url, timeout=10)
            headers = response.headers
            
            required_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': None,  # Should exist
                'Content-Security-Policy': None,    # Should exist
            }
            
            for header, expected_value in required_headers.items():
                if header not in headers:
                    self.vulnerabilities.append({
                        'type': 'Missing Security Header',
                        'header': header,
                        'note': f'Security header {header} not present'
                    })
                elif expected_value and isinstance(expected_value, list):
                    if headers[header] not in expected_value:
                        self.vulnerabilities.append({
                            'type': 'Weak Security Header',
                            'header': header,
                            'current_value': headers[header],
                            'expected_values': expected_value
                        })
                elif expected_value and headers[header] != expected_value:
                    self.vulnerabilities.append({
                        'type': 'Weak Security Header',
                        'header': header,
                        'current_value': headers[header],
                        'expected_value': expected_value
                    })
                    
        except Exception as e:
            print(f"Error testing security headers: {e}")
    
    def test_file_upload_vulnerabilities(self):
        """Test file upload security"""
        print("Testing file upload vulnerabilities...")
        
        # Test malicious file uploads if endpoint exists
        malicious_files = [
            ('test.php', '<?php echo "PHP executed"; ?>'),
            ('test.jsp', '<% out.println("JSP executed"); %>'),
            ('test.exe', b'MZ\x90\x00'),  # PE header
            ('test.html', '<script>alert("XSS")</script>'),
            ('../../../etc/passwd', 'root:x:0:0:root'),
        ]
        
        # Check if there are file upload endpoints
        upload_endpoints = ['/upload', '/contato', '/admin/upload']
        
        for endpoint in upload_endpoints:
            for filename, content in malicious_files:
                try:
                    files = {'file': (filename, content)}
                    response = self.session.post(f"{self.base_url}{endpoint}", files=files, timeout=10)
                    
                    if response.status_code == 200 and 'error' not in response.text.lower():
                        self.vulnerabilities.append({
                            'type': 'Malicious File Upload',
                            'endpoint': endpoint,
                            'filename': filename,
                            'status_code': response.status_code,
                            'note': 'Potentially malicious file accepted'
                        })
                        
                except Exception as e:
                    continue
    
    def run_comprehensive_tests(self):
        """Run all penetration tests"""
        print("🚀 Starting Comprehensive Penetration Testing...")
        print(f"Target: {self.base_url}")
        print("="*60)
        
        start_time = datetime.now()
        
        # Run all tests
        test_methods = [
            self.test_sql_injection,
            self.test_xss_vulnerabilities,
            self.test_csrf_protection,
            self.test_authentication_bypass,
            self.test_rate_limiting,
            self.test_information_disclosure,
            self.test_security_headers,
            self.test_file_upload_vulnerabilities
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"Error in {test_method.__name__}: {e}")
        
        end_time = datetime.now()
        test_duration = (end_time - start_time).total_seconds()
        
        # Generate report
        report = {
            'test_timestamp': start_time.isoformat(),
            'test_duration_seconds': test_duration,
            'target_url': self.base_url,
            'total_vulnerabilities': len(self.vulnerabilities),
            'vulnerabilities': self.vulnerabilities,
            'risk_assessment': self.assess_risk()
        }
        
        return report
    
    def assess_risk(self):
        """Assess overall security risk based on vulnerabilities found"""
        if not self.vulnerabilities:
            return "LOW - No significant vulnerabilities detected"
        
        high_risk_types = ['SQL Injection', 'XSS', 'Authentication Bypass', 'Malicious File Upload']
        medium_risk_types = ['CSRF Protection Missing', 'Information Disclosure']
        
        high_risk_count = sum(1 for vuln in self.vulnerabilities if vuln['type'] in high_risk_types)
        medium_risk_count = sum(1 for vuln in self.vulnerabilities if vuln['type'] in medium_risk_types)
        
        if high_risk_count > 0:
            return f"HIGH - {high_risk_count} critical vulnerabilities found"
        elif medium_risk_count > 2:
            return f"MEDIUM - {medium_risk_count} moderate vulnerabilities found"
        else:
            return f"LOW-MEDIUM - {len(self.vulnerabilities)} minor issues found"
    
    def print_report(self, report):
        """Print formatted penetration testing report"""
        print("\n" + "="*80)
        print("🛡️  PENETRATION TESTING REPORT")
        print("2ª Vara Cível de Cariacica - Security Assessment")
        print("="*80)
        
        print(f"\n📅 Test Date: {report['test_timestamp']}")
        print(f"⏱️  Test Duration: {report['test_duration_seconds']:.2f} seconds")
        print(f"🎯 Target URL: {report['target_url']}")
        print(f"🔍 Vulnerabilities Found: {report['total_vulnerabilities']}")
        print(f"⚠️  Risk Level: {report['risk_assessment']}")
        
        if report['vulnerabilities']:
            print("\n" + "-"*80)
            print("VULNERABILITY DETAILS")
            print("-"*80)
            
            for i, vuln in enumerate(report['vulnerabilities'], 1):
                print(f"\n{i}. {vuln['type']}")
                print(f"   Endpoint: {vuln.get('endpoint', 'N/A')}")
                
                if 'payload' in vuln:
                    print(f"   Payload: {vuln['payload']}")
                if 'status_code' in vuln:
                    print(f"   Status Code: {vuln['status_code']}")
                if 'note' in vuln:
                    print(f"   Note: {vuln['note']}")
        else:
            print("\n✅ No significant vulnerabilities detected during testing")
        
        print("\n" + "="*80)
        return report

def run_penetration_tests():
    """Main function to run penetration tests"""
    tester = PenetrationTester()
    report = tester.run_comprehensive_tests()
    formatted_report = tester.print_report(report)
    
    # Save detailed report
    with open('penetration_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

if __name__ == "__main__":
    run_penetration_tests()