#!/var/odoo/scholarixv2/venv/bin/python3
"""
Rental Management Module Upgrade - Direct Python Script
This script performs database cleanup and module upgrade for rental_management
"""
import os
import sys
import psycopg2
import time
from datetime import datetime

# Configuration
DB_NAME = "scholarixv2"
DB_USER = "odoo"
DB_HOST = "localhost"
DB_PORT = "5432"

def log_info(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ℹ️  {msg}")

def log_ok(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ {msg}")

def log_err(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ {msg}")

def log_warn(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️  {msg}")

def execute_sql(conn, sql, params=None):
    """Execute SQL command safely"""
    try:
        cur = conn.cursor()
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        conn.commit()
        return cur
    except Exception as e:
        conn.rollback()
        raise e

def main():
    print("=" * 50)
    print("🧹 RENTAL_MANAGEMENT MODULE UPGRADE")
    print("=" * 50)
    
    # Connect to database
    log_info("Connecting to database...")
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            host=DB_HOST,
            port=DB_PORT
        )
        log_ok("Database connected")
    except Exception as e:
        log_err(f"Failed to connect to database: {e}")
        return 1
    
    # Step 1: Check current module state
    log_info("Step 1: Checking current module state...")
    try:
        cur = execute_sql(conn, 
            "SELECT state FROM ir_module_module WHERE name = 'rental_management' LIMIT 1;")
        result = cur.fetchone()
        current_state = result[0] if result else "not_found"
        log_ok(f"Current state: {current_state}")
    except Exception as e:
        log_warn(f"Could not check module state: {e}")
    
    # Step 2: Clean stale view data
    log_info("Step 2: Cleaning stale views and orphaned data...")
    try:
        # Get the correct column name first
        cur = execute_sql(conn, 
            "SELECT column_name FROM information_schema.columns WHERE table_name='ir_ui_view' AND column_name IN ('module', 'key') LIMIT 1;")
        result = cur.fetchone()
        
        if result:
            key_col = result[0]
            log_ok(f"Using column: {key_col}")
            
            # Delete views that might reference non-existent fields
            patterns = [
                "rental_management%is_payment_plan%",
                "rental_management.property_details%"
            ]
            
            for pattern in patterns:
                sql = f"DELETE FROM ir_ui_view WHERE {key_col} LIKE %s;"
                execute_sql(conn, sql, (pattern,))
                log_ok(f"Cleaned views matching: {pattern}")
    except Exception as e:
        log_warn(f"View cleanup had issues: {e}")
    
    # Step 3: Mark module for upgrade
    log_info("Step 3: Marking rental_management for upgrade...")
    try:
        execute_sql(conn,
            "UPDATE ir_module_module SET state = 'to upgrade' WHERE name = 'rental_management';")
        log_ok("Module marked for upgrade")
    except Exception as e:
        log_err(f"Failed to mark module: {e}")
        return 1
    
    # Step 4: Verify cleanup
    log_info("Step 4: Verifying cleanup...")
    try:
        cur = execute_sql(conn,
            "SELECT COUNT(*) FROM ir_ui_view WHERE key LIKE 'rental_management%';")
        count = cur.fetchone()[0]
        log_ok(f"Remaining rental_management views: {count}")
    except Exception as e:
        log_warn(f"Could not verify cleanup: {e}")
    
    conn.close()
    
    print("\n" + "=" * 50)
    log_ok("DATABASE CLEANUP COMPLETE")
    print("=" * 50)
    log_ok("Module: rental_management")
    log_ok("Status: Marked for upgrade")
    log_ok("Next step: Restart Odoo service to apply upgrade")
    log_ok("Command: systemctl restart odoo OR odoo -u rental_management")
    print("=" * 50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
