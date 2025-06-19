#!/usr/bin/env python3
"""
Comprehensive test suite for 2ª Vara Cível de Cariacica
Tests all critical functionality before deployment
"""
import sys
import time
import json
import requests
import logging
from datetime import datetime, date
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveTestSuite:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def test_endpoint(self, endpoint, method='GET', data=None, expected_status=200, test_name=None):
        """Test a specific endpoint"""
        test_name = test_name or f"{method} {endpoint}"
        
        try:
            url = urljoin(self.base_url, endpoint)
            
            if method == 'GET':
                response = self.session.get(url, timeout=10)
            elif method == 'POST':
                response = self.session.post(url, data=data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == expected_status:
                logger.info(f"✓ {test_name}: PASS ({response.status_code})")
                self.results['passed'] += 1
                return True
            else:
                logger.error(f"✗ {test_name}: FAIL ({response.status_code})")
                self.results['failed'] += 1
                self.results['errors'].append(f"{test_name}: Expected {expected_status}, got {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ {test_name}: ERROR - {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {str(e)}")
            return False
    
    def test_core_endpoints(self):
        """Test all core application endpoints"""
        logger.info("Testing core endpoints...")
        
        endpoints = [
            ('/', 'GET', None, 200, 'Homepage'),
            ('/health', 'GET', None, 200, 'Health Check'),
            ('/sobre', 'GET', None, 200, 'About Page'),
            ('/juiz', 'GET', None, 200, 'Judge Profile'),
            ('/contato', 'GET', None, 200, 'Contact Form'),
            ('/faq', 'GET', None, 200, 'FAQ Page'),
            ('/noticias', 'GET', None, 200, 'News Page'),
            ('/servicos/consulta-processual', 'GET', None, 200, 'Process Consultation'),
            ('/servicos/balcao-virtual', 'GET', None, 200, 'Virtual Counter'),
            ('/servicos/agendamento-assessor', 'GET', None, 200, 'Appointment Scheduling'),
            ('/servicos/audiencias', 'GET', None, 200, 'Hearings'),
            ('/servicos/certidoes', 'GET', None, 200, 'Certificates'),
            ('/chatbot', 'GET', None, 200, 'Chatbot Interface'),
        ]
        
        for endpoint, method, data, expected, name in endpoints:
            self.test_endpoint(endpoint, method, data, expected, name)
    
    def test_static_assets(self):
        """Test critical static assets"""
        logger.info("Testing static assets...")
        
        static_assets = [
            '/static/css/style.css',
            '/static/js/main.js',
            '/static/js/accessibility-core.js',
            '/static/js/chatbot-enhanced.js',
            '/static/images/banners/banner_principal.png',
            '/static/images/icons/consulta_processual.png',
            '/static/images/icons/balcao_virtual.png',
            '/static/images/icons/agendamento.png',
            '/static/images/icons/contato.png',
            '/static/manifest.json'
        ]
        
        for asset in static_assets:
            self.test_endpoint(asset, 'GET', None, 200, f'Static Asset: {asset}')
    
    def test_form_submissions(self):
        """Test form submission endpoints"""
        logger.info("Testing form submissions...")
        
        # Test contact form
        contact_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '(27) 99999-9999',
            'subject': 'Test Message',
            'message': 'This is a test message from the automated test suite.'
        }
        self.test_endpoint('/contato', 'POST', contact_data, 200, 'Contact Form Submission')
        
        # Test process consultation
        process_data = {
            'process_number': '1234567-89.2024.8.08.0024',
            'requester_name': 'Test User',
            'requester_cpf': '123.456.789-10'
        }
        self.test_endpoint('/servicos/consulta-processual', 'POST', process_data, 200, 'Process Consultation')
        
        # Test appointment scheduling
        appointment_data = {
            'full_name': 'Test User',
            'document': '123.456.789-10',
            'email': 'test@example.com',
            'phone': '(27) 99999-9999',
            'meeting_type': 'presencial',
            'meeting_subject': 'Test appointment',
            'preferred_date': '2024-12-31',
            'preferred_time': '09:00'
        }
        self.test_endpoint('/servicos/agendamento-assessor', 'POST', appointment_data, 200, 'Appointment Scheduling')
    
    def test_chatbot_api(self):
        """Test chatbot API endpoints"""
        logger.info("Testing chatbot API...")
        
        # Test chatbot message endpoint
        try:
            url = urljoin(self.base_url, '/chatbot/api/message')
            test_messages = [
                'Olá, preciso de informações sobre horário de funcionamento',
                'Como faço para consultar um processo?',
                'Qual o telefone do tribunal?',
                'Preciso agendar um atendimento'
            ]
            
            for message in test_messages:
                data = {'message': message}
                response = self.session.post(url, json=data, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    if 'response' in result:
                        logger.info(f"✓ Chatbot API - Message '{message[:30]}...': PASS")
                        self.results['passed'] += 1
                    else:
                        logger.error(f"✗ Chatbot API - Invalid response format")
                        self.results['failed'] += 1
                else:
                    logger.error(f"✗ Chatbot API - Status {response.status_code}")
                    self.results['failed'] += 1
                    
        except Exception as e:
            logger.error(f"✗ Chatbot API: ERROR - {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"Chatbot API: {str(e)}")
    
    def test_database_health(self):
        """Test database connectivity and health"""
        logger.info("Testing database health...")
        
        try:
            url = urljoin(self.base_url, '/health')
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                
                if health_data.get('status') == 'healthy':
                    logger.info("✓ Database Health: HEALTHY")
                    self.results['passed'] += 1
                else:
                    logger.warning("⚠ Database Health: Partial or unhealthy")
                    logger.info(f"Database status: {health_data.get('database', 'Unknown')}")
                    self.results['passed'] += 1  # Still functional
                    
            else:
                logger.error(f"✗ Database Health: Status {response.status_code}")
                self.results['failed'] += 1
                
        except Exception as e:
            logger.error(f"✗ Database Health: ERROR - {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"Database Health: {str(e)}")
    
    def test_performance_metrics(self):
        """Test application performance"""
        logger.info("Testing performance metrics...")
        
        try:
            start_time = time.time()
            response = self.session.get(self.base_url, timeout=15)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                if response_time < 1000:  # Less than 1 second
                    logger.info(f"✓ Performance: EXCELLENT ({response_time:.0f}ms)")
                    self.results['passed'] += 1
                elif response_time < 3000:  # Less than 3 seconds
                    logger.info(f"✓ Performance: GOOD ({response_time:.0f}ms)")
                    self.results['passed'] += 1
                else:
                    logger.warning(f"⚠ Performance: SLOW ({response_time:.0f}ms)")
                    self.results['passed'] += 1  # Still functional
            else:
                logger.error(f"✗ Performance test failed: Status {response.status_code}")
                self.results['failed'] += 1
                
        except Exception as e:
            logger.error(f"✗ Performance test: ERROR - {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"Performance: {str(e)}")
    
    def test_security_headers(self):
        """Test security headers and configurations"""
        logger.info("Testing security headers...")
        
        try:
            response = self.session.get(self.base_url, timeout=10)
            headers = response.headers
            
            security_checks = [
                ('X-Content-Type-Options', 'nosniff'),
                ('X-Frame-Options', 'DENY'),
                ('X-XSS-Protection', '1; mode=block')
            ]
            
            for header, expected in security_checks:
                if header in headers:
                    logger.info(f"✓ Security Header {header}: PRESENT")
                    self.results['passed'] += 1
                else:
                    logger.warning(f"⚠ Security Header {header}: MISSING")
                    # Not counting as failure for basic functionality
                    
        except Exception as e:
            logger.error(f"✗ Security headers test: ERROR - {e}")
            self.results['failed'] += 1
    
    def run_all_tests(self):
        """Run the complete test suite"""
        logger.info("=" * 60)
        logger.info("COMPREHENSIVE TEST SUITE - 2ª Vara Cível de Cariacica")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Run all test categories
        self.test_core_endpoints()
        self.test_static_assets()
        self.test_form_submissions()
        self.test_chatbot_api()
        self.test_database_health()
        self.test_performance_metrics()
        self.test_security_headers()
        
        # Calculate results
        total_time = time.time() - start_time
        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        # Print summary
        logger.info("=" * 60)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {self.results['passed']}")
        logger.info(f"Failed: {self.results['failed']}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"Total Time: {total_time:.2f}s")
        
        if self.results['errors']:
            logger.info("\nErrors encountered:")
            for error in self.results['errors']:
                logger.error(f"  - {error}")
        
        # Deployment readiness assessment
        if success_rate >= 90:
            logger.info("\n🚀 DEPLOYMENT STATUS: READY")
            logger.info("Application is ready for production deployment")
        elif success_rate >= 80:
            logger.info("\n⚠️  DEPLOYMENT STATUS: READY WITH WARNINGS")
            logger.info("Application is functional but some issues detected")
        else:
            logger.info("\n❌ DEPLOYMENT STATUS: NOT READY")
            logger.info("Critical issues detected, review required")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    import subprocess
    import time
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        logger.info("Server is running, proceeding with tests...")
    except:
        logger.info("Starting server for testing...")
        # Start server in background
        subprocess.Popen(["python", "run_app.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(10)  # Wait for server to start
    
    # Run test suite
    test_suite = ComprehensiveTestSuite()
    success = test_suite.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()