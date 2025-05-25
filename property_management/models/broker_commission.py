from odoo import models, fields, api, _
from odoo.exceptions import UserError

class BrokerCommissionInvoice(models.Model):
    _name = 'broker.commission.invoice'
    _description = 'Broker Commission Invoice'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    property_sale_id = fields.Many2one('property.sale', string="Property Sale", required=True)
    property_offer_id = fields.Many2one('property.sale.offer', string="Property Offer")
    seller_id = fields.Many2one('res.partner', string="Seller/Broker", required=True, domain=[('is_company', '=', True)])
    commission_percentage = fields.Float(string="Commission Percentage", digits=(5, 2))
    commission_amount = fields.Monetary(string="Commission Amount", currency_field='currency_id')
    currency_id = fields.Many2one(related='property_sale_id.currency_id', string="Currency", readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    # One2many field for invoices
    invoice_ids = fields.One2many('account.move', 'broker_commission_id', string="Invoices", readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('invoiced', 'Invoiced'),
        ('cancelled', 'Cancelled')
    ], string="State", default='draft', tracking=True)

    display_name = fields.Char(string="Reference", compute='_compute_display_name', store=True)
    total_invoiced = fields.Monetary(string="Invoiced Amount", compute="_compute_payment_info", store=True, currency_field='currency_id')
    total_paid = fields.Monetary(string="Paid Amount", compute="_compute_payment_info", store=True, currency_field='currency_id')
    payment_progress = fields.Float(string="Payment Progress (%)", compute="_compute_payment_info", store=True)
    payment_state = fields.Selection([
        ('not_invoiced', 'Not Invoiced'),
        ('not_paid', 'Not Paid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid')
    ], string="Payment Status", compute="_compute_payment_info", store=True)

    @api.depends('property_sale_id', 'seller_id', 'create_date')
    def _compute_display_name(self):
        for record in self:
            if record.property_sale_id and record.seller_id:
                record.display_name = f"COMM/{record.property_sale_id.name}/{record.seller_id.name}"
            else:
                record.display_name = f"New Commission {record.id or ''}"

    @api.depends('invoice_ids.amount_total', 'invoice_ids.amount_residual', 'invoice_ids.payment_state')
    def _compute_payment_info(self):
        for record in self:
            invoices = record.invoice_ids.filtered(lambda i: i.state == 'posted')
            if not invoices:
                record.total_invoiced = 0
                record.total_paid = 0
                record.payment_progress = 0
                record.payment_state = 'not_invoiced'
            else:
                record.total_invoiced = sum(invoices.mapped('amount_total'))
                record.total_paid = sum(invoices.mapped('amount_total')) - sum(invoices.mapped('amount_residual'))
                
                if record.total_invoiced > 0:
                    record.payment_progress = (record.total_paid / record.total_invoiced) * 100
                else:
                    record.payment_progress = 0
                
                # Determine payment state
                if record.total_paid == 0:
                    record.payment_state = 'not_paid'
                elif record.total_paid < record.total_invoiced:
                    record.payment_state = 'partial'
                else:
                    record.payment_state = 'paid'

    def action_confirm(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_("Only draft commissions can be confirmed."))
            record.state = 'confirmed'

    def action_cancel(self):
        for record in self:
            if record.invoice_ids:
                raise UserError(_("Cannot cancel a commission that has been invoiced."))
            record.state = 'cancelled'

    def action_draft(self):
        for record in self:
            if record.state != 'cancelled':
                raise UserError(_("Only cancelled commissions can be reset to draft."))
            record.state = 'draft'

    def action_generate_customer_invoice(self):
        self.ensure_one()
        if not self.seller_id:
            raise UserError(_("Please specify a seller/broker before generating an invoice."))
        if not self.property_sale_id.property_id.revenue_account_id:
            raise UserError(_("No revenue account defined on the property."))

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.seller_id.id,
            'invoice_date': fields.Date.context_today(self),
            'invoice_line_ids': [(0, 0, {
                'name': f"Broker Commission for {self.property_sale_id.name}",
                'quantity': 1,
                'price_unit': self.commission_amount,
                'account_id': self.property_sale_id.property_id.revenue_account_id.id,
            })],
            'broker_commission_id': self.id,
            'property_order_id': self.property_sale_id.id,
        }

        # If this commission is related to an offer, link it
        if self.property_offer_id:
            invoice_vals['property_offer_id'] = self.property_offer_id.id

        invoice = self.env['account.move'].create(invoice_vals)
        self.write({
            'invoice_ids': [(4, invoice.id)],
            'state': 'invoiced'
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_invoices(self):
        self.ensure_one()
        if not self.invoice_ids:
            raise UserError(_("No invoices found for this commission."))
            
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoices'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.invoice_ids.ids)],
            'target': 'current',
        }
        
    def action_view_property_sale(self):
        """View related property sale"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Property Sale'),
            'res_model': 'property.sale',
            'res_id': self.property_sale_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
        
    def action_view_property_offer(self):
        """View related property offer"""
        self.ensure_one()
        if not self.property_offer_id:
            raise UserError(_("No property offer linked to this commission."))
            
        return {
            'type': 'ir.actions.act_window',
            'name': _('Property Offer'),
            'res_model': 'property.sale.offer',
            'res_id': self.property_offer_id.id,
            'view_mode': 'form',
            'target': 'current',
        }