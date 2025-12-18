#!/usr/bin/env python3
"""
Fix missing field metadata for schedule_from_property in property.vendor model
"""

print("""
# Run this with Odoo shell:
# cd /var/odoo/scholarixv2
# sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf -d scholarixv2 --no-http

# Then paste this code:

# Force update ir.model.fields for schedule_from_property
env.cr.execute(\"\"\"
    SELECT id FROM ir_model_fields 
    WHERE model = 'property.vendor' AND name = 'schedule_from_property'
\"\"\")
result = env.cr.fetchone()

if result:
    print(f"Field metadata exists with ID: {result[0]}")
else:
    print("Field metadata missing - will be created on next module update")
    
# Force model reflection
env['property.vendor']._fields['schedule_from_property']
print("Field exists in model:", 'schedule_from_property' in env['property.vendor']._fields)

# Force metadata sync
env['ir.model']._reflect_model(env['property.vendor'], ['schedule_from_property'])
env.cr.commit()
print("Metadata synchronized!")

exit()
""")
