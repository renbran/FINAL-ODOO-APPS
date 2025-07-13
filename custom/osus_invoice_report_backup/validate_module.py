#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSUS Invoice Report Module Validation Script
Validates the module structure and dependencies for production deployment.
"""

import os
import sys
from pathlib import Path

def validate_module_structure():
    """Validate the module file structure."""
    module_path = Path(__file__).parent
    required_files = [
        '__init__.py',
        '__manifest__.py', 
        'README.md',
        'models/__init__.py',
        'models/custom_reports.py',
        'views/account_move_views.xml',
        'views/report_invoice.xml',
        'views/report_bills.xml',
        'views/report_receipt.xml',
        'security/ir.model.access.csv',
        'data/report_paperformat.xml',
        'static/src/css/report_style.css'
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = module_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files present")
        return True

def validate_manifest():
    """Validate the manifest file."""
    try:
        manifest_path = Path(__file__).parent / '__manifest__.py'
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_content = f.read()
        
        # Check for required keys
        required_keys = ['name', 'version', 'depends', 'data', 'installable']
        for key in required_keys:
            if f"'{key}'" not in manifest_content and f'"{key}"' not in manifest_content:
                print(f"❌ Missing required key in manifest: {key}")
                return False
        
        print("✅ Manifest structure valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading manifest: {e}")
        return False

def validate_dependencies():
    """Check if required dependencies are available."""
    try:
        import num2words
        print("✅ num2words dependency available")
        return True
    except ImportError:
        print("❌ Missing dependency: num2words")
        print("   Install with: pip install num2words")
        return False

def validate_xml_syntax():
    """Basic XML syntax validation."""
    import xml.etree.ElementTree as ET
    
    xml_files = [
        'views/account_move_views.xml',
        'views/report_invoice.xml', 
        'views/report_bills.xml',
        'views/report_receipt.xml',
        'data/report_paperformat.xml'
    ]
    
    module_path = Path(__file__).parent
    
    for xml_file in xml_files:
        try:
            ET.parse(module_path / xml_file)
            print(f"✅ {xml_file} syntax valid")
        except ET.ParseError as e:
            print(f"❌ XML syntax error in {xml_file}: {e}")
            return False
        except FileNotFoundError:
            print(f"❌ File not found: {xml_file}")
            return False
    
    return True

def main():
    """Run all validation checks."""
    print("🔍 OSUS Invoice Report Module Validation")
    print("=" * 50)
    
    checks = [
        ("Module Structure", validate_module_structure),
        ("Manifest File", validate_manifest),
        ("Dependencies", validate_dependencies),
        ("XML Syntax", validate_xml_syntax)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n📋 Checking {check_name}...")
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ Error during {check_name}: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All validation checks passed! Module is ready for production.")
        print("\n📥 Installation Steps:")
        print("1. Copy the module to your Odoo addons directory")
        print("2. Update the apps list in Odoo")
        print("3. Install the 'OSUS Invoice Report' module")
        print("4. Test the print buttons in invoice forms")
    else:
        print("❌ Some validation checks failed. Please fix the issues before deployment.")
        sys.exit(1)

if __name__ == '__main__':
    main()
