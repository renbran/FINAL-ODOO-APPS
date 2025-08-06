#!/usr/bin/env python3
"""
Enhanced REST API - Final Working Test
Tests your working API key with available endpoints
"""
import requests
import json

def test_working_endpoints():
    """Test the working endpoints with your API key"""
    
    base_url = "https://testerp.cloudpepper.site"
    api_key = "9990ae0a2c22e17acc150028e83c9503cf83af5d"
    
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    print("🚀 Testing Your Working API Endpoints")
    print("=" * 50)
    print(f"🔐 API Key: {api_key}")
    print("=" * 50)
    
    # Working endpoints
    endpoints = [
        ("/api/v1/status", "Health Check"),
        ("/api/v1/crm/leads", "CRM Leads"),
        ("/api/v1/crm/dashboard", "CRM Dashboard"), 
        ("/api/v1/sales/orders", "Sales Orders"),
        ("/api/v1/sales/products", "Products List"),
        ("/api/v1/payments/vouchers", "Payment Vouchers"),
        ("/api/v1/payments/voucher/data/1", "Payment Voucher Data"),
    ]
    
    for endpoint, description in endpoints:
        url = f"{base_url}{endpoint}"
        
        try:
            print(f"📍 {description}")
            print(f"   🔗 {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    data = result.get('data', {})
                    
                    if isinstance(data, list):
                        print(f"   ✅ SUCCESS: Found {len(data)} records")
                        if data and len(data) > 0:
                            # Show sample of first record
                            sample = data[0]
                            if isinstance(sample, dict):
                                sample_keys = list(sample.keys())[:3]
                                print(f"   📄 Sample fields: {sample_keys}")
                    elif isinstance(data, dict):
                        print(f"   ✅ SUCCESS: Retrieved data object")
                        if data:
                            keys = list(data.keys())[:3]
                            print(f"   📄 Data keys: {keys}")
                    else:
                        print(f"   ✅ SUCCESS: {data}")
                        
                else:
                    error = result.get('error', {})
                    print(f"   ❌ ERROR: {error.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
        
        print()
    
    print("🎉 API Testing Complete!")
    print("\n📋 Next Steps:")
    print("1. Use these endpoints in your applications")
    print("2. Check enhanced_rest_api/README.md for full documentation")
    print("3. Import Postman collection for detailed testing")
    print("4. Install Payment Account Enhanced for payment endpoints")
    
    print(f"\n🔗 JotForm Webhook URL:")
    print(f"   {base_url}/api/v1/jotform/webhook")
    
    print(f"\n📱 Example cURL command:")
    print(f"curl -H 'X-API-Key: {api_key}' {base_url}/api/v1/crm/leads")

if __name__ == "__main__":
    test_working_endpoints()
