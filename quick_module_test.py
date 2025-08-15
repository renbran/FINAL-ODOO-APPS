#!/usr/bin/env python3
"""
Quick test to validate account_payment_approval module structure
"""

import os
import xml.etree.ElementTree as ET

def check_module_structure():
    module_path = 'account_payment_approval'
    
    print("üîç Checking account_payment_approval module structure...")
    
    # Check __manifest__.py
    manifest_path = os.path.join(module_path, '__manifest__.py')
    if os.path.exists(manifest_path):
        print("‚úÖ __manifest__.py exists")
        
        # Check for any problematic file references
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_content = f.read()
            
        # Check data files exist
        if "'views/account_move_enhanced_views.xml'" in manifest_content:
            print("‚ùå Found reference to removed file: account_move_enhanced_views.xml")
            return False
        
        if "'views/payment_report_wizard_views.xml'" in manifest_content:
            print("‚ùå Found reference to non-existent file: payment_report_wizard_views.xml")
            return False
            
        print("‚úÖ No problematic file references in manifest")
    else:
        print("‚ùå __manifest__.py not found")
        return False
    
    # Check critical view files
    critical_files = [
        'views/account_payment_views.xml',
        'views/payment_report_wizard.xml',
        'views/menu_views.xml'
    ]
    
    for file_path in critical_files:
        full_path = os.path.join(module_path, file_path)
        if os.path.exists(full_path):
            print(f"‚úÖ {file_path} exists")
            # Quick XML validation
            try:
                ET.parse(full_path)
                print(f"‚úÖ {file_path} is valid XML")
            except ET.ParseError as e:
                print(f"‚ùå {file_path} has XML errors: {e}")
                return False
        else:
            print(f"‚ùå {file_path} missing")
            return False
    
    # Check if problematic file was properly removed
    enhanced_views = os.path.join(module_path, 'views/account_move_enhanced_views.xml')
    if os.path.exists(enhanced_views):
        print("‚ùå account_move_enhanced_views.xml still exists - should be removed")
        return False
    else:
        print("‚úÖ account_move_enhanced_views.xml properly removed")
    
    print("\nüéâ MODULE STRUCTURE VALIDATION PASSED")
    print("‚úÖ Ready for CloudPepper deployment")
    return True

if __name__ == "__main__":
    success = check_module_structure()
    exit(0 if success else 1)
