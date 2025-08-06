#!/usr/bin/env python3
"""
Enhanced REST API - Installation Verification Script
Verifies that the Enhanced REST API is working correctly
"""
import requests
import json
import sys

def test_api_endpoint(base_url, endpoint, description):
    """Test a specific API endpoint"""
    url = f"{base_url}{endpoint}"
    try:
        print(f"🔍 Testing {description}")
        print(f"   URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ SUCCESS: {response.status_code}")
            try:
                data = response.json()
                print(f"   📄 Response: {json.dumps(data, indent=2)[:200]}...")
            except:
                print(f"   📄 Response: {response.text[:200]}...")
        else:
            print(f"   ❌ FAILED: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ CONNECTION ERROR: {str(e)}")
    
    print("-" * 50)

def main():
    """Main verification function"""
    print("🚀 Enhanced REST API Installation Verification")
    print("=" * 50)
    
    # Get base URL from user
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = input("Enter your Odoo base URL (e.g., http://localhost:8069): ").strip()
        
    if not base_url.startswith('http'):
        base_url = f"http://{base_url}"
        
    if not base_url.endswith('/'):
        base_url += '/'
    
    print(f"🌐 Testing API at: {base_url}")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        ("/api/v1/status", "Health Check"),
        ("/api/v1/auth/generate-key", "API Key Generation"),
        ("/api/v1/crm/leads", "CRM Leads"),
        ("/api/v1/sales/orders", "Sales Orders"),
        ("/api/v1/payments/vouchers", "Payment Vouchers"),
    ]
    
    for endpoint, description in endpoints:
        test_api_endpoint(base_url, endpoint, description)
    
    print("🎉 Verification Complete!")
    print("\n📋 Next Steps:")
    print("1. If health check passed, API is working!")
    print("2. Generate API keys for authentication")
    print("3. Use Postman collection for detailed testing")
    print("4. Check enhanced_rest_api/README.md for full documentation")

if __name__ == "__main__":
    main()
