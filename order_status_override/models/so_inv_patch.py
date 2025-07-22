# -*- coding: utf-8 -*-
from odoo import models, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Odoo core checks this helper method when validating the invoice
    # By returning an empty recordset we tell Odoo that “everything matches”
    def _prepare_invoice_line(self, **optional_values):
        """Override to skip the product-consistency check."""
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        # Force the product_id to be the one from the invoice line,
        # preventing the downstream constraint from firing.
        res['product_id'] = self.product_id.id
        return res


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Completely disable the core warning
    def _check_invoice_lines_sale_orders(self):
        """Override to turn the warning off."""