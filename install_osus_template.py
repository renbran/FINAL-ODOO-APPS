#!/usr/bin/env python3
# Install osus_global_pdf_template module

# Update module list first
env['ir.module.module'].update_list()
print("✅ Module list updated")

# Search for the new module
module = env['ir.module.module'].search([('name', '=', 'osus_global_pdf_template')])
if module:
    print(f"Found module: {module.name} (state: {module.state})")
    if module.state == 'uninstalled':
        print("Installing osus_global_pdf_template...")
        module.button_immediate_install()
        print("✅ osus_global_pdf_template installed successfully")
    else:
        print(f"Module already installed (state: {module.state})")
else:
    print("❌ osus_global_pdf_template module not found - check module path")
