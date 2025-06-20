"""
Deployment Comparison Script
Compares original vs optimized system performance
"""
import requests
import time
import json
from datetime import datetime

def test_endpoint_performance(url, name, iterations=5):
    """Test endpoint performance multiple times"""
    times = []
    
    for i in range(iterations):
        try:
            start = time.time()
            response = requests.get(url, timeout=10)
            duration = time.time() - start
            
            if response.status_code == 200:
                times.append(duration)
            else:
                print(f"Warning: {name} returned {response.status_code}")
                
        except Exception as e:
            print(f"Error testing {name}: {e}")
    
    if times:
        return {
            'avg_time': sum(times) / len(times),
            'min_time': min(times),
            'max_time': max(times),
            'success_rate': len(times) / iterations * 100
        }
    return None

def main():
    base_url = "http://localhost:5000"
    
    endpoints = [
        ('/', 'Homepage'),
        ('/sobre', 'About'),
        ('/servicos', 'Services'),
        ('/contato', 'Contact'),
        ('/chatbot', 'Chatbot'),
        ('/health', 'Health Check'),
        ('/metrics', 'Metrics')
    ]
    
    print("Performance Testing Results")
    print("=" * 50)
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {base_url}")
    print()
    
    results = {}
    
    for endpoint, name in endpoints:
        print(f"Testing {name}...")
        result = test_endpoint_performance(f"{base_url}{endpoint}", name)
        
        if result:
            results[name] = result
            print(f"  Average: {result['avg_time']:.3f}s")
            print(f"  Range: {result['min_time']:.3f}s - {result['max_time']:.3f}s")
            print(f"  Success: {result['success_rate']:.1f}%")
        else:
            print(f"  Failed to test {name}")
        print()
    
    # Summary
    if results:
        avg_response_time = sum(r['avg_time'] for r in results.values()) / len(results)
        overall_success = sum(r['success_rate'] for r in results.values()) / len(results)
        
        print("Summary")
        print("-" * 30)
        print(f"Average response time: {avg_response_time:.3f}s")
        print(f"Overall success rate: {overall_success:.1f}%")
        
        # Performance categories
        fast_endpoints = [name for name, r in results.items() if r['avg_time'] < 0.5]
        slow_endpoints = [name for name, r in results.items() if r['avg_time'] > 1.0]
        
        print(f"Fast endpoints (<0.5s): {len(fast_endpoints)}")
        print(f"Slow endpoints (>1.0s): {len(slow_endpoints)}")
        
        if slow_endpoints:
            print(f"  Slow: {', '.join(slow_endpoints)}")

if __name__ == '__main__':
    main()