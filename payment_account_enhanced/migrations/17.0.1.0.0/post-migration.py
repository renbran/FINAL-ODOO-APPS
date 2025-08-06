def migrate(cr, version):
    """
    Migration script to add missing res_company fields for payment_account_enhanced module
    """
    # Add voucher_footer_message column if it doesn't exist
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'res_company' AND column_name = 'voucher_footer_message'
    """)
    
    if not cr.fetchone():
        cr.execute("""
            ALTER TABLE res_company 
            ADD COLUMN voucher_footer_message TEXT DEFAULT 'Thank you for your business'
        """)
        print("✓ Added voucher_footer_message column to res_company")
    
    # Add voucher_terms column if it doesn't exist
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'res_company' AND column_name = 'voucher_terms'
    """)
    
    if not cr.fetchone():
        cr.execute("""
            ALTER TABLE res_company 
            ADD COLUMN voucher_terms TEXT
        """)
        print("✓ Added voucher_terms column to res_company")
    
    # Add use_osus_branding column if it doesn't exist
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'res_company' AND column_name = 'use_osus_branding'
    """)
    
    if not cr.fetchone():
        cr.execute("""
            ALTER TABLE res_company 
            ADD COLUMN use_osus_branding BOOLEAN DEFAULT TRUE
        """)
        print("✓ Added use_osus_branding column to res_company")
    
    # Add new signatory fields to account_payment table
    payment_columns = [
        ('reviewer_id', 'INTEGER'),
        ('reviewer_date', 'TIMESTAMP'),
        ('approver_id', 'INTEGER'), 
        ('approver_date', 'TIMESTAMP'),
        ('qr_in_report', 'BOOLEAN DEFAULT TRUE')
    ]
    
    for column_name, column_type in payment_columns:
        cr.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'account_payment' AND column_name = '{column_name}'
        """)
        
        if not cr.fetchone():
            cr.execute(f"""
                ALTER TABLE account_payment 
                ADD COLUMN {column_name} {column_type}
            """)
            print(f"✓ Added {column_name} column to account_payment")
        
    print("✓ Payment Account Enhanced migration completed successfully")
