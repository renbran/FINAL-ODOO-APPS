#!/usr/bin/env python3
"""
Comprehensive validation script for account_payment_final module
This script validates all XML files, Python syntax, and module structure
"""

import os
import sys
import xml.etree.ElementTree as ET
import ast
from pathlib import Path

def validate_xml_file(file_path):
    """Validate XML syntax and structure"""
    try:
        ET.parse(file_path)
        return True, "Valid"
    except ET.ParseError as e:
        return False, f"ParseError: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def validate_python_file(file_path):
    """Validate Python syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, "Valid"
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Main validation function"""
    module_path = Path("account_payment_final")
    
    if not module_path.exists():
        print(f"❌ Module directory {module_path} not found!")
        return False
    
    print("🔍 Validating account_payment_final module...")
    print("=" * 50)
    
    validation_passed = True
    
    # Validate XML files
    xml_files = list(module_path.rglob("*.xml"))
    print(f"\n📄 Validating {len(xml_files)} XML files:")
    
    for xml_file in xml_files:
        is_valid, message = validate_xml_file(xml_file)
        status = "✅" if is_valid else "❌"
        print(f"  {status} {xml_file.relative_to(module_path)}: {message}")
        if not is_valid:
            validation_passed = False
    
    # Validate Python files
    python_files = list(module_path.rglob("*.py"))
    print(f"\n🐍 Validating {len(python_files)} Python files:")
    
    for py_file in python_files:
        is_valid, message = validate_python_file(py_file)
        status = "✅" if is_valid else "❌"
        print(f"  {status} {py_file.relative_to(module_path)}: {message}")
        if not is_valid:
            validation_passed = False
    
    # Check critical files exist
    critical_files = [
        "__manifest__.py",
        "models/__init__.py",
        "models/account_payment.py",
        "views/account_payment_views.xml",
        "security/ir.model.access.csv",
        "security/payment_security.xml"
    ]
    
    print(f"\n📋 Checking critical files:")
    for file_path in critical_files:
        full_path = module_path / file_path
        exists = full_path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")
        if not exists:
            validation_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if validation_passed:
        print("✅ ALL VALIDATIONS PASSED! Module is ready for deployment.")
        return True
    else:
        print("❌ VALIDATION FAILED! Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
