#!/usr/bin/env python3
"""
Enhanced REST API - Diagnostic Tool
Debug API responses and check module status
"""
import requests
import json
import sys

def debug_endpoint(url, method="GET", data=None):
    """Debug a specific endpoint with detailed output"""
    print(f"🔍 Testing: {method} {url}")
    print("-" * 50)
    
    try:
        if method.upper() == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Content Length: {len(response.content)} bytes")
        print()
        print("Raw Response:")
        print(response.text[:1000])
        if len(response.text) > 1000:
            print("... (truncated)")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("=" * 60)

def main():
    """Main diagnostic function"""
    print("🔧 Enhanced REST API - Diagnostic Tool")
    print("=" * 60)
    
    base_url = "https://testerp.cloudpepper.site"
    
    # Test endpoints
    print("📍 Testing Health Check Endpoint")
    debug_endpoint(f"{base_url}/api/v1/status")
    
    print("📍 Testing API Key Generation Endpoint (GET)")
    debug_endpoint(f"{base_url}/api/v1/auth/generate-key", "GET")
    
    print("📍 Testing API Key Generation Endpoint (POST)")
    data = {
        'username': 'salescompliance@osusproperties.com',
        'password': '8586583'
    }
    debug_endpoint(f"{base_url}/api/v1/auth/generate-key", "POST", data)
    
    print("📍 Testing CRM Endpoint")
    debug_endpoint(f"{base_url}/api/v1/crm/leads")

if __name__ == "__main__":
    main()
