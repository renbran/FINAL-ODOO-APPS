from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PropertySaleLine(models.Model):
    _name = 'property.sale.line'
    _description = 'Property Sale Payment Line'
    _order = 'due_date, id'
    
    # Constants for state values
    STATE_PENDING = 'pending'
    STATE_PAID = 'paid'
    STATE_OVERDUE = 'overdue'
    
    sale_id = fields.Many2one('property.sale', string='Property Sale', required=True, ondelete='cascade')
    name = fields.Char(string='Description', required=True)
    due_date = fields.Date(string='Due Date', required=True)
    amount = fields.Monetary(string='Amount', required=True)
    currency_id = fields.Many2one(related='sale_id.currency_id', string='Currency', readonly=True)
    
    # Payment details
    payment_date = fields.Date(string='Payment Date')
    payment_reference = fields.Char(string='Payment Reference')
    
    # Line type flags
    is_down_payment = fields.Boolean(string='Is Down Payment', default=False)
    is_dld_fee = fields.Boolean(string='Is DLD Fee', default=False)
    is_admin_fee = fields.Boolean(string='Is Admin Fee', default=False)
    is_installment = fields.Boolean(string='Is Installment', default=False)
    
    # Status
    state = fields.Selection([
        (STATE_PENDING, 'Pending'),
        (STATE_PAID, 'Paid'),
        (STATE_OVERDUE, 'Overdue')
    ], string='Status', compute='_compute_state', store=True)
    
    notes = fields.Text(string='Notes')
    
    @api.depends('due_date', 'payment_date')
    def _compute_state(self):
        today = fields.Date.today()
        for record in self:
            if record.payment_date:
                record.state = record.STATE_PAID
            elif record.due_date < today:
                record.state = record.STATE_OVERDUE
            else:
                record.state = record.STATE_PENDING
    
    def action_mark_as_paid(self):
        """Mark the payment line as paid."""
        for record in self:
            if record.state == record.STATE_PAID:
                raise UserError(_("This payment is already marked as paid."))
            record.payment_date = fields.Date.today()
        return True