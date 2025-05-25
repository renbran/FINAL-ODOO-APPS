from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class InternalCommission(models.Model):
    _name = 'internal.commission'
    _description = 'Internal Commission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    property_sale_id = fields.Many2one('property.sale', string='Property Sale', required=True, ondelete='restrict')
    property_id = fields.Many2one('property.property', string='Property', related='property_sale_id.property_id', store=True)
    user_id = fields.Many2one('res.users', string='Salesperson', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', related='property_sale_id.partner_id', store=True)
    
    commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string='Commission Type', default='percentage', required=True)
    
    commission_percentage = fields.Float(string='Commission Percentage', digits=(5, 2))
    fixed_amount = fields.Monetary(string='Fixed Amount', currency_field='currency_id')
    commission_amount = fields.Monetary(string='Commission Amount', compute='_compute_commission_amount', store=True, currency_field='currency_id')
    
    property_value = fields.Monetary(string='Property Value', currency_field='currency_id')
    sale_price = fields.Monetary(string='Sale Price', currency_field='currency_id')
    
    payment_date = fields.Date(string='Payment Date')
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method')
    payment_reference = fields.Char(string='Payment Reference')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    notes = fields.Text(string='Notes')
    
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('internal.commission') or _('New')
        return super(InternalCommission, self).create(vals)
    
    @api.depends('commission_type', 'commission_percentage', 'fixed_amount', 'property_value')
    def _compute_commission_amount(self):
        for record in self:
            if record.commission_type == 'percentage' and record.commission_percentage and record.property_value:
                record.commission_amount = (record.commission_percentage / 100) * record.property_value
            elif record.commission_type == 'fixed' and record.fixed_amount:
                record.commission_amount = record.fixed_amount
            else:
                record.commission_amount = 0.0
    
    def action_confirm(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_("Only draft commissions can be confirmed."))
            record.state = 'confirmed'
    
    def action_mark_as_paid(self):
        for record in self:
            if record.state != 'confirmed':
                raise UserError(_("Only confirmed commissions can be marked as paid."))
            if not record.payment_date:
                record.payment_date = fields.Date.today()
            record.state = 'paid'
    
    def action_cancel(self):
        for record in self:
            if record.state == 'paid':
                raise UserError(_("Paid commissions cannot be cancelled."))
            record.state = 'cancelled'
    
    def action_draft(self):
        for record in self:
            if record.state != 'cancelled':
                raise UserError(_("Only cancelled commissions can be reset to draft."))
            record.state = 'draft'
    
    @api.constrains('commission_percentage')
    def _check_commission_percentage(self):
        """Ensure commission percentage is valid."""
        for record in self:
            if record.commission_type == 'percentage' and (record.commission_percentage <= 0 or record.commission_percentage > 100):
                raise ValidationError(_("Commission percentage must be between 0 and 100."))
    
    @api.constrains('fixed_amount')
    def _check_fixed_amount(self):
        """Ensure fixed amount is valid."""
        for record in self:
            if record.commission_type == 'fixed' and record.fixed_amount <= 0:
                raise ValidationError(_("Fixed commission amount must be positive."))
                
    def action_generate_report(self):
        """Generate commission report."""
        self.ensure_one()
        return {
            'type': 'ir.actions.report',
            'report_name': 'real_estate_management_v2.report_internal_commission',
            'report_type': 'qweb-pdf',
            'res_id': self.id,
        }
    
    def action_send_by_email(self):
        """Send commission details by email."""
        self.ensure_one()
        template_id = self.env.ref('real_estate_management_v2.email_template_internal_commission').id
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        ctx = {
            'default_model': 'internal.commission',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
        }
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }