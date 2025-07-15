#!/usr/bin/env python3
"""
Fix Duplicate Partner Names Script
This script resolves duplicate partner names that violate the unique constraint.
"""

import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
_logger = logging.getLogger(__name__)

def fix_duplicate_partners():
    """
    Find and fix duplicate partner names by renaming duplicates
    This function should be run in Odoo shell context
    """
    try:
        # Check if we're in Odoo environment
        try:
            import odoo
            from odoo import api, SUPERUSER_ID
            from odoo.tools import config
        except ImportError:
            return {
                'success': False,
                'error': 'Odoo not available. This script must be run in Odoo environment.'
            }
        
        # Try to get existing environment first (if running in shell)
        try:
            # This will work if we're in odoo shell
            global env
            if 'env' in globals():
                _logger.info("Using existing Odoo shell environment")
                current_env = env
            else:
                raise NameError("No existing environment")
        except NameError:
            # Connect to database manually
            _logger.info("Creating new database connection")
            db_name = 'osuspro'  # Your database name
            registry = odoo.registry(db_name)
            
            with registry.cursor() as cr:
                current_env = api.Environment(cr, SUPERUSER_ID, {})
        
        # Clear any aborted transaction state
        try:
            current_env.cr.rollback()
            _logger.info("Rolled back any existing transaction")
        except Exception as rollback_error:
            _logger.warning(f"Rollback attempt: {str(rollback_error)}")
        
        # Find duplicate partner names with transaction safety
        try:
            current_env.cr.execute("""
                SELECT name, COUNT(*), array_agg(id ORDER BY id) as ids
                FROM res_partner 
                WHERE name IS NOT NULL 
                GROUP BY name 
                HAVING COUNT(*) > 1
                ORDER BY COUNT(*) DESC
            """)
            
            duplicates = current_env.cr.fetchall()
            _logger.info(f"Found {len(duplicates)} duplicate partner name groups")
            
        except Exception as query_error:
            _logger.error(f"Error querying duplicates: {str(query_error)}")
            # Try to recover
            current_env.cr.rollback()
            return {
                'success': False,
                'error': f'Database query failed: {str(query_error)}'
            }
        
        fixed_count = 0
        
        for name, count, ids in duplicates:
            _logger.info(f"Fixing duplicate name '{name}' with {count} records: {ids}")
            
            # Keep the first record with original name, rename others
            keep_id = ids[0]
            duplicate_ids = ids[1:]
            
            for i, partner_id in enumerate(duplicate_ids, 1):
                # Use savepoint for each partner update
                savepoint_name = f"fix_partner_{partner_id}"
                
                try:
                    current_env.cr.execute(f"SAVEPOINT {savepoint_name}")
                    
                    partner = current_env['res.partner'].browse(partner_id)
                    if partner.exists():
                        # Generate unique name
                        if partner.email:
                            # Use email-based naming if available
                            email_part = partner.email.split('@')[0].upper()
                            new_name = f"{name} ({email_part})"
                        else:
                            # Use counter-based naming
                            new_name = f"{name} ({i})"
                        
                        # Ensure the new name is also unique
                        counter = 1
                        original_new_name = new_name
                        while current_env['res.partner'].search([('name', '=', new_name)], limit=1):
                            new_name = f"{original_new_name}-{counter}"
                            counter += 1
                        
                        # Update the partner name
                        partner.write({'name': new_name})
                        current_env.cr.execute(f"RELEASE SAVEPOINT {savepoint_name}")
                        _logger.info(f"Renamed partner {partner_id}: '{name}' -> '{new_name}'")
                        fixed_count += 1
                        
                except Exception as e:
                    _logger.error(f"Error fixing partner {partner_id}: {str(e)}")
                    try:
                        current_env.cr.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                    except:
                        current_env.cr.rollback()
        
        # Commit the changes if we have our own transaction
        if 'env' not in globals():
            current_env.cr.commit()
            _logger.info(f"Successfully committed {fixed_count} partner name fixes")
        else:
            _logger.info(f"Successfully fixed {fixed_count} partner names (commit manually)")
        
        return {
            'success': True,
            'message': f'Fixed {fixed_count} duplicate partner names',
            'duplicates_found': len(duplicates),
            'records_fixed': fixed_count
        }
        
    except Exception as e:
        _logger.error(f"Error fixing duplicate partners: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """Main function with better execution guidance"""
    print("🔧 Duplicate Partner Fix Script")
    print("=" * 50)
    
    # Check execution context
    try:
        # Try to detect if we're in Odoo shell
        if 'env' in globals():
            print("✅ Running in Odoo shell context")
            _logger.info("Starting duplicate partner fix...")
            result = fix_duplicate_partners()
        else:
            print("⚠️  NOT running in Odoo shell context")
            print("\nTo run this script properly:")
            print("1. Use the batch/shell scripts instead:")
            print("   - Windows: fix_duplicate_partners.bat")
            print("   - Linux/Mac: ./fix_duplicate_partners.sh")
            print("\n2. Or run in Odoo shell:")
            print("   docker-compose exec odoo python3 odoo-bin shell -d osuspro")
            print("   exec(open('/mnt/extra-addons/fix_duplicate_partners.py').read())")
            print("\n3. Or use the Odoo method directly:")
            print("   In shell: env['hr.employee'].fix_existing_duplicate_partners()")
            
            # Still try to run but expect it might fail
            print("\nAttempting to run anyway...")
            _logger.info("Starting duplicate partner fix...")
            result = fix_duplicate_partners()
    except Exception as e:
        print(f"❌ Execution context error: {str(e)}")
        result = {'success': False, 'error': str(e)}
    
    print("\n" + "=" * 50)
    if result['success']:
        print(f"✅ {result['message']}")
        if 'duplicates_found' in result:
            print(f"📊 Duplicates found: {result['duplicates_found']}")
            print(f"🔧 Records fixed: {result['records_fixed']}")
    else:
        print(f"❌ Error: {result['error']}")
        print("\n💡 Recommended solutions:")
        print("1. Use fix_duplicate_partners.bat (Windows)")
        print("2. Use ./fix_duplicate_partners.sh (Linux/Mac)")
        print("3. Run in Odoo shell environment")
        sys.exit(1)
    
    print("=" * 50)

if __name__ == '__main__':
    main()
