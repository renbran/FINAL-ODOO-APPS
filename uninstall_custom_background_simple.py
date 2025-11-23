#!/usr/bin/env python3
# Simple uninstall script for custom_background module

# Search and uninstall custom_background
module = env['ir.module.module'].search([('name', '=', 'custom_background')])
if module:
    print(f"Found module: {module.name} (state: {module.state})")
    if module.state == 'installed':
        print("Uninstalling custom_background...")
        module.button_immediate_uninstall()
        print("✅ custom_background uninstalled successfully")
    else:
        print(f"Module is not installed (state: {module.state})")
else:
    print("❌ custom_background module not found")
