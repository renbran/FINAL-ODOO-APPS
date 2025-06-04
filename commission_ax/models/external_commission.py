from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class ExternalCommission(models.Model):
    _name = 'external.commission'
    _description = 'External Commission'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Main Fields
    name = fields.Char(string='Reference', default=lambda self: _('New'), readonly=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
    partner_id = fields.Many2one('res.partner', string='External Partner', required=True, domain=[('is_external_agent', '=', True)])
    date = fields.Date(string='Date', default=fields.Date.today)
    
    # FIXED: Currency field to support Monetary fields
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='sale_order_id.currency_id',
        store=True,
        readonly=True
    )
    
    # FIXED: Source Values - Changed from Float to Monetary
    sale_value = fields.Monetary(
        string='Gross Sales Value',
        currency_field='currency_id',
        related='sale_order_id.sale_value',
        store=True,
        readonly=True
    )
    amount_untaxed = fields.Monetary(
        string='Untaxed Amount',
        currency_field='currency_id',
        related='sale_order_id.amount_untaxed',
        store=True,
        readonly=True
    )
    
    # Calculation Type Options
    CALCULATION_TYPES = [
        ('sales_value', 'Percentage of Sales Value'),
        ('untaxed', 'Percentage of Total Untaxed'),
        ('fixed', 'Fixed Amount'),
    ]
    
    # Commission Details
    calculation_type = fields.Selection(
        CALCULATION_TYPES,
        string='Calculation Type',
        default='sales_value',
        required=True
    )
    percentage = fields.Float(
        string='Percentage',
        digits=(5, 2)
    )
    # FIXED: Changed from Float to Monetary
    fixed_amount = fields.Monetary(
        string='Fixed Amount',
        currency_field='currency_id'
    )
    # FIXED: Changed from Float to Monetary
    commission_amount = fields.Monetary(
        string='Commission Amount',
        currency_field='currency_id',
        compute='_compute_commission_amount',
        store=True
    )
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('canceled', 'Canceled'),
    ], string='Status', default='draft', tracking=True)
    
    # Payment Info
    payment_date = fields.Date(string='Payment Date')
    payment_reference = fields.Char(string='Payment Reference')
    
    # New Fields
    notes = fields.Text(string='Notes')
    commission_status = fields.Selection([
        ('under', 'Under Allocated'),
        ('over', 'Over Allocated'),
        ('full', 'Fully Allocated')
    ], string='Commission Status', compute='_compute_commission_status', store=True)

    # Constraints and Computations
    @api.depends('calculation_type', 'percentage', 'fixed_amount', 'sale_value', 'amount_untaxed')
    def _compute_commission_amount(self):
        for record in self:
            if record.calculation_type == 'sales_value':
                record.commission_amount = record.sale_value * (record.percentage / 100) if record.sale_value and record.percentage else 0.0
            elif record.calculation_type == 'untaxed':
                record.commission_amount = record.amount_untaxed * (record.percentage / 100) if record.amount_untaxed and record.percentage else 0.0
            else:
                record.commission_amount = record.fixed_amount or 0.0

    @api.depends('commission_amount', 'amount_untaxed')
    def _compute_commission_status(self):
        for record in self:
            if not record.amount_untaxed:
                record.commission_status = 'under'
            elif record.commission_amount < record.amount_untaxed:
                record.commission_status = 'under'
            elif record.commission_amount > record.amount_untaxed:
                record.commission_status = 'over'
            else:
                record.commission_status = 'full'
    
    @api.constrains('calculation_type', 'percentage', 'fixed_amount', 'amount_untaxed')
    def _check_commission_allocation(self):
        for record in self:
            if not record.amount_untaxed:
                continue
                
            allocated = 0.0
            if record.calculation_type == 'sales_value':
                allocated = (record.sale_value or 0.0) * (record.percentage / 100) if record.percentage else 0.0
            elif record.calculation_type == 'untaxed':
                allocated = (record.amount_untaxed or 0.0) * (record.percentage / 100) if record.percentage else 0.0
            else:
                allocated = record.fixed_amount or 0.0
            
            if allocated > record.amount_untaxed:
                raise ValidationError(_(
                    "Commission allocation (%.2f) cannot exceed the untaxed amount (%.2f)!"
                ) % (allocated, record.amount_untaxed))
    
    @api.onchange('calculation_type', 'percentage', 'fixed_amount')
    def _onchange_commission_values(self):
        if not self.amount_untaxed:
            return
        
        allocated = 0.0
        if self.calculation_type == 'sales_value':
            allocated = (self.sale_value or 0.0) * (self.percentage / 100) if self.percentage else 0.0
        elif self.calculation_type == 'untaxed':
            allocated = (self.amount_untaxed or 0.0) * (self.percentage / 100) if self.percentage else 0.0
        else:
            allocated = self.fixed_amount or 0.0
        
        remaining = self.amount_untaxed - allocated
        
        if remaining < 0:
            return {
                'warning': {
                    'title': _("Allocation Error"),
                    'message': _("This allocation would exceed the available amount!")
                }
            }
        elif remaining < (0.1 * self.amount_untaxed):
            return {
                'warning': {
                    'title': _("Allocation Warning"),
                    'message': _("You're using %.0f%% of the available amount (%.2f remaining)") % 
                             ((allocated/self.amount_untaxed)*100, remaining)
                }
            }
    
    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        """Update currency when sale order changes"""
        if self.sale_order_id:
            self.currency_id = self.sale_order_id.currency_id
    
    # Sequence Generation
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('external.commission') or _('New')
        
        # Ensure currency is set
        if vals.get('sale_order_id') and not vals.get('currency_id'):
            sale_order = self.env['sale.order'].browse(vals['sale_order_id'])
            if sale_order.currency_id:
                vals['currency_id'] = sale_order.currency_id.id
        
        return super(ExternalCommission, self).create(vals)

    # Action Methods
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