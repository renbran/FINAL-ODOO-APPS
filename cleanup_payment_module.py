
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
