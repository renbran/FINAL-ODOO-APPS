#!/usr/bin/env python3
"""
Quick script to call the Odoo method to fix duplicate partners
This can be run from the Odoo shell or as a management command
"""

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

def run_duplicate_fix():
    """
    Call the fix method through Odoo environment
    This function should be run in Odoo shell context
    """
    try:
        # This assumes you're running in odoo shell with 'env' available
        hr_employee = env['hr.employee']
        
        _logger.info("Calling fix_existing_duplicate_partners method...")
        result = hr_employee.fix_existing_duplicate_partners()
        
        print("="*60)
        print("DUPLICATE PARTNER FIX RESULTS")
        print("="*60)
        print(f"Duplicates found: {result['duplicates_found']}")
        print(f"Records fixed: {result['fixed_count']}")
        print(f"Message: {result['message']}")
        print("="*60)
        
        if result['fixed_count'] > 0:
            # Commit the transaction
            env.cr.commit()
            print("✅ Changes committed to database")
        else:
            print("ℹ️  No changes made")
            
        return result
        
    except NameError:
        print("❌ Error: This script must be run in Odoo shell context")
        print("Run with: python3 odoo-bin shell -d osuspro --addons-path=/path/to/addons")
        print("Then execute: exec(open('fix_duplicate_partners_simple.py').read())")
    except Exception as e:
        print(f"❌ Error running duplicate fix: {str(e)}")
        return None

if __name__ == '__main__':
    # If running as standalone script, show instructions
    print("This script should be run in Odoo shell context:")
    print("1. docker-compose exec odoo python3 odoo-bin shell -d osuspro")
    print("2. In the shell, run: exec(open('/mnt/extra-addons/fix_duplicate_partners_simple.py').read())")
else:
    # If imported in Odoo shell, run the fix
    result = run_duplicate_fix()
