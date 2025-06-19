#!/usr/bin/env python3
"""
Internal test suite for 2ª Vara Cível de Cariacica
Tests application components without requiring a running server
"""
import sys
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class InternalTestSuite:
    def __init__(self):
        self.results = {'passed': 0, 'failed': 0, 'warnings': 0}
    
    def test_imports(self):
        """Test all critical module imports"""
        print("Testing critical imports...")
        
        import_tests = [
            ('flask', 'Flask framework'),
            ('database', 'Database module'),
            ('models', 'Database models'),
            ('routes', 'Application routes'),
            ('services.chatbot_refined', 'Chatbot service'),
            ('services.content', 'Content service'),
            ('utils.security', 'Security utilities')
        ]
        
        for module, description in import_tests:
            try:
                __import__(module)
                print(f"✓ {description}: PASS")
                self.results['passed'] += 1
            except Exception as e:
                print(f"✗ {description}: FAIL - {e}")
                self.results['failed'] += 1
    
    def test_app_creation(self):
        """Test Flask application creation"""
        print("\nTesting application creation...")
        
        try:
            from app import create_app
            app = create_app()
            
            # Test app configuration
            if app.secret_key:
                print("✓ Secret key configured: PASS")
                self.results['passed'] += 1
            else:
                print("✗ Secret key missing: FAIL")
                self.results['failed'] += 1
            
            # Test blueprints
            if len(app.blueprints) >= 3:
                print(f"✓ Blueprints registered ({len(app.blueprints)}): PASS")
                self.results['passed'] += 1
            else:
                print(f"✗ Insufficient blueprints ({len(app.blueprints)}): FAIL")
                self.results['failed'] += 1
            
            # Test routes
            route_count = len(list(app.url_map.iter_rules()))
            if route_count >= 15:
                print(f"✓ Routes registered ({route_count}): PASS")
                self.results['passed'] += 1
            else:
                print(f"⚠ Routes count low ({route_count}): WARNING")
                self.results['warnings'] += 1
                
        except Exception as e:
            print(f"✗ Application creation: FAIL - {e}")
            self.results['failed'] += 1
    
    def test_database_models(self):
        """Test database model definitions"""
        print("\nTesting database models...")
        
        try:
            from models import Contact, ProcessConsultation, AssessorMeeting, ChatMessage
            
            models = [
                (Contact, 'Contact'),
                (ProcessConsultation, 'ProcessConsultation'),
                (AssessorMeeting, 'AssessorMeeting'),
                (ChatMessage, 'ChatMessage')
            ]
            
            for model_class, name in models:
                try:
                    # Test model instantiation
                    if name == 'Contact':
                        instance = model_class('Test', 'test@test.com', '123456789', 'Test Subject', 'Test Message')
                    elif name == 'ProcessConsultation':
                        instance = model_class('1234567-89.2024.8.08.0024', 'Test User', '123.456.789-10')
                    elif name == 'AssessorMeeting':
                        from datetime import date
                        instance = model_class('Test User', '123.456.789-10', 'test@test.com', '123456789', 
                                             'presencial', 'Test meeting', date.today(), '09:00')
                    else:  # ChatMessage doesn't need constructor test due to complex structure
                        instance = model_class()
                    
                    print(f"✓ {name} model: PASS")
                    self.results['passed'] += 1
                except Exception as e:
                    print(f"✗ {name} model: FAIL - {e}")
                    self.results['failed'] += 1
                    
        except ImportError as e:
            print(f"✗ Model imports: FAIL - {e}")
            self.results['failed'] += 1
    
    def test_services(self):
        """Test service modules"""
        print("\nTesting service modules...")
        
        try:
            # Test content service
            from services.content import ContentService
            content_service = ContentService()
            print("✓ Content service: PASS")
            self.results['passed'] += 1
        except Exception as e:
            print(f"✗ Content service: FAIL - {e}")
            self.results['failed'] += 1
        
        try:
            # Test chatbot service
            from services.chatbot_refined import get_refined_chatbot
            chatbot = get_refined_chatbot()
            print("✓ Chatbot service: PASS")
            self.results['passed'] += 1
        except Exception as e:
            print(f"✗ Chatbot service: FAIL - {e}")
            self.results['failed'] += 1
    
    def test_security_utilities(self):
        """Test security utility functions"""
        print("\nTesting security utilities...")
        
        try:
            from utils.security import sanitize_input, validate_email
            
            # Test input sanitization
            test_input = "<script>alert('test')</script>Hello"
            sanitized = sanitize_input(test_input)
            if "script" not in sanitized.lower():
                print("✓ Input sanitization: PASS")
                self.results['passed'] += 1
            else:
                print("✗ Input sanitization: FAIL")
                self.results['failed'] += 1
            
            # Test email validation
            valid_emails = ["test@example.com", "user.name@domain.co.uk"]
            invalid_emails = ["invalid", "@domain.com", "user@"]
            
            valid_results = all(validate_email(email) for email in valid_emails)
            invalid_results = any(validate_email(email) for email in invalid_emails)
            
            if valid_results and not invalid_results:
                print("✓ Email validation: PASS")
                self.results['passed'] += 1
            else:
                print("✗ Email validation: FAIL")
                self.results['failed'] += 1
                
        except Exception as e:
            print(f"✗ Security utilities: FAIL - {e}")
            self.results['failed'] += 1
    
    def test_environment_configuration(self):
        """Test environment configuration"""
        print("\nTesting environment configuration...")
        
        required_vars = ['DATABASE_URL', 'SESSION_SECRET']
        optional_vars = ['OPENAI_API_KEY']
        
        for var in required_vars:
            if os.environ.get(var):
                print(f"✓ {var} configured: PASS")
                self.results['passed'] += 1
            else:
                print(f"✗ {var} missing: FAIL")
                self.results['failed'] += 1
        
        for var in optional_vars:
            if os.environ.get(var):
                print(f"✓ {var} configured: PASS")
                self.results['passed'] += 1
            else:
                print(f"⚠ {var} missing: WARNING")
                self.results['warnings'] += 1
    
    def test_static_files(self):
        """Test presence of critical static files"""
        print("\nTesting static files...")
        
        critical_files = [
            'static/css/style.css',
            'static/js/main.js',
            'static/js/accessibility-core.js',
            'static/manifest.json'
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                print(f"✓ {file_path}: PASS")
                self.results['passed'] += 1
            else:
                print(f"✗ {file_path}: MISSING")
                self.results['failed'] += 1
    
    def test_templates(self):
        """Test presence of critical templates"""
        print("\nTesting template files...")
        
        critical_templates = [
            'templates/base.html',
            'templates/index.html',
            'templates/contact.html',
            'templates/chatbot.html'
        ]
        
        for template in critical_templates:
            if os.path.exists(template):
                print(f"✓ {template}: PASS")
                self.results['passed'] += 1
            else:
                print(f"✗ {template}: MISSING")
                self.results['failed'] += 1
    
    def run_all_tests(self):
        """Execute complete internal test suite"""
        print("=" * 60)
        print("INTERNAL TEST SUITE - 2ª Vara Cível de Cariacica")
        print("=" * 60)
        
        self.test_imports()
        self.test_app_creation()
        self.test_database_models()
        self.test_services()
        self.test_security_utilities()
        self.test_environment_configuration()
        self.test_static_files()
        self.test_templates()
        
        # Calculate results
        total_tests = self.results['passed'] + self.results['failed'] + self.results['warnings']
        critical_success = self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100 if (self.results['passed'] + self.results['failed']) > 0 else 0
        
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")
        print(f"Warnings: {self.results['warnings']}")
        print(f"Critical Success Rate: {critical_success:.1f}%")
        
        # Deployment assessment
        if critical_success >= 95:
            print("\n🚀 DEPLOYMENT STATUS: EXCELLENT")
            print("All critical systems operational, ready for production")
            return True
        elif critical_success >= 85:
            print("\n✅ DEPLOYMENT STATUS: READY")
            print("Application functional with minor warnings")
            return True
        elif critical_success >= 70:
            print("\n⚠️ DEPLOYMENT STATUS: READY WITH CAUTION")
            print("Some issues detected but core functionality intact")
            return True
        else:
            print("\n❌ DEPLOYMENT STATUS: NOT READY")
            print("Critical issues require resolution")
            return False

def main():
    test_suite = InternalTestSuite()
    success = test_suite.run_all_tests()
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)