#!/usr/bin/env python3
"""
Quick fix script for OSUS Invoice Report module installation issues.
This script handles the paper format external ID issue and ensures proper module installation.

Usage:
    python fix_osus_module.py

Or via Odoo shell:
    odoo-bin shell -d your_database --addons-path=path/to/addons -c odoo.conf < fix_osus_module.py
"""

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def fix_osus_module():
    """Fix OSUS Invoice Report module installation issues."""
    try:
        # Get environment
        env = globals().get('env')
        if not env:
            logger.error("This script must be run in Odoo shell context")
            return False
            
        logger.info("Starting OSUS module fix...")
        
        # Step 1: Check if paper format exists
        paperformat_model = env['report.paperformat']
        ir_model_data = env['ir.model.data']
        
        # Check if external ID exists
        try:
            external_id = ir_model_data.search([
                ('module', '=', 'osus_invoice_report'),
                ('name', '=', 'paperformat_osus_invoice')
            ])
            
            if external_id:
                logger.info("Paper format external ID already exists")
                paperformat = paperformat_model.browse(external_id.res_id)
                if paperformat.exists():
                    logger.info(f"Paper format found: {paperformat.name}")
                else:
                    logger.warning("External ID exists but paper format record is missing")
                    external_id.unlink()
                    logger.info("Removed orphaned external ID")
            else:
                logger.info("Paper format external ID not found, will be created during module installation")
                
        except Exception as e:
            logger.warning(f"Error checking external ID: {e}")
        
        # Step 2: Update module list
        logger.info("Updating module list...")
        env['ir.module.module'].update_list()
        env.cr.commit()
        
        # Step 3: Find the OSUS module
        osus_module = env['ir.module.module'].search([
            ('name', '=', 'osus_invoice_report')
        ])
        
        if not osus_module:
            logger.error("OSUS Invoice Report module not found in module list")
            return False
            
        logger.info(f"Found module: {osus_module.name} - State: {osus_module.state}")
        
        # Step 4: Handle module installation/upgrade
        if osus_module.state == 'uninstalled':
            logger.info("Installing OSUS Invoice Report module...")
            try:
                osus_module.button_immediate_install()
                logger.info("Module installation initiated successfully")
            except Exception as e:
                logger.error(f"Error during installation: {e}")
                # Try alternative installation method
                logger.info("Trying alternative installation method...")
                osus_module.button_install()
                env.cr.commit()
                
        elif osus_module.state == 'installed':
            logger.info("Module is already installed, upgrading...")
            try:
                osus_module.button_immediate_upgrade()
                logger.info("Module upgrade initiated successfully")
            except Exception as e:
                logger.error(f"Error during upgrade: {e}")
                # Try alternative upgrade method
                logger.info("Trying alternative upgrade method...")
                osus_module.button_upgrade()
                env.cr.commit()
                
        elif osus_module.state == 'to install':
            logger.info("Module is marked for installation, applying...")
            try:
                env['base.module.upgrade'].upgrade_module()
                env.cr.commit()
            except Exception as e:
                logger.error(f"Error applying installation: {e}")
                
        elif osus_module.state == 'to upgrade':
            logger.info("Module is marked for upgrade, applying...")
            try:
                env['base.module.upgrade'].upgrade_module()
                env.cr.commit()
            except Exception as e:
                logger.error(f"Error applying upgrade: {e}")
        
        # Step 5: Verify installation
        osus_module = env['ir.module.module'].search([
            ('name', '=', 'osus_invoice_report')
        ])
        
        logger.info(f"Final module state: {osus_module.state}")
        
        if osus_module.state == 'installed':
            logger.info("✅ OSUS Invoice Report module is now installed successfully!")
            
            # Verify paper format
            try:
                external_id = ir_model_data.search([
                    ('module', '=', 'osus_invoice_report'),
                    ('name', '=', 'paperformat_osus_invoice')
                ])
                
                if external_id:
                    paperformat = paperformat_model.browse(external_id.res_id)
                    logger.info(f"✅ Paper format verified: {paperformat.name}")
                    return True
                else:
                    logger.warning("⚠️ Module installed but paper format external ID not found")
                    
            except Exception as e:
                logger.warning(f"⚠️ Error verifying paper format: {e}")
                
        else:
            logger.warning(f"⚠️ Module installation may not be complete. Current state: {osus_module.state}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during fix: {e}")
        import traceback
        traceback.print_exc()
        return False

def clean_orphaned_records():
    """Clean up any orphaned records that might interfere with module installation."""
    try:
        env = globals().get('env')
        if not env:
            return
            
        logger.info("Cleaning orphaned records...")
        
        # Clean orphaned external IDs
        orphaned_ids = env['ir.model.data'].search([
            ('module', '=', 'osus_invoice_report'),
            ('model', '=', 'report.paperformat')
        ])
        
        for external_id in orphaned_ids:
            # Check if the referenced record exists
            if external_id.model and external_id.res_id:
                try:
                    record = env[external_id.model].browse(external_id.res_id)
                    if not record.exists():
                        logger.info(f"Removing orphaned external ID: {external_id.complete_name}")
                        external_id.unlink()
                except Exception as e:
                    logger.warning(f"Error checking record for {external_id.complete_name}: {e}")
                    
        env.cr.commit()
        logger.info("Orphaned records cleanup completed")
        
    except Exception as e:
        logger.warning(f"Error during cleanup: {e}")

if __name__ == "__main__":
    # This will run when executed directly
    print("This script should be run in Odoo shell context.")
    print("Usage: odoo-bin shell -d your_database --addons-path=path/to/addons < fix_osus_module.py")
else:
    # This runs when imported in Odoo shell
    print("=" * 60)
    print("OSUS Invoice Report Module Fix")
    print("=" * 60)
    
    # Clean orphaned records first
    clean_orphaned_records()
    
    # Fix the module
    success = fix_osus_module()
    
    if success:
        print("\n" + "=" * 60)
        print("Fix completed! Check the logs above for details.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Fix encountered errors. Check the logs above.")
        print("=" * 60)
