# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Clean corrupted references in sale.order
    sale_orders = env['sale.order'].search([])
    for order in sale_orders:
        # List of all Many2one fields to check
        m2o_fields = [
            'external_party_id', 'consultant_id', 'second_agent_id',
            'manager_id', 'director_id', 'project_id', 'x_unit1'
        ]
        
        for field in m2o_fields:
            if field in order._fields and order[field]:
                if not order[field].exists():
                    _logger.warning(f"Fixing corrupted reference in {order.name} for field {field}")
                    order[field] = False

    # Clean corrupted references in purchase.order
    purchase_orders = env['purchase.order'].search([])
    for po in purchase_orders:
        if 'origin_so_id' in po._fields and po.origin_so_id and not po.origin_so_id.exists():
            _logger.warning(f"Fixing corrupted reference in PO {po.name} for origin_so_id")
            po.origin_so_id = False