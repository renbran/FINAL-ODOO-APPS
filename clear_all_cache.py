#!/var/odoo/osusproperties/venv/bin/python
import sys
sys.path.insert(0, '/var/odoo/osusproperties/src')

import odoo
from odoo import api, SUPERUSER_ID

odoo.tools.config.parse_config(['-c', '/var/odoo/osusproperties/odoo.conf'])
registry = odoo.registry('osusproperties')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Clear all asset bundles cache
    print("🗑️  Clearing asset bundle cache...")
    env['ir.qweb'].clear_caches()
    
    # Clear attachment cache for reports
    print("🗑️  Clearing report attachment cache...")
    attachments = env['ir.attachment'].search([
        ('name', 'like', 'web_assets'),
        ('res_model', '=', 'ir.ui.view')
    ])
    print(f"   Found {len(attachments)} asset attachments")
    attachments.unlink()
    
    # Clear view cache
    print("🗑️  Clearing view cache...")
    env['ir.ui.view'].clear_caches()
    
    # Clear all ir.qweb caches
    print("🗑️  Clearing QWeb template cache...")
    env.registry.clear_caches()
    
    cr.commit()
    print("✅ All caches cleared successfully!")
    print("\n📝 Summary of fixes applied:")
    print("   1. Email template: Fixed format_amount() + t-options conflict")
    print("   2. CSS: Reduced excessive header padding (150pt → auto)")
    print("   3. CSS: Reduced article margin (40pt → 5pt)")
    print("   4. CSS: Optimized all spacing values by 50-70%")
    print("\n🔄 Please restart Odoo service for changes to take effect")
