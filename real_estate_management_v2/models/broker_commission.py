from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class BrokerCommission(models.Model):
    _name = 'broker.commission'
    _description = 'Broker Commission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    property_sale_id = fields.Many2one('property.sale', string='Property Sale', required=True, ondelete='restrict', tracking=True)
    property_id = fields.Many2one('property.property', string='Property', related='property_sale_id.property_id', store=True, readonly=True)
    broker_id = fields.Many2one('res.partner', string='Broker', required=True, domain=[('is_broker', '=', True)], tracking=True)
    
    commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string='Commission Type', default='percentage', required=True, tracking=True)
    
    commission_percentage = fields.Float(string='Commission Percentage', digits=(5, 2), tracking=True)
    fixed_amount = fields.Monetary(string='Fixed Amount', currency_field='currency_id', tracking=True)
    commission_amount = fields.Monetary(string='Commission Amount', compute='_compute_commission_amount', store=True, currency_field='currency_id')
    
    sale_price = fields.Monetary(string='Sale Price', related='property_sale_id.sale_price', store=True, readonly=True, currency_field='currency_id')
    
    payment_date = fields.Date(string='Payment Date', tracking=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method', tracking=True)
    payment_reference = fields.Char(string='Payment Reference', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    notes = fields.Text(string='Notes')
    
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True, copy=False)
    invoice_state = fields.Selection(related='invoice_id.state', string='Invoice Status', readonly=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('broker.commission') or _('New')
        return super(BrokerCommission, self).create(vals)
    
    @api.depends('commission_type', 'commission_percentage', 'fixed_amount', 'sale_price')
    def _compute_commission_amount(self):
        for record in self:
            if record.commission_type == 'percentage' and record.commission_percentage and record.sale_price:
                record.commission_amount = (record.commission_percentage / 100.0) * record.sale_price
            elif record.commission_type == 'fixed' and record.fixed_amount:
                record.commission_amount = record.fixed_amount
            else:
                record.commission_amount = 0.0
    
    def action_confirm(self):
        for record in self:
            if record.state == 'draft':
                record.state = 'confirmed'
        return True
    
    def action_pay(self):
        for record in self:
            if record.state == 'confirmed':
                record.state = 'paid'
                record.payment_date = fields.Date.today()
        return True
    
    def action_cancel(self):
        for record in self:
            if record.state != 'paid':
                record.state = 'cancelled'
            else:
                raise UserError(_("Cannot cancel a paid commission. Please create a refund instead."))
        return True
    
    def action_draft(self):
        for record in self:
            if record.state == 'cancelled':
                record.state = 'draft'
        return True
    
    @api.constrains('commission_percentage')
    def _check_commission_percentage(self):
        for record in self:
            if record.commission_type == 'percentage' and (record.commission_percentage <= 0 or record.commission_percentage > 100):
                raise ValidationError(_("Commission percentage must be between 0 and 100."))
    
    @api.constrains('fixed_amount')
    def _check_fixed_amount(self):
        for record in self:
            if record.commission_type == 'fixed' and record.fixed_amount <= 0:
                raise ValidationError(_("Fixed commission amount must be positive."))
    
    def action_generate_report(self):
        """Generate broker commission report."""
        self.ensure_one()
        return {
            'type': 'ir.actions.report',
            'report_name': 'real_estate_management_v2.report_broker_commission',
            'report_type': 'qweb-pdf',
            'res_id': self.id,
        }
    
    def action_create_invoice(self):
        """Create vendor bill for broker commission."""
        self.ensure_one()
        if self.invoice_id:
            raise UserError(_("Invoice already exists for this commission."))
        
        if not self.broker_id.property_account_payable_id:
            raise UserError(_("Please set an account payable for this broker."))
        
        # Get expense account from settings
        expense_account_id = int(self.env['ir.config_parameter'].sudo().get_param(
            'real_estate_management_v2.broker_commission_expense_account_id', 'False'))
        if not expense_account_id:
            raise UserError(_("Please configure a broker commission expense account in settings."))
        
        invoice_vals = {
            'move_type': 'in_invoice',
            'partner_id': self.broker_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': f"Commission for {self.property_id.name} - {self.property_sale_id.name}",
                'quantity': 1,
                'price_unit': self.commission_amount,
                'account_id': expense_account_id,
            })],
            'ref': self.name,
        }
        
        invoice = self.env['account.move'].create(invoice_vals)
        self.invoice_id = invoice.id
        
        return {
            'name': _('Vendor Bill'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'type': 'ir.actions.act_window',
        }
    
    def action_view_invoice(self):
        """View related invoice."""
        self.ensure_one()
        if not self.invoice_id:
            raise UserError(_("No invoice exists for this commission."))
        
        return {
            'name': _('Vendor Bill'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'type': 'ir.actions.act_window',
        }