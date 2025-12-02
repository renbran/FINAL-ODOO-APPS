#!/bin/bash
cd /var/odoo/scholarixv2
echo "
# Test that all fields are properly registered
prop = env['property.details']
required_fields = ['dld_fee', 'admin_fee', 'is_payment_plan', 'payment_schedule_id', 'total_customer_obligation']
print('Field Status:')
for f in required_fields:
    exists = f in prop._fields
    field_type = type(prop._fields[f]).__name__ if exists else 'N/A'
    print(f'  {f}: {exists} ({field_type})')
print('')
print('All fields OK:', all(f in prop._fields for f in required_fields))
" | sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf --no-http 2>/dev/null | grep -E "Field Status:|dld_fee|admin_fee|is_payment_plan|payment_schedule_id|total_customer|All fields"
