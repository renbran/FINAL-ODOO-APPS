from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class InternalCommission(models.Model):
    _name = 'internal.commission'
    _description = 'Internal Commission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Reference', default=lambda self: _('New'), readonly=True, copy=False, tracking=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='sale_order_id.currency_id', readonly=True, store=True)
    sale_value = fields.Monetary(string='Gross Sales Value', related='sale_order_id.amount_total', readonly=True, store=True, currency_field='currency_id')
    
    commission_type = fields.Selection([
        ('sale_percentage', 'Percentage of Sale Value'),
        ('total_percentage', 'Percentage of Total Sale Order'),
        ('fixed', 'Fixed Amount')
    ], string='Commission Type', required=True, default='sale_percentage', tracking=True)

    # Agent 1 fields
    agent1_id = fields.Many2one('hr.employee', string='Agent 1 Name', tracking=True)
    agent1_rate = fields.Float(string='Agent 1 Rate (%)', tracking=True, digits=(5, 2))
    agent1_fixed = fields.Monetary(string='Agent 1 Fixed Amount', tracking=True, currency_field='currency_id')
    agent1_commission = fields.Monetary(string='Agent 1 Total Commission', compute='_compute_commissions', store=True, tracking=True, currency_field='currency_id')

    # Agent 2 fields
    agent2_id = fields.Many2one('hr.employee', string='Agent 2 Name', tracking=True)
    agent2_rate = fields.Float(string='Agent 2 Rate (%)', tracking=True, digits=(5, 2))
    agent2_fixed = fields.Monetary(string='Agent 2 Fixed Amount', tracking=True, currency_field='currency_id')
    agent2_commission = fields.Monetary(string='Agent 2 Total Commission', compute='_compute_commissions', store=True, tracking=True, currency_field='currency_id')

    # Manager fields
    manager_id = fields.Many2one('hr.employee', string='Manager Name', tracking=True)
    manager_rate = fields.Float(string='Manager Rate (%)', tracking=True, digits=(5, 2))
    manager_fixed = fields.Monetary(string='Manager Fixed Amount', tracking=True, currency_field='currency_id')
    manager_commission = fields.Monetary(string='Manager Total Commission', compute='_compute_commissions', store=True, tracking=True, currency_field='currency_id')

    # Director fields
    director_id = fields.Many2one('hr.employee', string='Director Name', tracking=True)
    director_rate = fields.Float(string='Director Rate (%)', tracking=True, digits=(5, 2))
    director_fixed = fields.Monetary(string='Director Fixed Amount', tracking=True, currency_field='currency_id')
    director_commission = fields.Monetary(string='Director Total Commission', compute='_compute_commissions', store=True, tracking=True, currency_field='currency_id')

    total_commission = fields.Monetary(string='Total Commission', compute='_compute_total_commission', store=True, tracking=True, currency_field='currency_id')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('canceled', 'Canceled'),
    ], string='Status', default='draft', tracking=True)

    payment_date = fields.Date(string='Payment Date', tracking=True)
    payment_reference = fields.Char(string='Payment Reference', tracking=True)
    notes = fields.Text(string='Notes', tracking=True)
    
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    create_date = fields.Datetime(string='Creation Date', readonly=True, default=fields.Datetime.now)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True, default=lambda self: self.env.user)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('internal.commission') or _('New')
        return super(InternalCommission, self).create(vals)

    @api.depends('sale_value', 'commission_type', 
                 'agent1_rate', 'agent1_fixed',
                 'agent2_rate', 'agent2_fixed',
                 'manager_rate', 'manager_fixed',
                 'director_rate', 'director_fixed')
    def _compute_commissions(self):
        for record in self:
            if record.commission_type == 'sale_percentage':
                record.agent1_commission = record.sale_value * (record.agent1_rate / 100)
                record.agent2_commission = record.sale_value * (record.agent2_rate / 100)
                record.manager_commission = record.sale_value * (record.manager_rate / 100)
                record.director_commission = record.sale_value * (record.director_rate / 100)
            elif record.commission_type == 'total_percentage':
                total_rate = record.agent1_rate + record.agent2_rate + record.manager_rate + record.director_rate
                total_commission = record.sale_value * (total_rate / 100)
                record.agent1_commission = total_commission * (record.agent1_rate / total_rate) if total_rate else 0
                record.agent2_commission = total_commission * (record.agent2_rate / total_rate) if total_rate else 0
                record.manager_commission = total_commission * (record.manager_rate / total_rate) if total_rate else 0
                record.director_commission = total_commission * (record.director_rate / total_rate) if total_rate else 0
            else:  # fixed
                record.agent1_commission = record.agent1_fixed
                record.agent2_commission = record.agent2_fixed
                record.manager_commission = record.manager_fixed
                record.director_commission = record.director_fixed

    @api.depends('agent1_commission', 'agent2_commission', 'manager_commission', 'director_commission')
    def _compute_total_commission(self):
        for record in self:
            record.total_commission = sum([
                record.agent1_commission,
                record.agent2_commission,
                record.manager_commission,
                record.director_commission
            ])

    @api.constrains('agent1_rate', 'agent2_rate', 'manager_rate', 'director_rate')
    def _check_rates(self):
        for record in self:
            if record.commission_type in ['sale_percentage', 'total_percentage']:
                for rate in [record.agent1_rate, record.agent2_rate, record.manager_rate, record.director_rate]:
                    if rate < 0 or rate > 100:
                        raise ValidationError(_("Commission rates must be between 0 and 100."))

    def action_confirm(self):
        for record in self:
            if record.state == 'draft':
                record.state = 'confirmed'

    def action_pay(self):
        for record in self:
            if record.state == 'confirmed':
                record.state = 'paid'
                record.payment_date = fields.Date.today()

    def action_cancel(self):
        for record in self:
            if record.state in ['draft', 'confirmed']:
                record.state = 'canceled'

    def action_reset_to_draft(self):
        for record in self:
            if record.state == 'canceled':
                record.state = 'draft'

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name} - {record.sale_order_id.name}"
            result.append((record.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('sale_order_id.name', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)

    def unlink(self):
        for record in self:
            if record.state not in ('draft', 'canceled'):
                raise ValidationError(_("You can only delete draft or canceled commissions."))
        return super(InternalCommission, self).unlink()

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': _('Copy of %s') % self.name,
            'state': 'draft',
            'payment_date': False,
            'payment_reference': False,
        })
        return super(InternalCommission, self).copy(default)

    def write(self, vals):
        if 'state' in vals and vals['state'] == 'paid' and 'payment_date' not in vals:
            vals['payment_date'] = fields.Date.today()
        return super(InternalCommission, self).write(vals)