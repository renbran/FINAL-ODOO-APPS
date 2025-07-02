"""
Quick Fix for osus_invoice_report Paper Format Issue
=================================================== 

This script creates the missing paper format and external ID.
Run this in Odoo shell:

python3 odoo-bin shell -d your_database_name --no-http

Then copy and paste this entire script.
"""

print("=== Fixing osus_invoice_report Paper Format ===")

try:
    # Check if external ID exists
    existing_xmlid = env['ir.model.data'].search([
        ('module', '=', 'osus_invoice_report'),
        ('name', '=', 'paperformat_osus_invoice'),
        ('model', '=', 'report.paperformat')
    ])
    
    if existing_xmlid:
        print("✅ Paper format external ID already exists")
    else:
        # Look for existing OSUS paper format
        existing_format = env['report.paperformat'].search([
            ('name', 'ilike', 'OSUS%'),
        ], limit=1)
        
        if existing_format:
            print(f"Found existing format: {existing_format.name}")
            # Create missing external ID
            env['ir.model.data'].create({
                'module': 'osus_invoice_report',
                'name': 'paperformat_osus_invoice',
                'model': 'report.paperformat',
                'res_id': existing_format.id,
                'noupdate': False,
            })
            print("✅ Created missing external ID")
        else:
            # Create new paper format
            print("Creating new OSUS paper format...")
            new_format = env['report.paperformat'].create({
                'name': 'OSUS Invoice Format',
                'format': 'A4',
                'orientation': 'Portrait',
                'margin_top': 50,
                'margin_bottom': 50,
                'margin_left': 10,
                'margin_right': 10,
                'header_line': False,
                'header_spacing': 40,
                'dpi': 90,
            })
            
            # Create external ID
            env['ir.model.data'].create({
                'module': 'osus_invoice_report',
                'name': 'paperformat_osus_invoice',
                'model': 'report.paperformat',
                'res_id': new_format.id,
                'noupdate': False,
            })
            print(f"✅ Created new paper format: {new_format.name}")
    
    # Commit changes
    env.cr.commit()
    print("\n🎉 Paper format fix completed!")
    print("Now try to install/upgrade the osus_invoice_report module.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    env.cr.rollback()
    raise
