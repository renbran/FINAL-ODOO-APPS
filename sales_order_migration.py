#!/usr/bin/env python3
"""
Sales Order Status Data Migration
Run this script in Odoo shell to sync order_status with sale state
"""

import logging
from datetime import datetime
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate_sales_order_status(cr, registry):
    """Migrate sales order status to match current sale state"""
    
    print("🔄 Starting Sales Order Status Migration...")
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Find all sales orders that need status sync
    confirmed_orders_wrong_status = env['sale.order'].search([
        ('state', 'in', ['sale', 'done']),
        ('order_status', 'not in', ['post', 'approved'])
    ])
    
    cancelled_orders_wrong_status = env['sale.order'].search([
        ('state', '=', 'cancel'),
        ('order_status', '!=', 'cancelled')
    ])
    
    draft_orders_to_fix = env['sale.order'].search([
        ('state', '=', 'draft'),
        ('order_status', 'not in', ['draft', 'document_review'])
    ])
    
    print(f"📊 Migration Statistics:")
    print(f"   - Confirmed/Done orders to sync: {len(confirmed_orders_wrong_status)}")
    print(f"   - Cancelled orders to sync: {len(cancelled_orders_wrong_status)}")
    print(f"   - Draft orders to fix: {len(draft_orders_to_fix)}")
    
    # Counter for tracking updates
    updated_count = 0
    
    # 1. Fix confirmed/done orders
    if confirmed_orders_wrong_status:
        print(f"\n🔧 Fixing {len(confirmed_orders_wrong_status)} confirmed/done orders...")
        
        for order in confirmed_orders_wrong_status:
            try:
                old_status = order.order_status
                
                # Update order status to match confirmed/done state
                order.write({
                    'order_status': 'post',
                })
                
                # Set workflow users if missing
                if not order.documentation_user_id and order.create_uid:
                    order.documentation_user_id = order.create_uid
                
                if not order.commission_user_id and order.write_uid:
                    order.commission_user_id = order.write_uid
                
                if not order.allocation_user_id and order.write_uid:
                    order.allocation_user_id = order.write_uid
                
                if not order.final_review_user_id and order.write_uid:
                    order.final_review_user_id = order.write_uid
                
                if not order.approval_user_id and order.write_uid:
                    order.approval_user_id = order.write_uid
                
                if not order.posting_user_id and order.write_uid:
                    order.posting_user_id = order.write_uid
                
                print(f"   ✅ Order {order.name}: {old_status} → post")
                updated_count += 1
                
            except Exception as e:
                print(f"   ❌ Error updating order {order.name}: {e}")
    
    # 2. Fix cancelled orders
    if cancelled_orders_wrong_status:
        print(f"\n🔧 Fixing {len(cancelled_orders_wrong_status)} cancelled orders...")
        
        # Note: There's no 'cancelled' state in order_status, so we'll set to 'draft'
        # or create a cancelled status if needed
        for order in cancelled_orders_wrong_status:
            try:
                old_status = order.order_status
                # Keep original status but log the change
                # Since there's no cancelled status in order_status, we leave as-is
                print(f"   ⚠️  Order {order.name}: Cancelled but keeping status {old_status} (no cancelled status available)")
                
            except Exception as e:
                print(f"   ❌ Error checking order {order.name}: {e}")
    
    # 3. Fix draft orders with advanced statuses
    if draft_orders_to_fix:
        print(f"\n🔧 Fixing {len(draft_orders_to_fix)} draft orders...")
        
        for order in draft_orders_to_fix:
            try:
                old_status = order.order_status
                order.order_status = 'draft'
                
                print(f"   ✅ Order {order.name}: {old_status} → draft")
                updated_count += 1
                
            except Exception as e:
                print(f"   ❌ Error updating order {order.name}: {e}")
    
    # 4. Fix missing workflow user assignments for all orders
    print(f"\n🔧 Fixing missing workflow user assignments...")
    
    all_orders = env['sale.order'].search([
        ('order_status', 'in', ['post', 'approved', 'final_review'])
    ])
    
    workflow_fixes = 0
    
    for order in all_orders:
        try:
            updates = {}
            
            # Set documentation user if missing
            if not order.documentation_user_id and order.create_uid:
                updates['documentation_user_id'] = order.create_uid.id
            
            # Set commission user if missing (use write_uid or create_uid)
            if not order.commission_user_id:
                if order.write_uid and order.write_uid != order.create_uid:
                    updates['commission_user_id'] = order.write_uid.id
                elif order.create_uid:
                    updates['commission_user_id'] = order.create_uid.id
            
            # Set allocation user if missing
            if not order.allocation_user_id:
                if order.write_uid:
                    updates['allocation_user_id'] = order.write_uid.id
                elif order.create_uid:
                    updates['allocation_user_id'] = order.create_uid.id
            
            # Set final review user if missing
            if not order.final_review_user_id:
                if order.write_uid:
                    updates['final_review_user_id'] = order.write_uid.id
                elif order.create_uid:
                    updates['final_review_user_id'] = order.create_uid.id
            
            # Set approval user if missing (for posted orders)
            if order.order_status == 'post' and not order.approval_user_id:
                if order.write_uid:
                    updates['approval_user_id'] = order.write_uid.id
                elif order.create_uid:
                    updates['approval_user_id'] = order.create_uid.id
            
            # Set posting user if missing (for posted orders)
            if order.order_status == 'post' and not order.posting_user_id:
                if order.write_uid:
                    updates['posting_user_id'] = order.write_uid.id
                elif order.create_uid:
                    updates['posting_user_id'] = order.create_uid.id
            
            if updates:
                order.write(updates)
                workflow_fixes += 1
                
        except Exception as e:
            print(f"   ⚠️ Error fixing workflow users for {order.name}: {e}")
    
    print(f"   ✅ Fixed workflow users for {workflow_fixes} orders")
    
    # Commit changes
    cr.commit()
    
    print(f"\n🎉 Migration Complete!")
    print(f"   📊 Total orders updated: {updated_count}")
    print(f"   📊 Workflow users fixed: {workflow_fixes}")
    print(f"   ✅ All changes committed to database")
    
    return updated_count + workflow_fixes

if __name__ == "__main__":
    # This should be run from Odoo shell
    print("Run this script from Odoo shell:")
    print("$ odoo shell -d your_database")
    print(">>> exec(open('sales_order_migration.py').read())")
    print(">>> migrate_sales_order_status(cr, registry)")
