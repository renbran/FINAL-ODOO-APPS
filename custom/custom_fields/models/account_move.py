from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    booking_date = fields.Date(
        string='Booking Date',
        tracking=True,
    )
    
    developer_commission = fields.Float(
        string='Developer Commission',
        tracking=True,
    )
    
    buyer = fields.Many2one(
        'res.partner',
        string='Buyer',
        tracking=True,
    )
    
    deal_id = fields.Integer(
        string='Deal ID',
        tracking=True,
    )
    
    project = fields.Many2one(
        'product.template',
        string='Project',
        tracking=True,
        domain=[('detailed_type', '=', 'service')],
    )
    
    sale_value = fields.Monetary(
        string='Sale Value',
        tracking=True,
        currency_field='currency_id',
    )
    
    unit = fields.Many2one(
        'product.product',
        string='Unit',
        tracking=True,
    )

    amount_total_words = fields.Char(
        string='Amount in Words',
        compute='_compute_amount_total_words',
        store=True,
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
                    'buyer': sale_order.buyer_id.id if sale_order.buyer_id else False,
                    'deal_id': sale_order.deal_id,
                    'project': sale_order.project_template_id.id if sale_order.project_template_id else False,
                    'sale_value': sale_order.sale_value,
                    'unit': sale_order.unit_id.id if sale_order.unit_id else False,
                })
        return record

    @api.onchange('project')
    def _onchange_project(self):
        """Update unit domain when project changes"""
        if self.project:
            domain = [('product_tmpl_id', '=', self.project.id)]
            return {'domain': {'unit': domain}}
        else:
            return {'domain': {'unit': []}}