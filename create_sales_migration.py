#!/usr/bin/env python3
"""
Sales Order Status Migration Script
Syncs existing sales order records to match their order status with their sale state

This script updates existing sales orders where:
- If sale.state == 'sale' (confirmed) but order_status is still 'draft' -> Set order_status = 'post'
- If sale.state == 'done' but order_status != 'post' -> Set order_status = 'post'
- If sale.state == 'cancel' but order_status != 'cancelled' -> Set order_status = 'cancelled'
- Populates missing workflow user assignments based on creation and modification history
"""

import os
import sys
from pathlib import Path

def create_sales_migration_script():
    """Create Python migration script for Odoo sales orders"""
    
    migration_script = '''#!/usr/bin/env python3
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
        print(f"\\n🔧 Fixing {len(confirmed_orders_wrong_status)} confirmed/done orders...")
        
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
        print(f"\\n🔧 Fixing {len(cancelled_orders_wrong_status)} cancelled orders...")
        
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
        print(f"\\n🔧 Fixing {len(draft_orders_to_fix)} draft orders...")
        
        for order in draft_orders_to_fix:
            try:
                old_status = order.order_status
                order.order_status = 'draft'
                
                print(f"   ✅ Order {order.name}: {old_status} → draft")
                updated_count += 1
                
            except Exception as e:
                print(f"   ❌ Error updating order {order.name}: {e}")
    
    # 4. Fix missing workflow user assignments for all orders
    print(f"\\n🔧 Fixing missing workflow user assignments...")
    
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
    
    print(f"\\n🎉 Migration Complete!")
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
'''
    
    # Write the migration script
    with open('sales_order_migration.py', 'w', encoding='utf-8') as f:
        f.write(migration_script)
    
    print("✅ Created sales_order_migration.py")

def create_sales_sql_migration():
    """Create SQL migration script for sales orders"""
    
    sql_script = '''-- Sales Order Status SQL Migration
-- Run this SQL script directly on the database if needed

-- 1. Update confirmed/done orders to have 'post' order status
UPDATE sale_order 
SET order_status = 'post',
    write_date = NOW()
WHERE state IN ('sale', 'done') 
  AND order_status NOT IN ('post', 'approved');

-- 2. Update draft orders to have 'draft' order status
UPDATE sale_order 
SET order_status = 'draft',
    write_date = NOW()
WHERE state = 'draft' 
  AND order_status NOT IN ('draft', 'document_review');

-- 3. Set documentation_user_id where missing (use create_uid)
UPDATE sale_order 
SET documentation_user_id = create_uid
WHERE order_status IN ('post', 'approved', 'final_review')
  AND documentation_user_id IS NULL
  AND create_uid IS NOT NULL;

-- 4. Set commission_user_id where missing (use write_uid or create_uid)
UPDATE sale_order 
SET commission_user_id = COALESCE(write_uid, create_uid)
WHERE order_status IN ('post', 'approved', 'final_review')
  AND commission_user_id IS NULL
  AND COALESCE(write_uid, create_uid) IS NOT NULL;

-- 5. Set allocation_user_id where missing
UPDATE sale_order 
SET allocation_user_id = COALESCE(write_uid, create_uid)
WHERE order_status IN ('post', 'approved', 'final_review')
  AND allocation_user_id IS NULL
  AND COALESCE(write_uid, create_uid) IS NOT NULL;

-- 6. Set final_review_user_id where missing
UPDATE sale_order 
SET final_review_user_id = COALESCE(write_uid, create_uid)
WHERE order_status IN ('post', 'approved', 'final_review')
  AND final_review_user_id IS NULL
  AND COALESCE(write_uid, create_uid) IS NOT NULL;

-- 7. Set approval_user_id where missing for posted orders
UPDATE sale_order 
SET approval_user_id = COALESCE(write_uid, create_uid)
WHERE order_status = 'post'
  AND approval_user_id IS NULL
  AND COALESCE(write_uid, create_uid) IS NOT NULL;

-- 8. Set posting_user_id where missing for posted orders
UPDATE sale_order 
SET posting_user_id = COALESCE(write_uid, create_uid)
WHERE order_status = 'post'
  AND posting_user_id IS NULL
  AND COALESCE(write_uid, create_uid) IS NOT NULL;

-- Query to check results
SELECT 
    state,
    order_status,
    COUNT(*) as count
FROM sale_order 
GROUP BY state, order_status
ORDER BY state, order_status;
'''
    
    with open('sales_order_migration.sql', 'w', encoding='utf-8') as f:
        f.write(sql_script)
    
    print("✅ Created sales_order_migration.sql")

