from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class Property(models.Model):
    _name = 'property.property'
    _description = 'Property Details'
    _order = 'name'
    
    # Constants for state values
    STATE_AVAILABLE = 'available'
    STATE_RESERVED = 'reserved'
    STATE_BOOKED = 'booked'
    STATE_SOLD = 'sold'

    name = fields.Char(string="Property Name", required=True)
    property_image = fields.Image("Property Image")
    floor_plan = fields.Image("Floor Plan")
    partner_id = fields.Many2one('res.partner', string="Partner")
    property_price = fields.Monetary(string="Property Price", required=True)
    revenue_account_id = fields.Many2one('account.account', string="Revenue Account", required=True, 
                                        default=lambda self: self.env['account.account'].search([('name', '=', 'Sales Account')], limit=1))
    address = fields.Text(string="Address")
    sale_rent = fields.Selection([
        ('for_sale', 'For Sale'),
        ('for_rent', 'For Rent'),
    ], string="Sale or Rent", required=True)
    state = fields.Selection([
        (STATE_AVAILABLE, 'Available'),
        (STATE_RESERVED, 'Reserved'),
        (STATE_BOOKED, 'Booked'),
        (STATE_SOLD, 'Sold')
    ], string="State", default=STATE_AVAILABLE, required=True)
    currency_id = fields.Many2one('res.currency', string="Currency", required=True, default=lambda self: self.env.company.currency_id)
    description = fields.Text(string="Description")
    
    property_sale_ids = fields.One2many('property.sale', 'property_id', string="Related Sales")
    sale_count = fields.Integer(string="Sale Count", compute="_compute_sale_count")
    
    # Payment tracking fields
    payment_progress = fields.Float(string="Payment Progress (%)", compute="_compute_payment_progress", store=True)
    total_invoiced = fields.Monetary(string="Total Invoiced", compute="_compute_payment_details", store=True)
    total_paid = fields.Monetary(string="Total Paid", compute="_compute_payment_details", store=True)
    remaining_amount = fields.Monetary(string="Remaining Amount", compute="_compute_payment_details", store=True)
    active_sale_id = fields.Many2one('property.sale', string="Active Sale", compute="_compute_active_sale")
    
    # Existing structural fields
    field_id = fields.Integer(string="ID")
    property_reference = fields.Char(string="Property Reference")
    status = fields.Char(string="Status", compute="_compute_status", store=True)
    tower = fields.Char(string="Tower")
    level = fields.Char(string="Level")
    project_name = fields.Char(string="Project Name", default="Sky Hills Astra")
    unit_no = fields.Char(string="Unit No")
    unit_view = fields.Char(string="Unit View")
    total_sqft = fields.Float(string="Total Sqft")
    price_per_sqft = fields.Float(string="Price / Sqft")
    total_sale_value = fields.Float(string="Total Sale Value", compute="_compute_total_sale_value", store=True)
    property_type = fields.Char(string="Type")
    
    @api.depends('state')
    def _compute_status(self):
        """Compute the status based on the state."""
        for record in self:
            if record.state == self.STATE_AVAILABLE:
                record.status = 'Available'
            elif record.state == self.STATE_RESERVED:
                record.status = 'Reserved'
            elif record.state == self.STATE_BOOKED:
                record.status = 'Booked'
            elif record.state == self.STATE_SOLD:
                record.status = 'Sold'
            else:
                record.status = 'Unknown'
    
    @api.depends('total_sqft', 'price_per_sqft')
    def _compute_total_sale_value(self):
        """Compute the total sale value based on square footage and price per square foot."""
        for record in self:
            record.total_sale_value = record.total_sqft * record.price_per_sqft
    
    @api.depends('property_sale_ids')
    def _compute_sale_count(self):
        """Compute the number of sales related to this property."""
        for record in self:
            record.sale_count = len(record.property_sale_ids)
    
    @api.depends('property_sale_ids')
    def _compute_active_sale(self):
        """Compute the active sale for this property."""
        for record in self:
            active_sales = record.property_sale_ids.filtered(lambda s: s.state in ['confirmed', 'invoiced'])
            record.active_sale_id = active_sales[0] if active_sales else False
    
    @api.depends('active_sale_id', 'active_sale_id.property_sale_line_ids', 
                 'active_sale_id.property_sale_line_ids.collection_status')
    def _compute_payment_progress(self):
        """Compute the payment progress based on paid installments."""
        for record in self:
            if record.active_sale_id:
                all_lines = record.active_sale_id.property_sale_line_ids
                if all_lines:
                    total_amount = sum(all_lines.mapped('capital_repayment'))
                    paid_amount = sum(all_lines.filtered(lambda l: l.collection_status == 'paid').mapped('capital_repayment'))
                    record.payment_progress = round((paid_amount / total_amount) * 100, 2) if total_amount > 0 else 0.0
                else:
                    record.payment_progress = 0.0
            else:
                record.payment_progress = 0.0
    
    @api.depends('active_sale_id', 'active_sale_id.property_sale_line_ids', 
                 'active_sale_id.property_sale_line_ids.collection_status',
                 'active_sale_id.sale_price')
    def _compute_payment_details(self):
        """Compute payment details (total invoiced, total paid, remaining amount)."""
        for record in self:
            if record.active_sale_id:
                all_lines = record.active_sale_id.property_sale_line_ids
                paid_amount = sum(all_lines.filtered(lambda l: l.collection_status == 'paid').mapped('capital_repayment'))
                record.total_invoiced = sum(all_lines.mapped('capital_repayment'))
                record.total_paid = paid_amount
                record.remaining_amount = record.active_sale_id.sale_price - paid_amount
            else:
                record.total_invoiced = 0.0
                record.total_paid = 0.0
                record.remaining_amount = 0.0
    
    @api.model
    def create(self, vals):
        """Override create to handle default values."""
        return super(Property, self).create(vals)
    
    def write(self, vals):
        """Override write to update property state and partner when sold."""
        res = super(Property, self).write(vals)
        if 'state' in vals and vals['state'] == self.STATE_SOLD:
            property_sale = self.env['property.sale'].search([('property_id', '=', self.id), ('state', '=', 'confirm')], limit=1)
            if property_sale and property_sale.partner_id:
                self.write({'partner_id': property_sale.partner_id.id})
        return res
    
    def action_create_sale(self):
        """Create a new property sale from the property."""
        self.ensure_one()
        sale = self.env['property.sale'].create({
            'name': f"{self.name} - Sale",
            'property_id': self.id,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'start_date': fields.Date.today(),
            'state': 'draft'
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Sale',
            'res_model': 'property.sale',
            'view_mode': 'form',
            'res_id': sale.id,
            'target': 'current',
        }

    def action_view_sales(self):
        """View all sales related to this property."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Sales',
            'res_model': 'property.sale',
            'view_mode': 'tree,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }