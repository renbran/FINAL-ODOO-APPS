from odoo import http
from odoo.http import request
import json

class PropertyDashboardController(http.Controller):
    @http.route('/property/dashboard/data', type='http', auth='user')
    def get_dashboard_data(self, **kw):
        """API endpoint for dashboard data"""
        dashboard_id = kw.get('dashboard_id')
        if not dashboard_id:
            # Return default dashboard data if no specific dashboard is requested
            return json.dumps({
                'error': 'No dashboard specified'
            })
        
        dashboard = request.env['property.dashboard'].browse(int(dashboard_id))
        if not dashboard.exists():
            return json.dumps({
                'error': 'Dashboard not found'
            })
        
        # Get the dashboard data
        return json.dumps({
            'name': dashboard.name,
            'metrics': {
                'total_properties': dashboard.total_properties,
                'available_properties': dashboard.available_properties,
                'reserved_properties': dashboard.reserved_properties,
                'sold_properties': dashboard.sold_properties,
                'maintenance_properties': dashboard.maintenance_properties,
                'rented_properties': dashboard.rented_properties,
                'total_value': dashboard.total_value,
                'avg_property_price': dashboard.avg_property_price,
            },
            'charts': {
                'property_status': json.loads(dashboard.property_status_chart or '{}'),
                'property_type': json.loads(dashboard.property_type_chart or '{}'),
                'sales_trend': json.loads(dashboard.sales_trend_chart or '{}'),
            },
            'trending_properties': [{
                'id': p.id,
                'name': p.name,
                'price': p.price,
                'status': p.status,
                'type': p.property_type_id.name,
            } for p in dashboard.trending_property_ids],
        })
    
    @http.route('/property/dashboard', type='http', auth='user', website=True)
    def dashboard(self, **kw):
        """Main dashboard view"""
        dashboard_id = kw.get('dashboard_id')
        if dashboard_id:
            dashboard = request.env['property.dashboard'].browse(int(dashboard_id))
        else:
            # Get the user's default dashboard or create one
            dashboard = request.env['property.dashboard'].search([('user_id', '=', request.env.user.id)], limit=1)
            if not dashboard:
                dashboard = request.env['property.dashboard'].create({
                    'name': f"{request.env.user.name}'s Dashboard",
                    'user_id': request.env.user.id,
                })
        
        return request.render('property_monitor.dashboard_main', {
            'dashboard': dashboard,
        })