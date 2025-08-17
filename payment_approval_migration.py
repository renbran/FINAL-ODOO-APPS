#!/usr/bin/env python3
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
        print(f"\n🔧 Fixing {len(posted_payments_wrong_approval)} posted payments...")
        
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
        print(f"\n🔧 Fixing {len(cancelled_payments_wrong_approval)} cancelled payments...")
        
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
        print(f"\n🔧 Fixing {len(draft_payments_to_fix)} draft payments...")
        
        for payment in draft_payments_to_fix:
            try:
                old_state = payment.approval_state
                payment.approval_state = 'draft'
                
                print(f"   ✅ Payment {payment.name}: {old_state} → draft")
                updated_count += 1
                
            except Exception as e:
                print(f"   ❌ Error updating payment {payment.name}: {e}")
    
    # 4. Fix missing workflow user assignments for all payments
    print(f"\n🔧 Fixing missing workflow user assignments...")
    
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
    
    print(f"\n🎉 Migration Complete!")
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
