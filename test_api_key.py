#!/usr/bin/env python3
"""
Enhanced REST API - Test Existing API Key
Tests the provided API key with all available endpoints
"""
import requests
import json
import time

def test_endpoint(base_url, endpoint, api_key, method="GET", data=None):
    """Test a specific API endpoint with the provided API key"""
    url = f"{base_url}{endpoint}"
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"🔍 Testing: {method} {endpoint}")
        
        if method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=15)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=15)
        else:
            response = requests.get(url, headers=headers, timeout=15)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('success'):
                    data_content = result.get('data', {})
                    if isinstance(data_content, list):
                        print(f"   ✅ SUCCESS: Found {len(data_content)} records")
                        if data_content:
                            print(f"   📄 Sample: {json.dumps(data_content[0], indent=2)[:200]}...")
                    elif isinstance(data_content, dict):
                        print(f"   ✅ SUCCESS: Retrieved data")
                        print(f"   📄 Data: {json.dumps(data_content, indent=2)[:200]}...")
                    else:
                        print(f"   ✅ SUCCESS: {data_content}")
                else:
                    error = result.get('error', {})
                    print(f"   ❌ API ERROR: {error.get('error', 'Unknown error')}")
                    print(f"   🔢 Code: {error.get('code', 'Unknown')}")
            except json.JSONDecodeError:
                print(f"   ⚠️  Non-JSON response: {response.text[:100]}...")
        else:
            print(f"   ❌ HTTP ERROR: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
        
        print()
        time.sleep(0.5)  # Small delay between requests
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ CONNECTION ERROR: {str(e)}")
        print()

def main():
    """Main test function"""
    print("🚀 Enhanced REST API - API Key Tester")
    print("=" * 60)
    
    # Configuration
    base_url = "https://testerp.cloudpepper.site"
    api_key = "9990ae0a2c22e17acc150028e83c9503cf83af5d"
    
    print(f"🌐 Base URL: {base_url}")
    print(f"🔐 API Key: {api_key}")
    print("=" * 60)
    
    # Test all endpoints
    endpoints = [
        # Health and Auth
        ("/api/v1/status", "GET", None, "Health Check"),
        
        # CRM Endpoints
        ("/api/v1/crm/leads", "GET", None, "CRM Leads List"),
        ("/api/v1/crm/leads/1", "GET", None, "CRM Lead Detail"),
        ("/api/v1/crm/dashboard", "GET", None, "CRM Dashboard"),
        
        # Sales Endpoints
        ("/api/v1/sales/orders", "GET", None, "Sales Orders List"),
        ("/api/v1/sales/orders/1", "GET", None, "Sales Order Detail"),
        ("/api/v1/sales/products", "GET", None, "Products List"),
        ("/api/v1/sales/analytics", "GET", None, "Sales Analytics"),
        
        # Payment Endpoints (if payment module is installed)
        ("/api/v1/payments/vouchers", "GET", None, "Payment Vouchers"),
        ("/api/v1/payments/qr-verify", "POST", {"qr_code": "TEST123"}, "QR Code Verification"),
    ]
    
    successful_tests = 0
    total_tests = len(endpoints)
    
    for endpoint, method, data, description in endpoints:
        print(f"📍 {description}")
        test_endpoint(base_url, endpoint, api_key, method, data)
        
        # Count successful tests (basic check)
        if "SUCCESS" in locals():
            successful_tests += 1
    
    print("=" * 60)
    print("🎉 API Testing Complete!")
    print(f"📊 Results: {successful_tests}/{total_tests} endpoints accessible")
    
    if successful_tests > 0:
        print("\n✅ Your API key is working!")
        print("\n📋 Available Endpoints:")
        print("🔗 Health Check: /api/v1/status")
        print("👥 CRM APIs: /api/v1/crm/*")
        print("💰 Sales APIs: /api/v1/sales/*")
        print("💳 Payment APIs: /api/v1/payments/*")
        
        print("\n📚 Next Steps:")
        print("1. Use Postman collection for detailed testing")
        print("2. Check API documentation in enhanced_rest_api/README.md")
        print("3. Integrate with your applications")
        
        print(f"\n🔐 Your API Key: {api_key}")
        print("📝 Add this header to all requests:")
        print(f"   X-API-Key: {api_key}")
    else:
        print("\n❌ API key may not be working properly")
        print("📋 Troubleshooting:")
        print("1. Ensure Enhanced REST API module is installed")
        print("2. Check if API key is valid in Odoo")
        print("3. Verify module dependencies are met")

if __name__ == "__main__":
    main()
