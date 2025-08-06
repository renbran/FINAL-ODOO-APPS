#!/usr/bin/env python3
"""
Odoo Database List Tool
Lists available databases on the Odoo server
"""
import requests
import json

def get_database_list(base_url):
    """Get list of available databases"""
    db_list_url = f"{base_url}/web/database/list"
    
    data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {}
    }
    
    try:
        print(f"🔍 Checking databases at: {base_url}")
        response = requests.post(db_list_url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('result'):
                databases = result['result']
                print(f"   ✅ Found {len(databases)} database(s):")
                for i, db in enumerate(databases, 1):
                    print(f"   {i}. {db}")
                return databases
            else:
                print(f"   ⚠️  No databases found or database manager disabled")
                return []
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return []

def test_direct_api_access(base_url):
    """Test if we can access API directly without authentication"""
    test_url = f"{base_url}/api/v1/status"
    
    try:
        print(f"🧪 Testing direct API access...")
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ API is accessible")
            print(f"   📊 Status: {result.get('data', {}).get('status', 'Unknown')}")
            return True
        else:
            print(f"   ❌ API not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    base_url = "https://testerp.cloudpepper.site"
    
    print("🔍 Odoo Server Diagnostic Tool")
    print("=" * 50)
    
    # Check databases
    databases = get_database_list(base_url)
    
    # Test API access
    test_direct_api_access(base_url)
    
    print("\n📋 Recommended next steps:")
    if databases:
        print(f"1. Try database name: {databases[0]}")
    else:
        print("1. Database manager might be disabled")
        print("2. Try common database names: 'odoo', 'postgres', or server-specific name")
    
    print("3. Contact system admin for correct database name")
    print("4. Check if Enhanced REST API module is installed in Apps")

if __name__ == "__main__":
    main()
