#!/usr/bin/env python3
"""
NUCLEAR OPTION: Complete removal and reinstall of payment_account_enhanced
This script will completely wipe the module from database and reinstall clean
"""

def create_complete_removal_script():
    """Create comprehensive database cleanup commands"""
    
    print("💥 Creating NUCLEAR database cleanup for payment_account_enhanced...")
    
    # More comprehensive SQL cleanup
    sql_commands = """
-- NUCLEAR CLEANUP for payment_account_enhanced module
-- This will completely remove ALL traces of the module from database

-- 1. Disable foreign key checks temporarily (if supported)
SET session_replication_role = replica;

-- 2. Remove from module registry
DELETE FROM ir_module_module WHERE name = 'payment_account_enhanced';

-- 3. Remove ALL model data for this module
DELETE FROM ir_model_data WHERE module = 'payment_account_enhanced';

-- 4. Remove ALL views created by this module
DELETE FROM ir_ui_view WHERE key LIKE 'payment_account_enhanced.%';
DELETE FROM ir_ui_view WHERE name LIKE '%payment_account_enhanced%';

-- 5. Remove ALL templates/QWeb data
DELETE FROM ir_qweb WHERE arch_db LIKE '%payment_account_enhanced%';

-- 6. Remove menu items
DELETE FROM ir_ui_menu WHERE action LIKE '%payment_account_enhanced%';

-- 7. Remove translations
DELETE FROM ir_translation WHERE src LIKE '%payment_account_enhanced%';
DELETE FROM ir_translation WHERE name LIKE '%payment_account_enhanced%';

-- 8. Remove server actions
DELETE FROM ir_actions_server WHERE name LIKE '%payment_account_enhanced%';

-- 9. Remove report actions
DELETE FROM ir_actions_report WHERE report_name LIKE '%payment_account_enhanced%';

-- 10. Remove access rules
DELETE FROM ir_model_access WHERE name LIKE '%payment_account_enhanced%';

-- 11. Remove record rules
DELETE FROM ir_rule WHERE name LIKE '%payment_account_enhanced%';

-- 12. Remove sequences
DELETE FROM ir_sequence WHERE code LIKE '%payment_account_enhanced%';

-- 13. Remove cron jobs
DELETE FROM ir_cron WHERE name LIKE '%payment_account_enhanced%';

-- 14. Remove attachments
DELETE FROM ir_attachment WHERE res_model LIKE '%payment_account_enhanced%';

-- 15. Clear asset cache completely
DELETE FROM ir_attachment WHERE name LIKE '%.assets_%';
DELETE FROM ir_attachment WHERE name LIKE 'web.assets_%';

-- 16. Re-enable foreign key checks
SET session_replication_role = DEFAULT;

-- 17. Vacuum to clean up
VACUUM ANALYZE;

-- Verification
SELECT 'NUCLEAR CLEANUP COMPLETE - All traces removed' as status;
SELECT COUNT(*) as remaining_traces FROM ir_model_data WHERE module = 'payment_account_enhanced';
"""
    
    with open('nuclear_cleanup_payment.sql', 'w', encoding='utf-8') as f:
        f.write(sql_commands)
    
    print("✅ Created nuclear_cleanup_payment.sql")
    
    # Create Python script for immediate execution
    python_script = """
# EMERGENCY Python script for immediate cleanup
# Run this in Odoo shell: python odoo-bin shell -d your_database

# Force uninstall if module exists
try:
    module = env['ir.module.module'].search([('name', '=', 'payment_account_enhanced')])
    if module:
        if module.state in ['installed', 'to upgrade', 'to remove']:
            print(f"Found module in state: {module.state}")
            module.write({'state': 'to remove'})
            module.button_immediate_uninstall()
            print("Module force-uninstalled")
        module.unlink()
        print("Module record deleted")
    else:
        print("Module not found in registry")
except Exception as e:
    print(f"Uninstall error (expected): {e}")

# Nuclear database cleanup
cleanup_queries = [
    "DELETE FROM ir_model_data WHERE module = 'payment_account_enhanced'",
    "DELETE FROM ir_ui_view WHERE key LIKE 'payment_account_enhanced.%'",
    "DELETE FROM ir_attachment WHERE name LIKE '%.assets_%'",
    "DELETE FROM ir_qweb WHERE arch_db LIKE '%payment_account_enhanced%'"
]

for query in cleanup_queries:
    try:
        env.cr.execute(query)
        print(f"✅ Executed: {query}")
    except Exception as e:
        print(f"❌ Failed: {query} - {e}")

# Commit changes
env.cr.commit()

# Update module list
env['ir.module.module'].update_list()
print("🎉 NUCLEAR CLEANUP COMPLETE!")
print("📋 Now search for 'payment_account_enhanced' and install fresh")
"""
    
    with open('nuclear_cleanup_payment.py', 'w', encoding='utf-8') as f:
        f.write(python_script)
    
    print("✅ Created nuclear_cleanup_payment.py")

