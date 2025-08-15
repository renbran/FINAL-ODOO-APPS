#!/usr/bin/env python3
"""
Comprehensive validation script for account_payment_approval module
Tests syntax, imports, and basic module structure
"""

import sys
import os
import py_compile
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_python_syntax(file_path):
    """Validate Python file syntax"""
    try:
        py_compile.compile(file_path, doraise=True)
        return True, None
    except Exception as e:
        return False, str(e)

def validate_xml_syntax(file_path):
    """Validate XML file syntax"""
    try:
        ET.parse(file_path)
        return True, None
    except Exception as e:
        return False, str(e)

def main():
    """Main validation function"""
    module_path = Path("account_payment_approval")
    
    if not module_path.exists():
        print("‚ùå Module directory not found!")
        return False
    
    print("üîç Starting comprehensive module validation...")
    print("=" * 60)
    
    # Track validation results
    errors = []
    warnings = []
    
    # Validate Python files
    print("\nüìù Validating Python files...")
    python_files = list(module_path.rglob("*.py"))
    
    for py_file in python_files:
        print(f"  Checking: {py_file}")
        success, error = validate_python_syntax(py_file)
        if success:
            print(f"    ‚úÖ Syntax OK")
        else:
            print(f"    ‚ùå Syntax Error: {error}")
            errors.append(f"Python syntax error in {py_file}: {error}")
    
    # Validate XML files
    print("\nüóÉÔ∏è  Validating XML files...")
    xml_files = list(module_path.rglob("*.xml"))
    
    for xml_file in xml_files:
        print(f"  Checking: {xml_file}")
        success, error = validate_xml_syntax(xml_file)
        if success:
            print(f"    ‚úÖ XML OK")
        else:
            print(f"    ‚ùå XML Error: {error}")
            errors.append(f"XML syntax error in {xml_file}: {error}")
    
    # Check manifest
    print("\nüìã Validating manifest...")
    manifest_file = module_path / "__manifest__.py"
    if manifest_file.exists():
        success, error = validate_python_syntax(manifest_file)
        if success:
            print("    ‚úÖ Manifest syntax OK")
        else:
            print(f"    ‚ùå Manifest error: {error}")
            errors.append(f"Manifest error: {error}")
    else:
        print("    ‚ö†Ô∏è  No manifest file found")
        warnings.append("No __manifest__.py file found")
    
    # Check key files exist
    print("\nüóÇÔ∏è  Checking key files...")
    key_files = [
        "models/__init__.py",
        "wizards/__init__.py", 
        "views/payment_report_wizard.xml",
        "security/payment_voucher_security.xml"
    ]
    
    for key_file in key_files:
        file_path = module_path / key_file
        if file_path.exists():
            print(f"    ‚úÖ {key_file}")
        else:
            print(f"    ‚ùå Missing: {key_file}")
            errors.append(f"Missing key file: {key_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("üìä VALIDATION SUMMARY")
    print("=" * 60)
    
    if not errors and not warnings:
        print("üéâ ALL VALIDATIONS PASSED!")
        print("‚úÖ Module appears ready for deployment")
        return True
    
    if warnings:
        print(f"‚ö†Ô∏è  {len(warnings)} WARNING(S):")
        for warning in warnings:
            print(f"   ‚Ä¢ {warning}")
    
    if errors:
        print(f"‚ùå {len(errors)} ERROR(S):")
        for error in errors:
            print(f"   ‚Ä¢ {error}")
        print("\nüí° Please fix these errors before deployment")
        return False
    
    if warnings and not errors:
        print("‚ö†Ô∏è  Module has warnings but may still work")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