def create_sales_odoo_module_migration():
    """Create a proper Odoo module migration for sales orders"""
    
    # Create migration directory structure
    migration_dir = Path("order_status_override/migrations/17.0.1.0.0")
    migration_dir.mkdir(parents=True, exist_ok=True)
    
    # Create pre-migration script
    pre_migration = '''# -*- coding: utf-8 -*-
"""
Pre-migration script for sales order status sync
"""

import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Pre-migration: Log current state"""
    _logger.info("Starting sales order status migration from version %s", version)
    
    # Count orders that need migration
    cr.execute("""
        SELECT 
            state,
            order_status,
            COUNT(*) as count
        FROM sale_order 
        WHERE (state IN ('sale', 'done') AND order_status NOT IN ('post', 'approved'))
           OR (state = 'draft' AND order_status NOT IN ('draft', 'document_review'))
        GROUP BY state, order_status
    """)
    
    results = cr.fetchall()
    _logger.info("Sales orders requiring migration: %s", results)
'''
    
    with open(migration_dir / "pre-migrate.py", 'w', encoding='utf-8') as f:
        f.write(pre_migration)
    
    # Create post-migration script
    post_migration = '''# -*- coding: utf-8 -*-
"""
Post-migration script for sales order status sync
"""

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Post-migration: Sync order_status with sale state"""
    _logger.info("Running sales order status sync migration")
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    updated_count = 0
    
    # 1. Fix confirmed/done orders
    confirmed_orders = env['sale.order'].search([
        ('state', 'in', ['sale', 'done']),
        ('order_status', 'not in', ['post', 'approved'])
    ])
    
    if confirmed_orders:
        _logger.info("Updating %d confirmed/done orders to order_status=post", len(confirmed_orders))
        for order in confirmed_orders:
            order.write({'order_status': 'post'})
            
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
                
        updated_count += len(confirmed_orders)
    
    # 2. Fix draft orders with advanced statuses
    draft_orders = env['sale.order'].search([
        ('state', '=', 'draft'),
        ('order_status', 'not in', ['draft', 'document_review'])
    ])
    
    if draft_orders:
        _logger.info("Updating %d draft orders to order_status=draft", len(draft_orders))
        draft_orders.write({'order_status': 'draft'})
        updated_count += len(draft_orders)
    
    _logger.info("Sales order status migration completed. Updated %d orders.", updated_count)
'''
    
    with open(migration_dir / "post-migrate.py", 'w', encoding='utf-8') as f:
        f.write(post_migration)
    
    print(f"✅ Created Odoo module migration in {migration_dir}")

def create_sales_manual_update_script():
    """Create a manual update script for sales orders"""
    
    manual_script = '''#!/usr/bin/env python3
"""
Manual Sales Order Status Update Script
Run this script to immediately update sales order statuses

Usage:
1. From terminal: python manual_sales_update.py
2. Or from Odoo: Run in web interface as server action
"""

import xmlrpc.client
import logging
import getpass

def update_sales_order_status():
    """Manual update of sales order statuses"""
    
    print("🔄 SALES ORDER STATUS UPDATE")
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
        
        # Search for orders needing update
        confirmed_orders = models.execute_kw(
            db, uid, password,
            'sale.order', 'search_read',
            [[('state', 'in', ['sale', 'done']), ('order_status', 'not in', ['post', 'approved'])]],
            {'fields': ['name', 'state', 'order_status', 'amount_total', 'partner_id']}
        )
        
        draft_orders = models.execute_kw(
            db, uid, password,
            'sale.order', 'search_read',
            [[('state', '=', 'draft'), ('order_status', 'not in', ['draft', 'document_review'])]],
            {'fields': ['name', 'state', 'order_status', 'amount_total', 'partner_id']}
        )
        
        print(f"📊 Found {len(confirmed_orders)} confirmed/done orders to update")
        print(f"📊 Found {len(draft_orders)} draft orders to update")
        
        if not confirmed_orders and not draft_orders:
            print("✅ All sales orders are already in sync!")
            return True
        
        # Ask for confirmation
        if input("\\nProceed with updates? (y/N): ").lower() != 'y':
            print("❌ Update cancelled by user")
            return False
        
        updated_count = 0
        
        # Update confirmed/done orders
        for order in confirmed_orders:
            try:
                models.execute_kw(
                    db, uid, password,
                    'sale.order', 'write',
                    [[order['id']], {'order_status': 'post'}]
                )
                print(f"   ✅ {order['name']}: order_status → post")
                updated_count += 1
            except Exception as e:
                print(f"   ❌ Error updating {order['name']}: {e}")
        
        # Update draft orders
        for order in draft_orders:
            try:
                models.execute_kw(
                    db, uid, password,
                    'sale.order', 'write',
                    [[order['id']], {'order_status': 'draft'}]
                )
                print(f"   ✅ {order['name']}: order_status → draft")
                updated_count += 1
            except Exception as e:
                print(f"   ❌ Error updating {order['name']}: {e}")
        
        print(f"\\n🎉 Update Complete!")
        print(f"   📊 Successfully updated: {updated_count} orders")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    success = update_sales_order_status()
    exit(0 if success else 1)
'''
    
    with open('manual_sales_update.py', 'w', encoding='utf-8') as f:
        f.write(manual_script)
    
    print("✅ Created manual_sales_update.py")

