# -*- coding: utf-8 -*-

def migrate(env):
    """
    Migration script for payment_account_enhanced module
    Adds missing company fields for voucher customization
    """
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
            cr.execute("ALTER TABLE res_company ADD COLUMN voucher_footer_message TEXT")
            cr.execute("""
                UPDATE res_company 
                SET voucher_footer_message = 'Thank you for your business' 
                WHERE voucher_footer_message IS NULL
            """)
            _logger.info("Added voucher_footer_message column to res_company")
        
        # Check and add voucher_terms column
        cr.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='res_company' AND column_name='voucher_terms'
        """)
        if not cr.fetchone():
            cr.execute("ALTER TABLE res_company ADD COLUMN voucher_terms TEXT")
            cr.execute("""
                UPDATE res_company 
                SET voucher_terms = 'This is a computer-generated document. No physical signature or stamp required for system verification.' 
                WHERE voucher_terms IS NULL
            """)
            _logger.info("Added voucher_terms column to res_company")
        
        # Check and add use_osus_branding column
        cr.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='res_company' AND column_name='use_osus_branding'
        """)
        if not cr.fetchone():
            cr.execute("ALTER TABLE res_company ADD COLUMN use_osus_branding BOOLEAN")
            cr.execute("""
                UPDATE res_company 
                SET use_osus_branding = TRUE 
                WHERE use_osus_branding IS NULL
            """)
            _logger.info("Added use_osus_branding column to res_company")
        
        # Commit the changes
        cr.commit()
        _logger.info("Payment account enhanced migration completed successfully")
        
    except Exception as e:
        _logger.error(f"Migration failed: {e}")
        cr.rollback()
        raise
