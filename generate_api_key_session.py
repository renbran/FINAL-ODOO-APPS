#!/usr/bin/env python3
"""
Enhanced REST API - Session-based API Key Generator
Generates API keys using Odoo session authentication
"""
import requests
import json
import sys
from urllib.parse import urljoin

class OdooAPIKeyGenerator:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def login(self, username, password, database='odoo'):
        """Login to Odoo and establish session"""
        login_url = f"{self.base_url}/web/session/authenticate"
        
        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'db': database,
                'login': username,
                'password': password
            }
        }
        
        print(f"🔐 Logging in as: {username}")
        
        try:
            response = self.session.post(login_url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('result') and result['result'].get('uid'):
                    print(f"   ✅ Login successful")
                    print(f"   👤 User ID: {result['result']['uid']}")
                    print(f"   🏢 Company: {result['result'].get('company_name', 'Unknown')}")
                    return True
                else:
                    error_msg = result.get('error', {}).get('message', 'Invalid credentials')
                    print(f"   ❌ Login failed: {error_msg}")
                    return False
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False
    
    def generate_api_key_via_rpc(self):
        """Generate API key using Odoo RPC after login"""
        rpc_url = f"{self.base_url}/web/dataset/call_kw"
        
        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'model': 'res.users',
                'method': 'generate_api_key',
                'args': [],
                'kwargs': {}
            }
        }
        
        print(f"🔑 Generating API key via RPC...")
        
        try:
            response = self.session.post(rpc_url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('result'):
                    api_key = result['result']
                    print(f"   ✅ API Key generated successfully")
                    print(f"   🔐 API Key: {api_key}")
                    return api_key
                else:
                    error = result.get('error', {})
                    print(f"   ❌ RPC Error: {error.get('message', 'Unknown error')}")
                    return None
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return None
    
    def test_api_key(self, api_key):
        """Test the generated API key"""
        test_url = f"{self.base_url}/api/v1/crm/leads"
        headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        print(f"🧪 Testing API key...")
        
        try:
            response = requests.get(test_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ API Key test successful")
                    data = result.get('data', [])
                    print(f"   📊 Found {len(data)} CRM leads")
                    return True
                else:
                    print(f"   ⚠️  API returned error: {result.get('error', 'Unknown')}")
                    return False
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False

def main():
    """Main function"""
    print("🔑 Enhanced REST API - Session-based API Key Generator")
    print("=" * 70)
    
    # Get inputs
    if len(sys.argv) >= 4:
        base_url = sys.argv[1]
        username = sys.argv[2]
        password = sys.argv[3]
        database = sys.argv[4] if len(sys.argv) > 4 else 'odoo'
    else:
        base_url = input("Enter Odoo base URL: ").strip()
        username = input("Enter username/email: ").strip()
        password = input("Enter password: ").strip()
        database = input("Enter database name (default: odoo): ").strip() or 'odoo'
    
    if not base_url.startswith('http'):
        base_url = f"https://{base_url}"
    
    print(f"\n🌐 URL: {base_url}")
    print(f"👤 User: {username}")
    print(f"🗄️  Database: {database}")
    print("=" * 70)
    
    # Initialize generator
    generator = OdooAPIKeyGenerator(base_url)
    
    # Login
    if not generator.login(username, password, database):
        print("\n❌ Login failed. Please check credentials and try again.")
        return
    
    # Generate API key
    api_key = generator.generate_api_key_via_rpc()
    
    if not api_key:
        print("\n❌ API key generation failed!")
        print("📋 Possible issues:")
        print("1. Enhanced REST API module not installed")
        print("2. User doesn't have permission to generate API keys")
        print("3. generate_api_key method not available")
        return
    
    # Test API key
    if generator.test_api_key(api_key):
        print("\n🎉 API Key Setup Complete!")
        print("=" * 70)
        print(f"🔐 Your API Key: {api_key}")
        print("\n📋 Usage Instructions:")
        print("1. Add this header to your API requests:")
        print(f"   X-API-Key: {api_key}")
        print("2. Test with Postman collection")
        print("3. Available endpoints:")
        print(f"   - Health: {base_url}/api/v1/status")
        print(f"   - CRM: {base_url}/api/v1/crm/*")
        print(f"   - Sales: {base_url}/api/v1/sales/*")
        print(f"   - Payments: {base_url}/api/v1/payments/*")
    else:
        print(f"\n⚠️  API Key generated but test failed")
        print(f"🔐 Your API Key: {api_key}")
        print("📋 Please test manually with Postman")

if __name__ == "__main__":
    main()
