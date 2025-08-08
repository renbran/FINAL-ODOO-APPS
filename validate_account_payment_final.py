#!/usr/bin/env python3
"""
Test script to validate the account_payment_final module structure and syntax
"""

import os
import sys
import xml.etree.ElementTree as ET
import py_compile
import tempfile

def validate_module_structure():
    """Validate the module has proper structure"""
    module_path = "account_payment_final"
    
    required_files = [
        "__init__.py",
        "__manifest__.py",
        "models/__init__.py",
        "models/account_payment.py",
        "views/account_payment_views.xml",
        "security/payment_security.xml",
        "security/ir.model.access.csv"
    ]
    
    print("🔍 Checking module structure...")
    missing_files = []
    
    for file_path in required_files:
        full_path = os.path.join(module_path, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files found!")
    return True

def validate_python_syntax():
    """Validate Python files syntax"""
    python_files = [
        "account_payment_final/__init__.py",
        "account_payment_final/__manifest__.py",
        "account_payment_final/models/__init__.py",
        "account_payment_final/models/account_payment.py",
        "account_payment_final/models/res_company.py",
        "account_payment_final/models/res_config_settings.py",
    ]
    
    print("\n🐍 Checking Python syntax...")
    
    for py_file in python_files:
        if os.path.exists(py_file):
            try:
                py_compile.compile(py_file, doraise=True)
                print(f"✅ {py_file}")
            except py_compile.PyCompileError as e:
                print(f"❌ {py_file}: {e}")
                return False
        else:
            print(f"⚠️  {py_file}: File not found")
    
    print("✅ All Python files have valid syntax!")
    return True

def validate_xml_syntax():
    """Validate XML files syntax"""
    xml_files = [
        "account_payment_final/views/account_payment_views.xml",
        "account_payment_final/security/payment_security.xml",
    ]
    
    print("\n📄 Checking XML syntax...")
    
    for xml_file in xml_files:
        if os.path.exists(xml_file):
            try:
                ET.parse(xml_file)
                print(f"✅ {xml_file}")
            except ET.ParseError as e:
                print(f"❌ {xml_file}: {e}")
                return False
        else:
            print(f"⚠️  {xml_file}: File not found")
    
    print("✅ All XML files have valid syntax!")
    return True

def validate_action_methods():
    """Check if all action methods referenced in views exist in the model"""
    print("\n🎯 Checking action methods...")
    
    # Read the model file
    model_file = "account_payment_final/models/account_payment.py"
    if not os.path.exists(model_file):
        print(f"❌ Model file not found: {model_file}")
        return False
    
    with open(model_file, 'r', encoding='utf-8') as f:
        model_content = f.read()
    
    # Read the view file
    view_file = "account_payment_final/views/account_payment_views.xml"
    if not os.path.exists(view_file):
        print(f"❌ View file not found: {view_file}")
        return False
    
    with open(view_file, 'r', encoding='utf-8') as f:
        view_content = f.read()
    
    # Extract action methods from views
    import re
    action_pattern = r'name="(action_[^"]+)"'
    view_actions = set(re.findall(action_pattern, view_content))
    
    missing_actions = []
    for action in view_actions:
        if f"def {action}(" not in model_content:
            missing_actions.append(action)
        else:
            print(f"✅ {action}")
    
    if missing_actions:
        print(f"❌ Missing action methods: {missing_actions}")
        return False
    
    print("✅ All action methods found in model!")
    return True

def main():
    """Main validation function"""
    print("🚀 Account Payment Final Module Validation")
    print("=" * 50)
    
    # Change to the module directory
    if not os.path.exists("account_payment_final"):
        print("❌ Module directory 'account_payment_final' not found!")
        print("Make sure you're running this script from the Odoo addons directory.")
        return False
    
    checks = [
        validate_module_structure,
        validate_python_syntax,
        validate_xml_syntax,
        validate_action_methods
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All validations passed! Module is ready for installation.")
        return True
    else:
        print("❌ Some validations failed. Please fix the issues before installing.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
