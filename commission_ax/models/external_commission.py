from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class ExternalCommission(models.Model):
    _name = 'external.commission'
    _description = 'External Commission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Reference', 
        default=lambda self: _('New'), 
        readonly=True, 
        copy=False,
        tracking=True
    )
    sale_order_id = fields.Many2one(
        'sale.order', 
        string='Sale Order', 
        required=True, 
        tracking=True,
        ondelete='cascade'
    )
    date = fields.Date(
        string='Date', 
        default=fields.Date.today, 
        tracking=True,
        required=True
    )
    
    # Source Values
    sale_value = fields.Monetary(
        string='Gross Sales Value', 
        related='sale_order_id.amount_total', 
        readonly=True, 
        currency_field='currency_id',
        store=True
    )
    amount_untaxed = fields.Monetary(
        string='Untaxed Amount', 
        related='sale_order_id.amount_untaxed', 
        readonly=True, 
        currency_field='currency_id',
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency', 
        related='sale_order_id.currency_id', 
        readonly=True, 
        store=True
    )

    # Commission Type Options
    COMMISSION_TYPES = [
        ('sale_value', 'As per Sale Value Percentage'),
        ('gross_commission', 'As per Gross Commission Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    # Broker/Agency Fields
    broker_agency_id = fields.Many2one(
        'res.partner', 
        string='Broker/Agency Name', 
        domain=[('is_broker_agency', '=', True)],
        tracking=True
    )
    broker_agency_commission_type = fields.Selection(
        COMMISSION_TYPES, 
        string='Broker/Agency Commission Type',
        tracking=True
    )
    broker_agency_rate = fields.Float(
        string='Broker/Agency Rate (%)', 
        digits=(5, 2),
        tracking=True
    )
    broker_agency_fixed = fields.Monetary(
        string='Broker/Agency Fixed Amount', 
        currency_field='currency_id',
        tracking=True
    )
    broker_agency_total = fields.Monetary(
        string='Broker/Agency Total', 
        compute='_compute_commission_amounts', 
        store=True, 
        currency_field='currency_id'
    )

    # Cashback Fields
    cashback_id = fields.Many2one(
        'res.partner', 
        string='Cashback Name', 
        domain=[('is_cashback_partner', '=', True)],
        tracking=True
    )
    cashback_commission_type = fields.Selection(
        COMMISSION_TYPES, 
        string='Cashback Commission Type',
        tracking=True
    )
    cashback_rate = fields.Float(
        string='Cashback Rate (%)', 
        digits=(5, 2),
        tracking=True
    )
    cashback_fixed = fields.Monetary(
        string='Cashback Fixed Amount', 
        currency_field='currency_id',
        tracking=True
    )
    cashback_total = fields.Monetary(
        string='Cashback Total', 
        compute='_compute_commission_amounts', 
        store=True, 
        currency_field='currency_id'
    )

    # Referral Fields
    referral_id = fields.Many2one(
        'res.partner', 
        string='Referral Name', 
        domain=[('is_referral_partner', '=', True)],
        tracking=True
    )
    referral_commission_type = fields.Selection(
        COMMISSION_TYPES, 
        string='Referral Commission Type',
        tracking=True
    )
    referral_rate = fields.Float(
        string='Referral Rate (%)', 
        digits=(5, 2),
        tracking=True
    )
    referral_fixed = fields.Monetary(
        string='Referral Fixed Amount', 
        currency_field='currency_id',
        tracking=True
    )
    referral_total = fields.Monetary(
        string='Referral Total', 
        compute='_compute_commission_amounts', 
        store=True, 
        currency_field='currency_id'
    )

    # Other Fields
    other_id = fields.Many2one(
        'res.partner', 
        string='Other Name',
        tracking=True
    )
    other_commission_type = fields.Selection(
        COMMISSION_TYPES, 
        string='Other Commission Type',
        tracking=True
    )
    other_rate = fields.Float(
        string='Other Rate (%)', 
        digits=(5, 2),
        tracking=True
    )
    other_fixed = fields.Monetary(
        string='Other Fixed Amount', 
        currency_field='currency_id',
        tracking=True
    )
    other_total = fields.Monetary(
        string='Other Total', 
        compute='_compute_commission_amounts', 
        store=True, 
        currency_field='currency_id'
    )

    total_commission = fields.Monetary(
        string='Total Commission', 
        compute='_compute_total_commission', 
        store=True, 
        currency_field='currency_id'
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('canceled', 'Canceled'),
    ], string='Status', default='draft', tracking=True, required=True)
    
    payment_date = fields.Date(string='Payment Date', tracking=True)
    payment_reference = fields.Char(string='Payment Reference', tracking=True)
    notes = fields.Text(string='Notes', tracking=True)
    
    # Additional fields for better tracking
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company, 
        required=True
    )

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
        """Calculate commission based on type and rate/amount"""
        if commission_type == 'sale_value':
            return self.sale_value * (rate / 100) if rate else 0
        elif commission_type == 'gross_commission':
            return self.amount_untaxed * (rate / 100) if rate else 0
        elif commission_type == 'fixed':
            return fixed_amount or 0
        return 0

    @api.depends('broker_agency_total', 'cashback_total', 'referral_total', 'other_total')
    def _compute_total_commission(self):
        for record in self:
            record.total_commission = sum([
                record.broker_agency_total or 0,
                record.cashback_total or 0,
                record.referral_total or 0,
                record.other_total or 0
            ])

    @api.constrains('total_commission', 'amount_untaxed')
    def _check_commission_allocation(self):
        for record in self:
            if record.total_commission and record.amount_untaxed and record.total_commission > record.amount_untaxed:
                raise ValidationError(
                    _("Total commission (%.2f) cannot exceed the untaxed amount (%.2f)!") 
                    % (record.total_commission, record.amount_untaxed)
                )

    @api.constrains('broker_agency_rate', 'cashback_rate', 'referral_rate', 'other_rate')
    def _check_commission_rates(self):
        for record in self:
            rates = [record.broker_agency_rate, record.cashback_rate, record.referral_rate, record.other_rate]
            for rate in rates:
                if rate and (rate < 0 or rate > 100):
                    raise ValidationError(_("Commission rates must be between 0 and 100."))

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('external.commission') or _('New')
        return super(ExternalCommission, self).create(vals)

    def action_confirm(self):
        """Confirm commission record"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_("Only draft commissions can be confirmed."))
            record.state = 'confirmed'

    def action_pay(self):
        """Mark commission as paid"""
        for record in self:
            if record.state != 'confirmed':
                raise UserError(_("Only confirmed commissions can be paid."))
            record.write({
                'state': 'paid', 
                'payment_date': fields.Date.today()
            })

    def action_cancel(self):
        """Cancel commission record"""
        for record in self:
            if record.state == 'paid':
                raise UserError(_("Paid commissions cannot be cancelled."))
            record.state = 'canceled'

    def action_draft(self):
        """Reset commission to draft"""
        for record in self:
            if record.state != 'canceled':
                raise UserError(_("Only canceled commissions can be reset to draft."))
            record.write({
                'state': 'draft',
                'payment_date': False,
                'payment_reference': False
            })

    def name_get(self):
        """Custom name display"""
        result = []
        for record in self:
            name = f"{record.name} - {record.sale_order_id.name}" if record.sale_order_id else record.name
            result.append((record.id, name))
        return result

    def unlink(self):
        """Prevent deletion of non-draft records"""
        for record in self:
            if record.state not in ('draft', 'canceled'):
                raise ValidationError(_("You can only delete draft or canceled commissions."))
        return super(ExternalCommission, self).unlink()