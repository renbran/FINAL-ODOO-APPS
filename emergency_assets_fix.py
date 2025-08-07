#!/usr/bin/env python3
"""
EMERGENCY ASSETS BACKEND FIX
This script fixes the missing web.assets_backend template and cleans up payment module issues
Run in Odoo shell: python odoo-bin shell -d your_database

COPY AND PASTE THE FOLLOWING CODE INTO ODOO SHELL:
"""

# EMERGENCY ASSETS BACKEND FIX
print("🚨 EMERGENCY ASSETS BACKEND FIX")
print("=" * 50)

# Step 1: Fix missing web.assets_backend
print("\n1️⃣ Fixing missing web.assets_backend...")
try:
    # Check if web.assets_backend exists
    assets_backend = env.ref('web.assets_backend', raise_if_not_found=False)
    if not assets_backend:
        print("❌ web.assets_backend is missing - recreating...")
        
        # Create the missing template
        template_data = {
            'name': 'assets_backend',
            'key': 'web.assets_backend',
            'type': 'qweb',
            'arch': '''<t t-name="web.assets_backend">
    <t t-call="web.assets_common"/>
    <link rel="stylesheet" type="text/css" href="/web/static/src/scss/webclient.scss"/>
    <link rel="stylesheet" type="text/css" href="/web/static/src/scss/webclient_layout.scss"/>
    <script type="text/javascript" src="/web/static/src/js/chrome/abstract_web_client.js"/>
    <script type="text/javascript" src="/web/static/src/js/chrome/web_client.js"/>
</t>''',
            'active': True,
        }
        
        # Create the view
        view = env['ir.ui.view'].create(template_data)
        
        # Create the corresponding ir.model.data record
        env['ir.model.data'].create({
            'name': 'assets_backend',
            'module': 'web',
            'model': 'ir.ui.view',
            'res_id': view.id,
        })
        
        print("✅ web.assets_backend recreated successfully")
    else:
        print("✅ web.assets_backend exists")
except Exception as e:
    print(f"❌ Error fixing assets_backend: {e}")

# Step 2: Nuclear cleanup of payment_account_enhanced
print("\n2️⃣ Nuclear cleanup of payment_account_enhanced...")
try:
        # Force uninstall module if exists
        module = env['ir.module.module'].search([('name', '=', 'payment_account_enhanced')])
        if module:
            print(f"Found module in state: {module.state}")
            if module.state in ['installed', 'to upgrade', 'to remove']:
                module.write({'state': 'uninstalled'})
                print("Module state changed to uninstalled")
            module.unlink()
            print("Module record deleted")
        
        # Comprehensive database cleanup
        cleanup_queries = [
            "DELETE FROM ir_model_data WHERE module = 'payment_account_enhanced'",
            "DELETE FROM ir_ui_view WHERE key LIKE 'payment_account_enhanced.%'",
            "DELETE FROM ir_ui_view WHERE name LIKE '%payment_account_enhanced%'",
            "DELETE FROM ir_attachment WHERE name LIKE '%payment_account_enhanced%'",
            "DELETE FROM ir_qweb WHERE arch_db LIKE '%payment_account_enhanced%'",
            "DELETE FROM ir_asset WHERE path LIKE '%payment_account_enhanced%'",
            "DELETE FROM ir_model_constraint WHERE name LIKE '%payment_account_enhanced%'",
            "DELETE FROM ir_model_field WHERE model LIKE '%payment_account_enhanced%'",
            "DELETE FROM ir_model WHERE model LIKE '%payment_account_enhanced%'",
            "DELETE FROM ir_model_access WHERE name LIKE '%payment_account_enhanced%'",
            "DELETE FROM ir_rule WHERE name LIKE '%payment_account_enhanced%'",
            # Clean up any broken template inheritance
            "DELETE FROM ir_ui_view WHERE arch_db LIKE '%inherit_id=\"web.assets_backend\"%' AND key LIKE '%payment_account_enhanced%'",
        ]
        
        for query in cleanup_queries:
            try:
                env.cr.execute(query)
                affected_rows = env.cr.rowcount
                if affected_rows > 0:
                    print(f"✅ Cleaned {affected_rows} records: {query[:50]}...")
            except Exception as e:
                print(f"⚠️ Query failed (may be expected): {query[:50]}... - {e}")
        
    print("✅ Database cleanup completed")
    
except Exception as e:
    print(f"❌ Error during cleanup: {e}")

# Step 3: Repair core web assets
print("\n3️⃣ Repairing core web assets...")
try:
        # Update module list to refresh everything
        env['ir.module.module'].update_list()
        
        # Force reload web module assets
        web_module = env['ir.module.module'].search([('name', '=', 'web')])
        if web_module:
            web_module.write({'state': 'to upgrade'})
            print("✅ Web module marked for upgrade")
        
        # Clear all caches
        env.registry.clear_cache()
        env.clear()
        
        print("✅ Assets repair completed")
        
    except Exception as e:
        print(f"❌ Error repairing assets: {e}")
    
    # Step 4: Commit changes
    print("\n4️⃣ Committing changes...")
    try:
        env.cr.commit()
        print("✅ All changes committed to database")
    except Exception as e:
        print(f"❌ Error committing: {e}")
    
    print("\n🎉 EMERGENCY FIX COMPLETE!")
    print("📋 NEXT STEPS:")
    print("1. Restart Odoo server completely")
    print("2. Go to Apps → Update Apps List")
    print("3. Try installing payment_account_enhanced again")
    print("4. If still issues, check Odoo logs for specific errors")

if __name__ == '__main__':
    emergency_fix()
