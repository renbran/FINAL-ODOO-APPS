# -*- coding: utf-8 -*-
# This module is under copyright of 'OdooElevate'

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Note: booking_date and sale_value fields are already defined 
    # in osus_invoice_report module, so we don't redefine them here
    # This module only provides the view enhancements
    
    pass
