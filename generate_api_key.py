#!/usr/bin/env python3
"""
Enhanced REST API - API Key Generator
Generates API keys for testing the Enhanced REST API
"""
import requests
import json
import sys

def generate_api_key(base_url, username, password):
    """Generate API key using POST request"""
    url = f"{base_url}/api/v1/auth/generate-key"
    
    data = {
        'username': username,
        'password': password
    }
    
    try:
        print(f"🔑 Generating API key for user: {username}")
        print(f"   URL: {url}")
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                api_key = result['data']['api_key']
                print(f"   ✅ SUCCESS: API Key Generated")
                print(f"   🔐 API Key: {api_key}")
                print(f"   📝 User ID: {result['data']['user_id']}")
                return api_key
            else:
                print(f"   ❌ FAILED: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ HTTP ERROR: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ CONNECTION ERROR: {str(e)}")
    
    return None

def test_with_api_key(base_url, api_key):
    """Test endpoints with generated API key"""
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    endpoints = [
        ("/api/v1/crm/leads", "CRM Leads with API Key"),
        ("/api/v1/sales/orders", "Sales Orders with API Key"),
    ]
    
    print("\n🔍 Testing endpoints with API key:")
    print("-" * 50)
    
    for endpoint, description in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            print(f"📍 Testing {description}")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ SUCCESS: Data retrieved")
                    data = result.get('data', {})
                    if isinstance(data, list):
                        print(f"   📊 Records found: {len(data)}")
                    else:
                        print(f"   📄 Response type: {type(data).__name__}")
                else:
                    print(f"   ⚠️  API Error: {result.get('error', 'Unknown')}")
            else:
                print(f"   ❌ HTTP ERROR: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ CONNECTION ERROR: {str(e)}")
        
        print()

def main():
    """Main function"""
    print("🔑 Enhanced REST API - API Key Generator")
    print("=" * 50)
    
    # Get inputs
    if len(sys.argv) >= 4:
        base_url = sys.argv[1]
        username = sys.argv[2]
        password = sys.argv[3]
    else:
        base_url = input("Enter Odoo base URL (e.g., https://testerp.cloudpepper.site): ").strip()
        username = input("Enter Odoo username (e.g., admin): ").strip()
        password = input("Enter Odoo password: ").strip()
    
    if not base_url.startswith('http'):
        base_url = f"http://{base_url}"
    
    base_url = base_url.rstrip('/')
    
    print(f"\n🌐 API Base URL: {base_url}")
    print(f"👤 Username: {username}")
    print("=" * 50)
    
    # Generate API key
    api_key = generate_api_key(base_url, username, password)
    
    if api_key:
        # Test with API key
        test_with_api_key(base_url, api_key)
        
        print("=" * 50)
        print("🎉 API Key Generation Complete!")
        print(f"\n🔐 Your API Key: {api_key}")
        print("\n📋 How to use:")
        print("1. Add this header to your requests:")
        print(f"   X-API-Key: {api_key}")
        print("2. Use Postman collection for detailed testing")
        print("3. Check documentation in enhanced_rest_api/README.md")
    else:
        print("\n❌ API Key generation failed!")
        print("📋 Troubleshooting:")
        print("1. Check username/password")
        print("2. Ensure Enhanced REST API module is installed")
        print("3. Verify Odoo server is running")

if __name__ == "__main__":
    main()
