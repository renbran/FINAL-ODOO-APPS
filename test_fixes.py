#!/usr/bin/env python3
"""
Test script to verify critical Odoo module fixes
"""

import sys
import os

def test_xml_syntax():
    """Test XML templates for syntax errors"""
    xml_files = [
        'dynamic_accounts_report/report/aged_receivable_templates.xml',
        'dynamic_accounts_report/report/aged_payable_templates.xml',
        'dynamic_accounts_report/report/general_ledger_templates.xml',
        'dynamic_accounts_report/report/trial_balance.xml',
        'dynamic_accounts_report/report/balance_sheet_report_templates.xml'
    ]
    
    import xml.etree.ElementTree as ET
    
    for xml_file in xml_files:
        if os.path.exists(xml_file):
            try:
                ET.parse(xml_file)
                print(f"✓ {xml_file} - XML syntax OK")
            except ET.ParseError as e:
                print(f"✗ {xml_file} - XML syntax error: {e}")
        else:
            print(f"? {xml_file} - File not found")

def test_python_syntax():
    """Test Python files for syntax errors"""
    python_files = [
        'commission_ax/models/sale_order.py',
        'osus_invoice_report/models/sale_order.py',
        'osus_invoice_report/models/custom_invoice.py',
        'all_in_one_dynamic_custom_fields/models/dynamic_fields.py',
        'base_accounting_kit/models/account_asset.py',
        'order_status_override/models/order_status.py'
    ]
    
    import ast
    
    for py_file in python_files:
        if os.path.exists(py_file):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
                print(f"✓ {py_file} - Python syntax OK")
            except SyntaxError as e:
                print(f"✗ {py_file} - Syntax error: {e}")
        else:
            print(f"? {py_file} - File not found")

def main():
    print("Testing XML syntax...")
    test_xml_syntax()
    print("\nTesting Python syntax...")
    test_python_syntax()
    print("\nTest completed!")

if __name__ == "__main__":
    main()
