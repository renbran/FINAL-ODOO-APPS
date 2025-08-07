#!/usr/bin/env python3
"""
Database cleanup script for payment_account_enhanced module
This will remove cached XML data causing the web.assets_backend error
"""

import os
import sys

def create_sql_cleanup_script():
    """Create SQL commands to clean up the module data"""
    
    sql_commands = """
-- SQL Commands to fix web.assets_backend error for payment_account_enhanced
-- These commands remove cached XML data from the database

-- 1. Remove all ir.model.data entries for the module
DELETE FROM ir_model_data WHERE module = 'payment_account_enhanced';

-- 2. Remove module from installed modules (to force clean reinstall)
DELETE FROM ir_module_module WHERE name = 'payment_account_enhanced';

-- 3. Clear any cached template data
DELETE FROM ir_ui_view WHERE key LIKE 'payment_account_enhanced.%';

-- 4. Clear any cached asset data
DELETE FROM ir_attachment WHERE res_model = 'ir.ui.view' AND res_name LIKE '%payment_account_enhanced%';

-- 5. Clear QWeb template cache
DELETE FROM ir_qweb WHERE arch_db LIKE '%payment_account_enhanced%';

-- Verify cleanup
SELECT 'Cleanup complete - module data removed';
"""
    
    with open('cleanup_payment_module.sql', 'w') as f:
        f.write(sql_commands)
    
    print("✅ Created cleanup_payment_module.sql")
    return 'cleanup_payment_module.sql'

def create_python_cleanup_script():
    """Create Python script for Odoo shell cleanup"""
    
    python_commands = """
# Python commands to run in Odoo shell
# Run this after connecting to your Odoo database

# Remove the module completely
try:
    module = env['ir.module.module'].search([('name', '=', 'payment_account_enhanced')])
    if module:
        module.button_immediate_uninstall()
        print("✅ Module uninstalled successfully")
    else:
        print("ℹ️ Module not found in database")
except Exception as e:
    print(f"❌ Error uninstalling: {e}")

# Clear all related data
try:
    env.cr.execute("DELETE FROM ir_model_data WHERE module = 'payment_account_enhanced'")
    env.cr.execute("DELETE FROM ir_ui_view WHERE key LIKE 'payment_account_enhanced.%'")
    env.cr.commit()
    print("✅ Cached data cleared")
except Exception as e:
    print(f"❌ Error clearing data: {e}")

# Update module list
try:
    env['ir.module.module'].update_list()
    print("✅ Module list updated")
except Exception as e:
    print(f"❌ Error updating list: {e}")

print("🎉 Cleanup complete! Now you can install the module fresh.")
"""
    
    with open('cleanup_payment_module.py', 'w', encoding='utf-8') as f:
        f.write(python_commands)
    
    print("✅ Created cleanup_payment_module.py")
    return 'cleanup_payment_module.py'

def main():
    """Main cleanup function"""
    
    print("🧹 Creating cleanup scripts for payment_account_enhanced module...")
    print("   This will resolve the web.assets_backend error by removing cached data")
    
    project_dir = r"d:\RUNNING APPS\ready production\latest\odoo17_final"
    os.chdir(project_dir)
    
    # Create cleanup scripts
    sql_file = create_sql_cleanup_script()
    python_file = create_python_cleanup_script()
    
    print(f"\n📋 CLEANUP INSTRUCTIONS:")
    print(f"   You have 3 options to fix this error:")
    print(f"")
    print(f"🔧 OPTION 1: Direct SQL (Fastest)")
    print(f"   1. Connect to your PostgreSQL database")
    print(f"   2. Run the commands in: {sql_file}")
    print(f"   3. Restart Odoo service")
    print(f"   4. Install module fresh (not upgrade)")
    print(f"")
    print(f"🔧 OPTION 2: Odoo Shell (Safest)")
    print(f"   1. Access Odoo shell: python odoo-bin shell -d your_database")
    print(f"   2. Run the commands in: {python_file}")
    print(f"   3. Restart Odoo")
    print(f"   4. Install module fresh")
    print(f"")
    print(f"🔧 OPTION 3: Manual UI (Easiest)")
    print(f"   1. Go to Odoo Apps menu")
    print(f"   2. Find 'OSUS Payment Voucher Enhanced'")
    print(f"   3. Click 'Uninstall' (if available)")
    print(f"   4. Wait for uninstall to complete")
    print(f"   5. Click 'Install' (not Upgrade)")
    print(f"")
    print(f"🚨 ROOT CAUSE: The database contains cached XML template inheritance")
    print(f"   data from before we fixed the assets.xml file. This cached data")
    print(f"   is trying to inherit from web.assets_backend which isn't found.")
    print(f"")
    print(f"✅ After cleanup: The module will work with the new manifest-based")
    print(f"   asset configuration without any XML template inheritance issues.")

if __name__ == "__main__":
    main()
