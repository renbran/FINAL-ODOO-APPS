from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Note: Most of these fields are defined in commission_fields and advance_commission modules
    # We only define the essential ones here that are specific to OSUS Invoice Report
    # If other commission modules are not installed, these will serve as fallbacks
    
    # Essential fields for invoice report functionality
    # Only defined if not already present from other modules
    pass  # All fields are now handled by other modules in the system
