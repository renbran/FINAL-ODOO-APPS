#!/usr/bin/env python3
"""
Fix missing company fields for payment_account_enhanced module
Server Environment: /var/odoo/osush/

USAGE OPTIONS:

1. Odoo Shell (Recommended):
   cd /var/odoo/osush && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf
   Then run: exec(open('/var/odoo/osush/extra-addons/payment_account_enhanced/fix_company_fields.py').read())
   Then run: fix_company_fields(env)

2. Module Update:
   cd /var/odoo/osush && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init --update payment_account_enhanced

3. Direct Python execution (if script is in the server):
   sudo -u odoo /var/odoo/osush/venv/bin/python3 fix_company_fields.py
"""

def fix_company_fields(env):
    """Fix missing company fields by adding them directly to the database"""
    import logging
    _logger = logging.getLogger(__name__)
    
    cr = env.cr
    
    try:
        # Check and add voucher_footer_message column
        cr.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='res_company' AND column_name='voucher_footer_message'
        """)
        
        if not cr.fetchone():
            _logger.info("Adding voucher_footer_message column...")
            cr.execute("ALTER TABLE res_company ADD COLUMN voucher_footer_message TEXT")
            cr.execute("""
                UPDATE res_company 
                SET voucher_footer_message = 'Thank you for your business' 
                WHERE voucher_footer_message IS NULL
            """)
            _logger.info("✅ Added voucher_footer_message column")
            print("✅ Added voucher_footer_message column")
        else:
            _logger.info("✅ voucher_footer_message column already exists")
            print("✅ voucher_footer_message column already exists")
        
        # Check and add voucher_terms column
        cr.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='res_company' AND column_name='voucher_terms'
        """)
        
        if not cr.fetchone():
            _logger.info("Adding voucher_terms column...")
            cr.execute("ALTER TABLE res_company ADD COLUMN voucher_terms TEXT")
            cr.execute("""
                UPDATE res_company 
                SET voucher_terms = 'This is a computer-generated document. No physical signature or stamp required for system verification.' 
                WHERE voucher_terms IS NULL
            """)
            _logger.info("✅ Added voucher_terms column")
            print("✅ Added voucher_terms column")
        else:
            _logger.info("✅ voucher_terms column already exists")
            print("✅ voucher_terms column already exists")
        
        # Check and add use_osus_branding column
        cr.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='res_company' AND column_name='use_osus_branding'
        """)
        
        if not cr.fetchone():
            _logger.info("Adding use_osus_branding column...")
            cr.execute("ALTER TABLE res_company ADD COLUMN use_osus_branding BOOLEAN")
            cr.execute("""
                UPDATE res_company 
                SET use_osus_branding = TRUE 
                WHERE use_osus_branding IS NULL
            """)
            _logger.info("✅ Added use_osus_branding column")
            print("✅ Added use_osus_branding column")
        else:
            _logger.info("✅ use_osus_branding column already exists")
            print("✅ use_osus_branding column already exists")
        
        # Commit the changes
        cr.commit()
        _logger.info("🎉 Payment account enhanced database fix completed successfully!")
        print("🎉 Payment account enhanced database fix completed successfully!")
        
        # Verify columns exist
        cr.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name='res_company' 
            AND column_name IN ('voucher_footer_message', 'voucher_terms', 'use_osus_branding')
            ORDER BY column_name
        """)
        
        columns = cr.fetchall()
        _logger.info("Verification - Found columns:")
        print("\nVerification - Found columns:")
        for col_name, col_type in columns:
            _logger.info(f"  - {col_name}: {col_type}")
            print(f"  - {col_name}: {col_type}")
            
    except Exception as e:
        _logger.error(f"❌ Error during database fix: {e}")
        print(f"❌ Error during database fix: {e}")
        cr.rollback()
        raise

if __name__ == "__main__":
    print("=== Payment Account Enhanced Database Fix ===")
    print("Server Path: /var/odoo/osush/")
    print("This script will add missing company fields to the database.")
    print("\nTo run this fix:")
    print("1. Connect to Odoo shell:")
    print("   cd /var/odoo/osush && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf")
    print("2. Load and execute this script:")
    print("   exec(open('/var/odoo/osush/extra-addons/payment_account_enhanced/fix_company_fields.py').read())")
    print("   fix_company_fields(env)")
    print("\nOr use module update:")
    print("   cd /var/odoo/osush && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init --update payment_account_enhanced")
