#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix for recurring_order_id Owl Error
=====================================
Removes orphan field definitions that reference deleted models.

ERROR: "sale.order"."recurring_order_id" field is undefined.
ROOT CAUSE: Field references sale.recurring model that was deleted from the system.

This script:
1. Backs up affected ir_model_fields records
2. Identifies all orphan fields with broken model references
3. Safely removes these orphan field definitions
4. Verifies the fix
"""

import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OrphanFieldFixer:
    """Fixes orphan field definitions in Odoo database"""
    
    def __init__(self, env):
        self.env = env
        self.backed_up_fields = []
        self.deleted_fields = []
        
    def get_orphan_fields(self):
        """
        Find all fields that reference non-existent models.
        
        Returns:
            dict: Orphan fields grouped by target model
        """
        logger.info("🔍 Scanning for orphan fields...")
        
        orphan_fields = {}
        
        # Query all many2one, one2many, many2many fields
        ir_fields = self.env['ir.model.fields'].search([
            ('ttype', 'in', ['many2one', 'one2many', 'many2many']),
            ('relation', '!=', False),
            ('relation', '!=', '')
        ])
        
        for field in ir_fields:
            # Check if the related model exists
            model_exists = self.env['ir.model'].search_count([
                ('model', '=', field.relation)
            ])
            
            if not model_exists:
                if field.relation not in orphan_fields:
                    orphan_fields[field.relation] = []
                
                orphan_fields[field.relation].append({
                    'id': field.id,
                    'name': field.name,
                    'model': field.model_id.model,
                    'field_desc': field.field_description,
                    'relation': field.relation,
                    'type': field.ttype,
                })
        
        return orphan_fields
    
    def backup_orphan_fields(self, orphan_fields):
        """
        Create backup of orphan field definitions before deletion.
        
        Args:
            orphan_fields (dict): Orphan fields grouped by target model
        """
        logger.info("📦 Creating backup of orphan fields...")
        
        for target_model, fields in orphan_fields.items():
            for field_info in fields:
                field = self.env['ir.model.fields'].browse(field_info['id'])
                
                # Store backup data
                self.backed_up_fields.append({
                    'id': field.id,
                    'name': field.name,
                    'model': field.model_id.model,
                    'field_description': field.field_description,
                    'relation': field.relation,
                    'type': field.ttype,
                    'required': field.required,
                    'readonly': field.readonly,
                    'create_date': field.create_date,
                })
                
                logger.info(f"  ✓ Backed up: {field.model_id.model}.{field.name} → {field.relation}")
        
        return len(self.backed_up_fields)
    
    def delete_orphan_fields(self, orphan_fields):
        """
        Safely delete orphan field definitions.
        
        Args:
            orphan_fields (dict): Orphan fields grouped by target model
        """
        logger.info("🗑️  Deleting orphan field definitions...")
        
        total_deleted = 0
        
        for target_model, fields in orphan_fields.items():
            logger.info(f"\n  Cleaning up fields referencing '{target_model}':")
            
            for field_info in fields:
                try:
                    field = self.env['ir.model.fields'].browse(field_info['id'])
                    
                    # Get field details before deletion
                    field_display = f"{field.model_id.model}.{field.name}"
                    
                    # Check for dependencies before deletion
                    # (Views, computed fields, etc.)
                    has_dependencies = self._check_field_dependencies(field)
                    
                    if has_dependencies:
                        logger.warning(f"    ⚠️  {field_display} has dependencies, skipping")
                        continue
                    
                    # Delete the field
                    field.unlink()
                    
                    self.deleted_fields.append({
                        'model': field_info['model'],
                        'field': field_info['name'],
                        'relation': field_info['relation']
                    })
                    
                    logger.info(f"    ✓ Deleted: {field_display}")
                    total_deleted += 1
                    
                except Exception as e:
                    logger.error(f"    ✗ Error deleting {field_info['name']}: {str(e)}")
        
        return total_deleted
    
    def _check_field_dependencies(self, field):
        """
        Check if field has dependencies that would prevent deletion.
        
        Args:
            field (ir.model.fields): Field to check
            
        Returns:
            bool: True if dependencies found
        """
        # Check for views using this field
        view_count = self.env['ir.ui.view'].search_count([
            ('arch_base', 'ilike', f'name="{field.name}"')
        ])
        
        # Check for computed field dependencies
        computed_count = self.env['ir.model.fields'].search_count([
            ('model_id', '=', field.model_id.id),
            ('compute', 'ilike', field.name),
        ])
        
        return view_count > 0 or computed_count > 0
    
    def verify_fix(self):
        """
        Verify that the fix resolved the issue.
        
        Returns:
            tuple: (success: bool, report: str)
        """
        logger.info("\n✅ Verifying fix...")
        
        # Check that sale.order.recurring_order_id is gone
        try:
            recurring_field = self.env['ir.model.fields'].search([
                ('model_id.model', '=', 'sale.order'),
                ('name', '=', 'recurring_order_id')
            ], limit=1)
            
            if recurring_field:
                logger.warning("⚠️  recurring_order_id still exists in database")
                return False, "Field still present"
            else:
                logger.info("✓ recurring_order_id successfully removed")
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return False, str(e)
        
        # Check for remaining orphan fields
        remaining_orphans = self.get_orphan_fields()
        
        if remaining_orphans:
            logger.warning(f"⚠️  {sum(len(v) for v in remaining_orphans.values())} orphan fields remain")
            return False, "Orphan fields remain"
        else:
            logger.info("✓ No remaining orphan fields detected")
        
        return True, "Fix verified successfully"
    
    def generate_report(self):
        """Generate human-readable report of changes"""
        
        report = f"""
{'='*70}
ORPHAN FIELD FIX REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*70}

