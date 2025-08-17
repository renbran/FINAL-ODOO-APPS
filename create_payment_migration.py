#!/usr/bin/env python3
"""
Payment Approval State Migration Script
Syncs existing payment records to match their approval workflow status with their posting status

This script updates existing payments where:
- If payment.state == 'posted' but approval_state != 'posted' -> Set approval_state = 'posted'
- If payment.state == 'cancel' but approval_state != 'cancelled' -> Set approval_state = 'cancelled'
- Populates missing workflow user assignments based on creation and modification history
"""

import os
import sys
from pathlib import Path

def create_migration_script():
    """Create Python migration script for Odoo"""
    
    migration_script = '''#!/usr/bin/env python3
"""
Payment Approval State Data Migration
Run this script in Odoo shell to sync approval states with posting states
"""

import logging
from datetime import datetime
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate_payment_approval_states(cr, registry):
    """Migrate payment approval states to match current posting status"""
    
    print("🔄 Starting Payment Approval State Migration...")
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Find all payments that need approval state sync
    posted_payments_wrong_approval = env['account.payment'].search([
        ('state', '=', 'posted'),
        ('approval_state', '!=', 'posted')
    ])
    
    cancelled_payments_wrong_approval = env['account.payment'].search([
        ('state', '=', 'cancel'),
        ('approval_state', '!=', 'cancelled')
    ])
    
    draft_payments_to_fix = env['account.payment'].search([
        ('state', '=', 'draft'),
        ('approval_state', 'not in', ['draft', 'under_review'])
    ])
    
    print(f"📊 Migration Statistics:")
    print(f"   - Posted payments to sync: {len(posted_payments_wrong_approval)}")
    print(f"   - Cancelled payments to sync: {len(cancelled_payments_wrong_approval)}")
    print(f"   - Draft payments to fix: {len(draft_payments_to_fix)}")
    
    # Counter for tracking updates
    updated_count = 0
    
    # 1. Fix posted payments
    if posted_payments_wrong_approval:
        print(f"\\n🔧 Fixing {len(posted_payments_wrong_approval)} posted payments...")
        
        for payment in posted_payments_wrong_approval:
            try:
                old_state = payment.approval_state
                
                # Update approval workflow to match posted state
                payment.write({
                    'approval_state': 'posted',
                    'approver_date': payment.write_date or payment.create_date,
                    'authorizer_date': payment.write_date or payment.create_date,
                })
                
                # Set workflow users if missing
                if not payment.reviewer_id and payment.create_uid:
                    payment.reviewer_id = payment.create_uid
                    payment.reviewer_date = payment.create_date
                
                if not payment.approver_id and payment.write_uid:
                    payment.approver_id = payment.write_uid
                    payment.approver_date = payment.write_date or payment.create_date
                
                if not payment.authorizer_id and payment.write_uid:
                    payment.authorizer_id = payment.write_uid
                    payment.authorizer_date = payment.write_date or payment.create_date
                
                print(f"   ✅ Payment {payment.name}: {old_state} → posted")
                updated_count += 1
                
            except Exception as e:
                print(f"   ❌ Error updating payment {payment.name}: {e}")
    
    # 2. Fix cancelled payments
    if cancelled_payments_wrong_approval:
        print(f"\\n🔧 Fixing {len(cancelled_payments_wrong_approval)} cancelled payments...")
        
        for payment in cancelled_payments_wrong_approval:
            try:
                old_state = payment.approval_state
                payment.approval_state = 'cancelled'
                
                print(f"   ✅ Payment {payment.name}: {old_state} → cancelled")
                updated_count += 1
                
            except Exception as e:
                print(f"   ❌ Error updating payment {payment.name}: {e}")
    
    # 3. Fix draft payments with wrong approval states
    if draft_payments_to_fix:
        print(f"\\n🔧 Fixing {len(draft_payments_to_fix)} draft payments...")
        
        for payment in draft_payments_to_fix:
            try:
                old_state = payment.approval_state
                payment.approval_state = 'draft'
                
                print(f"   ✅ Payment {payment.name}: {old_state} → draft")
                updated_count += 1
                
            except Exception as e:
                print(f"   ❌ Error updating payment {payment.name}: {e}")
    
    # 4. Fix missing workflow user assignments for all payments
    print(f"\\n🔧 Fixing missing workflow user assignments...")
    
    all_payments = env['account.payment'].search([
        ('approval_state', 'in', ['posted', 'approved', 'for_authorization'])
    ])
    
    workflow_fixes = 0
    
    for payment in all_payments:
        try:
            updates = {}
            
            # Set reviewer if missing
            if not payment.reviewer_id and payment.create_uid:
                updates['reviewer_id'] = payment.create_uid.id
                updates['reviewer_date'] = payment.create_date
            
            # Set approver if missing (use write_uid or create_uid)
            if not payment.approver_id:
                if payment.write_uid and payment.write_uid != payment.create_uid:
                    updates['approver_id'] = payment.write_uid.id
                    updates['approver_date'] = payment.write_date or payment.create_date
                elif payment.create_uid:
                    updates['approver_id'] = payment.create_uid.id
                    updates['approver_date'] = payment.create_date
            
            # Set authorizer if missing (for posted payments)
            if payment.approval_state == 'posted' and not payment.authorizer_id:
                if payment.write_uid:
                    updates['authorizer_id'] = payment.write_uid.id
                    updates['authorizer_date'] = payment.write_date or payment.create_date
                elif payment.create_uid:
                    updates['authorizer_id'] = payment.create_uid.id
                    updates['authorizer_date'] = payment.create_date
            
            if updates:
                payment.write(updates)
                workflow_fixes += 1
                
        except Exception as e:
            print(f"   ⚠️ Error fixing workflow users for {payment.name}: {e}")
    
    print(f"   ✅ Fixed workflow users for {workflow_fixes} payments")
    
    # Commit changes
    cr.commit()
    
    print(f"\\n🎉 Migration Complete!")
    print(f"   📊 Total payments updated: {updated_count}")
    print(f"   📊 Workflow users fixed: {workflow_fixes}")
    print(f"   ✅ All changes committed to database")
    
    return updated_count + workflow_fixes

if __name__ == "__main__":
    # This should be run from Odoo shell
    print("Run this script from Odoo shell:")
    print("$ odoo shell -d your_database")
    print(">>> exec(open('payment_approval_migration.py').read())")
    print(">>> migrate_payment_approval_states(cr, registry)")
'''
    
    # Write the migration script
    with open('payment_approval_migration.py', 'w', encoding='utf-8') as f:
        f.write(migration_script)
    
    print("✅ Created payment_approval_migration.py")

