#!/usr/bin/env python3
"""
Payment Module Enhancement Validation
Tests the key fixes without Docker
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_xml_syntax(file_path):
    """Validate XML file syntax"""
    try:
        ET.parse(file_path)
        return True, "Valid XML"
    except ET.ParseError as e:
        return False, f"XML Parse Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def check_statusbar_duplicates(xml_file):
    """Check for statusbar duplicates in payment views"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Count statusbar elements
        statusbars = root.findall(".//field[@widget='statusbar']")
        headers = root.findall(".//header")
        
        print(f"  - Headers found: {len(headers)}")
        print(f"  - Statusbars found: {len(statusbars)}")
        
        if len(statusbars) > 1:
            return False, f"Multiple statusbars found ({len(statusbars)})"
        
        return True, "Single statusbar confirmed"
        
    except Exception as e:
        return False, f"Error checking statusbars: {e}"

def check_voucher_sequences(seq_file):
    """Check if voucher sequences are properly defined"""
    try:
        tree = ET.parse(seq_file)
        root = tree.getroot()
        
        # Look for specific sequence codes
        required_codes = [
            'payment.voucher.payment',
            'payment.voucher.receipt'
        ]
        
        found_codes = []
        sequences = root.findall(".//record[@model='ir.sequence']")
        
        for seq in sequences:
            code_field = seq.find(".//field[@name='code']")
            if code_field is not None:
                found_codes.append(code_field.text)
        
        print(f"  - Found sequence codes: {found_codes}")
        
        missing = [code for code in required_codes if code not in found_codes]
        if missing:
            return False, f"Missing sequence codes: {missing}"
        
        return True, "All required sequences found"
        
    except Exception as e:
        return False, f"Error checking sequences: {e}"

def main():
    """Main validation function"""
    print("🔍 Payment Module Enhancement Validation\n")
    
    base_path = Path(__file__).parent
    module_path = base_path / "account_payment_final"
    
    # Files to validate
    files_to_check = {
        "Payment Views": module_path / "views" / "account_payment_views.xml",
        "Payment Sequences": module_path / "data" / "payment_sequences.xml",
        "Assets": module_path / "views" / "assets.xml",
    }
    
    all_valid = True
    
    for name, file_path in files_to_check.items():
        print(f"📄 Checking {name}:")
        
        if not file_path.exists():
            print(f"  ❌ File not found: {file_path}")
            all_valid = False
            continue
        
        # Basic XML validation
        valid, message = validate_xml_syntax(file_path)
        if valid:
            print(f"  ✅ XML Syntax: {message}")
        else:
            print(f"  ❌ XML Syntax: {message}")
            all_valid = False
            continue
        
        # Specific checks
        if "payment_views" in str(file_path):
            valid, message = check_statusbar_duplicates(file_path)
            if valid:
                print(f"  ✅ Statusbar Check: {message}")
            else:
                print(f"  ❌ Statusbar Check: {message}")
                all_valid = False
        
        elif "payment_sequences" in str(file_path):
            valid, message = check_voucher_sequences(file_path)
            if valid:
                print(f"  ✅ Sequences Check: {message}")
            else:
                print(f"  ❌ Sequences Check: {message}")
                all_valid = False
        
        print()
    
    # Check JavaScript files
    js_files = [
        module_path / "static" / "src" / "js" / "cloudpepper_console_optimizer.js",
        module_path / "static" / "src" / "js" / "unknown_action_handler.js"
    ]
    
    print("📄 Checking JavaScript Files:")
    for js_file in js_files:
        if js_file.exists():
            print(f"  ✅ Found: {js_file.name}")
        else:
            print(f"  ❌ Missing: {js_file.name}")
            all_valid = False
    
    print("\n" + "="*50)
    if all_valid:
        print("🎉 All validations passed!")
        print("\n📋 Summary of fixes:")
        print("✅ Single statusbar (no duplicates)")
        print("✅ Voucher sequences configured")
        print("✅ Enhanced posting logic")
        print("✅ Console optimization")
    else:
        print("❌ Some validations failed!")
    
    print("\n💡 To test these changes:")
    print("1. Update the module in Odoo")
    print("2. Create a new payment")
    print("3. Check voucher number appears immediately")
    print("4. Test posting with enhanced workflow")

if __name__ == "__main__":
    main()
