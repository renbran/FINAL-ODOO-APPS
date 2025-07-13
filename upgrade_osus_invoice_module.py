#!/usr/bin/env python3
"""
Script to upgrade the osus_invoice_report module and fix missing external ID issues.
"""

import logging
import sys
import os

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

def fix_osus_invoice_report_module():
    """
    Comprehensive fix for the osus_invoice_report module external ID issues.
    """
    print("=== OSUS Invoice Report Module Fix ===")
    print()
    
    # Check if we're in an Odoo environment
    try:
        import odoo
        from odoo import api, SUPERUSER_ID
        print("✓ Odoo environment detected")
        
        # Get database name from environment or prompt
        db_name = os.environ.get('ODOO_DB_NAME')
        if not db_name:
            print("Please set ODOO_DB_NAME environment variable or run this in Odoo shell")
            return False
            
        # Initialize Odoo registry
        registry = odoo.registry(db_name)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            
            # Check if module exists
            module = env['ir.module.module'].search([('name', '=', 'osus_invoice_report')])
            if not module:
                print("✗ Module 'osus_invoice_report' not found")
                return False
                
            print(f"✓ Module found - State: {module.state}")
            
            # Check if external IDs exist
            external_ids = [
                'osus_invoice_report.action_report_osus_invoice',
                'osus_invoice_report.action_report_osus_bill',
                'osus_invoice_report.report_osus_invoice_document',
                'osus_invoice_report.report_osus_bill_document'
            ]
            
            missing_ids = []
            for ext_id in external_ids:
                try:
                    env.ref(ext_id)
                    print(f"✓ External ID exists: {ext_id}")
                except ValueError:
                    print(f"✗ Missing external ID: {ext_id}")
                    missing_ids.append(ext_id)
            
            if missing_ids:
                print(f"\n🔧 Upgrading module to fix {len(missing_ids)} missing external IDs...")
                module.button_upgrade()
                cr.commit()
                print("✓ Module upgrade completed")
                
                # Verify fix
                remaining_missing = []
                for ext_id in missing_ids:
                    try:
                        env.ref(ext_id)
                        print(f"✓ Fixed: {ext_id}")
                    except ValueError:
                        remaining_missing.append(ext_id)
                        
                if remaining_missing:
                    print(f"\n⚠️  Still missing {len(remaining_missing)} external IDs after upgrade")
                    print("Attempting force reinstall...")
                    module.button_uninstall()
                    cr.commit()
                    module.button_install()
                    cr.commit()
                    print("✓ Force reinstall completed")
                else:
                    print("✅ All external IDs fixed successfully!")
                    
            else:
                print("✅ All external IDs are present!")
            
            return True
            
    except ImportError:
        print("ℹ️  Not in Odoo environment - providing manual instructions")
        
    print("""
    📋 MANUAL FIX INSTRUCTIONS:
    
    1. Stop your Odoo server
    
    2. Run one of these upgrade commands:
    
       Option A - Upgrade specific module:
       python3 odoo-bin -d your_database_name -u osus_invoice_report --stop-after-init
       
       Option B - Force reinstall:
       python3 odoo-bin -d your_database_name --uninstall osus_invoice_report --stop-after-init
       python3 odoo-bin -d your_database_name -i osus_invoice_report --stop-after-init
       
       Option C - Via Odoo shell:
       python3 odoo-bin shell -d your_database_name
       
       Then in the shell:
       >>> module = env['ir.module.module'].search([('name', '=', 'osus_invoice_report')])
       >>> module.button_upgrade()
       >>> env.cr.commit()
       >>> exit()
    
    3. Start your Odoo server
    
    4. Test the invoice printing functionality
    
    🚨 TEMPORARY WORKAROUND:
    If the issue persists, you can temporarily modify the custom_invoice.py file
    to use a fallback report action.
    """)
    
    return False

def create_fallback_solution():
    """Create a fallback solution in case the external ID issue persists"""
    print("\n🔧 Creating fallback solution...")
    
    fallback_code = '''
    def action_print_custom_invoice(self):
        """
        Print the PDF copy of the invoice using the custom report action.
        With fallback to standard invoice report if custom report is not available.
        """
        try:
            return self.env.ref('osus_invoice_report.action_report_osus_invoice').report_action(self)
        except ValueError:
            # Fallback to standard invoice report
            _logger.warning("Custom invoice report not found, using standard report")
            return self.env.ref('account.account_invoices').report_action(self)

    def action_print_custom_bill(self):
        """
        Print the PDF copy of the bill using the custom report action.
        With fallback to standard bill report if custom report is not available.
        """
        try:
            return self.env.ref('osus_invoice_report.action_report_osus_bill').report_action(self)
        except ValueError:
            # Fallback to standard bill report
            _logger.warning("Custom bill report not found, using standard report")
            return self.env.ref('account.account_invoices').report_action(self)

    def action_print_custom_receipt(self):
        """
        Print the PDF copy of the receipt using the custom report action.
        With fallback to standard invoice report if custom report is not available.
        """
        try:
            return self.env.ref('osus_invoice_report.action_report_osus_invoice').report_action(self)
        except ValueError:
            # Fallback to standard invoice report
            _logger.warning("Custom receipt report not found, using standard report")
            return self.env.ref('account.account_invoices').report_action(self)
    '''
    
    print("💡 Fallback code prepared. This can be applied to custom_invoice.py if needed.")
    return fallback_code

if __name__ == "__main__":
    success = fix_osus_invoice_report_module()
    if not success:
        create_fallback_solution()
        print("\n⚠️  Manual intervention required. Please follow the instructions above.")
