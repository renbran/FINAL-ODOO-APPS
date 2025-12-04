#!/usr/bin/env python3
"""
Simplify the print commission report method to just open commission dashboard
where users can then use the existing print buttons
"""

# Read the file
with open('/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/sale_deal_tracking/models/sale_order.py', 'r') as f:
    content = f.read()

# Find the current method
import re
pattern = r'def action_print_commission_report\(self\):.*?(?=\n    def |\Z)'
match = re.search(pattern, content, re.DOTALL)

if not match:
    print('❌ Method not found')
    exit(1)

# New simpler method that opens commission dashboard
new_method = """def action_print_commission_report(self):
        \"\"\"
        Open commission dashboard where users can view details and print reports.
        This is a workaround since commission report actions are not registered.
        \"\"\"
        self.ensure_one()
        
        # Use the existing commission dashboard action which works
        return self.action_view_commission_dashboard()"""

# Replace the method
content = re.sub(pattern, new_method, content, flags=re.DOTALL)

# Write back
with open('/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/sale_deal_tracking/models/sale_order.py', 'w') as f:
    f.write(content)

print('✅ Method simplified to use commission dashboard!')
