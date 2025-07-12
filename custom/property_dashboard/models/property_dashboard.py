from odoo import models, fields, api
import json

class PropertyDashboard(models.Model):
    _name = 'property.dashboard'
    _description = 'Property Dashboard'

    name = fields.Char(string='Dashboard Name', required=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    
    # Metrics fields
    total_properties = fields.Integer(string='Total Properties', compute='_compute_property_metrics')
    available_properties = fields.Integer(string='Available Properties', compute='_compute_property_metrics')
    reserved_properties = fields.Integer(string='Reserved Properties', compute='_compute_property_metrics')
    sold_properties = fields.Integer(string='Sold Properties', compute='_compute_property_metrics')
    maintenance_properties = fields.Integer(string='Under Maintenance', compute='_compute_property_metrics')
    rented_properties = fields.Integer(string='Rented Properties', compute='_compute_property_metrics')
    total_value = fields.Float(string='Total Property Value', compute='_compute_property_metrics')
    avg_property_price = fields.Float(string='Average Property Price', compute='_compute_property_metrics')
    
    # Chart data stored as JSON
    property_status_chart = fields.Text(string='Property Status Chart Data', compute='_compute_charts')
    property_type_chart = fields.Text(string='Property Type Chart Data', compute='_compute_charts')
    sales_trend_chart = fields.Text(string='Sales Trend Chart Data', compute='_compute_charts')
    
    # Trending properties
    trending_property_ids = fields.Many2many('property.property', string='Trending Properties', 
                                            compute='_compute_trending_properties')
    
    @api.depends('user_id')
    def _compute_property_metrics(self):
        for record in self:
            # Calculate total properties
            properties = self.env['property.property'].search([])
            record.total_properties = len(properties)
            
            # Calculate available properties (new status)
            record.available_properties = self.env['property.property'].search_count([('status', '=', 'new')])
            
            # Calculate reserved properties
            record.reserved_properties = self.env['property.property'].search_count([('status', '=', 'reserved')])
            
            # Calculate sold properties
            record.sold_properties = self.env['property.property'].search_count([('status', '=', 'sold')])
            
            # Calculate maintenance properties
            record.maintenance_properties = self.env['property.property'].search_count([('status', '=', 'under_maintenance')])
            
            # Calculate rented properties
            record.rented_properties = self.env['property.property'].search_count([('status', '=', 'rented')])
            
            # Calculate total value (sum of all property prices)
            record.total_value = sum(properties.mapped('price'))
            
            # Calculate average property price
            record.avg_property_price = record.total_value / record.total_properties if record.total_properties else 0
    
    @api.depends('user_id')
    def _compute_charts(self):
        for record in self:
            # Property Status Chart
            status_counts = {}
            for status, label in dict(self.env['property.property']._fields['status'].selection).items():
                count = self.env['property.property'].search_count([('status', '=', status)])
                status_counts[label] = count
            
            record.property_status_chart = json.dumps({
                'labels': list(status_counts.keys()),
                'datasets': [{
                    'data': list(status_counts.values()),
                    'backgroundColor': ['#4dc9f6', '#f67019', '#f53794', '#537bc4', '#acc236']
                }]
            })
            
            # Property Type Chart
            property_types = self.env['property.type'].search([])
            type_data = {}
            for prop_type in property_types:
                count = self.env['property.property'].search_count([('property_type_id', '=', prop_type.id)])
                type_data[prop_type.name] = count
            
            record.property_type_chart = json.dumps({
                'labels': list(type_data.keys()),
                'datasets': [{
                    'data': list(type_data.values()),
                    'backgroundColor': ['#4dc9f6', '#f67019', '#f53794', '#537bc4', '#acc236', '#8c9f5e']
                }]
            })
            
            # Sample sales trend chart (you'd typically have a date field to track this properly)
            record.sales_trend_chart = json.dumps({
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'datasets': [{
                    'label': 'Sales',
                    'data': [0, 0, 0, 0, 0, 0],  # Placeholder data
                    'borderColor': '#4dc9f6',
                    'fill': False
                }]
            })
    
    @api.depends('user_id')
    def _compute_trending_properties(self):
        for record in self:
            # Get 5 most expensive properties as "trending" (you might have other criteria)
            trending = self.env['property.property'].search([('status', '=', 'new')], 
                                                            order='price desc', limit=5)
            record.trending_property_ids = [(6, 0, trending.ids)]