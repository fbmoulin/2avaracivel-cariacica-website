#!/usr/bin/env python3
"""
Comprehensive Deployment Readiness Assessment
2ª Vara Cível de Cariacica - Production Deployment Check
"""

import os
import sys
import subprocess
import requests
import json
from datetime import datetime
from pathlib import Path

class DeploymentChecker:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.checks_passed = 0
        self.checks_failed = 0
        self.critical_issues = []
        self.warnings = []
        
    def check_application_health(self):
        """Check application health and service status"""
        print("Checking application health...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                overall_status = health_data.get('overall_status', 'unknown')
                
                if overall_status == 'healthy':
                    print("✓ Application health: EXCELLENT")
                    self.checks_passed += 1
                elif overall_status == 'warning':
                    print("⚠ Application health: GOOD (minor warnings)")
                    self.checks_passed += 1
                    self.warnings.append("Some services have warnings but are operational")
                else:
                    print("❌ Application health: CRITICAL")
                    self.checks_failed += 1
                    self.critical_issues.append("Critical health issues detected")
                    
                # Check individual services
                services = health_data.get('services', {})
                healthy_services = sum(1 for s in services.values() if s.get('status') == 'healthy')
                total_services = len(services)
                
                print(f"   Services: {healthy_services}/{total_services} healthy")
                
                if healthy_services >= total_services * 0.8:  # 80% threshold
                    self.checks_passed += 1
                else:
                    self.checks_failed += 1
                    self.critical_issues.append(f"Too many unhealthy services: {total_services - healthy_services}")
                    
            else:
                print("❌ Health endpoint not accessible")
                self.checks_failed += 1
                self.critical_issues.append("Health monitoring not working")
                
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            self.checks_failed += 1
            self.critical_issues.append("Application not responding")
    
    def check_core_functionality(self):
        """Test core application functionality"""
        print("Testing core functionality...")
        
        # Test main page
        try:
            response = requests.get(self.base_url, timeout=10)
            if response.status_code == 200:
                print("✓ Main page accessible")
                self.checks_passed += 1
            else:
                print("❌ Main page not accessible")
                self.checks_failed += 1
                self.critical_issues.append("Main page returning errors")
        except Exception as e:
            print(f"❌ Main page test failed: {e}")
            self.checks_failed += 1
            self.critical_issues.append("Main page not responding")
        
        # Test chatbot functionality
        try:
            chat_data = {"message": "teste funcionamento"}
            response = requests.post(
                f"{self.base_url}/chat", 
                json=chat_data, 
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            if response.status_code == 200:
                chat_response = response.json()
                if 'response' in chat_response:
                    print("✓ Chatbot functionality working")
                    self.checks_passed += 1
                else:
                    print("⚠ Chatbot responding but format unexpected")
                    self.warnings.append("Chatbot response format may need verification")
            else:
                print("❌ Chatbot not working properly")
                self.checks_failed += 1
                self.critical_issues.append("Chatbot functionality broken")
        except Exception as e:
            print(f"❌ Chatbot test failed: {e}")
            self.checks_failed += 1
            self.critical_issues.append("Chatbot not responding")
    
    def check_security_headers(self):
        """Verify security headers are properly configured"""
        print("Checking security configuration...")
        
        try:
            response = requests.head(self.base_url, timeout=10)
            headers = response.headers
            
            required_headers = {
                'Content-Security-Policy': 'CSP protection',
                'X-Content-Type-Options': 'MIME type protection',
                'X-Frame-Options': 'Clickjacking protection',
                'X-XSS-Protection': 'XSS protection',
                'Strict-Transport-Security': 'HTTPS enforcement'
            }
            
            security_score = 0
            for header, description in required_headers.items():
                if header in headers:
                    print(f"✓ {description}")
                    security_score += 1
                else:
                    print(f"❌ Missing {description}")
                    self.warnings.append(f"Missing security header: {header}")
            
            if security_score >= 4:
                print("✓ Security headers: GOOD")
                self.checks_passed += 1
            else:
                print("⚠ Security headers: NEEDS IMPROVEMENT")
                self.warnings.append("Some security headers missing")
                
        except Exception as e:
            print(f"❌ Security check failed: {e}")
            self.checks_failed += 1
            self.critical_issues.append("Security verification failed")
    
    def check_static_assets(self):
        """Verify static assets are accessible"""
        print("Checking static assets...")
        
        critical_assets = [
            '/static/css/style.css',
            '/static/js/main.js',
            '/static/images/banners/banner_principal.png'
        ]
        
        assets_working = 0
        for asset in critical_assets:
            try:
                response = requests.head(f"{self.base_url}{asset}", timeout=5)
                if response.status_code == 200:
                    assets_working += 1
                    
            except Exception:
                continue
        
        if assets_working == len(critical_assets):
            print("✓ All critical static assets accessible")
            self.checks_passed += 1
        elif assets_working >= len(critical_assets) * 0.8:
            print("⚠ Most static assets accessible")
            self.warnings.append("Some static assets may be missing")
        else:
            print("❌ Critical static assets missing")
            self.checks_failed += 1
            self.critical_issues.append("Static asset serving broken")
    
    def check_database_connectivity(self):
        """Check database connectivity through application"""
        print("Checking database connectivity...")
        
        try:
            # The health endpoint includes database status
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                db_status = health_data.get('services', {}).get('database', {}).get('status')
                
                if db_status in ['healthy', 'warning']:
                    print("✓ Database connectivity working")
                    self.checks_passed += 1
                else:
                    print("❌ Database connectivity issues")
                    self.checks_failed += 1
                    self.critical_issues.append("Database not accessible")
            else:
                print("⚠ Cannot verify database status")
                self.warnings.append("Database status unclear")
                
        except Exception as e:
            print(f"❌ Database check failed: {e}")
            self.checks_failed += 1
            self.critical_issues.append("Database verification failed")
    
    def check_environment_configuration(self):
        """Check essential environment variables"""
        print("Checking environment configuration...")
        
        required_env_vars = ['DATABASE_URL', 'SESSION_SECRET']
        optional_env_vars = ['OPENAI_API_KEY', 'EMAIL_USER', 'EMAIL_PASSWORD']
        
        missing_required = []
        missing_optional = []
        
        for var in required_env_vars:
            if not os.environ.get(var):
                missing_required.append(var)
        
        for var in optional_env_vars:
            if not os.environ.get(var):
                missing_optional.append(var)
        
        if not missing_required:
            print("✓ All required environment variables configured")
            self.checks_passed += 1
        else:
            print(f"❌ Missing required variables: {', '.join(missing_required)}")
            self.checks_failed += 1
            self.critical_issues.append(f"Missing environment variables: {missing_required}")
        
        if missing_optional:
            print(f"⚠ Optional variables not set: {', '.join(missing_optional)}")
            self.warnings.append(f"Optional features may not work: {missing_optional}")
    
    def check_file_structure(self):
        """Verify critical files and directories exist"""
        print("Checking file structure...")
        
        critical_files = [
            'main.py',
            'app_factory.py',
            'routes.py',
            'config.py',
            'templates/index.html',
            'static/css/style.css'
        ]
        
        missing_files = []
        for file_path in critical_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if not missing_files:
            print("✓ All critical files present")
            self.checks_passed += 1
        else:
            print(f"❌ Missing critical files: {', '.join(missing_files)}")
            self.checks_failed += 1
            self.critical_issues.append(f"Missing files: {missing_files}")
    
    def check_performance_metrics(self):
        """Check application performance"""
        print("Checking performance metrics...")
        
        try:
            import time
            start_time = time.time()
            response = requests.get(self.base_url, timeout=10)
            response_time = time.time() - start_time
            
            if response_time < 2.0:
                print(f"✓ Response time: {response_time:.2f}s (Good)")
                self.checks_passed += 1
            elif response_time < 5.0:
                print(f"⚠ Response time: {response_time:.2f}s (Acceptable)")
                self.warnings.append("Response time could be improved")
            else:
                print(f"❌ Response time: {response_time:.2f}s (Too slow)")
                self.checks_failed += 1
                self.critical_issues.append("Application too slow")
                
        except Exception as e:
            print(f"❌ Performance check failed: {e}")
            self.warnings.append("Could not measure performance")
    
    def run_comprehensive_check(self):
        """Run all deployment readiness checks"""
        print("🚀 DEPLOYMENT READINESS ASSESSMENT")
        print("2ª Vara Cível de Cariacica")
        print("=" * 60)
        print(f"Assessment Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all checks
        self.check_application_health()
        self.check_core_functionality()
        self.check_security_headers()
        self.check_static_assets()
        self.check_database_connectivity()
        self.check_environment_configuration()
        self.check_file_structure()
        self.check_performance_metrics()
        
        # Generate final assessment
        total_checks = self.checks_passed + self.checks_failed
        success_rate = (self.checks_passed / total_checks * 100) if total_checks > 0 else 0
        
        print("\n" + "=" * 60)
        print("DEPLOYMENT READINESS SUMMARY")
        print("=" * 60)
        
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {self.checks_passed}")
        print(f"Failed: {self.checks_failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Determine deployment readiness
        if self.checks_failed == 0 and len(self.critical_issues) == 0:
            deployment_status = "✅ READY FOR DEPLOYMENT"
            recommendation = "Application is production-ready and can be deployed safely."
        elif self.checks_failed <= 1 and len(self.critical_issues) == 0:
            deployment_status = "⚠️ READY WITH MINOR ISSUES"
            recommendation = "Application can be deployed but should address warnings soon."
        elif len(self.critical_issues) <= 2:
            deployment_status = "⚠️ DEPLOYMENT POSSIBLE WITH RISKS"
            recommendation = "Address critical issues before deployment for optimal stability."
        else:
            deployment_status = "❌ NOT READY FOR DEPLOYMENT"
            recommendation = "Critical issues must be resolved before deployment."
        
        print(f"Status: {deployment_status}")
        print(f"Recommendation: {recommendation}")
        
        if self.critical_issues:
            print("\n🚨 CRITICAL ISSUES:")
            for issue in self.critical_issues:
                print(f"  • {issue}")
        
        if self.warnings:
            print("\n⚠️ WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        print("\n" + "=" * 60)
        
        return {
            'ready_for_deployment': self.checks_failed == 0 and len(self.critical_issues) == 0,
            'deployment_status': deployment_status,
            'success_rate': success_rate,
            'checks_passed': self.checks_passed,
            'checks_failed': self.checks_failed,
            'critical_issues': self.critical_issues,
            'warnings': self.warnings,
            'recommendation': recommendation
        }

def main():
    checker = DeploymentChecker()
    return checker.run_comprehensive_check()

if __name__ == "__main__":
    main()