#!/usr/bin/env python3
"""
XML Validation Script for Odoo Module
Validates all XML files in the account_payment_final module
"""
import os
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_xml_file(filepath):
    """Validate a single XML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the XML
        ET.fromstring(content)
        return True, None
    except ET.ParseError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def main():
    """Main validation function"""
    module_path = Path("account_payment_final")
    xml_files = []
    
    # Find all XML files in the module
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(Path(root) / file)
    
    print(f"Found {len(xml_files)} XML files to validate:")
    print("-" * 50)
    
    all_valid = True
    for xml_file in xml_files:
        is_valid, error = validate_xml_file(xml_file)
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"{status}: {xml_file}")
        
        if not is_valid:
            print(f"   Error: {error}")
            all_valid = False
    
    print("-" * 50)
    if all_valid:
        print("🎉 All XML files are valid!")
    else:
        print("❌ Some XML files have errors!")
    
    return all_valid

if __name__ == "__main__":
    main()
