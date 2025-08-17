#!/usr/bin/env python3
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
        print(f"\n🔍 ORDERS NEEDING MIGRATION:")
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
        print(f"\n📈 STATE COMBINATION BREAKDOWN:")
        for combo, count in state_combinations.items():
            print(f"   {combo}: {count} orders")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
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
