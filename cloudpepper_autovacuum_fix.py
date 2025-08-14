#!/usr/bin/env python3
"""
CloudPepper Autovacuum Fix Script
"""

import logging
import psycopg2
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_autovacuum():
    """Apply autovacuum fixes"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'osustst'),
            user=os.getenv('DB_USER', 'odoo'),
            password=os.getenv('DB_PASSWORD', 'odoo')
        )
        
        cursor = conn.cursor()
        
        # Execute fixes
        with open('cloudpepper_autovacuum_fix.sql', 'r') as f:
            sql_script = f.read()
        
        cursor.execute(sql_script)
        conn.commit()
        
        logger.info("Autovacuum fixes applied successfully")
        
    except Exception as e:
        logger.error(f"Error applying autovacuum fixes: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_autovacuum()
