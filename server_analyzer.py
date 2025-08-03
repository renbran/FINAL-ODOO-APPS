#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Odoo Server Log Analyzer
Helps analyze server logs to identify issues causing 500 errors
"""

import requests
import json
from datetime import datetime

class OdooServerAnalyzer:
    def __init__(self, url, database, username, password):
        self.url = url.rstrip('/')
        self.database = database
        self.username = username
        self.password = password
        self.session = requests.Session()
        
    def authenticate(self):
        """Authenticate with Odoo"""
        try:
            auth_data = {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'service': 'common',
                    'method': 'authenticate',
                    'args': [self.database, self.username, self.password, {}]
                },
                'id': 1
            }
            
            response = self.session.post(
                f"{self.url}/jsonrpc",
                json=auth_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result and result['result']:
                    print("✅ Authentication successful")
                    return True
                else:
                    print("❌ Authentication failed")
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def check_server_info(self):
        """Get basic server information"""
        try:
            data = {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'service': 'common',
                    'method': 'version'
                },
                'id': 2
            }
            
            response = self.session.post(
                f"{self.url}/jsonrpc",
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    version_info = result['result']
                    print("📊 Server Information:")
                    print(f"   Version: {version_info.get('server_version', 'Unknown')}")
                    print(f"   Series: {version_info.get('server_serie', 'Unknown')}")
                    print(f"   Protocol: {version_info.get('protocol_version', 'Unknown')}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Server info error: {str(e)}")
            return False
    
    def test_basic_endpoints(self):
        """Test basic endpoints that are failing"""
        endpoints_to_test = [
            '/web/static/src/css/bootstrap.css',
            '/web/assets_frontend.min.css',
            '/web/image/website/1/favicon',
            '/web/assets_backend.min.css',
            '/web/static/src/libs/fontawesome/css/font-awesome.css'
        ]
        
        print("\n🔍 Testing problematic endpoints:")
        for endpoint in endpoints_to_test:
            try:
                response = self.session.get(f"{self.url}{endpoint}")
                if response.status_code == 200:
                    print(f"   ✅ {endpoint}: OK")
                elif response.status_code == 404:
                    print(f"   ⚠️  {endpoint}: Not Found (404)")
                elif response.status_code == 500:
                    print(f"   ❌ {endpoint}: Server Error (500)")
                else:
                    print(f"   ⚠️  {endpoint}: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {endpoint}: Exception - {str(e)}")
    
    def check_installed_modules(self):
        """Check key modules that might be causing issues"""
        try:
            critical_modules = [
                'base', 'web', 'website', 'crm', 'sales_team'
            ]
            
            print("\n📦 Checking critical modules:")
            
            for module_name in critical_modules:
                data = {
                    'jsonrpc': '2.0',
                    'method': 'call',
                    'params': {
                        'service': 'object',
                        'method': 'execute',
                        'args': [
                            self.database, 
                            self.username, 
                            self.password,
                            'ir.module.module',
                            'search_read',
                            [('name', '=', module_name)],
                            ['name', 'state']
                        ]
                    },
                    'id': 3
                }
                
                response = self.session.post(
                    f"{self.url}/jsonrpc",
                    json=data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'result' in result and result['result']:
                        module = result['result'][0]
                        state = module['state']
                        if state == 'installed':
                            print(f"   ✅ {module_name}: {state}")
                        else:
                            print(f"   ⚠️  {module_name}: {state}")
                    else:
                        print(f"   ❌ {module_name}: Not found")
                        
        except Exception as e:
            print(f"❌ Module check error: {str(e)}")
    
    def analyze_issues(self):
        """Analyze and provide recommendations"""
        print("\n🔧 ANALYSIS & RECOMMENDATIONS:")
        print("=" * 50)
        
        print("\n🚨 The 500 errors you're seeing suggest:")
        print("   1. Asset compilation issues")
        print("   2. Module dependency problems")
        print("   3. Database corruption")
        print("   4. Server resource limitations")
        
        print("\n💡 Immediate Actions to Try:")
        print("   1. Clear browser cache completely")
        print("   2. Restart Odoo service: sudo systemctl restart odoo")
        print("   3. Update all modules: -u all --stop-after-init")
        print("   4. Check server disk space and memory")
        print("   5. Review Odoo logs for specific Python errors")
        
        print("\n🔍 For CRM Dashboard specifically:")
        print("   1. Upload the crm_executive_dashboard module files")
        print("   2. Set proper file permissions")
        print("   3. Restart Odoo after uploading")
        print("   4. Update apps list in Odoo interface")
        print("   5. Install/upgrade the module")
        
        print("\n📋 Server Log Locations to Check:")
        print("   • /var/log/odoo/odoo.log")
        print("   • /var/log/odoo/odoo-server.log")
        print("   • /var/log/nginx/error.log (if using Nginx)")
        print("   • /var/log/apache2/error.log (if using Apache)")
        
        print("\n⚡ Quick Fixes for Common Issues:")
        print("   • Asset errors: Restart Odoo + clear browser cache")
        print("   • Module errors: Check file syntax and permissions")
        print("   • Database errors: Run database upgrade")
        print("   • Memory errors: Increase server resources")

def main():
    print("🔍 Odoo Server Analyzer")
    print("=" * 30)
    
    # Use existing connection
    url = "https://coatest.cloudpepper.site"
    database = "coatest"
    username = "salescompliance@osusproperties.com"
    password = "8586583"
    
    analyzer = OdooServerAnalyzer(url, database, username, password)
    
    if analyzer.authenticate():
        analyzer.check_server_info()
        analyzer.test_basic_endpoints()
        analyzer.check_installed_modules()
        analyzer.analyze_issues()
    else:
        print("❌ Cannot proceed without authentication")

if __name__ == "__main__":
    main()
