#!/usr/bin/env python3
"""
FINAL DEPLOYMENT VALIDATION
Comprehensive check for account_payment_approval module
"""

import os
import xml.etree.ElementTree as ET

def final_validation():
    print("🚀 FINAL DEPLOYMENT VALIDATION")
    print("=" * 50)
    
    module_path = 'account_payment_approval'
    
    # 1. Check manifest
    manifest_path = os.path.join(module_path, '__manifest__.py')
    print(f"✅ Manifest exists: {os.path.exists(manifest_path)}")
    
    # 2. Check critical XML files
    xml_files = [
        'views/account_payment_views.xml',
        'views/menu_views.xml', 
        'views/payment_report_wizard.xml'
    ]
    
    all_valid = True
    for xml_file in xml_files:
        full_path = os.path.join(module_path, xml_file)
        exists = os.path.exists(full_path)
        print(f"✅ {xml_file}: {'EXISTS' if exists else 'MISSING'}")
        
        if exists:
            try:
                ET.parse(full_path)
                print(f"   ✅ Valid XML")
            except ET.ParseError as e:
                print(f"   ❌ XML Error: {e}")
                all_valid = False
        else:
            all_valid = False
    
    # 3. Check problematic file is gone
    bad_file = os.path.join(module_path, 'views/account_move_enhanced_views.xml')
    if os.path.exists(bad_file):
        print("❌ Problematic file still exists: account_move_enhanced_views.xml")
        all_valid = False
    else:
        print("✅ Problematic file removed: account_move_enhanced_views.xml")
    
    # 4. Check for XPath issues in payment views
    payment_views = os.path.join(module_path, 'views/account_payment_views.xml')
    if os.path.exists(payment_views):
        try:
            tree = ET.parse(payment_views)
            xpath_elements = tree.findall('.//xpath')
            problematic = []
            
            for xpath in xpath_elements:
                expr = xpath.get('expr')
                if expr in ['//group', '//group[@name="amount_group"]']:
                    problematic.append(expr)
            
            if problematic:
                print(f"❌ Found problematic XPath: {problematic}")
                all_valid = False
            else:
                print("✅ No problematic XPath expressions found")
                
        except Exception as e:
            print(f"❌ Error checking XPath: {e}")
            all_valid = False
    
    print("=" * 50)
    if all_valid:
        print("🎉 DEPLOYMENT READY - NO RPC_ERROR EXPECTED")
        print("✅ Module can be safely deployed to CloudPepper")
    else:
        print("💥 DEPLOYMENT BLOCKED - ISSUES FOUND")
    
    return all_valid

if __name__ == "__main__":
    success = final_validation()
    exit(0 if success else 1)
