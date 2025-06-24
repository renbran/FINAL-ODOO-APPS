#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Validation Script for commission_fields
This script validates the commission_fields module structure and suggests installation steps.
"""

import os
import sys
import ast
from xml.etree import ElementTree as ET

def validate_python_syntax(file_path):
    """Validate Python file syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Syntax Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def validate_xml_syntax(file_path):
    """Validate XML file syntax"""
    try:
        ET.parse(file_path)
        return True, "OK"
    except ET.ParseError as e:
        return False, f"XML Parse Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def check_action_methods(file_path):
    """Check if action methods are defined in the Python file"""
    required_methods = [
        'action_pay_commission',
        'action_reset_commission',
        'action_confirm_commission',
        'action_calculate_commission',
        'action_reject_commission',
        'action_create_commission_purchase_order',
        'action_view_related_purchase_orders'
    ]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        found_methods = []
        missing_methods = []
        
        for method in required_methods:
            if f"def {method}(" in content:
                found_methods.append(method)
            else:
                missing_methods.append(method)
        
        return found_methods, missing_methods
    except Exception as e:
        return [], required_methods

def main():
    print("🔍 Commission Fields Module Validation")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('commission_fields'):
        print("❌ commission_fields directory not found!")
        print("Please run this script from the odoo17_final directory")
        return
    
    # Validate Python files
    print("\n📝 Validating Python Files:")
    python_files = [
        'commission_fields/__init__.py',
        'commission_fields/models/__init__.py',
        'commission_fields/models/sale_order.py'
    ]
    
    all_python_valid = True
    for file_path in python_files:
        if os.path.exists(file_path):
            valid, msg = validate_python_syntax(file_path)
            status = "✅" if valid else "❌"
            print(f"  {status} {file_path}: {msg}")
            if not valid:
                all_python_valid = False
        else:
            print(f"  ❌ {file_path}: File not found")
            all_python_valid = False
    
    # Validate XML files
    print("\n🔧 Validating XML Files:")
    xml_files = [
        'commission_fields/views/sale_order_views.xml',
        'commission_fields/__manifest__.py'
    ]
    
    all_xml_valid = True
    for file_path in xml_files:
        if file_path.endswith('.xml'):
            if os.path.exists(file_path):
                valid, msg = validate_xml_syntax(file_path)
                status = "✅" if valid else "❌"
                print(f"  {status} {file_path}: {msg}")
                if not valid:
                    all_xml_valid = False
            else:
                print(f"  ❌ {file_path}: File not found")
                all_xml_valid = False
        else:
            # Check if __manifest__.py exists
            if os.path.exists(file_path):
                print(f"  ✅ {file_path}: Found")
            else:
                print(f"  ❌ {file_path}: File not found")
                all_xml_valid = False
    
    # Check action methods
    print("\n⚡ Checking Action Methods:")
    sale_order_path = 'commission_fields/models/sale_order.py'
    if os.path.exists(sale_order_path):
        found_methods, missing_methods = check_action_methods(sale_order_path)
        
        for method in found_methods:
            print(f"  ✅ {method}")
        
        for method in missing_methods:
            print(f"  ❌ {method} - MISSING")
        
        if not missing_methods:
            print("  🎉 All required action methods are present!")
    
    # Summary and recommendations
    print("\n📋 Summary:")
    if all_python_valid and all_xml_valid and not missing_methods:
        print("✅ Module structure is valid!")
        print("\n🚀 Installation Steps:")
        print("1. Stop the Odoo server")
        print("2. If the module is already installed, upgrade it:")
        print("   - Go to Apps menu")
        print("   - Remove 'Apps' filter")
        print("   - Search for 'Sales Commission Management'")
        print("   - Click 'Upgrade' button")
        print("3. If the module is not installed:")
        print("   - Click 'Install' button")
        print("4. Restart the Odoo server")
        print("5. Clear browser cache and refresh")
    else:
        print("❌ Module has issues that need to be fixed!")
        print("Please fix the errors above before installing.")

if __name__ == "__main__":
    main()
