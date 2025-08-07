# CLOUDPEPPER EMERGENCY FIX FOR ASSETS BACKEND ERROR
# SSH into your CloudPepper server and run these commands

echo "🚨 CLOUDPEPPER EMERGENCY ASSETS BACKEND FIX"
echo "=============================================="

# Step 1: Connect to Odoo shell
# Run this command: sudo -u odoo python3 /opt/odoo/odoo-bin shell -d YOUR_DATABASE_NAME

# Step 2: Copy and paste this code into the Odoo shell:

print("🚨 EMERGENCY ASSETS BACKEND FIX")
print("=" * 50)

# Fix missing web.assets_backend
print("\n1️⃣ Fixing missing web.assets_backend...")
try:
    assets_backend = env.ref('web.assets_backend', raise_if_not_found=False)
    if not assets_backend:
        print("❌ web.assets_backend is missing - recreating...")
        
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
        
        view = env['ir.ui.view'].create(template_data)
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

# Nuclear cleanup of payment_account_enhanced
print("\n2️⃣ Nuclear cleanup of payment_account_enhanced...")
try:
    module = env['ir.module.module'].search([('name', '=', 'payment_account_enhanced')])
    if module:
        print(f"Found module in state: {module.state}")
        if module.state in ['installed', 'to upgrade', 'to remove']:
            module.write({'state': 'uninstalled'})
        module.unlink()
        print("Module record deleted")
    
    cleanup_queries = [
        "DELETE FROM ir_model_data WHERE module = 'payment_account_enhanced'",
        "DELETE FROM ir_ui_view WHERE key LIKE 'payment_account_enhanced.%'",
        "DELETE FROM ir_ui_view WHERE name LIKE '%payment_account_enhanced%'",
        "DELETE FROM ir_attachment WHERE name LIKE '%payment_account_enhanced%'",
        "DELETE FROM ir_asset WHERE path LIKE '%payment_account_enhanced%'",
        "DELETE FROM ir_model_constraint WHERE name LIKE '%payment_account_enhanced%'",
        "DELETE FROM ir_model_field WHERE model LIKE '%payment_account_enhanced%'",
        "DELETE FROM ir_model WHERE model LIKE '%payment_account_enhanced%'",
        "DELETE FROM ir_model_access WHERE name LIKE '%payment_account_enhanced%'",
        "DELETE FROM ir_rule WHERE name LIKE '%payment_account_enhanced%'",
        "DELETE FROM ir_ui_view WHERE arch_db LIKE '%inherit_id=\"web.assets_backend\"%' AND key LIKE '%payment_account_enhanced%'",
    ]
    
    for query in cleanup_queries:
        try:
            env.cr.execute(query)
            affected_rows = env.cr.rowcount
            if affected_rows > 0:
                print(f"✅ Cleaned {affected_rows} records")
        except Exception as e:
            print(f"⚠️ Query failed: {e}")
    
    print("✅ Database cleanup completed")
except Exception as e:
    print(f"❌ Error during cleanup: {e}")

# Repair core web assets
print("\n3️⃣ Repairing core web assets...")
try:
    env['ir.module.module'].update_list()
    web_module = env['ir.module.module'].search([('name', '=', 'web')])
    if web_module:
        web_module.write({'state': 'to upgrade'})
        print("✅ Web module marked for upgrade")
    
    env.registry.clear_cache()
    env.clear()
    print("✅ Assets repair completed")
except Exception as e:
    print(f"❌ Error repairing assets: {e}")

# Commit changes
print("\n4️⃣ Committing changes...")
try:
    env.cr.commit()
    print("✅ All changes committed to database")
except Exception as e:
    print(f"❌ Error committing: {e}")

print("\n🎉 EMERGENCY FIX COMPLETE!")
print("📋 NEXT STEPS:")
print("1. Exit shell (Ctrl+D)")
print("2. Restart Odoo: sudo systemctl restart odoo")
print("3. Go to Apps → Update Apps List")
print("4. Try installing payment_account_enhanced again")
