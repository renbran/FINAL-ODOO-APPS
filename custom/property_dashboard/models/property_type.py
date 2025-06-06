from odoo import models, fields

class PropertyType(models.Model):
    _name = 'property.type'
    _description = 'Property Type'
    _order = 'name asc'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    
    # Count related properties
    property_count = fields.Integer(string='Property Count', compute='_compute_property_count')
    
    def _compute_property_count(self):
        for record in self:
            record.property_count = self.env['property.property'].search_count([
                ('property_type_id', '=', record.id)
            ])