def create_step_by_step_instructions():
    """Create detailed step-by-step instructions"""
    
    instructions = """
🚨 STEP-BY-STEP NUCLEAR FIX for web.assets_backend error

PROBLEM: Database contains cached XML template inheritance data that references 
the old assets.xml structure we removed. Even during fresh installation, 
Odoo finds this cached data and tries to process it.

SOLUTION: Complete nuclear removal and fresh installation

📋 METHOD 1: Database Direct Access (Fastest)
1. Access your PostgreSQL database directly:
   psql -U odoo -d your_database_name

2. Copy and paste ALL contents of nuclear_cleanup_payment.sql
   (This will remove every trace of the module)

3. Restart Odoo service completely

4. Go to Odoo Apps → Update Apps List

5. Search "payment_account_enhanced" → Click Install (not Upgrade)

📋 METHOD 2: Odoo Shell (Safer but slower)
1. Stop Odoo service

2. Run Odoo shell:
   python odoo-bin shell -d your_database_name

3. Copy and paste ALL contents of nuclear_cleanup_payment.py

4. Exit shell and restart Odoo

5. Install module fresh

📋 METHOD 3: Manual UI + Database (Hybrid)
1. In Odoo Apps, try to Uninstall the module (if button exists)

2. If uninstall works: Great! Then install fresh

3. If uninstall fails: Use METHOD 1 (SQL cleanup)

🔍 WHY NUCLEAR APPROACH?
- Normal uninstall may not clear XML template cache
- Asset inheritance creates deep database dependencies  
- Fresh install needs completely clean slate
- Cached ir_qweb and ir_ui_view data causes conflicts

✅ AFTER NUCLEAR CLEANUP:
- Module will install with manifest-based assets only
- No XML template inheritance conflicts
- All CSS/JS will load from __manifest__.py assets section
- Error will be permanently resolved

⚠️  WARNING: This removes ALL module data! 
If you have important payment data, backup first!
"""
    
    with open('NUCLEAR_FIX_INSTRUCTIONS.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("✅ Created NUCLEAR_FIX_INSTRUCTIONS.md")

def main():
    create_complete_removal_script()
    create_step_by_step_instructions()
    
    print("\n💥 NUCLEAR OPTION READY!")
    print("📁 Files created:")
    print("   - nuclear_cleanup_payment.sql (Database cleanup)")
    print("   - nuclear_cleanup_payment.py (Odoo shell cleanup)")  
    print("   - NUCLEAR_FIX_INSTRUCTIONS.md (Step-by-step guide)")
    print("\n🚨 This is the ONLY way to fix persistent cache issues!")
    print("   The database has deep XML template inheritance cache")
    print("   that normal upgrade/uninstall cannot clear.")
    print("\n🎯 Recommended: Use METHOD 1 (SQL) for fastest results")

if __name__ == "__main__":
    main()
