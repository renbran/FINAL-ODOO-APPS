#!/usr/bin/env python3
"""
Module Installation Checker
Checks if Enhanced REST API module is properly installed
"""
import requests
import json

def check_module_installation(base_url):
    """Check if modules are installed by testing specific endpoints"""
    
    # Test if basic rest_api_odoo is working
    try:
        print("🔍 Checking basic REST API (rest_api_odoo)...")
        response = requests.get(f"{base_url}/api/v1/status")
        
        if response.status_code == 200:
            print("   ✅ Basic REST API is working")
            result = response.json()
            print(f"   📊 Status: {result.get('data', {}).get('status', 'Unknown')}")
        else:
            print(f"   ❌ Basic REST API not working: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test Enhanced REST API specific endpoints
    print("\n🔍 Checking Enhanced REST API...")
    
    test_endpoints = [
        "/api/v1/crm/leads",
        "/api/v1/sales/orders", 
        "/api/v1/payments/vouchers"
    ]
    
    enhanced_working = False
    
    for endpoint in test_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            
            if response.status_code == 200:
                result = response.json()
                error = result.get('error', {})
                
                if 'authenticate_api_key' in str(error):
                    print(f"   ❌ {endpoint}: Module code exists but not installed")
                elif 'API key required' in str(error):
                    print(f"   ✅ {endpoint}: Module installed and working")
                    enhanced_working = True
                else:
                    print(f"   ⚠️  {endpoint}: Unknown status")
            elif response.status_code == 404:
                print(f"   ❌ {endpoint}: Endpoint not found (module not installed)")
            else:
                print(f"   ❌ {endpoint}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {endpoint}: Error - {str(e)}")
    
    return enhanced_working

def main():
    print("🔍 Enhanced REST API - Installation Checker")
    print("=" * 50)
    
    base_url = "https://testerp.cloudpepper.site"
    print(f"🌐 Checking: {base_url}")
    print("=" * 50)
    
    if check_module_installation(base_url):
        print("\n🎉 Enhanced REST API is installed and working!")
        print("🔐 You can use your API key: 9990ae0a2c22e17acc150028e83c9503cf83af5d")
    else:
        print("\n❌ Enhanced REST API is NOT properly installed")
        print("\n📋 Installation Steps:")
        print("1. Login to Odoo: https://testerp.cloudpepper.site")
        print("2. Go to Apps menu")
        print("3. Click 'Update Apps List'")
        print("4. Search for 'Enhanced REST API'")
        print("5. Click 'Install'")
        print("\n👤 Login: salescompliance@osusproperties.com")

if __name__ == "__main__":
    main()
