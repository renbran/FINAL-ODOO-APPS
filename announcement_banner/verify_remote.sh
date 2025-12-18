#!/bin/bash
# Verification script for announcement_banner module on scholarixv2

echo "========================================================"
echo "Verifying announcement_banner module on scholarixv2"
echo "========================================================"
echo ""

cd /var/odoo/scholarixv2

sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf -d scholarixv2 << 'EOFPYTHON'
# Check module status
module = env['ir.module.module'].search([('name', '=', 'announcement_banner')])

print("\n" + "="*60)
if module:
    print(f"Module Name: {module.name}")
    print(f"Module State: {module.state}")
    print(f"Module Version: {module.latest_version}")
    print(f"Module Installed: {'YES' if module.state == 'installed' else 'NO'}")
else:
    print("ERROR: Module not found!")
    exit()
print("="*60)

# Check views
views = env['ir.ui.view'].search([('model', '=', 'announcement.banner')])
print(f"\nTotal Views: {len(views)}")
for view in views:
    print(f"  - {view.name} (Type: {view.type}, ID: {view.id})")

# Check for priority widget in form view
form_view = env['ir.ui.view'].search([
    ('model', '=', 'announcement.banner'),
    ('type', '=', 'form')
], limit=1)

print("\n" + "-"*60)
if form_view:
    arch_str = str(form_view.arch)
    has_priority_widget = 'widget="priority"' in arch_str
    
    if has_priority_widget:
        print("❌ ISSUE FOUND: Priority widget still in form view!")
        print("   The fix was NOT applied correctly")
    else:
        print("✅ FIX VERIFIED: Priority widget removed from form view")
        print("   The console error should be resolved")
else:
    print("⚠️  WARNING: Form view not found")
print("-"*60)

# Check active announcements
announcements = env['announcement.banner'].search([('active', '=', True)])
print(f"\nActive Announcements: {len(announcements)}")
if announcements:
    for ann in announcements:
        print(f"  - '{ann.name}' (Priority: {ann.priority})")
else:
    print("  (No active announcements)")

print("\n" + "="*60)
print("✅ Verification Complete")
print("="*60)
print("\nNext Steps:")
print("1. Clear browser cache (Ctrl+Shift+Delete)")
print("2. Login to scholarixv2 at: https://stagingtry.cloudpepper.site/")
print("3. Open browser console (F12)")
print("4. Check for 'undefined is not iterable' error")
print("5. The error should be GONE if fix is successful")
print("")

exit()
EOFPYTHON

echo ""
echo "========================================================"
