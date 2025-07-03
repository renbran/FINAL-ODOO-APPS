from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Deal Information Fields - Professional naming convention with _id suffix for relational fields
    booking_date = fields.Date(
        string='Booking Date',
        tracking=True,
        help="Date when the deal was booked"
    )
    
    developer_commission = fields.Float(
        string='Developer Commission',
        tracking=True,
        digits=(16, 2),
        help="Commission percentage for the developer"
    )
    
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        tracking=True,
        help="Customer who is purchasing the property"
    )
    
    deal_id = fields.Char(
        string='Deal Reference',
        tracking=True,
        help="Unique identifier for this deal"
    )
    
    project_id = fields.Many2one(
        'product.template',
        string='Project',
        tracking=True,
        domain=[('detailed_type', '=', 'service')],
        help="Select the project for this deal"
    )
    
    sale_value = fields.Monetary(
        string='Sale Value',
        tracking=True,
        currency_field='currency_id',
        help="Total value of the property sale"
    )
    
    unit_id = fields.Many2one(
        'product.product',
        string='Unit',
        tracking=True,
        help="Specific unit being sold"
    )

    amount_total_words = fields.Char(
        string='Amount in Words',
        compute='_compute_amount_total_words',
        store=True,
    )
    
    sale_order_type = fields.Char(
        string='Sale Order Type',
        compute='_compute_sale_order_type',
        store=True,
        help="Sale order type copied from the originating sale order"
    )

    @api.depends('amount_total')
    def _compute_amount_total_words(self):
        """Convert amount to words"""
        for record in self:
            if record.amount_total:
                # Simple implementation - you can enhance this with a proper number to words library
                currency_name = record.currency_id.name or 'USD'
                amount_str = f"{record.amount_total:.2f}"
                record.amount_total_words = f"{amount_str} {currency_name}"
            else:
                record.amount_total_words = ''

    @api.depends('invoice_origin')
    def _compute_sale_order_type(self):
        """Compute sale order type from originating sale order"""
        for record in self:
            if record.invoice_origin and record.move_type in ['out_invoice', 'out_refund']:
                sale_order = self.env['sale.order'].search([
                    ('name', '=', record.invoice_origin)
                ], limit=1)
                if sale_order and sale_order.sale_order_type_id:
                    record.sale_order_type = sale_order.sale_order_type_id.name
                else:
                    record.sale_order_type = ''
            else:
                record.sale_order_type = ''

    @api.model
    def create(self, vals):
        # First call the parent create method to ensure other modules' logic is executed
        record = super(AccountMove, self).create(vals)
        
        # Then populate our custom fields if this is an invoice from a sale order
        if record.move_type in ['out_invoice', 'out_refund'] and record.invoice_origin:
            sale_order = self.env['sale.order'].search([
                ('name', '=', record.invoice_origin)
            ], limit=1)
            if sale_order:
                record.write({
                    'booking_date': sale_order.booking_date,
                    'developer_commission': sale_order.developer_commission,
                    'buyer_id': sale_order.buyer_id.id if sale_order.buyer_id else False,
                    'deal_id': sale_order.deal_id,
                    'project_id': sale_order.project_id.id if sale_order.project_id else False,
                    'sale_value': sale_order.sale_value,
                    'unit_id': sale_order.unit_id.id if sale_order.unit_id else False,
                })
        return record

    @api.onchange('project_id')
    def _onchange_project_id(self):
        """Update unit domain when project changes"""
        if self.project_id:
            domain = [('product_tmpl_id', '=', self.project_id.id)]
            return {'domain': {'unit_id': domain}}
        else:
            return {'domain': {'unit_id': []}}