from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    booking_date = fields.Date(string='Booking Date', tracking=True)
    developer_commission = fields.Float(string='Broker Commission', tracking=True, digits=(16, 2))
    buyer = fields.Many2one('res.partner', string='Buyer', tracking=True)
    deal_id = fields.Char(string='Deal ID', tracking=True)
    project = fields.Many2one('product.template', string='Project', tracking=True)
    sale_value = fields.Monetary(string='Sale Value', tracking=True, currency_field='currency_id')
    unit = fields.Many2one('product.product', string='Unit', tracking=True, 
                          domain="[('product_tmpl_id', '=', project)]")
    sale_order_type_id = fields.Many2one('sale.order.type', string='Sales Order Type',
                                       compute='_compute_sale_order_type_id', store=True, readonly=False)
    amount_total_words = fields.Char(string='Amount in Words', compute='_compute_amount_total_words', store=True)

    @api.depends('amount_total')
    def _compute_amount_total_words(self):
        for move in self:
            move.amount_total_words = move.currency_id.amount_to_text(move.amount_total)

    @api.depends('invoice_origin')
    def _compute_sale_order_type_id(self):
        for move in self:
            sale_order = self.env['sale.order'].search([
                ('name', '=', move.invoice_origin)
            ], limit=1)
            move.sale_order_type_id = sale_order.type_id if sale_order and hasattr(sale_order, 'type_id') else False

    @api.onchange('invoice_origin')
    def _onchange_invoice_origin(self):
        if self.invoice_origin:
            sale_order = self.env['sale.order'].search([
                ('name', '=', self.invoice_origin)
            ], limit=1)
            if sale_order:
                self.update({
                    'booking_date': sale_order.booking_date,
                    'developer_commission': sale_order.developer_commission,
                    'buyer': sale_order.buyer_id,
                    'deal_id': str(sale_order.deal_id) if sale_order.deal_id else False,
                    'project': sale_order.project_id,
                    'sale_value': sale_order.sale_value,
                    'unit': sale_order.unit_id,
                })
                if hasattr(sale_order, 'type_id'):
                    self.sale_order_type_id = sale_order.type_id

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
                    'buyer': sale_order.buyer_id.id,
                    'deal_id': str(sale_order.deal_id) if sale_order.deal_id else False,
                    'project': sale_order.project_id.id,
                    'sale_value': sale_order.sale_value,
                    'unit': sale_order.unit_id.id,
                })
        return super(AccountMove, self).create(vals)