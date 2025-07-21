#!/usr/bin/env python3
"""
XML Validation Script for Odoo Modules
This script validates XML files for proper syntax and structure.
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_xml_file(file_path):
    """Validate a single XML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse XML to check for syntax errors
        ET.fromstring(content)
        return True, None
    except ET.ParseError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def main():
    print("=== XML Validation for Accounting PDF Reports ===\n")
    
    # Files to validate
    xml_files = [
        "accounting_pdf_reports/wizard/account_common_partner_view.xml",
        "accounting_pdf_reports/wizard/partner_ledger.xml", 
        "account_payment_approval/reports/payment_voucher_report.xml",
        "account_payment_approval/reports/payment_voucher_template.xml",
        "account_payment_approval/views/account_payment_views.xml"
    ]
    
    errors_found = False
    
    for xml_file in xml_files:
        if os.path.exists(xml_file):
            valid, error = validate_xml_file(xml_file)
            if valid:
                print(f"✅ {xml_file} - Valid")
            else:
                print(f"❌ {xml_file} - Error: {error}")
                errors_found = True
        else:
            print(f"⚠️  {xml_file} - File not found")
    
    print("\n" + "="*50)
    if errors_found:
        print("❌ Some XML files have errors. Please fix them before restarting Odoo.")
    else:
        print("✅ All XML files are valid!")
        print("\nNext steps:")
        print("1. Restart Odoo server")
        print("2. Update Apps List")
        print("3. Upgrade affected modules")
    
    return not errors_found

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
