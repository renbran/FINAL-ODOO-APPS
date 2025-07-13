#!/usr/bin/env python3
"""
Module validation script for OSUS Invoice Report
This script checks for common issues that could prevent module loading
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_xml_files(module_path):
    """Validate XML files for syntax errors"""
    print("Validating XML files...")
    xml_files = []
    
    # Find all XML files
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    
    errors = []
    for xml_file in xml_files:
        try:
            ET.parse(xml_file)
            print(f"✓ {os.path.relpath(xml_file, module_path)}")
        except ET.ParseError as e:
            errors.append(f"✗ {os.path.relpath(xml_file, module_path)}: {e}")
            print(f"✗ {os.path.relpath(xml_file, module_path)}: {e}")
    
    return errors

def validate_manifest(module_path):
    """Validate manifest file"""
    print("\nValidating manifest...")
    manifest_path = os.path.join(module_path, '__manifest__.py')
    
    if not os.path.exists(manifest_path):
        return ["__manifest__.py not found"]
    
    try:
        with open(manifest_path, 'r') as f:
            content = f.read()
        
        # Try to evaluate the manifest
        manifest = eval(content)
        
        print(f"✓ Module name: {manifest.get('name', 'Unknown')}")
        print(f"✓ Version: {manifest.get('version', 'Unknown')}")
        print(f"✓ Dependencies: {manifest.get('depends', [])}")
        
        # Check if all data files exist
        missing_files = []
        data_files = manifest.get('data', [])
        
        for data_file in data_files:
            file_path = os.path.join(module_path, data_file)
            if not os.path.exists(file_path):
                missing_files.append(data_file)
            else:
                print(f"✓ Data file: {data_file}")
        
        if missing_files:
            print(f"✗ Missing data files: {missing_files}")
            return missing_files
        
        return []
        
    except Exception as e:
        return [f"Error reading manifest: {e}"]

def validate_python_files(module_path):
    """Basic validation of Python files"""
    print("\nValidating Python files...")
    python_files = []
    
    # Find all Python files
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.py') and not file.startswith('test_'):
                python_files.append(os.path.join(root, file))
    
    errors = []
    for py_file in python_files:
        try:
            with open(py_file, 'r') as f:
                content = f.read()
            
            # Basic syntax check
            compile(content, py_file, 'exec')
            print(f"✓ {os.path.relpath(py_file, module_path)}")
            
        except SyntaxError as e:
            error_msg = f"✗ {os.path.relpath(py_file, module_path)}: Syntax error at line {e.lineno}: {e.msg}"
            errors.append(error_msg)
            print(error_msg)
        except Exception as e:
            error_msg = f"✗ {os.path.relpath(py_file, module_path)}: {e}"
            errors.append(error_msg)
            print(error_msg)
    
    return errors

def main():
    module_path = r"d:\RUNNING APPS\ready production\osus-main\odoo17_final\osus_invoice_report"
    
    if not os.path.exists(module_path):
        print(f"Module path not found: {module_path}")
        return
    
    print(f"Validating module: {module_path}")
    print("=" * 50)
    
    # Validate manifest
    manifest_errors = validate_manifest(module_path)
    
    # Validate XML files
    xml_errors = validate_xml_files(module_path)
    
    # Validate Python files
    python_errors = validate_python_files(module_path)
    
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    
    total_errors = len(manifest_errors) + len(xml_errors) + len(python_errors)
    
    if total_errors == 0:
        print("✓ All validations passed! Module should be loadable.")
    else:
        print(f"✗ Found {total_errors} error(s):")
        
        if manifest_errors:
            print("\nManifest errors:")
            for error in manifest_errors:
                print(f"  - {error}")
        
        if xml_errors:
            print("\nXML errors:")
            for error in xml_errors:
                print(f"  - {error}")
        
        if python_errors:
            print("\nPython errors:")
            for error in python_errors:
                print(f"  - {error}")

if __name__ == "__main__":
    main()
