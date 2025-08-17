#!/usr/bin/env python3
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
        if input("\nProceed with updates? (y/N): ").lower() != 'y':
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
        
        print(f"\n🎉 Update Complete!")
        print(f"   📊 Successfully updated: {updated_count} orders")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    success = update_sales_order_status()
    exit(0 if success else 1)
