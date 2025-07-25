#!/usr/bin/env python3
"""
Fix missing payment reference numbers
This script can be run to fix existing payment records that don't have proper reference numbers.
"""

def fix_payment_references(env):
    """Fix missing payment reference numbers"""
    payment_model = env['account.payment']
    
    print("Fixing missing payment reference numbers...")
    
    # Find payments with missing or default reference numbers
    payments_to_fix = payment_model.search([
        '|',
        ('name', '=', '/'),
        ('name', '=', False)
    ])
    
    print(f"Found {len(payments_to_fix)} payments to fix")
    
    for payment in payments_to_fix:
        try:
            if payment.payment_type == 'inbound':
                new_name = env['ir.sequence'].next_by_code('receipt.voucher.reference')
            else:
                new_name = env['ir.sequence'].next_by_code('payment.voucher.reference')
            
            if new_name:
                payment.name = new_name
                print(f"Fixed payment {payment.id}: {payment.name}")
        except Exception as e:
            print(f"Error fixing payment {payment.id}: {str(e)}")
    
    print(f"Fixed {len(payments_to_fix)} payment reference numbers")
    return True

if __name__ == "__main__":
    print("This script should be run from Odoo shell")
    print("Example: ")
    print("docker-compose exec odoo odoo shell -d your_database")
    print("Then run: exec(open('fix_payment_references.py').read())")
    print("And call: fix_payment_references(env)")
