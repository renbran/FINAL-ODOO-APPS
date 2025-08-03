#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Odoo Module Installation Helper
Helps install and update modules on remote Odoo instances
"""

import requests
import json
import sys

class OdooModuleInstaller:
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
    
    def update_apps_list(self):
        """Update the apps list to see new modules"""
        try:
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
                        'update_list'
                    ]
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
                    print("✅ Apps list updated successfully")
                    return True
                else:
                    print("❌ Failed to update apps list")
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Update apps list error: {str(e)}")
            return False
    
    def search_module(self, module_name):
        """Search for a module"""
        try:
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
                        ['name', 'state', 'summary', 'installed_version']
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
                    print(f"✅ Module found: {module['name']}")
                    print(f"   State: {module['state']}")
                    print(f"   Summary: {module.get('summary', 'N/A')}")
                    print(f"   Version: {module.get('installed_version', 'N/A')}")
                    return module
                else:
                    print(f"❌ Module '{module_name}' not found")
                    return None
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Search module error: {str(e)}")
            return None
    
    def install_module(self, module_name):
        """Install a module"""
        try:
            # First find the module
            module = self.search_module(module_name)
            if not module:
                return False
            
            if module['state'] == 'installed':
                print(f"✅ Module '{module_name}' is already installed")
                return True
            
            # Install the module
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
                        'button_immediate_install',
                        [module['id']]
                    ]
                },
                'id': 4
            }
            
            response = self.session.post(
                f"{self.url}/jsonrpc",
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Module '{module_name}' installation initiated")
                return True
            else:
                print(f"❌ Installation failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Install module error: {str(e)}")
            return False
    
    def upgrade_module(self, module_name):
        """Upgrade/Update a module"""
        try:
            # First find the module
            module = self.search_module(module_name)
            if not module:
                return False
            
            # Upgrade the module
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
                        'button_immediate_upgrade',
                        [module['id']]
                    ]
                },
                'id': 5
            }
            
            response = self.session.post(
                f"{self.url}/jsonrpc",
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Module '{module_name}' upgrade initiated")
                return True
            else:
                print(f"❌ Upgrade failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Upgrade module error: {str(e)}")
            return False

def main():
    print("🚀 Odoo Module Installation Helper")
    print("=" * 40)
    print("\n📋 Server Configuration:")
    print("   Source: /var/odoo/coatest/src")
    print("   Logs: /var/odoo/coatest/logs")
    print("   Config: /var/odoo/coatest/odoo.conf")
    print("   Python: /var/odoo/coatest/venv/bin/python3")
    print("")
    
    # Use the same connection details from before
    url = "https://coatest.cloudpepper.site"
    database = "coatest"
    username = "salescompliance@osusproperties.com"
    password = "8586583"
    
    installer = OdooModuleInstaller(url, database, username, password)
    
    if not installer.authenticate():
        print("❌ Cannot proceed without authentication")
        return
    
    print("\n🔄 Updating apps list...")
    if not installer.update_apps_list():
        print("⚠️  Apps list update failed - this might indicate server issues")
    
    print("\n🔍 Searching for CRM Executive Dashboard...")
    module = installer.search_module('crm_executive_dashboard')
    
    if module:
        if module['state'] != 'installed':
            print(f"\n📦 Installing module...")
            installer.install_module('crm_executive_dashboard')
        else:
            print(f"\n🔄 Module already installed, attempting upgrade...")
            installer.upgrade_module('crm_executive_dashboard')
    else:
        print("\n❌ Module not found. This could mean:")
        print("   1. The module files are not in the addons directory")
        print("   2. There are syntax errors in __manifest__.py")
        print("   3. The server needs to be restarted")
        print("   4. Database registry is corrupted")
        
        print("\n🔧 Server Commands to Run:")
        print("   # Check server status:")
        print("   ps aux | grep odoo-bin")
        print("")
        print("   # Restart Odoo server:")
        print("   sudo pkill -f odoo-bin")
        print("   cd /var/odoo/coatest && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --daemon")
        print("")
        print("   # Update all modules:")
        print("   cd /var/odoo/coatest && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init --update all")
        print("")
        print("   # Check logs:")
        print("   tail -f /var/odoo/coatest/logs/odoo.log")
        print("")
        print("   # Deploy CRM Dashboard:")
        print("   1. Upload crm_executive_dashboard folder to addons directory")
        print("   2. sudo chown -R odoo:odoo /path/to/addons/crm_executive_dashboard")
        print("   3. sudo chmod -R 755 /path/to/addons/crm_executive_dashboard")
        print("   4. Restart Odoo and update apps list")

if __name__ == "__main__":
    main()
