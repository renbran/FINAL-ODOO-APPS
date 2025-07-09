#!/usr/bin/env python3
"""
Comprehensive Odoo Module Verification Script
Tests all critical fixes before server restart
"""

import sys
import os
import xml.etree.ElementTree as ET
import ast

def test_xml_files():
    """Test all XML files for syntax errors"""
    print("🔍 Testing XML Files...")
    xml_files = [
        'dynamic_accounts_report/report/aged_receivable_templates.xml',
        'dynamic_accounts_report/report/aged_payable_templates.xml',
        'dynamic_accounts_report/report/general_ledger_templates.xml',
        'dynamic_accounts_report/report/trial_balance.xml',
        'dynamic_accounts_report/report/balance_sheet_report_templates.xml',
        'osus_invoice_report/views/account_move_views.xml'
    ]
    
    all_good = True
    for xml_file in xml_files:
        if os.path.exists(xml_file):
            try:
                ET.parse(xml_file)
                print(f"  ✅ {xml_file}")
            except ET.ParseError as e:
                print(f"  ❌ {xml_file} - ERROR: {e}")
                all_good = False
        else:
            print(f"  ⚠️  {xml_file} - File not found")
    
    return all_good

def test_python_files():
    """Test Python files for syntax errors"""
    print("\n🐍 Testing Python Files...")
    python_files = [
        'commission_ax/models/sale_order.py',
        'osus_invoice_report/models/sale_order.py',
        'osus_invoice_report/models/custom_invoice.py',
        'all_in_one_dynamic_custom_fields/models/dynamic_fields.py',
        'base_accounting_kit/models/account_asset.py',
        'order_status_override/models/order_status.py'
    ]
    
    all_good = True
    for py_file in python_files:
        if os.path.exists(py_file):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
                print(f"  ✅ {py_file}")
            except SyntaxError as e:
                print(f"  ❌ {py_file} - ERROR: {e}")
                all_good = False
        else:
            print(f"  ⚠️  {py_file} - File not found")
    
    return all_good

def check_critical_fixes():
    """Check specific critical fixes"""
    print("\n🔧 Checking Critical Fixes...")
    checks_passed = 0
    total_checks = 0
    
    # Check 1: XML ID ordering in osus_invoice_report
    total_checks += 1
    try:
        with open('osus_invoice_report/views/account_move_views.xml', 'r') as f:
            content = f.read()
        
        kanban_pos = content.find('<record id="view_move_kanban_deals"')
        action_pos = content.find('<record id="action_property_deals_dashboard"')
        
        if kanban_pos < action_pos and kanban_pos != -1 and action_pos != -1:
            print("  ✅ Kanban view defined before action (XML ID order fix)")
            checks_passed += 1
        else:
            print("  ❌ Kanban view not properly ordered before action")
    except Exception as e:
        print(f"  ❌ Error checking XML ID order: {e}")
    
    # Check 2: _valid_field_parameter in dynamic_fields.py
    total_checks += 1
    try:
        with open('all_in_one_dynamic_custom_fields/models/dynamic_fields.py', 'r') as f:
            content = f.read()
        
        if '_valid_field_parameter' in content and '@classmethod' in content:
            print("  ✅ _valid_field_parameter method added to dynamic_fields.py")
            checks_passed += 1
        else:
            print("  ❌ _valid_field_parameter method missing in dynamic_fields.py")
    except Exception as e:
        print(f"  ❌ Error checking dynamic_fields.py: {e}")
    
    # Check 3: _valid_field_parameter in account_asset.py
    total_checks += 1
    try:
        with open('base_accounting_kit/models/account_asset.py', 'r') as f:
            content = f.read()
        
        if '_valid_field_parameter' in content and 'hide' in content:
            print("  ✅ _valid_field_parameter method added to account_asset.py")
            checks_passed += 1
        else:
            print("  ❌ _valid_field_parameter method missing in account_asset.py")
    except Exception as e:
        print(f"  ❌ Error checking account_asset.py: {e}")
    
    # Check 4: Field label changes in commission_ax
    total_checks += 1
    try:
        with open('commission_ax/models/sale_order.py', 'r') as f:
            content = f.read()
        
        if 'Manager Commission (Legacy)' in content and 'Director Commission (Legacy)' in content:
            print("  ✅ Field labels updated in commission_ax/models/sale_order.py")
            checks_passed += 1
        else:
            print("  ❌ Field labels not properly updated in commission_ax")
    except Exception as e:
        print(f"  ❌ Error checking commission_ax field labels: {e}")
    
    return checks_passed, total_checks

def main():
    print("Starting comprehensive verification...\n")
    
    # Test XML syntax
    xml_ok = test_xml_files()
    
    # Test Python syntax
    python_ok = test_python_files()
    
    # Check critical fixes
    fixes_passed, total_fixes = check_critical_fixes()
    
    # Summary
    print(f"\n📊 VERIFICATION SUMMARY")
    print(f"{'='*50}")
    print(f"XML Files: {'✅ PASS' if xml_ok else '❌ FAIL'}")
    print(f"Python Files: {'✅ PASS' if python_ok else '❌ FAIL'}")
    print(f"Critical Fixes: {fixes_passed}/{total_fixes} {'✅ PASS' if fixes_passed == total_fixes else '❌ FAIL'}")
    
    overall_status = xml_ok and python_ok and (fixes_passed == total_fixes)
    print(f"\nOVERALL STATUS: {'🚀 READY FOR STARTUP' if overall_status else '⚠️ ISSUES DETECTED'}")
    
    return overall_status

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
