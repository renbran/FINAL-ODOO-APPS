from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class InternalCommission(models.Model):
    _name = 'internal.commission'
    _description = 'Internal Commission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'display_name'

    # Basic fields
    property_sale_id = fields.Many2one('property.sale', string="Property Sale", required=True, tracking=True)
    sales_person_id = fields.Many2one('res.users', string="Sales Person", required=True, tracking=True)
    commission_percentage = fields.Float(string="Commission Percentage", digits=(5, 2), tracking=True)
    commission_amount = fields.Monetary(string="Commission Amount", currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one(related='property_sale_id.currency_id', string="Currency", readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    # Computed fields
    display_name = fields.Char(string="Reference", compute='_compute_display_name', store=True)
    property_name = fields.Char(related='property_sale_id.property_id.name', string="Property", store=True)
    customer_name = fields.Char(related='property_sale_id.partner_id.name', string="Customer", store=True)
    payment_date = fields.Date(string="Payment Date")
    payment_reference = fields.Char(string="Payment Reference")
    
    # State field
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string="State", default='draft', tracking=True)
    
    # Additional fields
    notes = fields.Text(string="Notes")
    approved_by = fields.Many2one('res.users', string="Approved By")
    approval_date = fields.Date(string="Approval Date")
    rejection_reason = fields.Text(string="Rejection Reason")
    
    # Computed methods
    @api.depends('property_sale_id', 'sales_person_id', 'create_date')
    def _compute_display_name(self):
        """Generate a readable display name"""
        for record in self:
            if record.property_sale_id and record.sales_person_id:
                record.display_name = f"INT-COM/{record.property_sale_id.name}/{record.sales_person_id.name}"
            else:
                record.display_name = f"New Internal Commission {record.id or ''}"
    
    # Onchange methods
    @api.onchange('property_sale_id')
    def _onchange_property_sale(self):
        """Update commission values when property sale changes"""
        for record in self:
            if record.property_sale_id:
                record.commission_percentage = record.property_sale_id.internal_commission_percentage
                record.commission_amount = (record.commission_percentage / 100.0) * record.property_sale_id.property_value
                if record.property_sale_id.sales_person_id:
                    # Default to property sale's sales person
                    record.sales_person_id = record.property_sale_id.sales_person_id

    # Action methods
    def action_confirm(self):
        """Confirm the internal commission"""
        for record in self:
            if record.state == 'draft':
                record.state = 'confirmed'
    
    def action_approve(self):
        """Approve the internal commission"""
        for record in self:
            if record.state == 'confirmed':
                record.write({
                    'state': 'approved',
                    'approved_by': self.env.user.id,
                    'approval_date': fields.Date.today()
                })
    
    def action_reject(self):
        """Reject the internal commission"""
        for record in self:
            if record.state in ['draft', 'confirmed']:
                record.state = 'rejected'
    
    def action_cancel(self):
        """Cancel the internal commission"""
        for record in self:
            if record.state in ['draft', 'confirmed', 'approved'] and not record.payment_date:
                record.state = 'cancelled'
            else:
                raise UserError(_("Cannot cancel a commission that has been paid."))

    def action_mark_as_paid(self):
        """Mark the commission as paid"""
        for record in self:
            if record.state == 'approved':
                record.write({
                    'state': 'paid',
                    'payment_date': fields.Date.today()
                })
            else:
                raise UserError(_("Only approved commissions can be marked as paid."))
                
    def action_draft(self):
        """Reset to draft state"""
        for record in self:
            if record.state in ['confirmed', 'rejected', 'cancelled']:
                record.state = 'draft'
            else:
                raise UserError(_("Cannot reset to draft a commission that is approved or paid."))
