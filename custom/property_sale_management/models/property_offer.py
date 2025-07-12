from odoo import api, fields, models

class PropertySaleOffer(models.Model):
    _name = 'property.sale.offer'
    _description = 'Property Sale Offer'

    name = fields.Char(string='Offer Reference', required=True, copy=False, readonly=True, default='New')
    property_id = fields.Many2one('property.property', string='Property', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    offer_price = fields.Monetary(string='Offer Price', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    offer_date = fields.Date(string='Offer Date', default=fields.Date.today)
    expiration_date = fields.Date(string='Expiration Date', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', required=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('property.sale.offer') or 'New'
        return super(PropertySaleOffer, self).create(vals)