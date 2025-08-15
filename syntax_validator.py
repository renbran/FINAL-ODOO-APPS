#!/usr/bin/env python3
"""
Quick syntax validation script for order_status_override module
"""

import os
import py_compile
import xml.etree.ElementTree as ET
import sys

def validate_python_files():
    """Validate Python syntax"""
    python_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    errors = []
    for py_file in python_files:
        try:
            py_compile.compile(py_file, doraise=True)
            print(f"✅ {py_file} - Python syntax OK")
        except py_compile.PyCompileError as e:
            errors.append(f"❌ {py_file} - {str(e)}")
            print(f"❌ {py_file} - {str(e)}")
    
    return errors

def validate_xml_files():
    """Validate XML syntax"""
    xml_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    
    errors = []
    for xml_file in xml_files:
        try:
            ET.parse(xml_file)
            print(f"✅ {xml_file} - XML syntax OK")
        except ET.ParseError as e:
            errors.append(f"❌ {xml_file} - {str(e)}")
            print(f"❌ {xml_file} - {str(e)}")
        except Exception as e:
            errors.append(f"❌ {xml_file} - {str(e)}")
            print(f"❌ {xml_file} - {str(e)}")
    
    return errors

def main():
    print("="*60)
    print("ORDER STATUS OVERRIDE - SYNTAX VALIDATION")
    print("="*60)
    
    print("\n🐍 VALIDATING PYTHON FILES...")
    python_errors = validate_python_files()
    
    print("\n📄 VALIDATING XML FILES...")
    xml_errors = validate_xml_files()
    
    total_errors = len(python_errors) + len(xml_errors)
    
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    if total_errors == 0:
        print("✅ ALL FILES PASSED SYNTAX VALIDATION!")
        print("🚀 Module is ready for deployment!")
    else:
        print(f"❌ {total_errors} SYNTAX ERRORS FOUND:")
        for error in python_errors + xml_errors:
            print(f"   {error}")
    
    return total_errors

if __name__ == "__main__":
    os.chdir("order_status_override")
    exit_code = main()
    sys.exit(1 if exit_code > 0 else 0)
