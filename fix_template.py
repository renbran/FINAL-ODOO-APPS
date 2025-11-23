#!/var/odoo/osusproperties/venv/bin/python
import sys
sys.path.insert(0, '/var/odoo/osusproperties/src')

import odoo
from odoo import api, SUPERUSER_ID

# Fixed template - removed conflicting t-options from format_amount()
FIXED_BODY = '''<div style="margin: 0px; padding: 0px;">
    <p style="margin: 0px; padding: 0px; font-size: 13px;">
        <h4><b>Dear <t t-out="object.partner_id.name"/>,</b></h4>
        <br/>
        Invoice - <b><t t-out="object.name"/></b> is going to expire.
        The due date is on <b><t t-out="object.invoice_date_due"/></b>.
        <br/>
        Please take necessary actions.
        <br/>
        <br/>
        <b>More details of Invoice <t t-out="object.name"/></b> :<br/>
        Invoice Name : <t t-out="object.name"/><br/>
        Created Date : <t t-out="object.invoice_date"/><br/>
        Sales Person : <t t-out="object.user_id.partner_id.name"/><br/>
        Partner Name :  <t t-out="object.partner_id.name"/><br/>
        Total Order Amount : <t t-out="format_amount(object.amount_total, object.currency_id) or ''"/><br/>
        Amount Paid : <t t-out="format_amount(object.amount_paid, object.currency_id) or ''"/><br/>
        Amount Due : <t t-out="format_amount(object.amount_residual, object.currency_id) or ''"/><br/>
        <br/>
    </p>
</div>'''

odoo.tools.config.parse_config(['-c', '/var/odoo/osusproperties/odoo.conf'])
registry = odoo.registry('osusproperties')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    template = env['mail.template'].search([('name', '=', 'Invoice: Due Reminder Email')], limit=1)
    
    if template:
        print(f"Found: {template.name} (ID: {template.id})")
        template.write({'body_html': FIXED_BODY})
        cr.commit()
        print("✅ Template fixed - removed conflicting t-options from format_amount()")
    else:
        print("❌ Not found")
