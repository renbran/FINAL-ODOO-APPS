# Odoo 17 Production-Ready Patterns

from odoo import api, fields, models, Command, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

class ProductionModel(models.Model):
    """Template for production-ready Odoo 17 models"""
    _name = 'example.model'
    _description = 'Example Model'
    _order = 'name'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # Private attributes
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Name must be unique'),
    ]
    
    # Default methods
    def _default_state(self):
        return 'draft'
    
    # Field declarations with proper attributes
    name = fields.Char(
        string='Name', 
        required=True, 
        tracking=True,
        help="Descriptive name for the record"
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], default=_default_state, tracking=True)
    
    line_ids = fields.One2many(
        'example.line', 'model_id', 
        string='Lines',
        copy=True
    )
    
    total_amount = fields.Float(
        string='Total Amount',
        compute='_compute_total_amount',
        store=True,
        readonly=True
    )
    
    # Compute methods
    @api.depends('line_ids.amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))
    
    # Constraints
    @api.constrains('line_ids')
    def _check_line_ids(self):
        for record in self:
            if not record.line_ids:
                raise ValidationError(_("At least one line is required."))
    
    # Onchange methods
    @api.onchange('state')
    def _onchange_state(self):
        if self.state == 'cancelled':
            return {'warning': {
                'title': _('Warning'),
                'message': _('This action cannot be undone.')
            }}
    
    # CRUD overrides
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' not in vals or not vals['name']:
                vals['name'] = self.env['ir.sequence'].next_by_code('example.model')
        return super().create(vals_list)
    
    def write(self, vals):
        if 'state' in vals and vals['state'] == 'done':
            self.message_post(body=_("Record confirmed"))
        return super().write(vals)
    
    # Action methods
    def action_confirm(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Only draft records can be confirmed"))
        self.state = 'confirmed'
        return True
    
    # Business methods
    def _get_computed_value(self):
        """Business logic method with proper documentation"""
        self.ensure_one()
        return self.line_ids.filtered(lambda x: x.active).mapped('value')