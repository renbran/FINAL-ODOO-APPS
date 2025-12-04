#!/usr/bin/env python3
"""
Fix the print commission report method to work without XML ID reference
"""

# Read the file
with open('/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/sale_deal_tracking/models/sale_order.py', 'r') as f:
    content = f.read()

# Find and replace the problematic method
old_method = """    def action_print_commission_report(self):
        \"\"\"
        Generate and return the commission payout report for this sale order.
        This method is called by the Print Commission Report button.
        \"\"\"
        self.ensure_one()
        
        # Return the report action
        return self.env.ref('commission_ax.action_report_commission_payout_professional').report_action(self)"""

new_method = """    def action_print_commission_report(self):
        \"\"\"
        Generate and return the commission payout report for this sale order.
        This method is called by the Print Commission Report button.
        \"\"\"
        self.ensure_one()
        
        # Generate report directly using QWeb template
        # This works even if the ir.actions.report record doesn't exist
        report = self.env['ir.actions.report']
        
        # Try to find existing report action first
        try:
            report_action = self.env.ref('commission_ax.action_report_commission_payout_professional', raise_if_not_found=False)
            if report_action:
                return report_action.report_action(self)
        except ValueError:
            pass
        
        # Fallback: Generate report directly using the template name
        # This will work even without the ir.actions.report record
        return report._render_qweb_pdf('commission_ax.commission_payout_report_template_professional', self.ids)[0]"""

# Replace the method
if old_method in content:
    content = content.replace(old_method, new_method)
    print('✅ Method replaced successfully')
else:
    print('⚠️ Old method not found, trying to find method to update...')
    # If exact match not found, try to find the method and replace it
    import re
    pattern = r'def action_print_commission_report\(self\):.*?(?=\n    def |\n\nclass |\Z)'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, new_method.strip(), content, flags=re.DOTALL)
        print('✅ Method updated with regex')
    else:
        print('❌ Could not find method to replace')
        exit(1)

# Write back
with open('/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/sale_deal_tracking/models/sale_order.py', 'w') as f:
    f.write(content)

print('✅ File updated successfully!')
