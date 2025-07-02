#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom Fields Cleanup Script for Odoo 17
This script fixes orphaned references that cause '_unknown' object errors.

The error typically occurs when:
1. Many2one fields reference records that don't exist
2. There are database inconsistencies with foreign key references
3. Multiple modules define the same field causing conflicts

Run this script to clean up orphaned references before Odoo starts.
"""

import psycopg2
import logging
import sys
from contextlib import contextmanager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database connection parameters - UPDATE THESE WITH YOUR DATABASE CREDENTIALS
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'your_odoo_database_name',  # Replace with your database name
    'user': 'your_db_user',                 # Replace with your database user
    'password': 'your_db_password'          # Replace with your database password
}

@contextmanager
def get_db_connection():
    """Get database connection with proper error handling."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        yield conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def check_orphaned_sale_order_type_references():
    """Check for orphaned sale_order_type_id references in account_move."""
    logger.info("Checking for orphaned sale_order_type_id references...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if sale_order_type table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'sale_order_type'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            logger.warning("sale_order_type table does not exist, setting all references to NULL")
            
            # Set all sale_order_type_id fields to NULL in account_move
            cursor.execute("""
                UPDATE account_move 
                SET sale_order_type_id = NULL 
                WHERE sale_order_type_id IS NOT NULL;
            """)
            
            affected_rows = cursor.rowcount
            logger.info(f"Set {affected_rows} orphaned sale_order_type_id references to NULL in account_move")
            
        else:
            # Check for orphaned references
            cursor.execute("""
                SELECT COUNT(*) 
                FROM account_move am 
                LEFT JOIN sale_order_type sot ON am.sale_order_type_id = sot.id 
                WHERE am.sale_order_type_id IS NOT NULL AND sot.id IS NULL;
            """)
            
            orphaned_count = cursor.fetchone()[0]
            
            if orphaned_count > 0:
                logger.warning(f"Found {orphaned_count} orphaned sale_order_type_id references")
                
                # Fix orphaned references
                cursor.execute("""
                    UPDATE account_move 
                    SET sale_order_type_id = NULL 
                    WHERE sale_order_type_id NOT IN (SELECT id FROM sale_order_type);
                """)
                
                logger.info(f"Fixed {orphaned_count} orphaned sale_order_type_id references")
            else:
                logger.info("No orphaned sale_order_type_id references found")
        
        conn.commit()

def check_orphaned_project_references():
    """Check for orphaned project_id references in account_move."""
    logger.info("Checking for orphaned project_id references...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check for orphaned project references (product_template)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM account_move am 
            LEFT JOIN product_template pt ON am.project = pt.id 
            WHERE am.project IS NOT NULL AND pt.id IS NULL;
        """)
        
        orphaned_count = cursor.fetchone()[0]
        
        if orphaned_count > 0:
            logger.warning(f"Found {orphaned_count} orphaned project references")
            
            # Fix orphaned references
            cursor.execute("""
                UPDATE account_move 
                SET project = NULL 
                WHERE project NOT IN (SELECT id FROM product_template);
            """)
            
            logger.info(f"Fixed {orphaned_count} orphaned project references")
        else:
            logger.info("No orphaned project references found")
        
        conn.commit()

def check_orphaned_unit_references():
    """Check for orphaned unit_id references in account_move."""
    logger.info("Checking for orphaned unit_id references...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check for orphaned unit references (product_product)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM account_move am 
            LEFT JOIN product_product pp ON am.unit = pp.id 
            WHERE am.unit IS NOT NULL AND pp.id IS NULL;
        """)
        
        orphaned_count = cursor.fetchone()[0]
        
        if orphaned_count > 0:
            logger.warning(f"Found {orphaned_count} orphaned unit references")
            
            # Fix orphaned references
            cursor.execute("""
                UPDATE account_move 
                SET unit = NULL 
                WHERE unit NOT IN (SELECT id FROM product_product);
            """)
            
            logger.info(f"Fixed {orphaned_count} orphaned unit references")
        else:
            logger.info("No orphaned unit references found")
        
        conn.commit()

def check_orphaned_buyer_references():
    """Check for orphaned buyer references in account_move."""
    logger.info("Checking for orphaned buyer references...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check for orphaned buyer references (res_partner)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM account_move am 
            LEFT JOIN res_partner rp ON am.buyer = rp.id 
            WHERE am.buyer IS NOT NULL AND rp.id IS NULL;
        """)
        
        orphaned_count = cursor.fetchone()[0]
        
        if orphaned_count > 0:
            logger.warning(f"Found {orphaned_count} orphaned buyer references")
            
            # Fix orphaned references
            cursor.execute("""
                UPDATE account_move 
                SET buyer = NULL 
                WHERE buyer NOT IN (SELECT id FROM res_partner);
            """)
            
            logger.info(f"Fixed {orphaned_count} orphaned buyer references")
        else:
            logger.info("No orphaned buyer references found")
        
        conn.commit()

def check_duplicate_field_definitions():
    """Check for duplicate field definitions that might cause conflicts."""
    logger.info("Checking for duplicate field definitions...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check for duplicate field definitions in ir_model_fields
        cursor.execute("""
            SELECT name, model, COUNT(*) as count
            FROM ir_model_fields 
            WHERE model = 'account.move' 
            AND name IN ('sale_order_type_id', 'project', 'unit', 'buyer', 'project_id', 'unit_id', 'buyer_id')
            GROUP BY name, model 
            HAVING COUNT(*) > 1;
        """)
        
        duplicates = cursor.fetchall()
        
        if duplicates:
            logger.warning("Found duplicate field definitions:")
            for field_name, model, count in duplicates:
                logger.warning(f"  - {model}.{field_name}: {count} definitions")
                
                # Keep only the first definition, remove others
                cursor.execute("""
                    DELETE FROM ir_model_fields 
                    WHERE model = %s AND name = %s 
                    AND id NOT IN (
                        SELECT id FROM ir_model_fields 
                        WHERE model = %s AND name = %s 
                        ORDER BY id LIMIT 1
                    );
                """, (model, field_name, model, field_name))
                
                removed_count = cursor.rowcount
                logger.info(f"  - Removed {removed_count} duplicate definitions for {field_name}")
        else:
            logger.info("No duplicate field definitions found")
        
        conn.commit()

def main():
    """Main function to run all checks and fixes."""
    logger.info("Starting custom fields cleanup...")
    
    try:
        # Check for duplicate field definitions first
        check_duplicate_field_definitions()
        
        # Check for orphaned references
        check_orphaned_sale_order_type_references()
        check_orphaned_project_references()
        check_orphaned_unit_references()
        check_orphaned_buyer_references()
        
        logger.info("Custom fields cleanup completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
