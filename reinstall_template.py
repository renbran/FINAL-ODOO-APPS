#!/usr/bin/env python3
"""
Upgrade/Reinstall osus_global_pdf_template module
"""

# Update module list first
print("Updating module list...")
env['ir.module.module'].update_list()

# Find the module
module = env['ir.module.module'].search([('name', '=', 'osus_global_pdf_template')])

if module:
    print(f"Found module: {module.name}")
    print(f"Current state: {module.state}")
    
    if module.state == 'uninstalled':
        print("\nInstalling module...")
        module.button_immediate_install()
        print("✅ Module installed!")
    elif module.state == 'installed':
        print("\nUpgrading module...")
        module.button_immediate_upgrade()
        print("✅ Module upgraded!")
    else:
        print(f"\n⚠️ Module in unexpected state: {module.state}")
        print("Trying to install...")
        module.button_immediate_install()
else:
    print("❌ Module not found!")
    print("Make sure osus_global_pdf_template is in the addons path")
