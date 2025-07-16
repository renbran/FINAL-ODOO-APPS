from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db
from odoo.tools import json

class CustomSalesReportController(http.Controller):
    @http.route('/custom_sales/report', type='json', auth='user', methods=['POST'], csrf=False)
    def custom_sales_report(self, **kwargs):
        ensure_db()
        if not request.env.user.has_group('base.group_user'):
            return {'error': 'Unauthorized'}
        orders = request.env['sale.order'].search([])
        summary = [
            {
                'id': order.id,
                'name': order.name,
                'custom_field_1': order.custom_field_1,
                'custom_field_2': order.custom_field_2,
                'custom_field_3': order.custom_field_3 and order.custom_field_3.name or False,
                'amount_total': order.amount_total,
            }
            for order in orders
        ]
        return {'orders': summary}
