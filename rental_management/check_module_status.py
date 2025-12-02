#!/usr/bin/env python3
"""
Diagnostic Script: Check rental_management Module Status in Odoo
================================================================

This script helps diagnose why the invoice tracking features aren't visible.

Usage:
    python check_module_status.py

Requirements:
    - Run from Odoo directory or provide database connection
    - Can also be run via odoo-bin shell
"""

import sys
import os

def check_via_odoo_shell():
    """
    Instructions for checking via Odoo shell
    """
    print("\n" + "="*70)
    print("🔍 MODULE STATUS DIAGNOSTIC SCRIPT")
    print("="*70)
    
    print("\n📋 STEP 1: Check if rental_management is installed")
    print("-" * 70)
    print("Run these commands in Odoo shell:")
    print("\n  odoo shell -d your_database_name\n")
    print("  >>> module = self.env['ir.module.module'].search([('name', '=', 'rental_management')])")
    print("  >>> print(f'State: {module.state}')")
    print("  >>> print(f'Latest Version: {module.latest_version}')")
    print("  >>> print(f'Installed Version: {module.installed_version}')")
    
    print("\n✅ Expected Output:")
    print("   State: installed")
    print("   Latest Version: 3.5.0")
    print("   Installed Version: 3.5.0")
    
    print("\n❌ If versions don't match:")
    print("   → Module needs upgrade!")
    print("   → Follow MODULE_UPGRADE_GUIDE.md")
    
    print("\n" + "="*70)
    print("\n📋 STEP 2: Check if new fields exist in database")
    print("-" * 70)
    print("In Odoo shell:")
    print("\n  >>> contract = self.env['property.vendor']")
    print("  >>> fields_to_check = [")
    print("  ...     'booking_invoice_count',")
    print("  ...     'installment_invoice_count',")
    print("  ...     'total_invoice_count',")
    print("  ...     'created_invoice_count',")
    print("  ...     'paid_invoice_count',")
    print("  ...     'overall_payment_percentage',")
    print("  ...     'total_paid_to_date'")
    print("  ... ]")
    print("  >>> for field in fields_to_check:")
    print("  ...     exists = field in contract._fields")
    print("  ...     print(f'{field}: {\"✓\" if exists else \"✗\"}')")
    
    print("\n✅ All fields should show: ✓")
    print("❌ If any show ✗:")
    print("   → Fields not loaded into model")
    print("   → Module needs upgrade or restart")
    
    print("\n" + "="*70)
    print("\n📋 STEP 3: Check if action methods exist")
    print("-" * 70)
    print("In Odoo shell:")
    print("\n  >>> contract = self.env['property.vendor']")
    print("  >>> methods_to_check = [")
    print("  ...     'action_create_booking_invoices_button',")
    print("  ...     'action_view_booking_invoices',")
    print("  ...     'action_view_installment_invoices',")
    print("  ...     'action_view_all_invoices',")
    print("  ...     'action_confirm_booking_paid',")
    print("  ...     'action_create_installments_from_booking'")
    print("  ... ]")
    print("  >>> for method in methods_to_check:")
    print("  ...     exists = hasattr(contract, method)")
    print("  ...     print(f'{method}: {\"✓\" if exists else \"✗\"}')")
    
    print("\n✅ All methods should show: ✓")
    print("❌ If any show ✗:")
    print("   → Methods not loaded")
    print("   → Python file not reloaded")
    print("   → Restart Odoo service")
    
    print("\n" + "="*70)
    print("\n📋 STEP 4: Check if view has been updated")
    print("-" * 70)
    print("In Odoo shell:")
    print("\n  >>> view = self.env['ir.ui.view'].search([")
    print("  ...     ('name', '=', 'property.vendor.form.view')")
    print("  ... ], limit=1)")
    print("  >>> print(f'View ID: {view.id}')")
    print("  >>> print(f'Last Modified: {view.write_date}')")
    print("  >>> # Check if smart buttons are in the view")
    print("  >>> has_booking_button = 'booking_invoice_count' in view.arch")
    print("  >>> has_dashboard = 'Payment Progress Overview' in view.arch")
    print("  >>> print(f'Has Booking Button: {\"✓\" if has_booking_button else \"✗\"}')")
    print("  >>> print(f'Has Dashboard: {\"✓\" if has_dashboard else \"✗\"}')")
    
    print("\n✅ Expected:")
    print("   Last Modified: Recent date (after your git push)")
    print("   Has Booking Button: ✓")
    print("   Has Dashboard: ✓")
    
    print("\n❌ If buttons/dashboard missing:")
    print("   → View XML not reloaded")
    print("   → Upgrade module to reload views")
    
    print("\n" + "="*70)
    print("\n📋 STEP 5: Quick test on a sales contract")
    print("-" * 70)
    print("In Odoo shell:")
    print("\n  >>> # Get a sales contract")
    print("  >>> contract = self.env['property.vendor'].search([], limit=1)")
    print("  >>> print(f'Contract: {contract.name}')")
    print("  >>> print(f'Stage: {contract.stage}')")
    print("  >>> print(f'Booking Invoice Count: {contract.booking_invoice_count}')")
    print("  >>> print(f'Total Invoice Count: {contract.total_invoice_count}')")
    print("  >>> print(f'Overall Payment %: {contract.overall_payment_percentage}%')")
    
    print("\n✅ If you see numbers:")
    print("   → Fields are working!")
    print("   → Issue is only in UI/view")
    print("   → Clear browser cache")
    
    print("\n❌ If you see errors:")
    print("   → Fields not computed properly")
    print("   → Check Odoo logs for errors")
    
    print("\n" + "="*70)
    print("\n🎯 COMMON SOLUTIONS")
    print("-" * 70)
    print("\n1️⃣  MODULE NEEDS UPGRADE:")
    print("   • Go to Apps → Search 'rental_management' → Upgrade")
    print("   • OR: odoo -u rental_management --stop-after-init")
    
    print("\n2️⃣  BROWSER CACHE:")
    print("   • Press Ctrl + Shift + R (hard refresh)")
    print("   • OR: Clear all browser cache")
    
    print("\n3️⃣  ODOO SERVICE RESTART:")
    print("   • sudo systemctl restart odoo")
    print("   • Wait 30-60 seconds for startup")
    
    print("\n4️⃣  CLEAR ODOO ASSET CACHE:")
    print("   • rm -rf /path/to/filestore/your_db/assets/*")
    print("   • Odoo will regenerate on next load")
    
    print("\n5️⃣  VIEW CACHE ISSUE:")
    print("   • Settings → Technical → Views")
    print("   • Search: property.vendor.form.view")
    print("   • Delete the view")
    print("   • Upgrade module again")
    
    print("\n" + "="*70)
    print("\n📊 EXPECTED BEHAVIOR AFTER FIX")
    print("-" * 70)
    print("""
When you open a Sales Contract (property.vendor), you should see:

┌──────────────────────────────────────────────────────────────┐
│ Property Sale Contract                    [Smart Buttons]     │
│                                           ┌──────┬──────┐    │
│ Title: Property Name                      │📋 3  │💰 12 │    │
│ Reference: PS/2025/12/0079                └──────┴──────┘    │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 💰 Payment Progress Overview                            │ │
│ │ Overall Progress: [████████░░] 80%                     │ │
│ │ Paid: 400,000 / 500,000 AED                            │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ [Other fields...]                                             │
└──────────────────────────────────────────────────────────────┘

Smart Buttons (top right):
• 📋 Booking (count)
• 💰 Installments (count)
• 📄 All Invoices (count)
• 📚 Created (count)
• ✅ Paid (count)
• 🔧 Maintenance (count)
""")
    
    print("\n" + "="*70)
    print("\n📞 NEED MORE HELP?")
    print("-" * 70)
    print("\n📖 Read: MODULE_UPGRADE_GUIDE.md")
    print("📖 Read: INVOICE_TRACKING_QUICK_START.md")
    print("📖 Read: TROUBLESHOOTING_GUIDE.md")
    
    print("\n💡 Still not working?")
    print("   1. Check Odoo logs: tail -f /var/log/odoo/odoo.log")
    print("   2. Check Python syntax: python -m py_compile models/sale_contract.py")
    print("   3. Check XML syntax: xmllint views/property_vendor_view.xml")
    print("   4. Check database: SELECT * FROM property_vendor LIMIT 1;")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    check_via_odoo_shell()
