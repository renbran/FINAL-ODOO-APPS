#!/usr/bin/env python3
"""
Script to validate the automated_employee_announce module structure and syntax.
"""

import os
import ast
import xml.etree.ElementTree as ET
import sys

def validate_python_files(module_path):
    """Validate Python files syntax."""
    print("🔍 Validating Python files...")
    python_files = []
    
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    errors = []
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for merge conflict markers
            if any(marker in content for marker in ['<<<<<<< HEAD', '=======', '>>>>>>> staging']):
                errors.append(f"❌ {py_file}: Contains merge conflict markers")
                continue
                
            # Check syntax
            ast.parse(content)
            print(f"✅ {py_file}: Valid Python syntax")
            
        except SyntaxError as e:
            errors.append(f"❌ {py_file}: Syntax error - {e}")
        except Exception as e:
            errors.append(f"❌ {py_file}: Error - {e}")
    
    return errors

def validate_xml_files(module_path):
    """Validate XML files syntax."""
    print("🔍 Validating XML files...")
    xml_files = []
    
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    
    errors = []
    for xml_file in xml_files:
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for merge conflict markers
            if any(marker in content for marker in ['<<<<<<< HEAD', '=======', '>>>>>>> staging']):
                errors.append(f"❌ {xml_file}: Contains merge conflict markers")
                continue
            
            # Check XML syntax
            ET.parse(xml_file)
            print(f"✅ {xml_file}: Valid XML syntax")
            
        except ET.ParseError as e:
            errors.append(f"❌ {xml_file}: XML syntax error - {e}")
        except Exception as e:
            errors.append(f"❌ {xml_file}: Error - {e}")
    
    return errors

def validate_csv_files(module_path):
    """Validate CSV files."""
    print("🔍 Validating CSV files...")
    csv_files = []
    
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    errors = []
    for csv_file in csv_files:
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for merge conflict markers
            if any(marker in content for marker in ['<<<<<<< HEAD', '=======', '>>>>>>> staging']):
                errors.append(f"❌ {csv_file}: Contains merge conflict markers")
                continue
                
            print(f"✅ {csv_file}: No merge conflicts found")
            
        except Exception as e:
            errors.append(f"❌ {csv_file}: Error - {e}")
    
    return errors

def main():
    module_path = "automated_employee_announce"
    
    if not os.path.exists(module_path):
        print(f"❌ Module path {module_path} does not exist!")
        sys.exit(1)
    
    print(f"🚀 Validating module: {module_path}")
    print("=" * 50)
    
    all_errors = []
    
    # Validate Python files
    all_errors.extend(validate_python_files(module_path))
    
    # Validate XML files  
    all_errors.extend(validate_xml_files(module_path))
    
    # Validate CSV files
    all_errors.extend(validate_csv_files(module_path))
    
    print("\n" + "=" * 50)
    
    if all_errors:
        print("❌ VALIDATION FAILED!")
        print("\nErrors found:")
        for error in all_errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print("✅ VALIDATION SUCCESSFUL!")
        print("All files are valid and ready for installation.")
        sys.exit(0)

if __name__ == "__main__":
    main()
