#!/var/odoo/osusproperties/venv/bin/python
import sys
sys.path.insert(0, '/var/odoo/osusproperties/src')

import odoo
from odoo import api, SUPERUSER_ID

odoo.tools.config.parse_config(['-c', '/var/odoo/osusproperties/odoo.conf'])
registry = odoo.registry('osusproperties')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Search for custom_background module
    module = env['ir.module.module'].search([('name', '=', 'custom_background')], limit=1)
    
    if module and module.state == 'installed':
        print(f"Found custom_background module (ID: {module.id}, State: {module.state})")
        print("Uninstalling...")
        module.button_immediate_uninstall()
        cr.commit()
        print("✅ custom_background uninstalled successfully")
    else:
        print(f"ℹ️ custom_background module not installed or already uninstalled")
