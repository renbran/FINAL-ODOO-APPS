from odoo import models, fields, api

class CustomSalesOrder(models.Model):
    _inherit = 'sale.order'

    custom_field_1 = fields.Char(string="Custom Field 1")
    custom_field_2 = fields.Integer(string="Custom Field 2")
    custom_field_3 = fields.Many2one('res.partner', string="Custom Field 3")

    def create(self, vals):
        # Custom logic for custom_field_1 on create
        if 'custom_field_1' in vals:
            vals['custom_field_1'] = vals['custom_field_1'].upper()  # Example logic
        return super().create(vals)

    def write(self, vals):
        # Custom logic for custom_field_1 on write
        if 'custom_field_1' in vals:
            vals['custom_field_1'] = vals['custom_field_1'].upper()  # Example logic
        return super().write(vals)
