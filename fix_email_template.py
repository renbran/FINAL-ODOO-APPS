#!/usr/bin/env python3
# Fix email template for invoice due reminder

import odoo
from odoo import api, SUPERUSER_ID

# Configuration
db_name = 'osusproperties'

# Fixed template body
FIXED_BODY_HTML = """<div style="margin: 0px; padding: 0px;">
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
</div>"""

# Initialize Odoo
odoo.tools.config.parse_config(['-c', '/var/odoo/osusproperties/odoo.conf'])
registry = odoo.registry(db_name)

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Find the template
    template = env['mail.template'].search([
        ('name', '=', 'Invoice: Due Reminder Email'),
        ('model', '=', 'account.move')
    ], limit=1)
    
    if template:
        print(f"Found template: {template.name} (ID: {template.id})")
        print("Updating body_html...")
        template.write({'body_html': FIXED_BODY_HTML})
        cr.commit()
        print("✅ Template fixed successfully!")
        print("\nFixed issue: Removed conflicting t-options from format_amount() result")
    else:
        print("❌ Template not found!")