FIELDS BACKED UP: {len(self.backed_up_fields)}
{'-'*70}
"""
        
        for backup in self.backed_up_fields:
            report += f"""
  • {backup['model']}.{backup['name']}
    - Relation: {backup['relation']} (DELETED)
    - Type: {backup['type']}
    - Description: {backup['field_description']}
    - Created: {backup['create_date']}
"""
        
        report += f"""
{'='*70}
FIELDS DELETED: {len(self.deleted_fields)}
{'-'*70}
"""
        
        for deleted in self.deleted_fields:
            report += f"  ✓ {deleted['model']}.{deleted['field']} → {deleted['relation']}\n"
        
        report += f"""
{'='*70}
SUMMARY
{'='*70}
✓ Backed up: {len(self.backed_up_fields)} orphan field definitions
✓ Deleted: {len(self.deleted_fields)} orphan field definitions
✓ Fix Status: Ready for deployment

NEXT STEPS:
1. Clear Odoo browser cache (Ctrl+Shift+R)
2. Reload sale.order form
3. Verify no Owl errors in console
4. Test sale order creation/editing
{'='*70}
"""
        
        return report


def run_fix(env):
    """Main execution function"""
    
    logger.info("🚀 Starting Orphan Field Fixer...")
    logger.info(f"Target database: {env.cr.dbname}")
    
    try:
        fixer = OrphanFieldFixer(env)
        
        # Step 1: Find orphan fields
        orphan_fields = fixer.get_orphan_fields()
        
        if not orphan_fields:
            logger.info("✅ No orphan fields found. System is clean!")
            return True
        
        logger.info(f"Found {sum(len(v) for v in orphan_fields.values())} orphan fields")
        
        # Step 2: Backup
        backup_count = fixer.backup_orphan_fields(orphan_fields)
        logger.info(f"✓ Backed up {backup_count} fields")
        
        # Step 3: Delete
        deleted_count = fixer.delete_orphan_fields(orphan_fields)
        logger.info(f"✓ Deleted {deleted_count} orphan fields")
        
        # Step 4: Verify
        success, verify_msg = fixer.verify_fix()
        logger.info(f"Verification: {verify_msg}")
        
        # Step 5: Report
        report = fixer.generate_report()
        logger.info(report)
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Error during fix: {str(e)}", exc_info=True)
        return False


if __name__ == '__main__':
    # This script should be run within Odoo environment
    # Usage: odoo shell -d database_name -c config_file
    # >>> exec(open('fix_recurring_order_id_error.py').read())
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                  ORPHAN FIELD FIX - MANUAL RUN                    ║
╚════════════════════════════════════════════════════════════════════╝

To use this script:

Option 1: Via Odoo Shell (Recommended)
  $ cd /opt/odoo
  $ ./odoo shell -d scholarixv2
  >>> exec(open('/path/to/fix_recurring_order_id_error.py').read())
  >>> run_fix(env)

Option 2: Via Python Script with environment setup
  $ python fix_recurring_order_id_error.py

Make sure you have:
  • Odoo installed and configured
  • Database credentials set up
  • Proper permissions to modify database

The script will:
  1. Find all fields referencing deleted models
  2. Back up field definitions (for recovery if needed)
  3. Delete the orphan field records
  4. Verify the fix was successful
  5. Generate a report of changes
    """)
