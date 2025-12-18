#!/usr/bin/env python3
"""
Verification script for announcement_banner fix on scholarixv2
Checks module status, views, and provides browser testing instructions
"""

import sys

def main():
    print("=" * 80)
    print("🔍 ANNOUNCEMENT BANNER - VERIFICATION SCRIPT")
    print("=" * 80)
    print()
    
    verification_commands = """
# Connect to server
ssh -i ~/.ssh/odoo17_cloudpepper_new root@139.84.163.11 -p 22

# Check Odoo service status
systemctl status odoo

# Check module status in database
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf -d scholarixv2 << 'EOFPYTHON'
# Check module installation status
module = env['ir.module.module'].search([('name', '=', 'announcement_banner')])
if module:
    print(f"\\n{'='*60}")
    print(f"Module: {module.name}")
    print(f"State: {module.state}")
    print(f"Version: {module.latest_version}")
    print(f"{'='*60}")
else:
    print("❌ Module not found!")

# Check views
views = env['ir.ui.view'].search([('model', '=', 'announcement.banner')])
print(f"\\nFound {len(views)} views for announcement.banner:")
for view in views:
    print(f"  - {view.name} (ID: {view.id}, Type: {view.type})")

# Check if priority widget is still in view
form_view = env['ir.ui.view'].search([
    ('model', '=', 'announcement.banner'),
    ('type', '=', 'form')
], limit=1)

if form_view:
    arch_str = str(form_view.arch)
    if 'widget="priority"' in arch_str:
        print("\\n❌ WARNING: priority widget still found in form view!")
    else:
        print("\\n✅ Priority widget removed successfully")

# Check active announcements
announcements = env['announcement.banner'].search([('active', '=', True)])
print(f"\\nActive announcements: {len(announcements)}")
for ann in announcements:
    print(f"  - {ann.name} (Priority: {ann.priority})")

exit()
EOFPYTHON

# Check recent logs for errors
echo ""
echo "=== RECENT LOGS (last 50 lines with errors) ==="
journalctl -u odoo --since '15 minutes ago' | grep -i 'error\|traceback\|announcement' | tail -50
"""
    
    print("📋 VERIFICATION COMMANDS:")
    print(verification_commands)
    print()
    print("=" * 80)
    print("🌐 BROWSER VERIFICATION STEPS")
    print("=" * 80)
    print()
    print("1️⃣  CLEAR BROWSER CACHE")
    print("   - Press Ctrl+Shift+Delete")
    print("   - Select 'Cached images and files'")
    print("   - Click 'Clear data'")
    print("   - OR use Incognito/Private mode")
    print()
    print("2️⃣  OPEN BROWSER CONSOLE")
    print("   - Press F12 (or right-click → Inspect)")
    print("   - Click on 'Console' tab")
    print("   - Keep it open during testing")
    print()
    print("3️⃣  LOGIN TO SCHOLARIXV2")
    print("   - URL: https://stagingtry.cloudpepper.site/")
    print("   - Database: scholarixv2")
    print("   - Watch console for errors during login")
    print()
    print("4️⃣  CHECK FOR CONSOLE ERRORS")
    print("   Look for these SPECIFIC errors (should be GONE now):")
    print("   ❌ 'undefined is not iterable'")
    print("   ❌ 'cannot read property Symbol(Symbol.iterator)'")
    print("   ❌ 'priority widget' errors")
    print()
    print("5️⃣  TEST ANNOUNCEMENT BANNER")
    print("   - Navigate to Settings → Technical → Announcement Banner")
    print("   - Create a test announcement:")
    print("     * Title: 'Test Console Fix'")
    print("     * Message: 'Testing HTML <b>bold</b> and <i>italic</i>'")
    print("     * Priority: 10")
    print("     * Active: Yes")
    print("   - Save and logout")
    print("   - Login again")
    print("   - Banner should appear without console errors")
    print()
    print("6️⃣  VERIFY FIX")
    print("   ✅ No console errors on page load")
    print("   ✅ Banner displays correctly")
    print("   ✅ HTML content renders (bold/italic visible)")
    print("   ✅ Close button works")
    print("   ✅ Navigation works (if multiple announcements)")
    print("   ✅ Priority field shows as number input (not widget)")
    print()
    print("=" * 80)
    print("📊 EXPECTED RESULTS")
    print("=" * 80)
    print()
    print("✅ BEFORE FIX:")
    print("   - Console error: 'undefined is not iterable'")
    print("   - Error related to priority widget")
    print("   - OWL lifecycle error")
    print()
    print("✅ AFTER FIX:")
    print("   - No console errors")
    print("   - Banner displays smoothly")
    print("   - Priority shows as simple integer input")
    print()
    print("=" * 80)
    print("🐛 TROUBLESHOOTING")
    print("=" * 80)
    print()
    print("If errors persist:")
    print()
    print("1. Hard refresh browser (Ctrl+F5)")
    print("2. Clear ALL browser data (not just cache)")
    print("3. Try different browser")
    print("4. Check if error is from different module:")
    print("   - Look at error stack trace in console")
    print("   - Check file path in error message")
    print()
    print("5. Re-update module on server:")
    print("   ssh -i ~/.ssh/odoo17_cloudpepper_new root@139.84.163.11 -p 22")
    print("   sudo systemctl stop odoo")
    print("   cd /var/odoo/scholarixv2")
    print("   sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 \\")
    print("     -u announcement_banner --stop-after-init")
    print("   sudo systemctl start odoo")
    print()
    print("6. Clear Odoo caches:")
    print("   Settings → Technical → Clear Caches")
    print()
    print("=" * 80)
    print()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
