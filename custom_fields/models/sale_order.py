from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    booking_date = fields.Date(
        string='Booking Date',
        tracking=True,
        help="The date when the booking was made."
    )
    
    developer_commission = fields.Float(
        string='Broker Commission',
        tracking=True,
        digits='Account',
        help="Commission amount for the broker."
    )
    
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        tracking=True,
        domain=[('customer_rank', '>', 0)],
        help="The buyer associated with this sale order."
    )
    
    deal_id = fields.Integer(
        string='Deal ID',
        tracking=True,
        copy=False,
        index=True,
        help="Unique identifier for the deal."
    )
    
    project_id = fields.Many2one(
        'product.template',
        string='Project Name',
        tracking=True,
        domain=[('can_be_expensed', '=', False)],
        help="The project associated with this sale order."
    )
    
    sale_value = fields.Monetary(
        string='Sale Value',
        tracking=True,
        currency_field='currency_id',
        help="The total sale value of the order."
    )
    
    unit_id = fields.Many2one(
        'product.product',
        string='Unit',
        tracking=True,
        domain="[('product_tmpl_id', '=', project_id)]",
        help="The specific unit associated with this sale order."
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
        tracking=True
    )

    _sql_constraints = [
        ('deal_id_unique', 'UNIQUE(deal_id)', 'Deal ID must be unique!'),
    ]

    @api.constrains('developer_commission')
    def _check_developer_commission(self):
        for order in self:
            if order.developer_commission < 0:
                raise ValidationError(_("Commission cannot be negative."))

    def _prepare_invoice(self):
        """Extend invoice preparation with custom fields"""
        invoice_vals = super()._prepare_invoice()
        invoice_vals.update({
            'booking_date': self.booking_date,
            'developer_commission': self.developer_commission,
            'buyer': self.buyer_id.id,
            'deal_id': self.deal_id,
            'project': self.project_id.id,
            'sale_value': self.sale_value,
            'unit': self.unit_id.id,
        })
        return invoice_vals

    @api.model
    def create(self, vals):
        """Handle default values and validation on create"""
        if not vals.get('currency_id'):
            vals['currency_id'] = self.env.company.currency_id.id
        return super().create(vals)