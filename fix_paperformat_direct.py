#!/usr/bin/env python3
"""
Direct fix for the osus_invoice_report.paperformat_osus_invoice external ID issue.
This script creates the missing external ID if it doesn't exist.

Usage in Odoo shell:
    odoo-bin shell -d your_database < fix_paperformat_direct.py
"""

import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def fix_paperformat_external_id():
    """Create the missing paper format and external ID."""
    try:
        env = globals().get('env')
        if not env:
            logger.error("This script must be run in Odoo shell context")
            return False
            
        logger.info("Fixing paper format external ID...")
        
        ir_model_data = env['ir.model.data']
        paperformat_model = env['report.paperformat']
        
        # Check if external ID already exists
        existing_external_id = ir_model_data.search([
            ('module', '=', 'osus_invoice_report'),
            ('name', '=', 'paperformat_osus_invoice')
        ])
        
        if existing_external_id:
            # Check if the referenced record exists
            if existing_external_id.res_id:
                paperformat = paperformat_model.browse(existing_external_id.res_id)
                if paperformat.exists():
                    logger.info(f"✅ Paper format already exists: {paperformat.name}")
                    return True
                else:
                    logger.info("External ID exists but referenced record is missing, recreating...")
                    existing_external_id.unlink()
            else:
                logger.info("External ID exists but has no res_id, removing...")
                existing_external_id.unlink()
        
        # Create the paper format
        logger.info("Creating OSUS paper format...")
        paperformat = paperformat_model.create({
            'name': 'OSUS Invoice Format',
            'format': 'A4',
            'orientation': 'Portrait',
            'margin_top': 50,
            'margin_bottom': 50,
            'margin_left': 10,
            'margin_right': 10,
            'header_line': False,
            'header_spacing': 40,
            'dpi': 90,
        })
        
        # Create the external ID
        logger.info("Creating external ID...")
        ir_model_data.create({
            'module': 'osus_invoice_report',
            'name': 'paperformat_osus_invoice',
            'model': 'report.paperformat',
            'res_id': paperformat.id,
            'noupdate': True,
        })
        
        env.cr.commit()
        
        logger.info(f"✅ Successfully created paper format: {paperformat.name} (ID: {paperformat.id})")
        logger.info("✅ External ID osus_invoice_report.paperformat_osus_invoice created")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fixing paper format: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_fix():
    """Verify that the fix was successful."""
    try:
        env = globals().get('env')
        if not env:
            return False
            
        # Try to resolve the external ID
        try:
            paperformat_ref = env.ref('osus_invoice_report.paperformat_osus_invoice')
            logger.info(f"✅ External ID resolved successfully: {paperformat_ref.name}")
            return True
        except ValueError as e:
            logger.error(f"❌ External ID still cannot be resolved: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error verifying fix: {e}")
        return False

if __name__ == "__main__":
    print("This script should be run in Odoo shell context.")
    print("Usage: odoo-bin shell -d your_database < fix_paperformat_direct.py")
else:
    print("=" * 60)
    print("OSUS Paper Format Fix")
    print("=" * 60)
    
    success = fix_paperformat_external_id()
    
    if success:
        print("\nVerifying fix...")
        if verify_fix():
            print("\n✅ Paper format fix completed successfully!")
            print("You can now try installing the osus_invoice_report module.")
        else:
            print("\n⚠️ Paper format created but verification failed.")
    else:
        print("\n❌ Paper format fix failed.")
    
    print("=" * 60)
