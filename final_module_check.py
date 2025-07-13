#!/usr/bin/env python3
"""
Final Module Readiness Check
"""

import os

def check_module_readiness():
    module_path = r"d:\RUNNING APPS\ready production\osus-main\odoo17_final\osus_invoice_report"
    
    required_files = [
        '__manifest__.py',
        '__init__.py',
        'models/__init__.py',
        'models/account_move.py',
        'models/custom_invoice.py',
        'models/sale_order.py',
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
        'report/report_action.xml',
        'report/bill_report_action.xml',
        'report/invoice_report.xml',
        'report/bill_report.xml',
        'security/ir.model.access.csv',
        'data/report_paperformat.xml'
    ]
    
    print("🔍 OSUS Invoice Report - Module Readiness Check")
    print("=" * 50)
    
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(module_path, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    print("\n" + "=" * 50)
    if missing_files:
        print(f"❌ {len(missing_files)} required files are missing:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\n🚫 Module is NOT ready for upgrade")
    else:
        print("✅ All required files are present")
        print("\n🎉 Module is READY for upgrade!")
        
        print("\n📝 To upgrade the module in Odoo:")
        print("1. Restart Odoo server")
        print("2. Go to Apps menu")
        print("3. Search for 'OSUS Invoice Report'")
        print("4. Click 'Upgrade' button")
        print("\n⚠️  Make sure to backup your database before upgrading!")

if __name__ == "__main__":
    check_module_readiness()
