from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class ExternalCommission(models.Model):
    _name = 'external.commission'
    _description = 'External Commission'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', default=lambda self: _('New'), readonly=True, tracking=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True, tracking=True)
    date = fields.Date(string='Date', default=fields.Date.today, tracking=True)
    
    # Source Values
    sale_value = fields.Monetary(string='Gross Sales Value', related='sale_order_id.amount_total', readonly=True, currency_field='currency_id')
    amount_untaxed = fields.Monetary(string='Untaxed Amount', related='sale_order_id.amount_untaxed', readonly=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='sale_order_id.currency_id', readonly=True, store=True)

    # Commission Type Options
    COMMISSION_TYPES = [
        ('sale_value', 'As per Sale Value Percentage'),
        ('gross_commission', 'As per Gross Commission Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    # Broker/Agency Fields
    broker_agency_id = fields.Many2one('res.partner', string='Broker/Agency Name', domain=[('is_broker_agency', '=', True)])
    broker_agency_commission_type = fields.Selection(COMMISSION_TYPES, string='Broker/Agency Commission Type')
    broker_agency_rate = fields.Float(string='Broker/Agency Rate (%)', digits=(5, 2))
    broker_agency_fixed = fields.Monetary(string='Broker/Agency Fixed Amount', currency_field='currency_id')
    broker_agency_total = fields.Monetary(string='Broker/Agency Total', compute='_compute_commission_amounts', store=True, currency_field='currency_id')

    # Cashback Fields
    cashback_id = fields.Many2one('res.partner', string='Cashback Name', domain=[('is_cashback_partner', '=', True)])
    cashback_commission_type = fields.Selection(COMMISSION_TYPES, string='Cashback Commission Type')
    cashback_rate = fields.Float(string='Cashback Rate (%)', digits=(5, 2))
    cashback_fixed = fields.Monetary(string='Cashback Fixed Amount', currency_field='currency_id')
    cashback_total = fields.Monetary(string='Cashback Total', compute='_compute_commission_amounts', store=True, currency_field='currency_id')

    # Referral Fields
    referral_id = fields.Many2one('res.partner', string='Referral Name', domain=[('is_referral_partner', '=', True)])
    referral_commission_type = fields.Selection(COMMISSION_TYPES, string='Referral Commission Type')
    referral_rate = fields.Float(string='Referral Rate (%)', digits=(5, 2))
    referral_fixed = fields.Monetary(string='Referral Fixed Amount', currency_field='currency_id')
    referral_total = fields.Monetary(string='Referral Total', compute='_compute_commission_amounts', store=True, currency_field='currency_id')

    # Other Fields
    other_id = fields.Many2one('res.partner', string='Other Name')
    other_commission_type = fields.Selection(COMMISSION_TYPES, string='Other Commission Type')
    other_rate = fields.Float(string='Other Rate (%)', digits=(5, 2))
    other_fixed = fields.Monetary(string='Other Fixed Amount', currency_field='currency_id')
    other_total = fields.Monetary(string='Other Total', compute='_compute_commission_amounts', store=True, currency_field='currency_id')

    total_commission = fields.Monetary(string='Total Commission', compute='_compute_total_commission', store=True, currency_field='currency_id')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('canceled', 'Canceled'),
    ], string='Status', default='draft', tracking=True)
    
    payment_date = fields.Date(string='Payment Date', tracking=True)
    payment_reference = fields.Char(string='Payment Reference', tracking=True)
    notes = fields.Text(string='Notes', tracking=True)

    @api.depends('sale_value', 'amount_untaxed',
                 'broker_agency_commission_type', 'broker_agency_rate', 'broker_agency_fixed',
                 'cashback_commission_type', 'cashback_rate', 'cashback_fixed',
                 'referral_commission_type', 'referral_rate', 'referral_fixed',
                 'other_commission_type', 'other_rate', 'other_fixed')
    def _compute_commission_amounts(self):
        for record in self:
            record.broker_agency_total = record._calculate_commission(
                record.broker_agency_commission_type, record.broker_agency_rate, record.broker_agency_fixed)
            record.cashback_total = record._calculate_commission(
                record.cashback_commission_type, record.cashback_rate, record.cashback_fixed)
            record.referral_total = record._calculate_commission(
                record.referral_commission_type, record.referral_rate, record.referral_fixed)
            record.other_total = record._calculate_commission(
                record.other_commission_type, record.other_rate, record.other_fixed)

    def _calculate_commission(self, commission_type, rate, fixed_amount):
        if commission_type == 'sale_value':
            return self.sale_value * (rate / 100)
        elif commission_type == 'gross_commission':
            return self.amount_untaxed * (rate / 100)
        elif commission_type == 'fixed':
            return fixed_amount
        return 0

    @api.depends('broker_agency_total', 'cashback_total', 'referral_total', 'other_total')
    def _compute_total_commission(self):
        for record in self:
            record.total_commission = sum([
                record.broker_agency_total,
                record.cashback_total,
                record.referral_total,
                record.other_total
            ])

    @api.constrains('total_commission', 'amount_untaxed')
    def _check_commission_allocation(self):
        for record in self:
            if record.total_commission > record.amount_untaxed:
                raise ValidationError(_("Total commission (%.2f) cannot exceed the untaxed amount (%.2f)!") 
                                      % (record.total_commission, record.amount_untaxed))

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('external.commission') or _('New')
        return super(ExternalCommission, self).create(vals)

    def action_confirm(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_("Only draft commissions can be confirmed."))
            record.write({'state': 'confirmed'})

    def action_pay(self):
        for record in self:
            if record.state != 'confirmed':
                raise UserError(_("Only confirmed commissions can be paid."))
            record.write({'state': 'paid', 'payment_date': fields.Date.today()})

    def action_cancel(self):
        for record in self:
            if record.state in ['paid']:
                raise UserError(_("Paid commissions cannot be cancelled."))
            record.write({'state': 'canceled'})

    def action_draft(self):
        for record in self:
            if record.state != 'canceled':
                raise UserError(_("Only canceled commissions can be reset to draft."))
            record.write({'state': 'draft'})