def create_sql_migration():
    """Create SQL migration script as alternative"""
    
    sql_script = '''-- Payment Approval State SQL Migration
-- Run this SQL script directly on the database if needed

-- 1. Update posted payments to have posted approval state
UPDATE account_payment 
SET approval_state = 'posted',
    write_date = NOW()
WHERE state = 'posted' 
  AND approval_state != 'posted';

-- 2. Update cancelled payments to have cancelled approval state  
UPDATE account_payment 
SET approval_state = 'cancelled',
    write_date = NOW()
WHERE state = 'cancel' 
  AND approval_state != 'cancelled';

-- 3. Update draft payments to have draft approval state
UPDATE account_payment 
SET approval_state = 'draft',
    write_date = NOW()
WHERE state = 'draft' 
  AND approval_state NOT IN ('draft', 'under_review');

-- 4. Set reviewer_id where missing (use create_uid)
UPDATE account_payment 
SET reviewer_id = create_uid,
    reviewer_date = create_date
WHERE approval_state IN ('posted', 'approved', 'for_authorization')
  AND reviewer_id IS NULL
  AND create_uid IS NOT NULL;

-- 5. Set approver_id where missing (use write_uid or create_uid)
UPDATE account_payment 
SET approver_id = COALESCE(write_uid, create_uid),
    approver_date = COALESCE(write_date, create_date)
WHERE approval_state IN ('posted', 'approved', 'for_authorization')
  AND approver_id IS NULL
  AND COALESCE(write_uid, create_uid) IS NOT NULL;

-- 6. Set authorizer_id where missing for posted payments
UPDATE account_payment 
SET authorizer_id = COALESCE(write_uid, create_uid),
    authorizer_date = COALESCE(write_date, create_date)
WHERE approval_state = 'posted'
  AND authorizer_id IS NULL
  AND COALESCE(write_uid, create_uid) IS NOT NULL;

-- Query to check results
SELECT 
    state,
    approval_state,
    COUNT(*) as count
FROM account_payment 
GROUP BY state, approval_state
ORDER BY state, approval_state;
'''
    
    with open('payment_approval_migration.sql', 'w', encoding='utf-8') as f:
        f.write(sql_script)
    
    print("✅ Created payment_approval_migration.sql")

