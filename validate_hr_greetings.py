#!/usr/bin/env python3
"""
Quick validation script for comprehensive_greetings module
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_module():
    """Validate the simplified comprehensive_greetings module"""
    print("🔍 Validating OSUS HR Greetings module...")
    
    module_path = Path('comprehensive_greetings')
    
    # Check required files exist
    required_files = [
        '__init__.py',
        '__manifest__.py',
        'models/__init__.py',
        'models/hr_employee.py',
        'security/greetings_security.xml',
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'data/ir_cron.xml',
        'data/mail_template_birthday.xml',
        'data/mail_template_anniversary.xml',
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = module_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    # Validate XML files
    xml_files = [
        'security/greetings_security.xml',
        'views/hr_employee_views.xml',
        'data/ir_cron.xml',
        'data/mail_template_birthday.xml',
        'data/mail_template_anniversary.xml',
    ]
    
    print(f"\n🔍 Validating XML files...")
    for xml_file in xml_files:
        try:
            ET.parse(module_path / xml_file)
            print(f"✅ {xml_file} - valid XML")
        except ET.ParseError as e:
            print(f"❌ {xml_file} - XML error: {e}")
            return False
    
    print(f"\n🎉 Module validation passed!")
    print(f"✅ All required files present")
    print(f"✅ All XML files are valid") 
    print(f"✅ Module ready for installation")
    
    return True

if __name__ == "__main__":
    validate_module()
