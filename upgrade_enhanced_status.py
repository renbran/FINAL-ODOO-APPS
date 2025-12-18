#!/usr/bin/env python3
"""
Upgrade enhanced_status module to load new commission report template
"""

import xmlrpc.client

URL = "http://127.0.0.1:3000"
DB = "osusproperties"
USERNAME = "admin"
PASSWORD = "admin123"

def upgrade_module():
    print("=" * 60)
    print("UPGRADING enhanced_status MODULE")
    print("=" * 60)
    
    # Connect
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    print(f"\nServer: {common.version()['server_version']}")
    
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    if not uid:
        print("ERROR: Authentication failed!")
        return False
    print(f"Authenticated as UID: {uid}")
    
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    
    # Find the enhanced_status module
    print("\n1. Finding enhanced_status module...")
    module = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
        [[['name', '=', 'enhanced_status']]],
        {'fields': ['id', 'name', 'state', 'latest_version']}
    )
    
    if not module:
        print("   ERROR: enhanced_status module not found!")
        return False
    
    mod = module[0]
    print(f"   Module: {mod['name']}")
    print(f"   State: {mod['state']}")
    print(f"   Version: {mod.get('latest_version', 'N/A')}")
    print(f"   ID: {mod['id']}")
    
    # Upgrade the module
    print("\n2. Triggering module upgrade...")
    try:
        # Set module to upgrade
        models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'button_immediate_upgrade',
            [[mod['id']]]
        )
        print("   Upgrade triggered successfully!")
    except Exception as e:
        print(f"   Error during upgrade: {e}")
        print("   This is expected - the server may restart during upgrade")
        print("   Please check server status manually")
    
    return True

if __name__ == "__main__":
    upgrade_module()
    print("\n" + "=" * 60)
    print("After upgrade, test the report by:")
    print("1. Go to Sales -> Orders -> Select any confirmed order")
    print("2. Click Print -> Commission Payout Report")
    print("=" * 60)
