#!/usr/bin/env python3
"""
Python Payment Validation Script
Run in Odoo shell to validate payment states
"""

from odoo import api, SUPERUSER_ID

def validate_payment_states(cr, registry):
    """Validate current payment approval states"""
    
    print("🔍 PAYMENT APPROVAL STATE VALIDATION")
    print("=" * 50)
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Get all payments
    all_payments = env['account.payment'].search([])
    
    # Categorize payments
    synced_payments = []
    needs_migration = []
    
    for payment in all_payments:
        if ((payment.state == 'posted' and payment.approval_state == 'posted') or
            (payment.state == 'cancel' and payment.approval_state == 'cancelled') or
            (payment.state == 'draft' and payment.approval_state in ['draft', 'under_review'])):
            synced_payments.append(payment)
        else:
            needs_migration.append({
                'payment': payment,
                'name': payment.name,
                'state': payment.state,
                'approval_state': payment.approval_state,
                'partner': payment.partner_id.name if payment.partner_id else 'N/A',
                'amount': payment.amount
            })
    
    print(f"📊 VALIDATION RESULTS:")
    print(f"   ✅ Already synced: {len(synced_payments)} payments")
    print(f"   ⚠️  Need migration: {len(needs_migration)} payments")
    
    if needs_migration:
        print(f"\n🔍 PAYMENTS NEEDING MIGRATION:")
        print("-" * 80)
        print(f"{'Name':<20} {'State':<10} {'Approval':<15} {'Partner':<20} {'Amount':<10}")
        print("-" * 80)
        
        for item in needs_migration[:20]:  # Show first 20
            print(f"{item['name']:<20} {item['state']:<10} {item['approval_state']:<15} {item['partner']:<20} {item['amount']:<10}")
        
        if len(needs_migration) > 20:
            print(f"... and {len(needs_migration) - 20} more")
    
    # Group by state combinations
    state_combinations = {}
    for item in needs_migration:
        key = f"{item['state']} -> {item['approval_state']}"
        if key not in state_combinations:
            state_combinations[key] = 0
        state_combinations[key] += 1
    
    if state_combinations:
        print(f"\n📈 STATE COMBINATION BREAKDOWN:")
        for combo, count in state_combinations.items():
            print(f"   {combo}: {count} payments")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if not needs_migration:
        print("   ✅ All payments are already in sync! No migration needed.")
    else:
        print("   🔧 Run migration script to sync approval states")
        print("   📋 Use one of the generated migration options:")
        print("      - manual_payment_update.py (for CloudPepper)")
        print("      - payment_approval_migration.py (for Odoo shell)")
        print("      - Auto-migration on module update")
    
    return len(needs_migration)

if __name__ == "__main__":
    print("Run this in Odoo shell:")
    print(">>> exec(open('payment_validation.py').read())")
    print(">>> validate_payment_states(cr, registry)")
