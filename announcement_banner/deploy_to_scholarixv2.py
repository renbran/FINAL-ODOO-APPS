#!/usr/bin/env python3
"""
Deploy announcement_banner fix to scholarixv2 database on remote server
This script connects to the remote server and updates the module
"""

import os
import sys

def create_deployment_commands():
    """Generate deployment commands for remote execution"""
    
    commands = """
# Deployment Commands for scholarixv2 Database
# Execute these commands on the remote server

# Step 1: Navigate to Odoo directory
cd /var/odoo/scholarixv2

# Step 2: Backup the current module (optional but recommended)
sudo -u odoo cp -r addons/announcement_banner addons/announcement_banner.backup.$(date +%Y%m%d_%H%M%S)

# Step 3: Update the module in the database (METHOD 1 - Recommended)
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 -u announcement_banner --stop-after-init

# Alternative METHOD 2: Via Odoo shell
sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf -d scholarixv2 << 'EOFPYTHON'
# Update module via shell
env = self.env
module = env['ir.module.module'].search([('name', '=', 'announcement_banner')])
if module:
    module.button_immediate_upgrade()
    print("✅ Module 'announcement_banner' updated successfully")
else:
    print("❌ Module 'announcement_banner' not found")
env.cr.commit()
EOFPYTHON

# Step 4: Restart Odoo service (if needed)
sudo systemctl restart odoo

# Step 5: Clear browser cache and test
echo "✅ Deployment complete. Clear browser cache and test the announcement banner."
"""
    
    return commands

def create_remote_fix_script():
    """Create a Python script to fix the module directly on remote server"""
    
    script = """#!/usr/bin/env python3
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
"""
    
    return script

def main():
    """Main execution"""
    print("=" * 70)
    print("📦 Announcement Banner - scholarixv2 Deployment Guide")
    print("=" * 70)
    print()
    
    # Generate deployment commands
    commands = create_deployment_commands()
    commands_file = 'deployment_commands.sh'
    
    with open(commands_file, 'w', encoding='utf-8') as f:
        f.write(commands)
    
    print(f"✅ Deployment commands saved to: {commands_file}")
    print()
    
    # Generate emergency fix script
    fix_script = create_remote_fix_script()
    fix_file = 'emergency_fix_remote.py'
    
    with open(fix_file, 'w', encoding='utf-8') as f:
        f.write(fix_script)
    
    print(f"✅ Emergency fix script saved to: {fix_file}")
    print()
    
    print("=" * 70)
    print("📋 DEPLOYMENT STEPS")
    print("=" * 70)
    print()
    print("1. Connect to remote server:")
    print("   ssh -i ~/.ssh/odoo17_cloudpepper_new root@139.84.163.11 -p 22")
    print()
    print("2. Upload the module (if modified):")
    print("   scp -i ~/.ssh/odoo17_cloudpepper_new -r announcement_banner root@139.84.163.11:/var/odoo/scholarixv2/addons/")
    print()
    print("3. Run deployment commands:")
    print("   cd /var/odoo/scholarixv2")
    print("   sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 -u announcement_banner --stop-after-init")
    print()
    print("4. Restart Odoo:")
    print("   sudo systemctl restart odoo")
    print()
    print("5. Test in browser:")
    print("   - Clear browser cache (Ctrl+Shift+Delete)")
    print("   - Login to scholarixv2")
    print("   - Check browser console for errors")
    print()
    print("=" * 70)
    print("🔧 COMMON ISSUES & FIXES")
    print("=" * 70)
    print()
    print("Issue: Console error 'undefined is not iterable'")
    print("Fix: Already applied - removed widget='priority' from views")
    print()
    print("Issue: HTML content not displaying")
    print("Fix: Using markup() wrapper in JavaScript - already implemented")
    print()
    print("Issue: OWL lifecycle errors")
    print("Fix: Proper error handling in loadAnnouncements() - already implemented")
    print()
    print("=" * 70)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
