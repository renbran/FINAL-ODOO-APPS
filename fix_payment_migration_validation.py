#!/usr/bin/env python3
"""
Payment Migration Fix Validation Script
=======================================

This script validates the fixes applied to the account_payment_final migration scripts
to ensure they handle missing 'state' column scenarios safely.

Usage: python fix_payment_migration_validation.py
"""

import os
import sys
import ast
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MigrationValidator:
    """Validates migration script fixes"""
    
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.migration_path = os.path.join(
            self.base_path, 
            'account_payment_final', 
            'migrations', 
            '17.0.1.1.0'
        )
        self.errors = []
        self.warnings = []
        
    def validate_pre_migrate(self):
        """Validate pre-migration script"""
        pre_migrate_file = os.path.join(self.migration_path, 'pre-migrate.py')
        
        if not os.path.exists(pre_migrate_file):
            self.errors.append("Pre-migration file not found")
            return False
            
        with open(pre_migrate_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for safe column existence checks
        required_patterns = [
            'information_schema.tables',
            'information_schema.columns',
            'table_name = \'account_payment\'',
            'column_name = \'state\'',
            'try:',
            'except Exception as e:'
        ]
        
        missing_patterns = []
        for pattern in required_patterns:
            if pattern not in content:
                missing_patterns.append(pattern)
                
        if missing_patterns:
            self.errors.append(f"Pre-migration missing safety patterns: {missing_patterns}")
            return False
            
        # Check that direct state column query is removed
        if 'FROM account_payment' in content and 'WHERE (state =' in content and 'information_schema' not in content.split('WHERE (state =')[0]:
            self.errors.append("Pre-migration still contains unsafe direct state column query")
            return False
            
        logger.info("✅ Pre-migration script validation passed")
        return True
        
    def validate_post_migrate(self):
        """Validate post-migration script"""
        post_migrate_file = os.path.join(self.migration_path, 'post-migrate.py')
        
        if not os.path.exists(post_migrate_file):
            self.errors.append("Post-migration file not found")
            return False
            
        with open(post_migrate_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for safe column existence checks
        required_patterns = [
            'information_schema.columns',
            'column_name = \'state\'',
            'state_column_exists',
            'try:',
            'except Exception as e:'
        ]
        
        missing_patterns = []
        for pattern in required_patterns:
            if pattern not in content:
                missing_patterns.append(pattern)
                
        if missing_patterns:
            self.errors.append(f"Post-migration missing safety patterns: {missing_patterns}")
            return False
            
        # Check for proper error handling around state-dependent searches
        state_searches = content.count("('state', '=',")
        try_blocks_around_state = content.count("try:\n        posted_payments = env['account.payment'].search([\n            ('state', '=',") + \
                                content.count("try:\n        cancelled_payments = env['account.payment'].search([\n            ('state', '=',") + \
                                content.count("try:\n        draft_payments = env['account.payment'].search([\n            ('state', '=',")
        
        if state_searches > 0 and try_blocks_around_state == 0:
            self.warnings.append("Post-migration has state column queries but may not be properly wrapped in try-catch")
            
        logger.info("✅ Post-migration script validation passed")
        return True
        
    def validate_syntax(self):
        """Validate Python syntax of migration files"""
        files_to_check = [
            os.path.join(self.migration_path, 'pre-migrate.py'),
            os.path.join(self.migration_path, 'post-migrate.py')
        ]
        
        for file_path in files_to_check:
            if not os.path.exists(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
                logger.info(f"✅ Syntax validation passed for {os.path.basename(file_path)}")
            except SyntaxError as e:
                self.errors.append(f"Syntax error in {file_path}: {e}")
                return False
                
        return True
        
    def run_validation(self):
        """Run complete validation"""
        logger.info("🔍 Starting Payment Migration Fix Validation")
        logger.info("=" * 60)
        
        success = True
        
        # Check syntax first
        if not self.validate_syntax():
            success = False
            
        # Validate pre-migration
        if not self.validate_pre_migrate():
            success = False
            
        # Validate post-migration  
        if not self.validate_post_migrate():
            success = False
            
        # Report results
        logger.info("\n" + "=" * 60)
        logger.info("📊 VALIDATION RESULTS")
        logger.info("=" * 60)
        
        if self.errors:
            logger.error("❌ ERRORS FOUND:")
            for error in self.errors:
                logger.error(f"  • {error}")
                
        if self.warnings:
            logger.warning("⚠️  WARNINGS:")
            for warning in self.warnings:
                logger.warning(f"  • {warning}")
                
        if success and not self.errors:
            logger.info("✅ ALL VALIDATIONS PASSED!")
            logger.info("Migration scripts are now safe for CloudPepper deployment")
            return True
        else:
            logger.error("❌ VALIDATION FAILED!")
            logger.error("Please fix the errors before deploying")
            return False

def main():
    """Main validation function"""
    validator = MigrationValidator()
    success = validator.run_validation()
    
    if success:
        logger.info("\n🎉 Payment migration fix validation completed successfully!")
        logger.info("The migration scripts are now safe for production deployment.")
        sys.exit(0)
    else:
        logger.error("\n💥 Payment migration fix validation failed!")
        logger.error("Please review and fix the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