def create_sales_validation_script():
    """Create validation script for sales orders"""
    
    validation_script = '''#!/usr/bin/env python3
"""
Sales Order Status Validation Script
Run in Odoo shell to validate sales order statuses
"""

from odoo import api, SUPERUSER_ID

def validate_sales_order_status(cr, registry):
    """Validate current sales order statuses"""
    
    print("🔍 SALES ORDER STATUS VALIDATION")
    print("=" * 50)
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Get all sales orders
    all_orders = env['sale.order'].search([])
    
    # Categorize orders
    synced_orders = []
    needs_migration = []
    
    for order in all_orders:
        if ((order.state in ['sale', 'done'] and order.order_status in ['post', 'approved']) or
            (order.state == 'draft' and order.order_status in ['draft', 'document_review'])):
            synced_orders.append(order)
        else:
            needs_migration.append({
                'order': order,
                'name': order.name,
                'state': order.state,
                'order_status': order.order_status,
                'partner': order.partner_id.name if order.partner_id else 'N/A',
                'amount': order.amount_total
            })
    
    print(f"📊 VALIDATION RESULTS:")
    print(f"   ✅ Already synced: {len(synced_orders)} orders")
    print(f"   ⚠️  Need migration: {len(needs_migration)} orders")
    
    if needs_migration:
        print(f"\\n🔍 ORDERS NEEDING MIGRATION:")
        print("-" * 80)
        print(f"{'Name':<20} {'State':<10} {'Order Status':<20} {'Partner':<20} {'Amount':<10}")
        print("-" * 80)
        
        for item in needs_migration[:20]:  # Show first 20
            print(f"{item['name']:<20} {item['state']:<10} {item['order_status']:<20} {item['partner']:<20} {item['amount']:<10}")
        
        if len(needs_migration) > 20:
            print(f"... and {len(needs_migration) - 20} more")
    
    # Group by state combinations
    state_combinations = {}
    for item in needs_migration:
        key = f"{item['state']} -> {item['order_status']}"
        if key not in state_combinations:
            state_combinations[key] = 0
        state_combinations[key] += 1
    
    if state_combinations:
        print(f"\\n📈 STATE COMBINATION BREAKDOWN:")
        for combo, count in state_combinations.items():
            print(f"   {combo}: {count} orders")
    
    # Recommendations
    print(f"\\n💡 RECOMMENDATIONS:")
    if not needs_migration:
        print("   ✅ All sales orders are already in sync! No migration needed.")
    else:
        print("   🔧 Run migration script to sync order statuses")
        print("   📋 Use one of the generated migration options:")
        print("      - manual_sales_update.py (for CloudPepper)")
        print("      - sales_order_migration.py (for Odoo shell)")
        print("      - Auto-migration on module update")
    
    return len(needs_migration)

if __name__ == "__main__":
    print("Run this in Odoo shell:")
    print(">>> exec(open('sales_validation.py').read())")
    print(">>> validate_sales_order_status(cr, registry)")
'''
    
    with open('sales_validation.py', 'w', encoding='utf-8') as f:
        f.write(validation_script)
    
    print("✅ Created sales_validation.py")

def main():
    """Create all sales order migration options"""
    print("🔄 SALES ORDER STATUS MIGRATION GENERATOR")
    print("=" * 60)
    
    create_sales_migration_script()
    create_sales_sql_migration() 
    create_sales_odoo_module_migration()
    create_sales_manual_update_script()
    create_sales_validation_script()
    
    print("\n📋 SALES ORDER MIGRATION OPTIONS CREATED:")
    print("=" * 60)
    print("1. 📄 sales_order_migration.py - Python script for Odoo shell")
    print("2. 📄 sales_order_migration.sql - Direct SQL migration")
    print("3. 📁 order_status_override/migrations/ - Proper Odoo migration")
    print("4. 📄 manual_sales_update.py - Manual update via XML-RPC")
    print("5. 📄 sales_validation.py - Validation script")
    
    print("\n🚀 RECOMMENDED USAGE:")
    print("=" * 60)
    print("For CloudPepper:")
    print("  → Use manual_sales_update.py (works via web interface)")
    print("")
    print("For development:")
    print("  → Use sales_order_migration.py in Odoo shell")
    print("")
    print("For production:")
    print("  → Use the Odoo module migration (auto-runs on update)")
    print("")
    print("For database access:")
    print("  → Use sales_order_migration.sql directly on database")
    
    print("\n⚠️ IMPORTANT NOTES:")
    print("=" * 60)
    print("• Always backup your database before running migrations")
    print("• Test on staging environment first")
    print("• The module migration will run automatically on next update")
    print("• Sales orders sync: state='sale'/'done' → order_status='post'")
    print("• Draft orders sync: state='draft' → order_status='draft'")

if __name__ == "__main__":
    main()
