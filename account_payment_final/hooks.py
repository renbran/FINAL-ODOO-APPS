import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def _post_init_hook(cr, registry):
    """Post-install hook to set up module data"""
    try:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # Create sequences for companies that don't have them
        companies = env['res.company'].search([])
        for company in companies:
            _create_company_sequences(env, company)
        
        # Set default OSUS branding for existing companies
        if companies:
            companies.write({
                'use_osus_branding': True,
                'voucher_footer_message': 'Thank you for your business with OSUS Properties',
                'voucher_terms': 'This is a computer-generated document. No physical signature required for system verification.',
            })
        
        _logger.info("OSUS Payment Voucher module post-install setup completed successfully")
        
    except Exception as e:
        _logger.error(f"Error in post-install hook: {e}")
        # Don't raise the exception to prevent module installation failure
        pass
            'voucher_terms': 'This is a computer-generated document. No physical signature required for system verification.',
        })
        
        _logger.info("OSUS Payment Voucher module post-install setup completed successfully")
        
    except Exception as e:
        _logger.error(f"Error in post-install hook: {e}")


def _create_company_sequences(env, company):
    """Create voucher sequences for a company"""
    sequences = [
        {
            'name': f'Payment Voucher - {company.name}',
            'code': 'payment.voucher',
            'prefix': f'PV/{company.name[:3].upper()}/%(year)s/',
            'padding': 5,
            'company_id': company.id,
        },
        {
            'name': f'Receipt Voucher - {company.name}',
            'code': 'receipt.voucher', 
            'prefix': f'RV/{company.name[:3].upper()}/%(year)s/',
            'padding': 5,
            'company_id': company.id,
        }
    ]
    
    for seq_data in sequences:
        existing = env['ir.sequence'].search([
            ('code', '=', seq_data['code']),
            ('company_id', '=', company.id)
        ], limit=1)
        
        if not existing:
            env['ir.sequence'].create(seq_data)
            _logger.info(f"Created sequence {seq_data['name']} for company {company.name}")


def _pre_init_hook(cr):
    """Pre-install hook"""
    _logger.info("Starting OSUS Payment Voucher module installation")