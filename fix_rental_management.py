#!/usr/bin/env python3
"""
Emergency fix for rental_management module - uninstalls it to remove bad view data
"""
import sys
import os

# Add Odoo to path
sys.path.insert(0, '/var/odoo/scholarixv2/src')

import odoo
from odoo import api, SUPERUSER_ID

def uninstall_rental_management():
    """Uninstall rental_management module to clean bad views"""
    config = '/var/odoo/scholarixv2/odoo.conf'
    odoo.tools.config.parse_config(['-c', config])
    
    registry = odoo.registry('scholarixv2')
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # Find rental_management module
        module = env['ir.module.module'].search([
            ('name', '=', 'rental_management'),
            ('state', '=', 'installed')
        ])
        
        if module:
            print(f"Found module: {module.name} (state: {module.state})")
            print("Uninstalling rental_management...")
            module.button_immediate_uninstall()
            cr.commit()
            print("✅ Module uninstalled successfully")
        else:
            print("❌ rental_management module not found or not installed")

if __name__ == '__main__':
    uninstall_rental_management()
