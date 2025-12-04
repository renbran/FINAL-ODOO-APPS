#!/usr/bin/env python3
"""
Validation script for commission_ax module
Checks for the presence of commission_lines_count field and its dependencies
"""

import sys
import os

def validate_field_exists():
    """Check if commission_lines_count field exists in sale_order.py"""
    file_path = 'models/sale_order.py'
    
    if not os.path.exists(file_path):
        print("❌ ERROR: sale_order.py not found!")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for field definition
    if 'commission_lines_count' not in content:
        print("❌ ERROR: commission_lines_count field not found in sale_order.py")
        return False
    
    print("✅ commission_lines_count field exists")
    
    # Check for compute method
    if '_compute_commission_lines_count' not in content:
        print("❌ ERROR: _compute_commission_lines_count method not found")
        return False
    
    print("✅ _compute_commission_lines_count method exists")
    
    # Check for @api.depends decorator
    if '@api.depends' not in content:
        print("⚠️  WARNING: @api.depends decorator not found (this is unusual)")
    else:
        print("✅ @api.depends decorator present")
    
    return True

def check_xml_syntax():
    """Basic XML syntax check for sale_order.xml"""
    import xml.etree.ElementTree as ET
    
    file_path = 'views/sale_order.xml'
    
    if not os.path.exists(file_path):
        print("❌ ERROR: sale_order.xml not found!")
        return False
    
    try:
        ET.parse(file_path)
        print("✅ sale_order.xml is valid XML")
        return True
    except ET.ParseError as e:
        print(f"❌ ERROR: XML parsing error in sale_order.xml: {e}")
        return False

def main():
    print("="*70)
    print("COMMISSION_AX MODULE VALIDATION")
    print("="*70)
    print()
    
    # Change to module directory
    module_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(module_dir)
    
    print("Module Directory:", module_dir)
    print()
    
    results = []
    
    print("1. Checking field definition...")
    results.append(validate_field_exists())
    print()
    
    print("2. Checking XML syntax...")
    results.append(check_xml_syntax())
    print()
    
    print("="*70)
    if all(results):
        print("✅ ALL CHECKS PASSED - Module is ready for deployment")
        print("="*70)
        print()
        print("Next steps:")
        print("1. SSH to CloudPepper: ssh user@cloudpepper.site")
        print("2. Update module: odoo -u commission_ax --stop-after-init")
        print("3. Restart Odoo: sudo systemctl restart odoo")
        print("4. Monitor logs: tail -f /var/log/odoo/odoo.log")
        return 0
    else:
        print("❌ VALIDATION FAILED - Fix errors before deployment")
        print("="*70)
        return 1

if __name__ == '__main__':
    sys.exit(main())
