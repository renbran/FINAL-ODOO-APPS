#!/bin/bash
cd /var/odoo/scholarixv2
echo "
prop = env['property.details']
fields_list = ['total_customer_obligation', 'dld_fee', 'admin_fee']
for f in fields_list:
    exists = f in prop._fields
    print(f'{f}: {exists}')
" | sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf --no-http 2>/dev/null | grep -E "total_customer|dld_fee|admin_fee"
