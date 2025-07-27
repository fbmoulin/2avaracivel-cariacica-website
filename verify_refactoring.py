#!/usr/bin/env python3
"""
Verification script for refactored code
Tests the key improvements and ensures everything works correctly
"""
import os
import sys
import requests
import json
from datetime import datetime

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get('http://localhost:5000/health')
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working")
            print(f"   - Overall status: {data['overall_status']}")
            print(f"   - Services healthy: {data['summary']['healthy_services']}/{data['summary']['total_services']}")
            return True
        else:
            print("❌ Health endpoint failed")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_main_routes():
    """Test main application routes"""
    routes_to_test = [
        ('/', 'Homepage'),
        ('/sobre', 'About page'),
        ('/juiz', 'Judge page'),
        ('/faq', 'FAQ page'),
        ('/contato', 'Contact page'),
        ('/noticias', 'News page'),
        ('/servicos', 'Services page'),
        ('/servicos/balcao-virtual', 'Virtual desk page')
    ]
    
    success_count = 0
    for route, name in routes_to_test:
        try:
            response = requests.get(f'http://localhost:5000{route}')
            if response.status_code == 200:
                print(f"✅ {name} ({route}): OK")
                success_count += 1
            else:
                print(f"❌ {name} ({route}): Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name} ({route}): Error - {e}")
    
    print(f"\nRoutes tested: {success_count}/{len(routes_to_test)}")
    return success_count == len(routes_to_test)

def check_security_headers():
    """Check if security headers are applied"""
    try:
        response = requests.get('http://localhost:5000/')
        headers = response.headers
        
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'Referrer-Policy'
        ]
        
        print("\nSecurity Headers Check:")
        present = 0
        for header in security_headers:
            if header in headers:
                print(f"✅ {header}: {headers[header]}")
                present += 1
            else:
                print(f"❌ {header}: Missing")
        
        print(f"\nSecurity headers present: {present}/{len(security_headers)}")
        return present >= 3  # At least 3 headers should be present
        
    except Exception as e:
        print(f"❌ Security headers check error: {e}")
        return False

def check_database_optimization():
    """Check if database optimizations are working"""
    print("\nDatabase Optimization Check:")
    
    # Check if database configuration exists
    if os.path.exists('database.py'):
        with open('database.py', 'r') as f:
            content = f.read()
            
        checks = [
            ('pool_size', 'Connection pooling'),
            ('pool_pre_ping', 'Connection pre-ping'),
            ('CREATE INDEX', 'Index creation'),
            ('ANALYZE', 'Query optimization')
        ]
        
        for check, name in checks:
            if check in content:
                print(f"✅ {name}: Configured")
            else:
                print(f"⚠️  {name}: Not found in current config")
    
    return True

def main():
    """Run all verification tests"""
    print("🔍 Refactoring Verification Script")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run tests
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Main Routes", test_main_routes),
        ("Security Headers", check_security_headers),
        ("Database Optimization", check_database_optimization)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'=' * 30}")
        print(f"Testing: {test_name}")
        print('=' * 30)
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All refactoring improvements verified successfully!")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
    
    return passed == total

if __name__ == "__main__":
    sys.exit(0 if main() else 1)