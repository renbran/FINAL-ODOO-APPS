from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class InternalCommission(models.Model):
    _name = 'internal.commission'
    _description = 'Internal Commission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

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
    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency', 
        related='sale_order_id.currency_id', 
        readonly=True, 
        store=True
    )
    sale_value = fields.Monetary(
        string='Gross Sales Value', 
        related='sale_order_id.amount_total', 
        readonly=True, 
        store=True, 
        currency_field='currency_id'
    )
    
    commission_type = fields.Selection([
        ('sale_percentage', 'Percentage of Sale Value'),
        ('total_percentage', 'Percentage of Total Sale Order'),
        ('fixed', 'Fixed Amount')
    ], string='Commission Type', required=True, default='sale_percentage', tracking=True)

    # Agent 1 fields
    agent1_id = fields.Many2one(
        'hr.employee', 
        string='Agent 1 Name', 
        tracking=True
    )
    agent1_rate = fields.Float(
        string='Agent 1 Rate (%)', 
        tracking=True, 
        digits=(5, 2)
    )
    agent1_fixed = fields.Monetary(
        string='Agent 1 Fixed Amount', 
        tracking=True, 
        currency_field='currency_id'
    )
    agent1_commission = fields.Monetary(
        string='Agent 1 Total Commission', 
        compute='_compute_commissions', 
        store=True, 
        tracking=True, 
        currency_field='currency_id'
    )

    # Agent 2 fields
    agent2_id = fields.Many2one(
        'hr.employee', 
        string='Agent 2 Name', 
        tracking=True
    )
    agent2_rate = fields.Float(
        string='Agent 2 Rate (%)', 
        tracking=True, 
        digits=(5, 2)
    )
    agent2_fixed = fields.Monetary(
        string='Agent 2 Fixed Amount', 
        tracking=True, 
        currency_field='currency_id'
    )
    agent2_commission = fields.Monetary(
        string='Agent 2 Total Commission', 
        compute='_compute_commissions', 
        store=True, 
        tracking=True, 
        currency_field='currency_id'
    )

    # Manager fields
    manager_id = fields.Many2one(
        'hr.employee', 
        string='Manager Name', 
        tracking=True
    )
    manager_rate = fields.Float(
        string='Manager Rate (%)', 
        tracking=True, 
        digits=(5, 2)
    )
    manager_fixed = fields.Monetary(
        string='Manager Fixed Amount', 
        tracking=True, 
        currency_field='currency_id'
    )
    manager_commission = fields.Monetary(
        string='Manager Total Commission', 
        compute='_compute_commissions', 
        store=True, 
        tracking=True, 
        currency_field='currency_id'
    )

    # Director fields
    director_id = fields.Many2one(
        'hr.employee', 
        string='Director Name', 
        tracking=True
    )
    director_rate = fields.Float(
        string='Director Rate (%)', 
        tracking=True, 
        digits=(5, 2)
    )
    director_fixed = fields.Monetary(
        string='Director Fixed Amount', 
        tracking=True, 
        currency_field='currency_id'
    )
    director_commission = fields.Monetary(
        string='Director Total Commission', 
        compute='_compute_commissions', 
        store=True, 
        tracking=True, 
        currency_field='currency_id'
    )

    total_commission = fields.Monetary(
        string='Total Commission', 
        compute='_compute_total_commission', 
        store=True, 
        tracking=True, 
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
    
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company, 
        required=True
    )
    create_date = fields.Datetime(
        string='Creation Date', 
        readonly=True, 
        default=fields.Datetime.now
    )
    create_uid = fields.Many2one(
        'res.users', 
        string='Created by', 
        readonly=True, 
        default=lambda self: self.env.user
    )

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
                record.agent1_commission = record.sale_value * (record.agent1_rate / 100) if record.agent1_rate else 0
                record.agent2_commission = record.sale_value * (record.agent2_rate / 100) if record.agent2_rate else 0
                record.manager_commission = record.sale_value * (record.manager_rate / 100) if record.manager_rate else 0
                record.director_commission = record.sale_value * (record.director_rate / 100) if record.director_rate else 0
            elif record.commission_type == 'total_percentage':
                total_rate = (record.agent1_rate or 0) + (record.agent2_rate or 0) + (record.manager_rate or 0) + (record.director_rate or 0)
                if total_rate > 0:
                    total_commission = record.sale_value * (total_rate / 100)
                    record.agent1_commission = total_commission * ((record.agent1_rate or 0) / total_rate)
                    record.agent2_commission = total_commission * ((record.agent2_rate or 0) / total_rate)
                    record.manager_commission = total_commission * ((record.manager_rate or 0) / total_rate)
                    record.director_commission = total_commission * ((record.director_rate or 0) / total_rate)
                else:
                    record.agent1_commission = record.agent2_commission = record.manager_commission = record.director_commission = 0
            else:  # fixed
                record.agent1_commission = record.agent1_fixed or 0
                record.agent2_commission = record.agent2_fixed or 0
                record.manager_commission = record.manager_fixed or 0
                record.director_commission = record.director_fixed or 0

    @api.depends('agent1_commission', 'agent2_commission', 'manager_commission', 'director_commission')
    def _compute_total_commission(self):
        for record in self:
            record.total_commission = sum([
                record.agent1_commission or 0,
                record.agent2_commission or 0,
                record.manager_commission or 0,
                record.director_commission or 0
            ])

    @api.constrains('agent1_rate', 'agent2_rate', 'manager_rate', 'director_rate')
    def _check_rates(self):
        for record in self:
            if record.commission_type in ['sale_percentage', 'total_percentage']:
                rates = [record.agent1_rate, record.agent2_rate, record.manager_rate, record.director_rate]
                for rate in rates:
                    if rate and (rate < 0 or rate > 100):
                        raise ValidationError(_("Commission rates must be between 0 and 100."))

    @api.constrains('total_commission', 'sale_value')
    def _check_total_commission(self):
        for record in self:
            if record.total_commission and record.sale_value and record.total_commission > record.sale_value:
                raise ValidationError(_("Total commission cannot exceed the sale value."))

    def action_confirm(self):
        """Confirm commission record"""
        for record in self:
            if record.state == 'draft':
                record.state = 'confirmed'

    def action_pay(self):
        """Mark commission as paid"""
        for record in self:
            if record.state == 'confirmed':
                record.write({
                    'state': 'paid',
                    'payment_date': fields.Date.today()
                })

    def action_cancel(self):
        """Cancel commission record"""
        for record in self:
            if record.state in ['draft', 'confirmed']:
                record.state = 'canceled'

    def action_reset_to_draft(self):
        """Reset commission to draft"""
        for record in self:
            if record.state == 'canceled':
                record.write({
                    'state': 'draft',
                    'payment_date': False,
                    'payment_reference': False
                })

    def name_get(self):
        """Custom name display"""
        result = []
        for record in self:
            if record.sale_order_id:
                name = f"{record.name} - {record.sale_order_id.name}"
            else:
                name = record.name
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
        """Prevent deletion of non-draft records"""
        for record in self:
            if record.state not in ('draft', 'canceled'):
                raise ValidationError(_("You can only delete draft or canceled commissions."))
        return super(InternalCommission, self).unlink()

    def copy(self, default=None):
        """Custom copy method"""
        default = dict(default or {})
        default.update({
            'name': _('Copy of %s') % self.name,
            'state': 'draft',
            'payment_date': False,
            'payment_reference': False,
        })
        return super(InternalCommission, self).copy(default)

    def write(self, vals):
        """Override write to handle automatic payment date"""
        if 'state' in vals and vals['state'] == 'paid' and 'payment_date' not in vals:
            vals['payment_date'] = fields.Date.today()
        return super(InternalCommission, self).write(vals)