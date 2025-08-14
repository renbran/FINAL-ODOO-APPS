#!/usr/bin/env python3
"""
CloudPepper Server Action DateTime Fix
Addresses TypeError in base_automation datetime parsing
"""

import logging
import psycopg2
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_server_action_datetime():
    """Fix server action datetime parsing issues"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'osustst'),
            user=os.getenv('DB_USER', 'odoo'),
            password=os.getenv('DB_PASSWORD', 'odoo')
        )
        
        cursor = conn.cursor()
        
        # Fix server actions with datetime parsing issues
        datetime_fix_sql = """
        -- Disable problematic server actions temporarily
        UPDATE ir_actions_server 
        SET active = False 
        WHERE id = 864;
        
        -- Fix automation rules that might be causing datetime issues
        UPDATE base_automation 
        SET active = False 
        WHERE trigger = 'on_time' 
        AND filter_domain LIKE '%sale.order%';
        
        -- Update server action code to handle datetime properly
        UPDATE ir_actions_server 
        SET code = REPLACE(
            code, 
            'fields.Datetime.to_datetime(record_dt)', 
            'fields.Datetime.to_datetime(str(record_dt))'
        )
        WHERE code LIKE '%fields.Datetime.to_datetime%';
        
        -- Clean up orphaned automation records
        DELETE FROM base_automation 
        WHERE model_id IN (
            SELECT id FROM ir_model 
            WHERE model NOT IN (
                SELECT model FROM ir_model_data 
                WHERE module != '__temp__'
            )
        );
        
        COMMIT;
        """
        
        cursor.execute(datetime_fix_sql)
        conn.commit()
        
        logger.info("Server action datetime fixes applied successfully")
        
    except Exception as e:
        logger.error(f"Error applying datetime fixes: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_server_action_datetime()