def create_odoo_module_migration():
    """Create a proper Odoo module migration"""
    
    # Create migration directory structure
    migration_dir = Path("account_payment_final/migrations/17.0.1.1.0")
    migration_dir.mkdir(parents=True, exist_ok=True)
    
    # Create pre-migration script
    pre_migration = '''# -*- coding: utf-8 -*-
"""
Pre-migration script for payment approval state sync
"""

import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Pre-migration: Log current state"""
    _logger.info("Starting payment approval state migration from version %s", version)
    
    # Count payments that need migration
    cr.execute("""
        SELECT 
            state,
            approval_state,
            COUNT(*) as count
        FROM account_payment 
        WHERE (state = 'posted' AND approval_state != 'posted')
           OR (state = 'cancel' AND approval_state != 'cancelled')
           OR (state = 'draft' AND approval_state NOT IN ('draft', 'under_review'))
        GROUP BY state, approval_state
    """)
    
    results = cr.fetchall()
    _logger.info("Payments requiring migration: %s", results)
'''
    
    with open(migration_dir / "pre-migrate.py", 'w', encoding='utf-8') as f:
        f.write(pre_migration)
    
    # Create post-migration script
    post_migration = '''# -*- coding: utf-8 -*-
"""
Post-migration script for payment approval state sync
"""

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Post-migration: Sync approval states with posting states"""
    _logger.info("Running payment approval state sync migration")
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    updated_count = 0
    
    # 1. Fix posted payments
    posted_payments = env['account.payment'].search([
        ('state', '=', 'posted'),
        ('approval_state', '!=', 'posted')
    ])
    
    if posted_payments:
        _logger.info("Updating %d posted payments to approval_state=posted", len(posted_payments))
        for payment in posted_payments:
            payment.write({
                'approval_state': 'posted',
                'approver_date': payment.write_date or payment.create_date,
                'authorizer_date': payment.write_date or payment.create_date,
            })
            
            # Set workflow users if missing
            if not payment.reviewer_id and payment.create_uid:
                payment.reviewer_id = payment.create_uid
                payment.reviewer_date = payment.create_date
            
            if not payment.approver_id and payment.write_uid:
                payment.approver_id = payment.write_uid
                payment.approver_date = payment.write_date or payment.create_date
            
            if not payment.authorizer_id and payment.write_uid:
                payment.authorizer_id = payment.write_uid
                payment.authorizer_date = payment.write_date or payment.create_date
                
        updated_count += len(posted_payments)
    
    # 2. Fix cancelled payments
    cancelled_payments = env['account.payment'].search([
        ('state', '=', 'cancel'),
        ('approval_state', '!=', 'cancelled')
    ])
    
    if cancelled_payments:
        _logger.info("Updating %d cancelled payments to approval_state=cancelled", len(cancelled_payments))
        cancelled_payments.write({'approval_state': 'cancelled'})
        updated_count += len(cancelled_payments)
    
    # 3. Fix draft payments
    draft_payments = env['account.payment'].search([
        ('state', '=', 'draft'),
        ('approval_state', 'not in', ['draft', 'under_review'])
    ])
    
    if draft_payments:
        _logger.info("Updating %d draft payments to approval_state=draft", len(draft_payments))
        draft_payments.write({'approval_state': 'draft'})
        updated_count += len(draft_payments)
    
    _logger.info("Payment approval state migration completed. Updated %d payments.", updated_count)
'''
    
    with open(migration_dir / "post-migrate.py", 'w', encoding='utf-8') as f:
        f.write(post_migration)
    
    print(f"✅ Created Odoo module migration in {migration_dir}")

