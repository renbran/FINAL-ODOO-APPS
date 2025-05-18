from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PropertyType(models.Model):
    _name = 'property.type'
    _description = 'Property Type'
    
    name = fields.Char(string='Type Name', required=True)
    code = fields.Char(string='Type Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
    
    # Pricing and size defaults
    default_price_per_sqft = fields.Float(string='Default Price per Sqft')
    min_sqft = fields.Float(string='Minimum Sqft')
    max_sqft = fields.Float(string='Maximum Sqft')
    
    # Properties of this type
    property_ids = fields.One2many('property.property', 'type_id', string='Properties')
    property_count = fields.Integer(string='Property Count', compute='_compute_property_count')
    
    @api.depends('property_ids')
    def _compute_property_count(self):
        for record in self:
            record.property_count = len(record.property_ids)
    
    @api.constrains('code')
    def _check_unique_code(self):
        for record in self:
            if record.code:
                duplicate = self.search([('code', '=', record.code), ('id', '!=', record.id)])
                if duplicate:
                    raise UserError(_('Property Type code must be unique! This code is already used by %s') % duplicate.name)
    
    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.code:
                name = f'[{record.code}] {name}'
            result.append((record.id, name))
        return result