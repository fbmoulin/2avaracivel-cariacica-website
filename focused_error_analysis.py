#!/usr/bin/env python3
"""
Focused Error Analysis and Resolution
2ª Vara Cível de Cariacica - Targeted error identification and fixes
"""

import requests
import json
import time
from datetime import datetime

class FocusedErrorAnalyzer:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.errors_found = []
        self.fixes_applied = []
        
    def test_core_functionality(self):
        """Test core functionality quickly and identify specific errors"""
        print("Analyzing core functionality...")
        
        # Test 1: Main page
        try:
            response = self.session.get(self.base_url, timeout=5)
            if response.status_code == 200:
                print("✓ Main page: Working")
            else:
                self.errors_found.append(f"Main page returned {response.status_code}")
        except Exception as e:
            self.errors_found.append(f"Main page error: {e}")
        
        # Test 2: Health endpoint
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Health check: {data.get('overall_status', 'unknown')}")
            else:
                self.errors_found.append(f"Health endpoint returned {response.status_code}")
        except Exception as e:
            self.errors_found.append(f"Health endpoint error: {e}")
        
        # Test 3: Static assets
        critical_assets = ['/static/css/style.css', '/static/js/main.js']
        for asset in critical_assets:
            try:
                response = self.session.get(f"{self.base_url}{asset}", timeout=3)
                if response.status_code == 200:
                    print(f"✓ {asset}: Available")
                else:
                    self.errors_found.append(f"{asset} returned {response.status_code}")
            except Exception as e:
                self.errors_found.append(f"{asset} error: {e}")
        
        # Test 4: Chatbot (single test)
        try:
            response = self.session.post(
                f"{self.base_url}/chat",
                json={'message': 'teste'},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if 'response' in data:
                    print("✓ Chatbot: Functional")
                else:
                    self.errors_found.append("Chatbot: No response field")
            else:
                self.errors_found.append(f"Chatbot returned {response.status_code}")
        except Exception as e:
            self.errors_found.append(f"Chatbot error: {e}")
    
    def check_missing_routes(self):
        """Check for missing routes that were being tested"""
        print("Checking route availability...")
        
        routes_to_check = [
            '/contato',
            '/consulta', 
            '/agendamento',
            '/servicos',
            '/balcao-virtual'
        ]
        
        missing_routes = []
        
        for route in routes_to_check:
            try:
                response = self.session.get(f"{self.base_url}{route}", timeout=3)
                if response.status_code == 404:
                    missing_routes.append(route)
                else:
                    print(f"✓ {route}: Available")
            except:
                missing_routes.append(route)
        
        if missing_routes:
            self.errors_found.append(f"Missing routes: {missing_routes}")
            return missing_routes
        return []
    
    def check_security_middleware_issues(self):
        """Check for security middleware blocking legitimate requests"""
        print("Checking security middleware...")
        
        # The logs show IP blocking occurred - check if this is affecting normal operation
        try:
            # Test multiple requests to see if rate limiting is too aggressive
            for i in range(3):
                response = self.session.get(self.base_url, timeout=3)
                if response.status_code == 403:
                    self.errors_found.append("Security middleware blocking legitimate requests")
                    return True
                time.sleep(0.5)
            print("✓ Security middleware: Not blocking normal requests")
        except Exception as e:
            self.errors_found.append(f"Security middleware test error: {e}")
        
        return False
    
    def run_analysis(self):
        """Run focused error analysis"""
        print("🔍 FOCUSED ERROR ANALYSIS")
        print("=" * 50)
        print(f"Start time: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        self.test_core_functionality()
        missing_routes = self.check_missing_routes()
        security_issues = self.check_security_middleware_issues()
        
        print("\n" + "=" * 50)
        print("ANALYSIS RESULTS")
        print("=" * 50)
        
        if not self.errors_found:
            print("✅ No critical errors found")
            print("Application appears to be functioning correctly")
        else:
            print(f"❌ Found {len(self.errors_found)} issues:")
            for i, error in enumerate(self.errors_found, 1):
                print(f"  {i}. {error}")
        
        return {
            'errors_found': self.errors_found,
            'missing_routes': missing_routes,
            'security_issues': security_issues
        }

def main():
    analyzer = FocusedErrorAnalyzer()
    results = analyzer.run_analysis()
    
    with open('focused_error_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    main()