#!/usr/bin/env python3
import re

# Read the file
with open('/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/sale_deal_tracking/models/sale_order.py', 'r') as f:
    content = f.read()

# Simple method
pattern = r'def action_print_commission_report\(self\):.*?(?=\n    def |\Z)'

simple_method = """def action_print_commission_report(self):
        \"\"\"Generate and return commission payout report.\"\"\"
        self.ensure_one()
        return self.env.ref('commission_ax.action_report_commission_payout_professional').report_action(self)"""

content = re.sub(pattern, simple_method, content, flags=re.DOTALL)

with open('/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/sale_deal_tracking/models/sale_order.py', 'w') as f:
    f.write(content)

print('✅ Method restored!')
