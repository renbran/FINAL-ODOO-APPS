# -*- coding: utf-8 -*-

from . import models

def post_init_hook(env):
    """Post-installation hook to initialize company branding fields"""
    try:
        # First, try to add the database columns if they don't exist
        cr = env.cr
        
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
        
        # Commit the database changes
        cr.commit()
        
        # Now update company records through ORM
        companies = env['res.company'].search([])
        for company in companies:
            vals = {}
            if not company.voucher_footer_message:
                vals['voucher_footer_message'] = 'Thank you for your business'
            if not company.voucher_terms:
                vals['voucher_terms'] = 'This is a computer-generated document. No physical signature or stamp required for system verification.'
            if company.use_osus_branding is None:
                vals['use_osus_branding'] = True
            
            if vals:
                company.write(vals)
                
    except Exception as e:
        # Log the error but don't fail module installation
        import logging
        _logger = logging.getLogger(__name__)
        _logger.warning(f"Could not initialize company branding fields: {e}")
        _logger.warning("Please run the manual database fix script: fix_company_fields.sql")
