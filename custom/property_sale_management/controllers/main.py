from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, MissingError

class PropertyFormController(http.Controller):

    @http.route('/property/property/<model("property.property"):property_id>', type='http', auth='user', website=True)
    def property_detail(self, property_id, **kw):
        try:
            property_sudo = property_id.sudo().exists()
            if not property_sudo:
                return request.redirect('/my')
            
            return request.render('property_sale_management.property_detail_template', {
                'property': property_sudo,
                'user': request.env.user,
            })
        except AccessError:
            return request.redirect('/my')

    @http.route('/property/api/properties', type='json', auth='user')
    def get_properties(self, **kw):
        Property = request.env['property.property'].sudo()
        domain = kw.get('domain', [])
        limit = int(kw.get('limit', 0))
        offset = int(kw.get('offset', 0))
        order = kw.get('order', 'name asc')

        properties = Property.search(domain, limit=limit, offset=offset, order=order)
        return {
            'count': Property.search_count(domain),
            'properties': [{
                'id': prop.id,
                'name': prop.name,
                'street': prop.address,
                'city': prop.city,
                'state': prop.state_id.name if prop.state_id else '',
                'sale_price': prop.property_price,
                'status': prop.state,
                'image_url': f'/web/image/property.property/{prop.id}/property_image',
            } for prop in properties]
        }

    @http.route('/property/api/property/<int:property_id>', type='json', auth='user')
    def get_property(self, property_id, **kw):
        try:
            property = request.env['property.property'].sudo().browse(property_id).exists()
            if not property:
                return {'error': _('Property not found')}

            return {
                'id': property.id,
                'name': property.name,
                'street': property.address,
                'city': property.city,
                'state': property.state_id.name if property.state_id else '',
                'sale_price': property.property_price,
                'status': property.state,
                'description': property.description,
                'image_url': f'/web/image/property.property/{property.id}/property_image',
                'floor_plan_url': f'/web/image/property.property/{property.id}/floor_plan',
            }
        except Exception as e:
            return {'error': str(e)}

    @http.route('/property/dashboard', type='http', auth='user', website=True)
    def property_dashboard(self, **kw):
        Property = request.env['property.property'].sudo()
        PropertySale = request.env['property.sale'].sudo()

        total_properties = Property.search_count([])
        available_properties = Property.search_count([('state', '=', 'available')])
        sold_properties = Property.search_count([('state', '=', 'sold')])
        total_sales_value = sum(PropertySale.search([('state', '=', 'done')]).mapped('total_selling_price'))

        return request.render('property_sale_management.property_dashboard_template', {
            'total_properties': total_properties,
            'available_properties': available_properties,
            'sold_properties': sold_properties,
            'total_sales_value': total_sales_value,
            'user': request.env.user,
        })

    @http.route('/property/api/search', type='json', auth='user')
    def search_properties(self, **kw):
        domain = []
        fields = ['name', 'city', 'state', 'min_price', 'max_price']
        
        for field in fields:
            if kw.get(field):
                if field == 'min_price':
                    domain.append(('property_price', '>=', float(kw.get(field))))
                elif field == 'max_price':
                    domain.append(('property_price', '<=', float(kw.get(field))))
                else:
                    domain.append((field, 'ilike', kw.get(field)))

        Property = request.env['property.property'].sudo()
        properties = Property.search(domain)
        return {
            'count': len(properties),
            'properties': [{
                'id': prop.id,
                'name': prop.name,
                'street': prop.address,
                'city': prop.city,
                'state': prop.state_id.name if prop.state_id else '',
                'sale_price': prop.property_price,
                'status': prop.state,
                'image_url': f'/web/image/property.property/{prop.id}/property_image',
            } for prop in properties]
        }