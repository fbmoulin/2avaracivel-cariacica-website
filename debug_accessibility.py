#!/usr/bin/env python3
"""
Debug Accessibility Issues - 2ª Vara Cível de Cariacica
Comprehensive debugging tool for accessibility and performance issues
"""

import requests
import time
import json
from datetime import datetime

class AccessibilityDebugger:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.issues = []
        self.fixes_applied = []
        
    def check_application_health(self):
        """Check if application is running and healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print("✅ Application is healthy")
                print(f"   Services: {health_data['summary']['healthy_services']}/{health_data['summary']['total_services']} healthy")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to application: {e}")
            return False
    
    def check_contrast_issues(self):
        """Check for contrast ratio issues that were reported in console"""
        print("\n🔍 Checking contrast ratio fixes...")
        
        # Test main pages for contrast issues
        test_pages = [
            "/",
            "/sobre/",
            "/contato/",
            "/servicos/"
        ]
        
        for page in test_pages:
            try:
                response = requests.get(f"{self.base_url}{page}", timeout=10)
                if response.status_code == 200:
                    content = response.text
                    
                    # Check if emergency fixes CSS is loaded
                    if 'emergency-fixes.css' in content:
                        print(f"✅ {page}: Emergency fixes CSS loaded")
                        self.fixes_applied.append(f"Contrast fixes loaded on {page}")
                    else:
                        print(f"⚠️  {page}: Emergency fixes CSS not found")
                        self.issues.append(f"Missing emergency fixes CSS on {page}")
                        
                    # Check for proper color usage
                    if '#2c5aa0' in content or '#1e3d72' in content:
                        print(f"✅ {page}: Proper contrast colors detected")
                    else:
                        print(f"⚠️  {page}: Standard contrast colors not found")
                        
                else:
                    print(f"❌ {page}: HTTP {response.status_code}")
                    self.issues.append(f"Page {page} returned {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {page}: Error - {e}")
                self.issues.append(f"Cannot access {page}: {e}")
    
    def check_cls_fixes(self):
        """Check for Cumulative Layout Shift fixes"""
        print("\n📐 Checking CLS (Cumulative Layout Shift) fixes...")
        
        try:
            response = requests.get(self.base_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Check for image size specifications
                if 'min-height' in content and 'service-icon-custom' in content:
                    print("✅ Image size constraints applied")
                    self.fixes_applied.append("Image dimensions fixed to prevent CLS")
                
                # Check for font loading optimizations
                if 'font-display: swap' in content:
                    print("✅ Font loading optimizations applied")
                    self.fixes_applied.append("Font loading optimized")
                
                # Check for container constraints
                if 'min-height' in content and 'quick-access-card' in content:
                    print("✅ Container height constraints applied")
                    self.fixes_applied.append("Container heights fixed")
                    
        except Exception as e:
            print(f"❌ Error checking CLS fixes: {e}")
            self.issues.append(f"Cannot verify CLS fixes: {e}")
    
    def check_performance_metrics(self):
        """Check basic performance metrics"""
        print("\n⚡ Checking performance metrics...")
        
        start_time = time.time()
        try:
            response = requests.get(self.base_url, timeout=30)
            load_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"✅ Page loaded in {load_time:.2f}s")
                if load_time < 2.0:
                    self.fixes_applied.append(f"Good load time: {load_time:.2f}s")
                else:
                    self.issues.append(f"Slow load time: {load_time:.2f}s")
                    
                # Check response size
                content_length = len(response.content)
                print(f"📊 Page size: {content_length/1024:.1f}KB")
                
        except Exception as e:
            print(f"❌ Performance check failed: {e}")
            self.issues.append(f"Performance check failed: {e}")
    
    def test_accessibility_features(self):
        """Test accessibility features"""
        print("\n♿ Testing accessibility features...")
        
        try:
            response = requests.get(self.base_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Check for accessibility toggle
                if 'accessibility-toggle' in content:
                    print("✅ Accessibility toggle present")
                    self.fixes_applied.append("Accessibility controls available")
                
                # Check for ARIA labels
                if 'aria-label' in content:
                    print("✅ ARIA labels detected")
                    self.fixes_applied.append("ARIA accessibility labels present")
                
                # Check for skip links
                if 'skip-link' in content or 'skip-to-content' in content:
                    print("✅ Skip navigation links present")
                    self.fixes_applied.append("Skip navigation implemented")
                
                # Check for proper heading structure
                if '<h1' in content and '<h2' in content:
                    print("✅ Proper heading hierarchy detected")
                    self.fixes_applied.append("Proper heading structure")
                    
        except Exception as e:
            print(f"❌ Accessibility check failed: {e}")
            self.issues.append(f"Accessibility check failed: {e}")
    
    def generate_debug_report(self):
        """Generate comprehensive debug report"""
        print("\n" + "="*60)
        print("🔧 DEBUG REPORT - 2ª Vara Cível de Cariacica")
        print("="*60)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n✅ FIXES APPLIED ({len(self.fixes_applied)}):")
        for fix in self.fixes_applied:
            print(f"   • {fix}")
        
        if self.issues:
            print(f"\n⚠️  REMAINING ISSUES ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   • {issue}")
        else:
            print(f"\n🎉 NO ISSUES FOUND - All systems working properly!")
        
        # Overall status
        if len(self.issues) == 0:
            status = "🟢 EXCELLENT"
        elif len(self.issues) <= 2:
            status = "🟡 GOOD"
        else:
            status = "🔴 NEEDS ATTENTION"
            
        print(f"\nOverall Status: {status}")
        print("="*60)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'fixes_applied': self.fixes_applied,
            'issues': self.issues,
            'status': status,
            'summary': {
                'fixes_count': len(self.fixes_applied),
                'issues_count': len(self.issues)
            }
        }
    
    def run_full_debug(self):
        """Run complete debugging sequence"""
        print("🚀 Starting comprehensive accessibility debug...")
        
        if not self.check_application_health():
            print("❌ Cannot proceed - application not healthy")
            return False
        
        self.check_contrast_issues()
        self.check_cls_fixes()
        self.check_performance_metrics()
        self.test_accessibility_features()
        
        report = self.generate_debug_report()
        
        # Save report to file
        with open('debug_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Debug report saved to: debug_report.json")
        return True

def main():
    debugger = AccessibilityDebugger()
    success = debugger.run_full_debug()
    
    if success:
        print("\n🎯 Debug completed successfully!")
        print("💡 Recommendation: Monitor console logs for any remaining CLS warnings")
    else:
        print("\n❌ Debug failed - check application status")

if __name__ == "__main__":
    main()