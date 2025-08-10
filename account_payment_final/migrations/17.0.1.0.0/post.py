# -*- coding: utf-8 -*-

def migrate(cr, version):
    """
    Pre-migration script to clean up data before installing account_payment_final
    """
    
    # Clean up any problematic data in account_payment table
    try:
        # Check if account_payment table exists
        cr.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'account_payment';
        """)
        
        columns = cr.fetchall()
        if not columns:
            return  # Table doesn't exist yet
        
        # Get list of existing columns
        existing_columns = [col[0] for col in columns]
        
        # Clean up any text values in integer/many2one fields
        problematic_fields = [
            'submitted_by', 'reviewed_by', 'approved_by', 
            'authorized_by', 'posted_by', 'cancelled_by',
            'create_uid', 'write_uid', 'company_id',
            'journal_id', 'partner_id'
        ]
        
        for field in problematic_fields:
            if field in existing_columns:
                try:
                    # Convert any non-numeric values to NULL
                    cr.execute(f"""
                        UPDATE account_payment 
                        SET {field} = NULL 
                        WHERE {field} IS NOT NULL 
                        AND NOT ({field}::text ~ '^[0-9]+$' OR {field}::text = '');
                    """)
                except Exception:
                    # If conversion fails, just continue
                    continue
        
        # Clean up any orphaned records
        cr.execute("""
            UPDATE account_payment 
            SET journal_id = NULL 
            WHERE journal_id IS NOT NULL 
            AND journal_id::text !~ '^[0-9]+$';
        """)
        
        cr.execute("""
            UPDATE account_payment 
            SET partner_id = NULL 
            WHERE partner_id IS NOT NULL 
            AND partner_id::text !~ '^[0-9]+$';
        """)
        
        # Commit changes
        cr.commit()
        
    except Exception as e:
        # If anything fails, just continue - fresh install will work
        cr.rollback()
