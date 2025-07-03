from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    booking_date = fields.Date(
        string='Booking Date',
        tracking=False,
    )
    
    developer_commission = fields.Float(
        string='Broker Commission',
        tracking=True,
    )
    
    deal_id = fields.Integer(
        string='Deal ID',
        tracking=True,
    )
    
    sale_value = fields.Monetary(
        string='Sale Value',
        tracking=True,
        currency_field='currency_id',
    )
    
    sale_order_type_id = fields.Many2one(
        'sale.order.type',  # Correct model name
        string='Sales Order Type',
        tracking=True,
    )

    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        tracking=True,
    )
    # Custom project field, not to be confused with Odoo's project_id
    project = fields.Many2one(
        'product.template',
        string='Project',
        tracking=True,
    )
    unit_id = fields.Many2one(
        'product.product',
        string='Unit',
        tracking=True,
        domain="[('product_tmpl_id', '=', project)]",
    )
    deal_id = fields.Char(
        string='Deal ID',
        tracking=True,
    )
    amount_total_words = fields.Char(
        string='Amount in Words',
        compute='_compute_amount_total_words',
        store=True,
    )

    @api.model
    def create(self, vals):
        if vals.get('move_type') in ['out_invoice', 'out_refund'] and vals.get('invoice_origin'):
            sale_order = self.env['sale.order'].search([
                ('name', '=', vals.get('invoice_origin'))
            ], limit=1)
            if sale_order:
                vals.update({
                    'booking_date': sale_order.booking_date,
                    'developer_commission': sale_order.developer_commission,
                    'buyer_id': sale_order.buyer_id.id if sale_order.buyer_id else False,
                    'deal_id': sale_order.deal_id,
                    'project': sale_order.project_id.id if sale_order.project_id else False,
                    'sale_value': sale_order.sale_value,
                    'unit_id': sale_order.unit_id.id if sale_order.unit_id else False,
                    'sale_order_type_id': sale_order.sale_order_type_id.id if sale_order.sale_order_type_id else False,
                })
        return super(AccountMove, self).create(vals)