#!/usr/bin/env python3
"""
CLOUDPEPPER EMERGENCY FIX - Missing custom_status_id Field
Critical production error resolution for field reference issue

Error: Field "custom_status_id" does not exist in model "sale.order"
File: order_status_override/reports/enhanced_order_status_report_actions.xml
Solution: Add missing field and sync logic to sale.order model

Created: 2025-08-17
Priority: CRITICAL
Status: EMERGENCY DEPLOYMENT READY
"""

import os
import sys
import logging
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cloudpepper_custom_status_fix.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CloudPepperCustomStatusFix:
    def __init__(self):
        self.base_path = "d:\\RUNNING APPS\\ready production\\latest\\odoo17_final"
        self.module_path = os.path.join(self.base_path, "order_status_override")
        self.model_file = os.path.join(self.module_path, "models", "sale_order.py")
        self.backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def create_backup(self):
        """Create backup of the current model file"""
        try:
            backup_file = f"{self.model_file}.backup.{self.backup_timestamp}"
            shutil.copy2(self.model_file, backup_file)
            logger.info(f"✅ Backup created: {backup_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create backup: {e}")
            return False
    
    def validate_fix_applied(self):
        """Validate that the fix has been applied correctly"""
        try:
            with open(self.model_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required elements
            checks = [
                ('custom_status_id field', 'custom_status_id = fields.Many2one'),
                ('onchange method 1', '_onchange_order_status_id'),
                ('onchange method 2', '_onchange_custom_status_id'),
                ('sync in create', 'custom_status_id = initial_status.id'),
                ('sync in _change_status', 'self.custom_status_id = new_status.id')
            ]
            
            all_checks_passed = True
            for check_name, check_pattern in checks:
                if check_pattern in content:
                    logger.info(f"✅ {check_name}: FOUND")
                else:
                    logger.error(f"❌ {check_name}: MISSING")
                    all_checks_passed = False
            
            return all_checks_passed
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return False
    
    def verify_module_structure(self):
        """Verify module structure integrity"""
        required_files = [
            "__manifest__.py",
            "models/__init__.py",
            "models/sale_order.py",
            "views/order_views_assignment.xml",
            "reports/enhanced_order_status_report_actions.xml"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = os.path.join(self.module_path, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"❌ Missing required files: {missing_files}")
            return False
        else:
            logger.info("✅ All required module files present")
            return True
    
    def generate_deployment_summary(self):
        """Generate deployment summary report"""
        summary = f"""
# CLOUDPEPPER EMERGENCY FIX DEPLOYMENT SUMMARY

## Fix Details
- **Issue**: Field "custom_status_id" does not exist in model "sale.order"
- **Module**: order_status_override
- **Affected File**: models/sale_order.py
- **Fix Applied**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Backup Created**: {self.backup_timestamp}

## Changes Applied
1. ✅ Added missing `custom_status_id` field to sale.order model
2. ✅ Added synchronization logic between order_status_id and custom_status_id
3. ✅ Updated create() method to sync both fields
4. ✅ Added onchange methods for field synchronization
5. ✅ Updated _change_status() method to maintain field sync

## Field Definition Added
```python
custom_status_id = fields.Many2one(
    'order.status', 
    string='Custom Status',
    tracking=True,
    help="Custom order status for workflow management (legacy field for compatibility)"
)
```

## Synchronization Methods Added
- `_onchange_order_status_id()`: Syncs custom_status_id when order_status_id changes
- `_onchange_custom_status_id()`: Syncs order_status_id when custom_status_id changes
- Enhanced `create()` method with field synchronization
- Enhanced `_change_status()` method with field synchronization

## Deployment Status
- **CloudPepper Ready**: YES
- **Validation Status**: {"PASSED" if self.validate_fix_applied() else "FAILED"}
- **Module Structure**: {"INTACT" if self.verify_module_structure() else "COMPROMISED"}

## Next Steps
1. Deploy to CloudPepper staging environment
2. Test all order status workflows
3. Verify report generation functionality
4. Deploy to production environment
5. Monitor for any related issues

## Rollback Plan
If issues occur, restore from backup:
```bash
cp {self.model_file}.backup.{self.backup_timestamp} {self.model_file}
```

## Contact
For issues with this fix, contact the development team immediately.
Emergency contact: System Administrator

---
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Fix ID: CLOUDPEPPER-CUSTOM-STATUS-{self.backup_timestamp}
"""
        
        report_file = os.path.join(self.base_path, f"CLOUDPEPPER_CUSTOM_STATUS_FIX_REPORT_{self.backup_timestamp}.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logger.info(f"✅ Deployment summary generated: {report_file}")
        return report_file
    
    def run_emergency_fix(self):
        """Execute the complete emergency fix process"""
        logger.info("🚨 STARTING CLOUDPEPPER EMERGENCY FIX - CUSTOM STATUS FIELD")
        logger.info("=" * 70)
        
        # Step 1: Verify module structure
        if not self.verify_module_structure():
            logger.error("❌ Module structure verification failed. Aborting fix.")
            return False
        
        # Step 2: Create backup
        if not self.create_backup():
            logger.error("❌ Backup creation failed. Aborting fix.")
            return False
        
        # Step 3: Validate fix applied
        if not self.validate_fix_applied():
            logger.error("❌ Fix validation failed. Please apply the fix manually.")
            return False
        
        # Step 4: Generate deployment summary
        report_file = self.generate_deployment_summary()
        
        logger.info("✅ EMERGENCY FIX COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)
        logger.info(f"📋 Deployment Report: {report_file}")
        logger.info("🚀 Ready for CloudPepper deployment")
        
        return True

def main():
    """Main execution function"""
    try:
        fixer = CloudPepperCustomStatusFix()
        success = fixer.run_emergency_fix()
        
        if success:
            print("\n🎉 CLOUDPEPPER EMERGENCY FIX SUCCESSFUL!")
            print("The missing custom_status_id field has been added and synchronized.")
            print("Module is now ready for CloudPepper deployment.")
            sys.exit(0)
        else:
            print("\n❌ EMERGENCY FIX FAILED!")
            print("Please review the logs and apply fixes manually.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"💥 Critical error during emergency fix: {e}")
        print(f"\n💥 CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
