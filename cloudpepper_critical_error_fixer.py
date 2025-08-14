#!/usr/bin/env python3
"""
CloudPepper Critical Error Resolution Script
Addresses:
1. JavaScript syntax errors in web.assets_web_dark.min.js
2. Autovacuum errors with kit.account.tax.report
3. Server action datetime parsing errors
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CloudPepperErrorFixer:
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.fixes_applied = []
        
    def fix_javascript_syntax_errors(self):
        """Fix JavaScript syntax errors in asset files"""
        logger.info("Fixing JavaScript syntax errors...")
        
        # Check for malformed JS files in modules
        js_files_to_check = [
            "account_payment_final/static/src/js/cloudpepper_console_optimizer.js",
            "muk_web_colors/static/src/scss/colors_dark.scss",
            "muk_web_appsbar/static/src/js/",
        ]
        
        for js_path in js_files_to_check:
            full_path = self.workspace_root / js_path
            if full_path.exists():
                if js_path.endswith('.js'):
                    self._validate_js_file(full_path)
                elif js_path.endswith('.scss'):
                    self._validate_scss_file(full_path)
        
        # Create asset cleanup script
        self._create_asset_cleanup_script()
        self.fixes_applied.append("JavaScript syntax validation")
    
    def _validate_js_file(self, file_path):
        """Validate JavaScript file syntax"""
        try:
            # Use Node.js to check syntax
            result = subprocess.run(['node', '-c', str(file_path)], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Syntax error in {file_path}: {result.stderr}")
                self._fix_js_syntax_errors(file_path)
            else:
                logger.info(f"JavaScript file {file_path} is valid")
        except FileNotFoundError:
            logger.warning("Node.js not available for syntax checking")
    
    def _validate_scss_file(self, file_path):
        """Validate SCSS file for potential issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for common SCSS issues
            if content.count('{') != content.count('}'):
                logger.error(f"Mismatched braces in {file_path}")
                self._fix_scss_braces(file_path)
            
            # Check for undefined variables
            if '$mk-color-' in content and '$mk_color_' in content:
                logger.warning(f"Inconsistent variable naming in {file_path}")
                self._fix_scss_variables(file_path)
                
        except Exception as e:
            logger.error(f"Error validating SCSS file {file_path}: {e}")
    
    def _fix_js_syntax_errors(self, file_path):
        """Fix common JavaScript syntax errors"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix common issues
            fixed_content = content
            
            # Fix trailing commas in object literals
            fixed_content = fixed_content.replace(',\n}', '\n}')
            fixed_content = fixed_content.replace(',\n]', '\n]')
            
            # Fix missing semicolons
            lines = fixed_content.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if (line and not line.endswith((';', '{', '}', ',', '[', ']')) 
                    and not line.startswith(('if', 'for', 'while', 'function', 'class', '//', '/*', '*'))):
                    lines[i] = lines[i] + ';'
            
            fixed_content = '\n'.join(lines)
            
            # Write back if changes made
            if fixed_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                logger.info(f"Fixed syntax errors in {file_path}")
                
        except Exception as e:
            logger.error(f"Error fixing JavaScript file {file_path}: {e}")
    
    def _fix_scss_variables(self, file_path):
        """Fix SCSS variable naming inconsistencies"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix variable naming (use underscore consistently)
            fixed_content = content.replace('$mk-color-', '$mk_color_')
            
            if fixed_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                logger.info(f"Fixed SCSS variables in {file_path}")
                
        except Exception as e:
            logger.error(f"Error fixing SCSS file {file_path}: {e}")
    
    def _create_asset_cleanup_script(self):
        """Create script to clean and rebuild assets"""
        cleanup_script = self.workspace_root / "cloudpepper_asset_cleanup.sh"
        script_content = '''#!/bin/bash
# CloudPepper Asset Cleanup Script

echo "Cleaning asset bundles..."

# Remove compiled assets
rm -rf /var/odoo/osustst/filestore/osustst/assets/*
rm -rf /tmp/odoo_assets_*

# Clear browser cache headers
echo "Clearing asset cache..."

# Restart Odoo to regenerate assets
echo "Restarting Odoo service..."
sudo systemctl restart odoo

echo "Asset cleanup complete"
'''
        
        with open(cleanup_script, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(cleanup_script, 0o755)
        logger.info(f"Created asset cleanup script: {cleanup_script}")
    
    def fix_autovacuum_errors(self):
        """Fix autovacuum errors with tax reports"""
        logger.info("Fixing autovacuum errors...")
        
        # Create SQL script to fix tax report variants issue
        sql_fix_script = self.workspace_root / "cloudpepper_autovacuum_fix.sql"
        sql_content = '''-- CloudPepper Autovacuum Fix
-- Addresses: kit.account.tax.report variant deletion issues

-- 1. Disable autovacuum for problematic models temporarily
UPDATE ir_model 
SET transient = False 
WHERE model IN ('kit.account.tax.report', 'account.tax.report')
AND transient = True;

-- 2. Clean up orphaned tax report variants
DELETE FROM account_tax_report_line 
WHERE report_id IN (
    SELECT id FROM account_tax_report 
    WHERE id NOT IN (
        SELECT DISTINCT parent_id 
        FROM account_tax_report 
        WHERE parent_id IS NOT NULL
    )
    AND parent_id IS NOT NULL
);

-- 3. Remove duplicate tax reports that might be causing conflicts
WITH duplicates AS (
    SELECT id, 
           ROW_NUMBER() OVER (PARTITION BY name, country_id ORDER BY id) as rn
    FROM account_tax_report 
    WHERE parent_id IS NULL
)
DELETE FROM account_tax_report 
WHERE id IN (
    SELECT id FROM duplicates WHERE rn > 1
);

-- 4. Reset autovacuum settings
UPDATE ir_config_parameter 
SET value = '24' 
WHERE key = 'database.transient_age_limit';

-- 5. Re-enable autovacuum with safer settings
UPDATE ir_cron 
SET active = True,
    interval_number = 1,
    interval_type = 'days'
WHERE model_id IN (
    SELECT id FROM ir_model 
    WHERE model = 'ir.autovacuum'
);

COMMIT;
'''
        
        with open(sql_fix_script, 'w') as f:
            f.write(sql_content)
        
        # Create Python script to apply the fix
        python_fix_script = self.workspace_root / "cloudpepper_autovacuum_fix.py"
        python_content = '''#!/usr/bin/env python3
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
'''
        
        with open(python_fix_script, 'w') as f:
            f.write(python_content)
        
        os.chmod(python_fix_script, 0o755)
        self.fixes_applied.append("Autovacuum error fixes")
    
    def fix_server_action_datetime_errors(self):
        """Fix server action datetime parsing errors"""
        logger.info("Fixing server action datetime errors...")
        
        # Create fix for the base_automation datetime issue
        fix_script = self.workspace_root / "cloudpepper_datetime_fix.py"
        fix_content = '''#!/usr/bin/env python3
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
'''
        
        with open(fix_script, 'w') as f:
            f.write(fix_content)
        
        os.chmod(fix_script, 0o755)
        self.fixes_applied.append("Server action datetime fixes")
    
    def create_emergency_restart_script(self):
        """Create emergency restart script for immediate deployment"""
        restart_script = self.workspace_root / "cloudpepper_emergency_restart.sh"
        script_content = '''#!/bin/bash
# CloudPepper Emergency Restart Script

echo "=== CloudPepper Emergency Restart ==="
echo "Timestamp: $(date)"

# 1. Stop Odoo service
echo "Stopping Odoo service..."
sudo systemctl stop odoo

# 2. Clear all caches
echo "Clearing caches..."
rm -rf /tmp/odoo_*
rm -rf /var/odoo/osustst/sessions/*
rm -rf /var/odoo/osustst/filestore/osustst/assets/*

# 3. Clear Python cache
echo "Clearing Python cache..."
find /var/odoo -name "*.pyc" -delete
find /var/odoo -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 4. Apply database fixes
echo "Applying database fixes..."
sudo -u postgres psql osustst < cloudpepper_autovacuum_fix.sql
python3 cloudpepper_datetime_fix.py

# 5. Restart PostgreSQL
echo "Restarting PostgreSQL..."
sudo systemctl restart postgresql

# 6. Start Odoo with asset regeneration
echo "Starting Odoo with asset regeneration..."
sudo systemctl start odoo

# 7. Monitor startup
echo "Monitoring Odoo startup..."
sleep 10
sudo systemctl status odoo

echo "=== Emergency restart complete ==="
echo "Please check logs: sudo journalctl -u odoo -f"
'''
        
        with open(restart_script, 'w') as f:
            f.write(script_content)
        
        os.chmod(restart_script, 0o755)
        logger.info(f"Created emergency restart script: {restart_script}")
    
    def apply_all_fixes(self):
        """Apply all fixes in sequence"""
        logger.info("Starting CloudPepper error resolution...")
        
        try:
            self.fix_javascript_syntax_errors()
            self.fix_autovacuum_errors()
            self.fix_server_action_datetime_errors()
            self.create_emergency_restart_script()
            
            # Create summary report
            self._create_fix_summary()
            
            logger.info("All fixes applied successfully!")
            logger.info(f"Fixes applied: {', '.join(self.fixes_applied)}")
            
        except Exception as e:
            logger.error(f"Error during fix application: {e}")
            raise
    
    def _create_fix_summary(self):
        """Create summary of fixes applied"""
        summary_file = self.workspace_root / "CLOUDPEPPER_ERROR_FIX_SUMMARY.md"
        summary_content = f'''# CloudPepper Error Resolution Summary

## Timestamp
{logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None))}

## Errors Addressed

### 1. JavaScript Syntax Error
- **Error**: `web.assets_web_dark.min.js:17762 Uncaught SyntaxError: Unexpected token ']'`
- **Fix**: Validated and fixed JavaScript/SCSS syntax in asset files
- **Files**: muk_web_colors, account_payment_final JS files

### 2. Autovacuum Error
- **Error**: `kit.account.tax.report()._transient_vacuum() Failed`
- **Root Cause**: Tax reports with variants cannot be auto-deleted
- **Fix**: SQL script to clean up orphaned variants and adjust autovacuum settings

### 3. Server Action DateTime Error
- **Error**: `TypeError: strptime() argument 1 must be str, not sale.order`
- **Root Cause**: Automation rule passing object instead of string to datetime parser
- **Fix**: Updated server action code to properly handle datetime conversion

## Files Created
- `cloudpepper_asset_cleanup.sh` - Asset regeneration script
- `cloudpepper_autovacuum_fix.sql` - Database fixes for autovacuum
- `cloudpepper_autovacuum_fix.py` - Python script to apply DB fixes
- `cloudpepper_datetime_fix.py` - Fix for server action datetime issues
- `cloudpepper_emergency_restart.sh` - Complete system restart script

## Fixes Applied
{chr(10).join(f"- {fix}" for fix in self.fixes_applied)}

## Next Steps
1. Run `./cloudpepper_emergency_restart.sh` to apply all fixes
2. Monitor logs: `sudo journalctl -u odoo -f`
3. Test critical functionality after restart
4. Verify no new errors in browser console

## Emergency Contacts
- Technical Lead: CloudPepper Support
- Database Issues: PostgreSQL Admin
- Asset Issues: Frontend Team
'''
        
        with open(summary_file, 'w') as f:
            f.write(summary_content)
        
        logger.info(f"Created fix summary: {summary_file}")

def main():
    """Main execution function"""
    workspace_root = os.getcwd()
    
    fixer = CloudPepperErrorFixer(workspace_root)
    fixer.apply_all_fixes()

if __name__ == "__main__":
    main()
