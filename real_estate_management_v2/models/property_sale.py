from odoo import api, fields, models, _
from datetime import datetime

class PropertySale(models.Model):
    _name = 'property.sale'
    _description = 'Property Sale'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    # Constants for state values
    STATE_DRAFT = 'draft'
    STATE_CONFIRMED = 'confirmed'
    STATE_CANCELLED = 'cancelled'
    STATE_COMPLETED = 'completed'
    
    name = fields.Char(string='Reference', readonly=True, copy=False, default=lambda self: _('New'))
    property_id = fields.Many2one('property.property', string='Property', required=True, tracking=True)
    offer_id = fields.Many2one('property.offer', string='Accepted Offer', required=True, tracking=True)
    partner_id = fields.Many2one(related='offer_id.partner_id', string='Customer', store=True)
    user_id = fields.Many2one(related='offer_id.user_id', string='Salesperson', store=True)
    sale_date = fields.Date(string='Sale Date', default=fields.Date.today, tracking=True)
    
    # Financial details
    sale_price = fields.Monetary(related='offer_id.offer_price', string='Sale Price', store=True)
    currency_id = fields.Many2one(related='property_id.currency_id', string='Currency', readonly=True)
    payment_option = fields.Selection(related='offer_id.payment_option', string='Payment Option', store=True)
    
    # Status tracking
    state = fields.Selection([
        (STATE_DRAFT, 'Draft'),
        (STATE_CONFIRMED, 'Confirmed'),
        (STATE_CANCELLED, 'Cancelled'),
        (STATE_COMPLETED, 'Completed')
    ], string='Status', default=STATE_DRAFT, tracking=True)
    
    # Commission related fields
    commission_ids = fields.One2many('internal.commission', 'sale_id', string='Commissions')
    commission_count = fields.Integer(compute='_compute_commission_count', string='Commission Count')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('property.sale') or _('New')
        return super(PropertySale, self).create(vals)
    
    def _compute_commission_count(self):
        for record in self:
            record.commission_count = len(record.commission_ids)
    
    def action_confirm(self):
        self.ensure_one()
        self.state = self.STATE_CONFIRMED
        self.property_id.write({'state': 'sold'})
        
        # Auto-create commission if configured
        if self.env['ir.config_parameter'].sudo().get_param('real_estate_management_v2.auto_create_commission', False):
            self._create_internal_commission()
        
        return True
    
    def action_cancel(self):
        self.ensure_one()
        self.state = self.STATE_CANCELLED
        return True
    
    def action_complete(self):
        self.ensure_one()
        self.state = self.STATE_COMPLETED
        return True
    
    def _create_internal_commission(self):
        """Create internal commission based on configuration"""
        self.ensure_one()
        default_percentage = float(self.env['ir.config_parameter'].sudo().get_param(
            'real_estate_management_v2.default_commission_percentage', 2.0))
        
        commission_vals = {
            'name': _('New'),
            'sale_id': self.id,
            'property_id': self.property_id.id,
            'partner_id': self.partner_id.id,
            'user_id': self.user_id.id,
            'commission_type': 'percentage',
            'commission_percentage': default_percentage,
            'property_value': self.sale_price,
            'state': 'draft',
        }
        
        self.env['internal.commission'].create(commission_vals)
        def action_accept(self):
            self.ensure_one()
            
            # Check if property is available
            if self.property_id.state != 'available':
                raise models.ValidationError(_("Cannot accept offer for property that is not available."))
            
            # Create property sale
            sale_vals = {
                'name': _('New'),
                'property_id': self.property_id.id,
                'offer_id': self.id,
                'sale_date': fields.Date.today(),
            }
            
            sale = self.env['property.sale'].create(sale_vals)
            self.write({
                'state': self.STATE_ACCEPTED,
                'sale_id': sale.id
            })
            
            # Reject other offers for this property
            other_offers = self.env['property.offer'].search([
                ('property_id', '=', self.property_id.id),
                ('id', '!=', self.id),
                ('state', 'in', [self.STATE_DRAFT, self.STATE_SENT, self.STATE_NEGOTIATION])
            ])
            if other_offers:
                other_offers.write({'state': self.STATE_REJECTED})
            
            return True