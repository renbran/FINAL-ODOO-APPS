from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PropertyDashboard(models.Model):
    _name = 'property.dashboard'
    _description = 'Property Dashboard'
    _auto = False  # This tells Odoo that this is a database view
    
    name = fields.Char(string='Name')
    property_id = fields.Many2one('property.property', string='Property')
    project_name = fields.Char(string='Project')
    property_type = fields.Char(string='Type')
    state = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('booked', 'Booked'),
        ('sold', 'Sold')
    ], string='Status')
    sale_rent = fields.Selection([
        ('for_sale', 'For Sale'),
        ('for_rent', 'For Rent'),
    ], string='Sale or Rent')
    property_price = fields.Monetary(string='Property Price', currency_field='currency_id')
    total_sqft = fields.Float(string='Total Sqft')
    payment_progress = fields.Float(string='Payment Progress %')
    partner_id = fields.Many2one('res.partner', string='Customer')
    sales_count = fields.Integer(string='Sales Count')
    active_sale_id = fields.Many2one('property.sale', string='Active Sale')
    company_id = fields.Many2one('res.company', string='Company')
    currency_id = fields.Many2one('res.currency', string='Currency')
    
    def init(self):
        tools = self.env['ir.module.module']._get_module_path('property_sale_management')
        if not tools:
            return
            
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW property_dashboard AS (
                SELECT
                    p.id AS id,
                    p.id AS property_id,
                    p.name AS name,
                    p.project_name AS project_name,
                    p.property_type AS property_type,
                    p.state AS state,
                    p.sale_rent AS sale_rent,
                    p.property_price AS property_price,
                    p.total_sqft AS total_sqft,
                    p.payment_progress AS payment_progress,
                    p.partner_id AS partner_id,
                    p.sale_count AS sales_count,
                    p.active_sale_id AS active_sale_id,
                    p.company_id AS company_id,
                    p.currency_id AS currency_id
                FROM
                    property_property p
            )
        """)

    def action_view_property(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property',
            'res_model': 'property.property',
            'view_mode': 'form',
            'res_id': self.property_id.id,
            'target': 'current',
        }
        
    def action_view_active_sale(self):
        self.ensure_one()
        if not self.active_sale_id:
            raise UserError(_('No active sale found for this property.'))
            
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Sale',
            'res_model': 'property.sale',
            'view_mode': 'form',
            'res_id': self.active_sale_id.id,
            'target': 'current',
        }