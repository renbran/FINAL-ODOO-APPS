#!/usr/bin/env python3
"""
Script to add print commission report method to sale_order.py
"""

# Read the file
with open('/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/sale_deal_tracking/models/sale_order.py', 'r') as f:
    content = f.read()

# Method to add
new_method = """
    def action_print_commission_report(self):
        \"\"\"
        Generate and return the commission payout report for this sale order.
        This method is called by the Print Commission Report button.
        \"\"\"
        self.ensure_one()
        
        # Return the report action
        return self.env.ref('commission_ax.action_report_commission_payout_professional').report_action(self)
"""

# Find the last line and insert before it
lines = content.split('\n')
# Insert before the last line (which is likely "return super(SaleOrder, self).create(vals)")
insert_position = len(lines) - 1
lines.insert(insert_position, new_method)

# Write back
new_content = '\n'.join(lines)
with open('/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/sale_deal_tracking/models/sale_order.py', 'w') as f:
    f.write(new_content)

print('✅ Method added successfully!')
