"""
Fix for osus_invoice_report External ID Error
============================================

This script fixes the missing paperformat_osus_invoice external ID error.

Run this in Odoo shell:
python3 odoo-bin shell -d your_database_name --no-http

Then copy and paste this script.
"""

print("=== Fixing osus_invoice_report External ID Error ===")

# Get database cursor
cr = env.cr

try:
    # 1. Check if the paper format record exists but missing external ID
    print("1. Checking for existing paper format...")
    
    # Look for existing paper format with similar name
    existing_format = env['report.paperformat'].search([
        ('name', 'like', 'OSUS%'),
    ], limit=1)
    
    if existing_format:
        print(f"   Found existing paper format: {existing_format.name} (ID: {existing_format.id})")
        
        # Check if external ID exists
        existing_xmlid = env['ir.model.data'].search([
            ('module', '=', 'osus_invoice_report'),
            ('name', '=', 'paperformat_osus_invoice'),
            ('model', '=', 'report.paperformat'),
            ('res_id', '=', existing_format.id)
        ])
        
        if not existing_xmlid:
            print("   Creating missing external ID...")
            env['ir.model.data'].create({
                'module': 'osus_invoice_report',
                'name': 'paperformat_osus_invoice',
                'model': 'report.paperformat',
                'res_id': existing_format.id,
                'noupdate': False,
            })
            print("   ✅ Created external ID for existing paper format")
        else:
            print("   ✅ External ID already exists")
    else:
        # 2. Create the paper format if it doesn't exist
        print("   No existing paper format found, creating new one...")
        
        # Create the paper format
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
        
        print(f"   Created new paper format: {new_format.name} (ID: {new_format.id})")
        
        # Create the external ID
        env['ir.model.data'].create({
            'module': 'osus_invoice_report',
            'name': 'paperformat_osus_invoice',
            'model': 'report.paperformat',
            'res_id': new_format.id,
            'noupdate': False,
        })
        
        print("   ✅ Created external ID for new paper format")
    
    # 3. Alternative: Use base paper format if issues persist
    print("\n2. Setting up fallback options...")
    
    # Get base A4 paper format as fallback
    base_format = env.ref('base.paperformat_euro', raise_if_not_found=False)
    if not base_format:
        base_format = env['report.paperformat'].search([('format', '=', 'A4')], limit=1)
    
    if base_format:
        print(f"   Fallback paper format available: {base_format.name} (ID: {base_format.id})")
    
    # Commit changes
    cr.commit()
    
    print("\n✅ Paper format fix completed!")
    print("Now try to install/upgrade the osus_invoice_report module again.")
    
except Exception as e:
    print(f"\n❌ Error fixing paper format: {e}")
    cr.rollback()
    raise
