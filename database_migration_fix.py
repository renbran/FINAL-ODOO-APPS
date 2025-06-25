#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Migration Script for Odoo 17
This script fixes NOT NULL constraint errors for required fields.

Run this script to update NULL values in the database before Odoo starts.
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

def fix_hr_employee_fields():
    """Fix NULL values in hr_employee table for required fields."""
    logger.info("Fixing hr_employee table...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Check if the columns exist first
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'hr_employee' 
                AND column_name IN ('agent_id', 'labour_card_number', 'salary_card_number')
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
            
            if not existing_columns:
                logger.info("hr_employee columns not found, skipping...")
                return
            
            # Get the default bank for agent_id (use the first bank record)
            if 'agent_id' in existing_columns:
                cursor.execute("SELECT id FROM res_bank ORDER BY id LIMIT 1")
                default_bank = cursor.fetchone()
                
                if default_bank:
                    default_bank_id = default_bank[0]
                    
                    # Update NULL agent_id values
                    cursor.execute("""
                        UPDATE hr_employee 
                        SET agent_id = %s 
                        WHERE agent_id IS NULL
                    """, (default_bank_id,))
                    
                    updated_rows = cursor.rowcount
                    logger.info(f"Updated {updated_rows} NULL agent_id values in hr_employee")
                else:
                    logger.warning("No bank records found! Creating a default bank...")
                    cursor.execute("""
                        INSERT INTO res_bank (name, routing_code, create_date, write_date, create_uid, write_uid)
                        VALUES ('Default Bank', '000000000', NOW(), NOW(), 1, 1)
                        RETURNING id
                    """)
                    default_bank_id = cursor.fetchone()[0]
                    
                    cursor.execute("""
                        UPDATE hr_employee 
                        SET agent_id = %s 
                        WHERE agent_id IS NULL
                    """, (default_bank_id,))
                    
                    updated_rows = cursor.rowcount
                    logger.info(f"Created default bank and updated {updated_rows} NULL agent_id values")
            
            # Update NULL labour_card_number values
            if 'labour_card_number' in existing_columns:
                cursor.execute("""
                    UPDATE hr_employee 
                    SET labour_card_number = LPAD(CAST(id AS TEXT), 14, '0')
                    WHERE labour_card_number IS NULL OR labour_card_number = ''
                """)
                updated_rows = cursor.rowcount
                logger.info(f"Updated {updated_rows} NULL labour_card_number values in hr_employee")
            
            # Update NULL salary_card_number values
            if 'salary_card_number' in existing_columns:
                cursor.execute("""
                    UPDATE hr_employee 
                    SET salary_card_number = LPAD(CAST(id AS TEXT), 16, '0')
                    WHERE salary_card_number IS NULL OR salary_card_number = ''
                """)
                updated_rows = cursor.rowcount
                logger.info(f"Updated {updated_rows} NULL salary_card_number values in hr_employee")
            
            conn.commit()
            logger.info("hr_employee table fixes completed successfully")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error fixing hr_employee table: {e}")
            raise

def fix_res_bank_fields():
    """Fix NULL values in res_bank table for routing_code field."""
    logger.info("Fixing res_bank table...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Check if the routing_code column exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'res_bank' 
                AND column_name = 'routing_code'
            """)
            
            if not cursor.fetchone():
                logger.info("routing_code column not found in res_bank, skipping...")
                return
            
            # Update NULL routing_code values
            cursor.execute("""
                UPDATE res_bank 
                SET routing_code = LPAD(CAST(id AS TEXT), 9, '0')
                WHERE routing_code IS NULL OR routing_code = ''
            """)
            
            updated_rows = cursor.rowcount
            logger.info(f"Updated {updated_rows} NULL routing_code values in res_bank")
            
            conn.commit()
            logger.info("res_bank table fixes completed successfully")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error fixing res_bank table: {e}")
            raise

def verify_constraints():
    """Verify that all constraints can be safely applied."""
    logger.info("Verifying constraints...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Check hr_employee constraints
            cursor.execute("""
                SELECT COUNT(*) FROM hr_employee 
                WHERE agent_id IS NULL OR labour_card_number IS NULL OR salary_card_number IS NULL
                OR labour_card_number = '' OR salary_card_number = ''
            """)
            hr_employee_nulls = cursor.fetchone()[0]
            
            # Check res_bank constraints
            cursor.execute("""
                SELECT COUNT(*) FROM res_bank 
                WHERE routing_code IS NULL OR routing_code = ''
            """)
            res_bank_nulls = cursor.fetchone()[0]
            
            if hr_employee_nulls == 0 and res_bank_nulls == 0:
                logger.info("✅ All constraints verified - no NULL values found")
                return True
            else:
                logger.warning(f"❌ Found {hr_employee_nulls} NULL hr_employee records and {res_bank_nulls} NULL res_bank records")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying constraints: {e}")
            return False

def main():
    """Main function to run all fixes."""
    logger.info("Starting database migration fixes...")
    
    try:
        # Before fixing, show current status
        logger.info("Checking current database status...")
        verify_constraints()
        
        # Apply fixes
        fix_res_bank_fields()
        fix_hr_employee_fields()
        
        # Verify fixes
        if verify_constraints():
            logger.info("🎉 Database migration completed successfully!")
            logger.info("You can now start Odoo without NOT NULL constraint errors.")
        else:
            logger.error("❌ Some issues remain. Please check the logs above.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        Odoo 17 Database Migration Fix                       ║
║                                                                              ║
║  This script fixes NOT NULL constraint errors for:                          ║
║  - hr_employee.agent_id                                                     ║
║  - hr_employee.labour_card_number                                           ║
║  - hr_employee.salary_card_number                                           ║
║  - res_bank.routing_code                                                    ║
║                                                                              ║
║  IMPORTANT: Update the DB_CONFIG section with your database credentials!    ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    main()
