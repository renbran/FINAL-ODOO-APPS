#!/bin/bash
cd /var/odoo/scholarixv2
echo "from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry
registry = Registry.new('scholarixv2')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    Property = env['property.details']
    if 'total_customer_obligation' in Property._fields:
        print('FIELD EXISTS: total_customer_obligation')
        print('Field type:', type(Property._fields['total_customer_obligation']))
    else:
        print('FIELD MISSING!')
    print('DLD Fee field:', 'dld_fee' in Property._fields)
" | sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf --no-http 2>/dev/null | tail -5
