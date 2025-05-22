from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class InternalCommission(models.Model):
    _name = 'internal.commission'
    _description = 'Internal Commission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Reference', default=lambda self: _('New'), readonly=True, copy=False, tracking=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id', store=True, readonly=True)
    position = fields.Selection([
        ('consultant', 'Consultant'),
        ('manager', 'Manager'),
        ('director', 'Director'),
        ('other', 'Other')
    ], string='Position', required=True, tracking=True)
    
    sale_value = fields.Float(string='Gross Sales Value', related='sale_order_id.amount_total', readonly=True, store=True)
    amount_untaxed = fields.Float(string='Untaxed Amount', related='sale_order_id.amount_untaxed', readonly=True, store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='sale_order_id.currency_id', readonly=True, store=True)
    
    percentage = fields.Float(string='Percentage', tracking=True, digits=(5, 2))
    commission_amount = fields.Monetary(string='Commission Amount', compute='_compute_commission_amount', 
                                        store=True, tracking=True, currency_field='currency_id')
    
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

    @api.depends('percentage', 'sale_value')
    def _compute_commission_amount(self):
        for record in self:
            record.commission_amount = record.sale_value * (record.percentage / 100)

    @api.constrains('percentage')
    def _check_percentage(self):
        for record in self:
            if record.percentage < 0 or record.percentage > 100:
                raise ValidationError(_("Percentage must be between 0 and 100."))

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

    @api.onchange('employee_id')
    def _onchange_employee(self):
        if self.employee_id:
            if self.employee_id.job_id:
                if 'consultant' in self.employee_id.job_id.name.lower():
                    self.position = 'consultant'
                elif 'manager' in self.employee_id.job_id.name.lower():
                    self.position = 'manager'
                elif 'director' in self.employee_id.job_id.name.lower():
                    self.position = 'director'
                else:
                    self.position = 'other'

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name} - {record.employee_id.name}"
            result.append((record.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('employee_id.name', operator, name)]
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

    @api.model
    def _read_group_position_ids(self, positions, domain, order):
        return [key for key, _ in self._fields['position'].selection]

    _group_by_full = {
        'position': _read_group_position_ids,
    }