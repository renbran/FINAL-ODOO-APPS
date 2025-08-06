#!/usr/bin/env python3
"""
Emergency Database Fix for Payment Account Enhanced Module

This script fixes the missing database columns that are causing websocket errors.
Run this script to immediately resolve the UndefinedColumn error.
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_sql_script():
    """Run the SQL fix script via Docker"""
    try:
        # Path to the SQL fix script
        sql_script_path = "./payment_account_enhanced/migrations/fix_missing_columns.sql"
        
        # Run SQL script via Docker Compose
        cmd = [
            "docker-compose", "exec", "-T", "db", 
            "psql", "-U", "odoo", "-d", "odoo", "-f", "/dev/stdin"
        ]
        
        with open(sql_script_path, 'r') as sql_file:
            result = subprocess.run(
                cmd, 
                input=sql_file.read(), 
                text=True, 
                capture_output=True
            )
            
        if result.returncode == 0:
            logger.info("✓ Database fix applied successfully")
            logger.info(result.stdout)
            return True
        else:
            logger.error(f"✗ Database fix failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error running database fix: {e}")
        return False

def update_odoo_module():
    """Update the payment_account_enhanced module in Odoo"""
    try:
        cmd = [
            "docker-compose", "exec", "-T", "odoo",
            "odoo", "--update=payment_account_enhanced", 
            "--stop-after-init", "--no-http"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✓ Module updated successfully")
            return True
        else:
            logger.error(f"✗ Module update failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error updating module: {e}")
        return False

def restart_odoo():
    """Restart Odoo container to clear any cached schema"""
    try:
        logger.info("Restarting Odoo container...")
        subprocess.run(["docker-compose", "restart", "odoo"], check=True)
        logger.info("✓ Odoo container restarted")
        return True
    except Exception as e:
        logger.error(f"✗ Error restarting Odoo: {e}")
        return False

def main():
    """Main fix procedure"""
    logger.info("🔧 Starting Emergency Database Fix for Payment Account Enhanced")
    
    # Step 1: Apply database schema fix
    logger.info("Step 1: Applying database schema fix...")
    if not run_sql_script():
        logger.error("❌ Database fix failed - stopping")
        sys.exit(1)
    
    # Step 2: Update module in Odoo
    logger.info("Step 2: Updating Odoo module...")
    if not update_odoo_module():
        logger.warning("⚠️ Module update failed - continuing with restart")
    
    # Step 3: Restart Odoo
    logger.info("Step 3: Restarting Odoo...")
    if not restart_odoo():
        logger.error("❌ Restart failed")
        sys.exit(1)
    
    logger.info("✅ Emergency fix completed successfully!")
    logger.info("   The websocket error should now be resolved.")
    logger.info("   Check Odoo logs to confirm the fix.")

if __name__ == "__main__":
    main()
