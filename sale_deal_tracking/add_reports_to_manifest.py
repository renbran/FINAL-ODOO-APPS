#!/usr/bin/env python3
"""
Add report files to commission_ax manifest
"""

# Read manifest
with open('/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_ax/__manifest__.py', 'r') as f:
    content = f.read()

# Find the data section and add reports before the closing bracket
old_section = """        'views/commission_profit_analysis_wizard_views.xml',     # ✅ Analysis Wizard
    ],"""

new_section = """        'views/commission_profit_analysis_wizard_views.xml',     # ✅ Analysis Wizard

        # ============================================
        # STEP 6: Reports
        # ============================================
        'reports/commission_report.xml',                         # ✅ Commission Reports
        'reports/commission_partner_statement_reports.xml',      # ✅ Partner Statement
    ],"""

# Replace
if old_section in content:
    content = content.replace(old_section, new_section)
    print('✅ Reports added to manifest!')
else:
    print('❌ Could not find section to replace')
    exit(1)

# Write back
with open('/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_ax/__manifest__.py', 'w') as f:
    f.write(content)

print('✅ Manifest updated successfully!')
