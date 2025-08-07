#!/usr/bin/env python3
"""
Force clean update script for payment_account_enhanced module
This will completely remove and reinstall the module to clear cached XML data
"""

import os
import sys
import subprocess

def force_clean_module_update():
    """Force clean update of payment_account_enhanced module"""
    
    print("🧹 Force cleaning payment_account_enhanced module...")
    
    project_dir = r"d:\RUNNING APPS\ready production\latest\odoo17_final"
    os.chdir(project_dir)
    
    print("\n🔍 Step 1: Checking for Python cache files...")
    cache_files = []
    for root, dirs, files in os.walk('payment_account_enhanced'):
        for file in files:
            if file.endswith('.pyc') or file.endswith('.pyo'):
                cache_files.append(os.path.join(root, file))
    
    if cache_files:
        print(f"   Found {len(cache_files)} cache files to remove:")
        for cache_file in cache_files:
            print(f"      Removing: {cache_file}")
            try:
                os.remove(cache_file)
            except:
                pass
    else:
        print("   ✓ No Python cache files found")
    
    print("\n🔍 Step 2: Checking for __pycache__ directories...")
    pycache_dirs = []
    for root, dirs, files in os.walk('payment_account_enhanced'):
        if '__pycache__' in dirs:
            pycache_dirs.append(os.path.join(root, '__pycache__'))
    
    if pycache_dirs:
        print(f"   Found {len(pycache_dirs)} __pycache__ directories to remove:")
        for pycache_dir in pycache_dirs:
            print(f"      Removing: {pycache_dir}")
            try:
                import shutil
                shutil.rmtree(pycache_dir)
            except:
                pass
    else:
        print("   ✓ No __pycache__ directories found")
    
    print("\n📋 Step 3: Generating Odoo commands for manual execution...")
    
    commands = """
    
    🐳 DOCKER COMMANDS TO RUN MANUALLY:
    
    1. Stop Odoo:
       docker-compose stop odoo
    
    2. Start Odoo with module uninstall:
       docker-compose exec db psql -U odoo -d odoo -c "DELETE FROM ir_module_module WHERE name='payment_account_enhanced';"
       docker-compose exec db psql -U odoo -d odoo -c "DELETE FROM ir_model_data WHERE module='payment_account_enhanced';"
    
    3. Restart Odoo:
       docker-compose start odoo
    
    4. Update apps list and reinstall:
       - Go to http://localhost:8069
       - Apps → Update Apps List
       - Search for "OSUS Payment Voucher Enhanced"
       - Click Install (not Upgrade)
    
    ALTERNATIVE SIMPLE RESTART:
    
    docker-compose down
    docker-compose up -d
    
    Then try upgrading the module again.
    """
    
    print(commands)
    
    print("\n💡 The error suggests cached XML data in the database.")
    print("   This often happens when XML template inheritance conflicts occur.")
    print("   A complete restart should resolve the web.assets_backend error.")
    
    return True

if __name__ == "__main__":
    force_clean_module_update()
