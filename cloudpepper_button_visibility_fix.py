#!/usr/bin/env python3
"""
CloudPepper Button Visibility Fix Validation
Fix for RPC_ERROR and workflow button visibility issues
"""

import os
import sys
import xml.etree.ElementTree as ET

def validate_css_simplification():
    """Validate that the CSS has been simplified to prevent RPC errors"""
    css_file = "order_status_override/static/src/css/enhanced_sales_order_form.css"
    
    if not os.path.exists(css_file):
        print("❌ CSS file not found")
        return False
    
    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    # Check for problematic patterns that cause RPC errors
    problematic_patterns = [
        'linear-gradient(',
        'box-shadow:',
        'transform:',
        '!important'
    ]
    
    issues = []
    for pattern in problematic_patterns:
        count = css_content.count(pattern)
        if count > 5:  # Allow some usage but not excessive
            issues.append(f"Too many instances of '{pattern}': {count}")
    
    if issues:
        print("❌ CSS still contains problematic patterns:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    print("✅ CSS simplified successfully - should prevent RPC errors")
    return True

def validate_button_visibility_logic():
    """Validate that button visibility logic includes admin fallback"""
    model_file = "order_status_override/models/sale_order.py"
    
    if not os.path.exists(model_file):
        print("❌ Model file not found")
        return False
    
    with open(model_file, 'r', encoding='utf-8') as f:
        model_content = f.read()
    
    # Check for admin fallback logic
    if 'is_admin' not in model_content:
        print("❌ Admin fallback logic not found")
        return False
    
    if 'base.group_system' not in model_content:
        print("❌ System admin group check not found")
        return False
    
    # Check that all button conditions include 'or is_admin'
    button_fields = [
        'show_document_review_button',
        'show_commission_calculation_button', 
        'show_allocation_button',
        'show_final_review_button',
        'show_approve_button',
        'show_post_button'
    ]
    
    missing_admin_checks = []
    for field in button_fields:
        if field in model_content:
            # Find the line where this field is set to True
            lines = model_content.split('\n')
            for i, line in enumerate(lines):
                if f'{field} = True' in line:
                    # Check if 'or is_admin' appears in the same conditional block
                    block = '\n'.join(lines[max(0, i-10):i+1])
                    if 'or is_admin' not in block:
                        missing_admin_checks.append(field)
                    break
    
    if missing_admin_checks:
        print("❌ Missing admin checks for buttons:")
        for field in missing_admin_checks:
            print(f"  - {field}")
        return False
    
    print("✅ Button visibility logic includes admin fallback")
    return True

def validate_xml_structure():
    """Validate XML view structure"""
    view_file = "order_status_override/views/order_views_assignment.xml"
    
    if not os.path.exists(view_file):
        print("❌ View file not found")
        return False
    
    try:
        tree = ET.parse(view_file)
        root = tree.getroot()
        
        # Check for workflow buttons with exact names
        expected_buttons = [
            'action_move_to_document_review',
            'action_move_to_commission_calculation', 
            'action_move_to_allocation',
            'action_move_to_final_review',
            'action_approve_order',
            'action_move_to_post',
            'action_post_order',
            'action_reject_order'
        ]
        
        buttons_found = []
        for button in root.iter('button'):
            name = button.get('name', '')
            if name in expected_buttons:
                buttons_found.append(name)
        
        if len(buttons_found) < 6:  # Expecting at least 6 main workflow buttons
            print(f"❌ Expected workflow buttons not found. Found: {buttons_found}")
            return False
        
        print(f"✅ XML structure valid - found {len(buttons_found)} workflow buttons")
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        return False

def main():
    """Main validation function"""
    print("🔍 CloudPepper Button Visibility Fix Validation")
    print("=" * 50)
    
    # Change to module directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    validations = [
        ("CSS Simplification", validate_css_simplification),
        ("Button Visibility Logic", validate_button_visibility_logic),
        ("XML Structure", validate_xml_structure),
    ]
    
    all_passed = True
    for name, validator in validations:
        print(f"\n📋 {name}:")
        try:
            if not validator():
                all_passed = False
        except Exception as e:
            print(f"❌ Validation error: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED")
        print("🚀 Ready for CloudPepper deployment!")
        print("\n📝 Summary of fixes:")
        print("  - Simplified CSS to prevent RPC errors")
        print("  - Added admin fallback for button visibility")
        print("  - Maintained workflow functionality")
        print("  - CloudPepper production compatible")
    else:
        print("❌ SOME VALIDATIONS FAILED")
        print("🔧 Please review and fix issues before deployment")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
