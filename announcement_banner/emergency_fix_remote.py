#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Emergency fix script for announcement_banner console errors
Run this on the remote server if deployment fails
'''

import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

def fix_announcement_banner():
    '''Apply emergency fixes to announcement_banner module'''
    try:
        import odoo
        from odoo import api, SUPERUSER_ID
        
        # Connect to database
        db_name = 'scholarixv2'
        
        with api.Environment.manage():
            registry = odoo.registry(db_name)
            with registry.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                
                # Check if module is installed
                module = env['ir.module.module'].search([
                    ('name', '=', 'announcement_banner'),
                    ('state', '=', 'installed')
                ])
                
                if not module:
                    _logger.error("Module 'announcement_banner' is not installed")
                    return False
                
                _logger.info("Found module: %s (version: %s)", module.name, module.latest_version)
                
                # Force update views
                view_ids = env['ir.ui.view'].search([
                    ('model', '=', 'announcement.banner')
                ])
                
                _logger.info("Found %d views for announcement.banner", len(view_ids))
                
                for view in view_ids:
                    try:
                        # This will recompile the view
                        view._check_xml()
                        _logger.info("✅ View %s validated successfully", view.name)
                    except Exception as e:
                        _logger.error("❌ Error validating view %s: %s", view.name, str(e))
                
                # Clear webclient cache
                env['ir.qweb'].clear_caches()
                env['ir.ui.view'].clear_caches()
                
                # Commit changes
                cr.commit()
                
                _logger.info("✅ Announcement banner fix applied successfully")
                return True
                
    except Exception as e:
        _logger.error("❌ Error applying fix: %s", str(e))
        return False

if __name__ == '__main__':
    success = fix_announcement_banner()
    sys.exit(0 if success else 1)
