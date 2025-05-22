from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class BrokerCommissionInvoice(models.Model):
    _name = 'broker.commission.invoice'
    _description = 'Broker Commission Invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'display_name'

    # Basic fields
    property_sale_id = fields.Many2one('property.sale', string="Property Sale", required=True, tracking=True)
    seller_id = fields.Many2one('res.partner', string="Seller/Broker", required=True, 
                              domain=[('is_company', '=', True)],
                              help="The seller/broker who will receive the commission",
                              tracking=True)
    commission_percentage = fields.Float(string="Commission Percentage", digits=(5, 2), tracking=True)
    commission_amount = fields.Monetary(string="Commission Amount", currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one(related='property_sale_id.currency_id', string="Currency", readonly=True)
    invoice_id = fields.Many2one('account.move', string="Invoice", readonly=True)
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
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string="State", default='draft', tracking=True)
    
    # Computed methods
    @api.depends('property_sale_id', 'seller_id', 'create_date')
    def _compute_display_name(self):
        """Generate a readable display name"""
        for record in self:
            if record.property_sale_id and record.seller_id:
                record.display_name = f"COM/{record.property_sale_id.name}/{record.seller_id.name}"
            else:
                record.display_name = f"New Commission {record.id or ''}"
    
    # Onchange methods
    @api.onchange('property_sale_id')
    def _onchange_property_sale(self):
        """Update commission values when property sale changes"""
        for record in self:
            if record.property_sale_id:
                record.commission_percentage = record.property_sale_id.broker_commission_percentage
                record.commission_amount = (record.commission_percentage / 100.0) * record.property_sale_id.property_value
                if record.property_sale_id.seller_name:
                    # Default to property's seller/broker
                    record.seller_id = record.property_sale_id.seller_name

    # Action methods
    def action_confirm(self):
        """Confirm the broker commission"""
        for record in self:
            if record.state == 'draft':
                record.state = 'confirmed'
    
    def action_cancel(self):
        """Cancel the broker commission"""
        for record in self:
            if record.state in ['draft', 'confirmed'] and not record.invoice_id:
                record.state = 'cancelled'
            else:
                raise UserError(_("Cannot cancel a commission that has been invoiced."))

    def action_mark_as_paid(self):
        """Mark the commission as paid"""
        for record in self:
            if record.state == 'invoiced':
                record.write({
                    'state': 'paid',
                    'payment_date': fields.Date.today()
                })
            else:
                raise UserError(_("Only invoiced commissions can be marked as paid."))

    def action_generate_customer_invoice(self):
        """Generate a customer invoice for the broker commission."""
        self.ensure_one()
        if self.invoice_id:
            raise UserError(_("An invoice already exists for this commission."))
            
        if not self.seller_id:
            raise UserError(_("Please specify a seller/broker before generating an invoice."))

        if not self.property_sale_id.property_id.revenue_account_id:
            raise UserError(_("No revenue account defined on the property. Please set it before generating an invoice."))
            
        # Create the invoice with the seller as the partner
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.seller_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': f"Broker Commission for {self.property_sale_id.name} - {self.property_sale_id.property_id.name}",
                'quantity': 1,
                'price_unit': self.commission_amount,
                'account_id': self.property_sale_id.property_id.revenue_account_id.id,
            })],
            'property_order_id': self.property_sale_id.id,
        }
        
        invoice = self.env['account.move'].create(invoice_vals)

        # Link the invoice to the broker commission record
        self.invoice_id = invoice.id

        # Update the state to 'invoiced'
        self.state = 'invoiced'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }
        
    def action_view_invoice(self):
        """View the related invoice"""
        self.ensure_one()
        if not self.invoice_id:
            raise UserError(_("No invoice exists for this commission."))
            
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
            'target': 'current',
        }