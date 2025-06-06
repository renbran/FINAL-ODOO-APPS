from odoo import models, fields, api

class PropertyProperty(models.Model):
    _name = 'property.property'
    _description = 'Property Monitoring System'
    _order = 'id desc'

    # Basic Information
    name = fields.Char(string='Property Name', required=True)
    status = fields.Selection([
        ('new', 'New'),
        ('rented', 'Rented'),
        ('sold', 'Sold'),
        ('under_maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved')
    ], string='Status', default='new', required=True)
    property_type_id = fields.Many2one('property.type', string='Property Type', required=True)
    location = fields.Char(string='Location', required=True)

    # Property Specifications
    bedrooms = fields.Integer(string='Bedrooms')
    bathrooms = fields.Integer(string='Bathrooms')
    area = fields.Float(string='Area (sqm)', digits=(6,2))
    garage = fields.Boolean(string='Garage')
    balcony = fields.Boolean(string='Balcony')
    pool = fields.Boolean(string='Pool')

    # Pricing Information
    price = fields.Float(string='Price', required=True)
    rental_price = fields.Float(string='Rental Price')
    sale_price = fields.Float(string='Sale Price')

    # Additional Information
    description = fields.Text(string='Description')
    image = fields.Binary(string='Property Image', attachment=True)
    last_inspection_date = fields.Date(string='Last Inspection Date')

    # Track Changes
    create_date = fields.Datetime('Created On', readonly=True)
    write_date = fields.Datetime('Last Updated', readonly=True)