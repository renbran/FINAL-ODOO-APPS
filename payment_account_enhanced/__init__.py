# -*- coding: utf-8 -*-

from . import models

def post_init_hook(env):
    """Post-installation hook to initialize company branding fields"""
    try:
        companies = env['res.company'].search([])
        for company in companies:
            # Set default values if fields are empty
            if not company.voucher_footer_message:
                company.write({'voucher_footer_message': 'Thank you for your business'})
            if not company.voucher_terms:
                company.write({'voucher_terms': 'This is a computer-generated document. No physical signature or stamp required for system verification.'})
            if not hasattr(company, 'use_osus_branding') or company.use_osus_branding is None:
                company.write({'use_osus_branding': True})
    except Exception as e:
        # If fields don't exist yet, they will be created by the ORM
        pass
