# This script should be run in Odoo shell:
# docker-compose exec odoo odoo shell -d odoo
# Then paste this code

# Simple payment reference extraction script
try:
    # Clear any transaction errors first
    env.cr.rollback()
except:
    pass

print("Extracting payment references from journal entries...")
print("=" * 60)

# Find payments with missing references
payment_model = env['account.payment']

# Simple search without complex ordering to avoid SQL errors
try:
    payments_to_update = payment_model.search([
        ('name', 'in', ['/', False])
    ])
    print(f"Found {len(payments_to_update)} payments to analyze")
except Exception as e:
    print(f"Search error: {e}")
    # Try even simpler approach
    payments_to_update = payment_model.search([('name', '=', '/')])
    print(f"Found {len(payments_to_update)} payments with '/' reference")

updated_count = 0
skipped_count = 0

for payment in payments_to_update[:50]:  # Limit to first 50 to avoid overwhelming
    try:
        print(f"\nProcessing Payment ID: {payment.id}")
        
        # Check if payment has journal entry
        if not payment.move_id:
            print(f"  ❌ No journal entry found")
            skipped_count += 1
            continue
            
        journal_ref = None
        source = ""
        
        # Method 1: Use journal entry name
        if payment.move_id.name and payment.move_id.name != '/':
            journal_ref = payment.move_id.name
            source = "journal entry"
            
        # Method 2: Use journal entry reference  
        elif payment.move_id.ref and payment.move_id.ref != '/':
            journal_ref = payment.move_id.ref
            source = "move reference"
            
        # Method 3: Look at similar payments in same journal
        elif payment.journal_id:
            try:
                similar_payments = payment_model.search([
                    ('journal_id', '=', payment.journal_id.id),
                    ('payment_type', '=', payment.payment_type),
                    ('name', '!=', '/'),
                    ('name', '!=', False),
                    ('id', '!=', payment.id)
                ], limit=3, order='id desc')
                
                if similar_payments:
                    existing_ref = similar_payments[0].name
                    if existing_ref and '/' in existing_ref:
                        # Extract pattern and increment
                        parts = existing_ref.split('/')
                        if len(parts) >= 2 and parts[-1].isdigit():
                            prefix = '/'.join(parts[:-1])
                            # Find highest number
                            max_num = 0
                            for sim_pay in similar_payments:
                                if sim_pay.name and sim_pay.name.startswith(prefix):
                                    try:
                                        num = int(sim_pay.name.split('/')[-1])
                                        max_num = max(max_num, num)
                                    except:
                                        pass
                            journal_ref = f"{prefix}/{max_num + 1:05d}"
                            source = "payment pattern"
            except Exception as pattern_error:
                print(f"  ⚠️  Pattern detection error: {pattern_error}")
                
        # Method 4: Generate from journal code
        if not journal_ref and payment.journal_id:
            journal_code = payment.journal_id.code or 'PAY'
            payment_type = 'IN' if payment.payment_type == 'inbound' else 'OUT'
            journal_ref = f"{journal_code}/{payment_type}/{payment.id:05d}"
            source = "generated"
            
        # Update payment if we found a reference
        if journal_ref:
            old_ref = payment.name
            if payment.state == 'posted':
                print(f"  📋 POSTED: '{old_ref}' → '{journal_ref}' (from {source})")
                print(f"  ⚠️  Not updating posted payment for audit safety")
                skipped_count += 1
            else:
                try:
                    payment.name = journal_ref
                    env.cr.commit()  # Commit each update
                    print(f"  ✅ UPDATED: '{old_ref}' → '{journal_ref}' (from {source})")
                    updated_count += 1
                except Exception as update_error:
                    print(f"  ❌ Update failed: {update_error}")
                    env.cr.rollback()
                    skipped_count += 1
        else:
            print(f"  ❌ Could not determine reference")
            skipped_count += 1
            
    except Exception as e:
        print(f"  ❌ Error processing payment {payment.id}: {str(e)}")
        env.cr.rollback()
        skipped_count += 1

print()
print("=" * 60) 
print("SUMMARY:")
print(f"✅ Updated: {updated_count} payments")
print(f"⏭️  Skipped: {skipped_count} payments")
print()
print("Run script again to process more payments if needed")
