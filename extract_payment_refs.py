# This script should be run in Odoo shell:
# docker-compose exec odoo odoo shell -d odoo
# Then paste this code

def extract_payment_references_from_journal():
    """Extract payment reference numbers from journal entries and update payment records"""
    try:
        # Clear any existing transaction errors
        env.cr.rollback()
        
        payment_model = env['account.payment']
        move_line_model = env['account.move.line']
        
        print("Extracting payment references from journal entries...")
        print("=" * 60)
        
        # First, commit any pending transaction to clear the error state
        env.cr.commit()
        
        # Find payments with missing or default reference numbers - simplified query
        payments_to_update = payment_model.search([
            '|',
            ('name', '=', '/'),
            ('name', '=', False),
            ('state', '!=', 'cancelled')  # Skip cancelled payments
        ], order='id desc')
        
    except Exception as e:
        print(f"Error in initial setup: {e}")
        print("Trying to recover...")
        env.cr.rollback()
        
        # Try a simpler approach
        try:
            payment_model = env['account.payment']
            payments_to_update = payment_model.search([
                ('name', 'in', ['/', False])
            ])
        except Exception as e2:
            print(f"Recovery failed: {e2}")
            return {'error': str(e2)}
    
    print(f"Found {len(payments_to_update)} payments to analyze")
    print()
    
    updated_count = 0
    skipped_count = 0
    
    for payment in payments_to_update:
        try:
            # Get the journal entry associated with this payment
            move_id = payment.move_id
            
            if not move_id:
                print(f"⚠️  Payment {payment.id}: No journal entry found")
                skipped_count += 1
                continue
            
            # Look for reference in the journal entry itself
            journal_ref = None
            
            # Method 1: Check move.name (journal entry number)
            if move_id.name and move_id.name != '/':
                journal_ref = move_id.name
                source = "journal entry name"
            
            # Method 2: Check move.ref (reference field)
            elif move_id.ref and move_id.ref != '/':
                journal_ref = move_id.ref
                source = "journal entry reference"
            
            # Method 3: Extract from journal entry lines or payment method
            elif payment.journal_id:
                # Check if journal has specific payment sequences configured
                journal_ref = None
                
                # Look for customer payment sequences
                if payment.payment_type == 'inbound':
                    # Check for customer payment specific sequences
                    customer_sequences = env['ir.sequence'].search([
                        ('code', 'in', [
                            'account.payment.customer.invoice', 
                            'account.payment.customer',
                            f'account.payment.{payment.journal_id.code}.inbound'
                        ]),
                        '|', ('company_id', '=', payment.company_id.id), ('company_id', '=', False)
                    ], order='id desc', limit=1)
                    
                    if customer_sequences:
                        # Get the pattern from existing payments with this sequence
                        similar_payments = payment_model.search([
                            ('journal_id', '=', payment.journal_id.id),
                            ('payment_type', '=', 'inbound'),
                            ('name', '!=', '/'),
                            ('name', '!=', False),
                            ('id', '!=', payment.id)
                        ], limit=5, order='id desc')
                        
                        if similar_payments:
                            # Extract pattern from existing customer payments
                            existing_ref = similar_payments[0].name
                            if existing_ref and '/' in existing_ref:
                                # Extract prefix pattern
                                parts = existing_ref.split('/')
                                if len(parts) >= 2:
                                    prefix = '/'.join(parts[:-1])
                                    next_num = 1
                                    # Find the highest number in this pattern
                                    for ref_payment in similar_payments:
                                        if ref_payment.name and ref_payment.name.startswith(prefix):
                                            try:
                                                num_part = ref_payment.name.split('/')[-1]
                                                if num_part.isdigit():
                                                    next_num = max(next_num, int(num_part) + 1)
                                            except:
                                                pass
                                    journal_ref = f"{prefix}/{next_num:05d}"
                                    source = "customer payment pattern"
                        
                        # Fallback to sequence if pattern detection failed
                        if not journal_ref:
                            journal_ref = customer_sequences.next_by_id()
                            source = f"customer sequence {customer_sequences.code}"
                    
                # Look for vendor payment sequences
                else:
                    # Check for vendor payment specific sequences  
                    vendor_sequences = env['ir.sequence'].search([
                        ('code', 'in', [
                            'account.payment.supplier.invoice',
                            'account.payment.supplier', 
                            f'account.payment.{payment.journal_id.code}.outbound'
                        ]),
                        '|', ('company_id', '=', payment.company_id.id), ('company_id', '=', False)
                    ], order='id desc', limit=1)
                    
                    if vendor_sequences:
                        # Get pattern from existing vendor payments
                        similar_payments = payment_model.search([
                            ('journal_id', '=', payment.journal_id.id),
                            ('payment_type', '=', 'outbound'),
                            ('name', '!=', '/'),
                            ('name', '!=', False),
                            ('id', '!=', payment.id)
                        ], limit=5, order='id desc')
                        
                        if similar_payments:
                            # Extract pattern from existing vendor payments
                            existing_ref = similar_payments[0].name
                            if existing_ref and '/' in existing_ref:
                                parts = existing_ref.split('/')
                                if len(parts) >= 2:
                                    prefix = '/'.join(parts[:-1])
                                    next_num = 1
                                    for ref_payment in similar_payments:
                                        if ref_payment.name and ref_payment.name.startswith(prefix):
                                            try:
                                                num_part = ref_payment.name.split('/')[-1]
                                                if num_part.isdigit():
                                                    next_num = max(next_num, int(num_part) + 1)
                                            except:
                                                pass
                                    journal_ref = f"{prefix}/{next_num:05d}"
                                    source = "vendor payment pattern"
                        
                        # Fallback to sequence
                        if not journal_ref:
                            journal_ref = vendor_sequences.next_by_id()
                            source = f"vendor sequence {vendor_sequences.code}"
            
            # Method 4: Use journal code + payment ID as fallback
            if not journal_ref:
                journal_code = payment.journal_id.code or 'PAY'
                if payment.payment_type == 'inbound':
                    journal_ref = f"{journal_code}/IN/{payment.id:05d}"
                else:
                    journal_ref = f"{journal_code}/OUT/{payment.id:05d}"
                source = "generated from journal code"
            
            # Update the payment reference
            if journal_ref:
                old_ref = payment.name
                
                # Only update if we found a better reference
                if old_ref in ['/', False, None, ''] or len(journal_ref) > len(str(old_ref)):
                    # Check if this is a posted payment (be more careful)
                    if payment.state == 'posted':
                        print(f"📋 Payment {payment.id} (POSTED): '{old_ref}' → '{journal_ref}' (from {source})")
                        # For posted payments, you might want to be more conservative
                        # Uncomment the next line to actually update posted payments
                        # payment.name = journal_ref
                        print(f"   ⚠️  POSTED payment - reference NOT updated for audit safety")
                    else:
                        payment.name = journal_ref
                        print(f"✅ Payment {payment.id} ({payment.state}): '{old_ref}' → '{journal_ref}' (from {source})")
                        updated_count += 1
                else:
                    print(f"⏭️  Payment {payment.id}: Current ref '{old_ref}' seems better than '{journal_ref}'")
                    skipped_count += 1
            else:
                print(f"❌ Payment {payment.id}: Could not determine reference")
                skipped_count += 1
                
        except Exception as e:
            print(f"❌ Error processing payment {payment.id}: {str(e)}")
            skipped_count += 1
    
    print()
    print("=" * 60)
    print("SUMMARY:")
    print(f"✅ Updated: {updated_count} payments")
    print(f"⏭️  Skipped: {skipped_count} payments")
    print(f"📋 Posted payments were analyzed but not modified for audit safety")
    print()
    print("To update POSTED payments as well, uncomment the line in the script")
    print("and run again (use with caution in production)")
    
    return {
        'updated': updated_count,
        'skipped': skipped_count,
        'total_analyzed': len(payments_to_update)
    }

# Run the function
result = extract_payment_references_from_journal()
print(f"Extraction completed: {result}")
