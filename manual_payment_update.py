#!/usr/bin/env python3
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
        if input("\nProceed with updates? (y/N): ").lower() != 'y':
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
        
        print(f"\n🎉 Update Complete!")
        print(f"   📊 Successfully updated: {updated_count} payments")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    success = update_payment_approval_states()
    exit(0 if success else 1)
