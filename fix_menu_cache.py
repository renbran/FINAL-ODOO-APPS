#!/usr/bin/env python3
"""
Odoo Template Cache Cleaner and Menu Fix
This script helps clear cached templates and fix menu-related issues.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_odoo_cache():
    """Clear Odoo cache and restart services if running in Docker."""
    try:
        logger.info("Attempting to clear Odoo cache...")
        
        # If running in Docker, restart containers
        if os.path.exists('docker-compose.yml'):
            logger.info("Docker setup detected. Restarting containers...")
            subprocess.run(['docker-compose', 'down'], check=False)
            subprocess.run(['docker-compose', 'up', '-d'], check=False)
            logger.info("Docker containers restarted.")
        
        # Clear any Python cache files
        for cache_file in Path('.').rglob('*.pyc'):
            try:
                cache_file.unlink()
            except Exception as e:
                logger.debug(f"Could not remove {cache_file}: {e}")
        
        for cache_dir in Path('.').rglob('__pycache__'):
            try:
                cache_dir.rmdir()
            except Exception as e:
                logger.debug(f"Could not remove {cache_dir}: {e}")
        
        logger.info("Cache clearing completed.")
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")

def create_database_fix_script():
    """Create a SQL script to fix menu-related database issues."""
    sql_script = """
-- Odoo Menu Fix SQL Script
-- Run this in your PostgreSQL database to fix menu-related issues

-- 1. Update ir.ui.view records that might have problematic templates
UPDATE ir_ui_view 
SET active = false 
WHERE arch_db LIKE '%load_menus_root%' 
  AND arch_db LIKE '%website.layout%';

-- 2. Clear view cache
DELETE FROM ir_ui_view_custom WHERE view_id IN (
    SELECT id FROM ir_ui_view WHERE arch_db LIKE '%load_menus_root%'
);

-- 3. Update website menu structure to ensure proper hierarchy
UPDATE website_menu SET parent_id = NULL WHERE parent_id NOT IN (SELECT id FROM website_menu);

-- 4. Rebuild menu structure
UPDATE ir_ui_menu SET active = true WHERE active = false AND parent_id IS NOT NULL;

-- 5. Fix any orphaned website menus
DELETE FROM website_menu WHERE website_id NOT IN (SELECT id FROM website);

-- Commit changes
COMMIT;
"""
    
    with open('fix_database_menus.sql', 'w') as f:
        f.write(sql_script)
    
    logger.info("Database fix script created: fix_database_menus.sql")

def check_module_dependencies():
    """Check for conflicting modules that might cause menu issues."""
    problematic_modules = [
        'backend_theme_infinito',
        'theme_levelup', 
        'theme_upshift'
    ]
    
    logger.info("Checking for potentially conflicting modules...")
    
    for module in problematic_modules:
        module_path = Path(module)
        if module_path.exists():
            manifest_path = module_path / '__manifest__.py'
            if manifest_path.exists():
                logger.warning(f"Found theme module: {module}")
                logger.info(f"  - Check {manifest_path} for website dependencies")
    
def main():
    print("=== Odoo Menu Fix and Cache Cleaner ===\n")
    
    # Step 1: Clear cache
    clear_odoo_cache()
    
    # Step 2: Create database fix script
    create_database_fix_script()
    
    # Step 3: Check module dependencies
    check_module_dependencies()
    
    print("\n=== Fix Steps Completed ===")
    print("1. Cache cleared and Docker containers restarted (if applicable)")
    print("2. Database fix script created: fix_database_menus.sql")
    print("3. Module dependency check completed")
    
    print("\n=== Manual Steps Required ===")
    print("1. Install the website_menu_fix module:")
    print("   - Go to Apps > Update Apps List")
    print("   - Search for 'Website Menu Fix'")
    print("   - Install the module")
    
    print("\n2. If the error persists, run the database fix script:")
    print("   - Connect to your PostgreSQL database")
    print("   - Run: \\i fix_database_menus.sql")
    
    print("\n3. Clear browser cache and try accessing the website again")
    
    print("\n4. If using themes, consider temporarily disabling them:")
    print("   - Uninstall theme_levelup and theme_upshift")
    print("   - Test with the default website theme")

if __name__ == "__main__":
    main()
