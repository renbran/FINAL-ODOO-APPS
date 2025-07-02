#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom Fields Cleanup Script for Odoo 17 - Odoo Shell Version
This script runs from within Odoo shell to fix orphaned references.

Usage:
1. SSH into your server
2. Navigate to your Odoo directory
3. Run: python3 odoo-bin shell -d your_database_name --no-http
4. Copy and paste this script in the shell

Or save this file and run:
python3 odoo-bin shell -d your_database_name --no-http < custom_fields_cleanup_shell.py
"""

import logging

# Set up logging
_logger = logging.getLogger(__name__)

def cleanup_orphaned_references():
    """Clean up orphaned references using Odoo ORM and direct SQL when needed."""
    
    _logger.info("Starting custom fields cleanup from Odoo shell...")
    
    # Get the database cursor
    cr = env.cr
    
    try:
        # 1. Check and fix orphaned sale_order_type_id references
        _logger.info("Checking orphaned sale_order_type_id references...")
        
        # Check if sale_order_type table exists
        cr.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'sale_order_type'
            );
        """)
        
        table_exists = cr.fetchone()[0]
        
        if not table_exists:
            _logger.warning("sale_order_type table does not exist, setting all references to NULL")
            cr.execute("""
                UPDATE account_move 
                SET sale_order_type_id = NULL 
                WHERE sale_order_type_id IS NOT NULL;
            """)
            _logger.info(f"Set {cr.rowcount} orphaned sale_order_type_id references to NULL")
        else:
            # Fix orphaned references
            cr.execute("""
                UPDATE account_move 
                SET sale_order_type_id = NULL 
                WHERE sale_order_type_id IS NOT NULL 
                AND sale_order_type_id NOT IN (SELECT id FROM sale_order_type);
            """)
            if cr.rowcount > 0:
                _logger.info(f"Fixed {cr.rowcount} orphaned sale_order_type_id references")
            else:
                _logger.info("No orphaned sale_order_type_id references found")
        
        # 2. Fix orphaned project references
        _logger.info("Checking orphaned project references...")
        cr.execute("""
            UPDATE account_move 
            SET project = NULL 
            WHERE project IS NOT NULL 
            AND project NOT IN (SELECT id FROM product_template);
        """)
        if cr.rowcount > 0:
            _logger.info(f"Fixed {cr.rowcount} orphaned project references")
        else:
            _logger.info("No orphaned project references found")
        
        # 3. Fix orphaned unit references
        _logger.info("Checking orphaned unit references...")
        cr.execute("""
            UPDATE account_move 
            SET unit = NULL 
            WHERE unit IS NOT NULL 
            AND unit NOT IN (SELECT id FROM product_product);
        """)
        if cr.rowcount > 0:
            _logger.info(f"Fixed {cr.rowcount} orphaned unit references")
        else:
            _logger.info("No orphaned unit references found")
        
        # 4. Fix orphaned buyer references
        _logger.info("Checking orphaned buyer references...")
        cr.execute("""
            UPDATE account_move 
            SET buyer = NULL 
            WHERE buyer IS NOT NULL 
            AND buyer NOT IN (SELECT id FROM res_partner);
        """)
        if cr.rowcount > 0:
            _logger.info(f"Fixed {cr.rowcount} orphaned buyer references")
        else:
            _logger.info("No orphaned buyer references found")
        
        # 5. Fix orphaned project_id references (alternative field name)
        _logger.info("Checking orphaned project_id references...")
        cr.execute("""
            UPDATE account_move 
            SET project_id = NULL 
            WHERE project_id IS NOT NULL 
            AND project_id NOT IN (SELECT id FROM product_template);
        """)
        if cr.rowcount > 0:
            _logger.info(f"Fixed {cr.rowcount} orphaned project_id references")
        
        # 6. Fix orphaned unit_id references (alternative field name)
        _logger.info("Checking orphaned unit_id references...")
        cr.execute("""
            UPDATE account_move 
            SET unit_id = NULL 
            WHERE unit_id IS NOT NULL 
            AND unit_id NOT IN (SELECT id FROM product_product);
        """)
        if cr.rowcount > 0:
            _logger.info(f"Fixed {cr.rowcount} orphaned unit_id references")
        
        # 7. Fix orphaned buyer_id references (alternative field name)
        _logger.info("Checking orphaned buyer_id references...")
        cr.execute("""
            UPDATE account_move 
            SET buyer_id = NULL 
            WHERE buyer_id IS NOT NULL 
            AND buyer_id NOT IN (SELECT id FROM res_partner);
        """)
        if cr.rowcount > 0:
            _logger.info(f"Fixed {cr.rowcount} orphaned buyer_id references")
        
        # 8. Clean up duplicate field definitions using ORM
        _logger.info("Checking for duplicate field definitions...")
        
        field_names = ['sale_order_type_id', 'project', 'unit', 'buyer', 'project_id', 'unit_id', 'buyer_id']
        for field_name in field_names:
            duplicate_fields = env['ir.model.fields'].search([
                ('model', '=', 'account.move'),
                ('name', '=', field_name)
            ])
            
            if len(duplicate_fields) > 1:
                # Keep the first one, remove the rest
                fields_to_remove = duplicate_fields[1:]
                _logger.warning(f"Found {len(duplicate_fields)} definitions for {field_name}, removing {len(fields_to_remove)} duplicates")
                fields_to_remove.unlink()
        
        # 9. Clean up orphaned ir_model_data entries
        _logger.info("Cleaning up orphaned ir_model_data entries...")
        
        if table_exists:
            cr.execute("""
                DELETE FROM ir_model_data 
                WHERE model = 'sale.order.type' 
                AND res_id IS NOT NULL 
                AND res_id NOT IN (SELECT id FROM sale_order_type);
            """)
            if cr.rowcount > 0:
                _logger.info(f"Cleaned up {cr.rowcount} orphaned ir_model_data entries")
        
        # Commit all changes
        cr.commit()
        
        _logger.info("✅ Custom fields cleanup completed successfully!")
        _logger.info("You can now restart Odoo. The '_unknown' object error should be resolved.")
        
    except Exception as e:
        _logger.error(f"❌ Error during cleanup: {e}")
        cr.rollback()
        raise

# Run the cleanup
cleanup_orphaned_references()
