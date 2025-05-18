from odoo import http
from odoo.http import request

class PropertyFormController(http.Controller):

    @http.route('/property/property/<model("property.property"):property_id>', type='http', auth='user', website=True)
    def property_detail(self, property_id, **kw):
        """Display detailed information about a specific property"""
        return request.render('property_sale_management.property_detail_template', {
            'property': property_id,
        })

    @http.route('/property/api/properties', type='json', auth='user')
    def get_properties(self, **kw):
        """API endpoint to get properties as JSON"""
        properties = request.env['property.property'].search([])
        return {
            'properties': [{
                'id': prop.id,
                'name': prop.name,
                'street': prop.street,
                'city': prop.city,
                'state': prop.state_id.name if prop.state_id else '',
                'sale_price': prop.sale_price,
                'status': prop.status,
            } for prop in properties]
        }

    @http.route('/property/api/property/<int:property_id>', type='json', auth='user')
    def get_property(self, property_id, **kw):
        """API endpoint to get a specific property as JSON"""
        try:
            property = request.env['property.property'].browse(property_id).exists()
            if not property:
                return {'error': 'Property not found'}

            return {
                'id': property.id,
                'name': property.name,
                'street': property.street,
                'city': property.city,
                'state': property.state_id.name if property.state_id else '',
                'sale_price': property.sale_price,
                'status': property.status,
            }
        except Exception as e:
            return {'error': str(e)}

    @http.route('/property/dashboard', type='http', auth='user', website=True)
    def property_dashboard(self, **kw):
        """Display a dashboard with property statistics"""
        Property = request.env['property.property']
        total_properties = Property.search_count([])
        available_properties = Property.search_count([('status', '=', 'available')])
        sold_properties = Property.search_count([('status', '=', 'sold')])
        total_sales_value = sum(Property.search([('status', '=', 'sold')]).mapped('sale_price'))

        return request.render('property_sale_management.property_dashboard_template', {
            'total_properties': total_properties,
            'available_properties': available_properties,
            'sold_properties': sold_properties,
            'total_sales_value': total_sales_value,
        })

    @http.route('/property/api/search', type='json', auth='user')
    def search_properties(self, **kw):
        """API endpoint to search properties based on criteria"""
        domain = []
        fields = ['name', 'city', 'status', 'min_price', 'max_price']
        
        for field in fields:
            if kw.get(field):
                if field == 'min_price':
                    domain.append(('sale_price', '>=', float(kw.get(field))))
                elif field == 'max_price':
                    domain.append(('sale_price', '<=', float(kw.get(field))))
                else:
                    domain.append((field, 'ilike' if field != 'status' else '=', kw.get(field)))

        properties = request.env['property.property'].search(domain)
        return {
            'count': len(properties),
            'properties': [{
                'id': prop.id,
                'name': prop.name,
                'street': prop.street,
                'city': prop.city,
                'state': prop.state_id.name if prop.state_id else '',
                'sale_price': prop.sale_price,
                'status': prop.status,
            } for prop in properties]
        }