def create_manual_update_script():
    """Create a manual update script for immediate use"""
    
    manual_script = '''#!/usr/bin/env python3
"""
Manual Payment Approval State Update Script
Run this script to immediately update payment approval states

Usage:
1. From terminal: python manual_payment_update.py
2. Or from Odoo: Run in web interface as server action
"""

import xmlrpc.client
import logging
import getpass

def update_payment_approval_states():
    """Manual update of payment approval states"""
    
    print("🔄 PAYMENT APPROVAL STATE UPDATE")
    print("=" * 50)
    
    # Configuration - Update these values for your environment
    url = input("Enter Odoo URL (e.g., https://stagingtry.cloudpepper.site): ").strip()
    db = input("Enter database name: ").strip()
    username = input("Enter username: ").strip()
    password = getpass.getpass("Enter password: ")
    
    # Connect to Odoo
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    try:
        # Authenticate
        uid = common.authenticate(db, username, password, {})
        if not uid:
            print("❌ Authentication failed!")
            return False
        
        print(f"✅ Connected to {url} as {username}")
        
        # Search for payments needing update
        posted_payments = models.execute_kw(
            db, uid, password,
            'account.payment', 'search_read',
            [[('state', '=', 'posted'), ('approval_state', '!=', 'posted')]],
            {'fields': ['name', 'state', 'approval_state', 'amount', 'partner_id']}
        )
        
        cancelled_payments = models.execute_kw(
            db, uid, password,
            'account.payment', 'search_read',
            [[('state', '=', 'cancel'), ('approval_state', '!=', 'cancelled')]],
            {'fields': ['name', 'state', 'approval_state', 'amount', 'partner_id']}
        )
        
        print(f"📊 Found {len(posted_payments)} posted payments to update")
        print(f"📊 Found {len(cancelled_payments)} cancelled payments to update")
        
        if not posted_payments and not cancelled_payments:
            print("✅ All payments are already in sync!")
            return True
        
        # Ask for confirmation
        if input("\\nProceed with updates? (y/N): ").lower() != 'y':
            print("❌ Update cancelled by user")
            return False
        
        updated_count = 0
        
        # Update posted payments
        for payment in posted_payments:
            try:
                models.execute_kw(
                    db, uid, password,
                    'account.payment', 'write',
                    [[payment['id']], {'approval_state': 'posted'}]
                )
                print(f"   ✅ {payment['name']}: approval_state → posted")
                updated_count += 1
            except Exception as e:
                print(f"   ❌ Error updating {payment['name']}: {e}")
        
        # Update cancelled payments
        for payment in cancelled_payments:
            try:
                models.execute_kw(
                    db, uid, password,
                    'account.payment', 'write',
                    [[payment['id']], {'approval_state': 'cancelled'}]
                )
                print(f"   ✅ {payment['name']}: approval_state → cancelled")
                updated_count += 1
            except Exception as e:
                print(f"   ❌ Error updating {payment['name']}: {e}")
        
        print(f"\\n🎉 Update Complete!")
        print(f"   📊 Successfully updated: {updated_count} payments")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    success = update_payment_approval_states()
    exit(0 if success else 1)
'''
    
    with open('manual_payment_update.py', 'w', encoding='utf-8') as f:
        f.write(manual_script)
    
    print("✅ Created manual_payment_update.py")

def main():
    """Create all migration options"""
    print("🔄 PAYMENT APPROVAL STATE MIGRATION GENERATOR")
    print("=" * 60)
    
    create_migration_script()
    create_sql_migration() 
    create_odoo_module_migration()
    create_manual_update_script()
    
    print("\n📋 MIGRATION OPTIONS CREATED:")
    print("=" * 60)
    print("1. 📄 payment_approval_migration.py - Python script for Odoo shell")
    print("2. 📄 payment_approval_migration.sql - Direct SQL migration")
    print("3. 📁 account_payment_final/migrations/ - Proper Odoo migration")
    print("4. 📄 manual_payment_update.py - Manual update via XML-RPC")
    
    print("\n🚀 RECOMMENDED USAGE:")
    print("=" * 60)
    print("For CloudPepper:")
    print("  → Use manual_payment_update.py (works via web interface)")
    print("")
    print("For development:")
    print("  → Use payment_approval_migration.py in Odoo shell")
    print("")
    print("For production:")
    print("  → Use the Odoo module migration (auto-runs on update)")
    print("")
    print("For database access:")
    print("  → Use payment_approval_migration.sql directly on database")
    
    print("\n⚠️ IMPORTANT NOTES:")
    print("=" * 60)
    print("• Always backup your database before running migrations")
    print("• Test on staging environment first")
    print("• The module migration will run automatically on next update")
    print("• Check results with query: SELECT state, approval_state, COUNT(*) FROM account_payment GROUP BY state, approval_state")

if __name__ == "__main__":
    main()
