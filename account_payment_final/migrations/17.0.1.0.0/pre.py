# -*- coding: utf-8 -*-

"""
Database Migration Script for account_payment_final Module
Handles data type conversion issues during module installation/upgrade
"""

def migrate(cr, version):
    """
    Handle database migration for account_payment_final module
    Fixes data type conversion issues
    """
    
    # Check if the account_payment table exists
    cr.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'account_payment'
        );
    """)
    
    if not cr.fetchone()[0]:
        return
    
    # Fix any ADMINISTRATOR string values in Many2one fields
    # Common fields that might have this issue:
    fields_to_check = [
        'submitted_by',
        'reviewed_by', 
        'approved_by',
        'authorized_by',
        'posted_by',
        'cancelled_by',
        'create_uid',
        'write_uid'
    ]
    
    for field in fields_to_check:
        # Check if the field exists in the table
        cr.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'account_payment' 
                AND column_name = %s
            );
        """, (field,))
        
        if cr.fetchone()[0]:
            try:
                # Convert ADMINISTRATOR string to NULL (will be handled by Odoo's default)
                cr.execute(f"""
                    UPDATE account_payment 
                    SET {field} = NULL 
                    WHERE {field}::text = 'ADMINISTRATOR' 
                    OR {field}::text ~ '^[A-Za-z]';
                """)
                
                # Also handle any other non-numeric values
                cr.execute(f"""
                    UPDATE account_payment 
                    SET {field} = NULL 
                    WHERE {field} IS NOT NULL 
                    AND {field}::text !~ '^[0-9]+$';
                """)
                
            except Exception as e:
                # If field doesn't exist or other error, continue
                continue
    
    # Clean up any orphaned records that might cause issues
    try:
        # Remove any account_payment records with invalid journal_id
        cr.execute("""
            DELETE FROM account_payment 
            WHERE journal_id IS NOT NULL 
            AND journal_id NOT IN (SELECT id FROM account_journal);
        """)
        
        # Remove any account_payment records with invalid partner_id
        cr.execute("""
            DELETE FROM account_payment 
            WHERE partner_id IS NOT NULL 
            AND partner_id NOT IN (SELECT id FROM res_partner);
        """)
        
    except Exception:
        # If these tables don't exist yet, skip cleanup
        pass
    
    # Commit the changes
    cr.commit()
