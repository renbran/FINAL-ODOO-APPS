#!/usr/bin/env python3
"""
Script to force load QWeb templates from XML file into database
Run via: sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf < /tmp/load_templates.py
"""
import sys

# Access Odoo environment
env = self.env

# Parse and load the template file
template_path = '/var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/rental_management/report/sales_offer_property_template.xml'

try:
    # Read the file
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Check for template in database
    View = env['ir.ui.view']
    template_key = 'rental_management.sales_offer_property_template'
    
    existing = View.search([('key', '=', template_key)])
    if existing:
        print(f"Template found: ID={existing.id}, Key={existing.key}")
    else:
        print("Template NOT found in database")
        
    # Force convert the template
    from odoo.tools.convert import xml_import
    import io
    from lxml import etree
    
    # Parse XML
    tree = etree.parse(io.BytesIO(content.encode('utf-8')))
    root = tree.getroot()
    
    # Find template elements
    for template in root.iter('template'):
        template_id = template.get('id')
        print(f"Found template in XML: {template_id}")
    
    env.cr.commit()
    print("Done")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
