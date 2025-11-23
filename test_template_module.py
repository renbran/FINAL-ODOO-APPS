#!/usr/bin/env python3
"""
Test script to verify OSUS template is being applied to reports
"""

# Test 1: Check if module is installed and active
module = env['ir.module.module'].search([('name', '=', 'osus_global_pdf_template')])
print(f"\n1. Module Status:")
print(f"   Name: {module.name}")
print(f"   State: {module.state}")
print(f"   Installed: {'✅' if module.state == 'installed' else '❌'}")

# Test 2: Check if template file exists
import os
template_path = '/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/osus_global_pdf_template/static/template/osus_template.pdf'
template_exists = os.path.exists(template_path)
template_size = os.path.getsize(template_path) if template_exists else 0
print(f"\n2. Template File:")
print(f"   Exists: {'✅' if template_exists else '❌'}")
print(f"   Size: {template_size:,} bytes")

# Test 3: Get a sample report
reports = env['ir.actions.report'].search([('report_type', '=', 'qweb-pdf')], limit=5)
print(f"\n3. Sample Reports (showing first 5):")
for idx, report in enumerate(reports, 1):
    has_field = hasattr(report, 'apply_osus_template')
    field_value = report.apply_osus_template if has_field else 'N/A'
    print(f"   {idx}. {report.name}")
    print(f"      Model: {report.model}")
    print(f"      Has apply_osus_template field: {'✅' if has_field else '❌'}")
    print(f"      Template enabled: {field_value}")

# Test 4: Check method override
print(f"\n4. Method Override Check:")
report_obj = env['ir.actions.report']
has_method = hasattr(report_obj, '_render_qweb_pdf_prepare_streams')
has_apply_method = hasattr(report_obj, '_apply_osus_template_to_pdf')
print(f"   Has _render_qweb_pdf_prepare_streams: {'✅' if has_method else '❌'}")
print(f"   Has _apply_osus_template_to_pdf: {'✅' if has_apply_method else '❌'}")

print(f"\n{'='*60}")
print("✅ Module is ready to apply templates!" if all([
    module.state == 'installed',
    template_exists,
    has_method,
    has_apply_method
]) else "❌ Some checks failed - review above")
print('='*60)
