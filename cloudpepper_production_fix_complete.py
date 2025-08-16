#!/usr/bin/env python3
"""
CloudPepper Production Fix Validation - Complete Check
Validates all fixes for RPC errors, missing templates, and workflow functionality
"""

import os
import sys
import xml.etree.ElementTree as ET

def validate_report_template_exists():
    """Validate that the missing report template now exists"""
    template_file = "order_status_override/reports/enhanced_order_status_report_template.xml"
    
    if not os.path.exists(template_file):
        print("❌ Report template file not found")
        return False
    
    try:
        tree = ET.parse(template_file)
        root = tree.getroot()
        
        # Check for the specific template that was missing
        template_found = False
        for template in root.iter('template'):
            template_id = template.get('id', '')
            if template_id == 'enhanced_order_status_report_template':
                template_found = True
                break
        
        if not template_found:
            print("❌ Required template 'enhanced_order_status_report_template' not found")
            return False
        
        print("✅ Report template 'enhanced_order_status_report_template' found")
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML parsing error in report template: {e}")
        return False

def validate_css_no_aggressive_styling():
    """Validate CSS has no aggressive styling that causes RPC errors"""
    css_file = "order_status_override/static/src/css/enhanced_sales_order_form.css"
    
    if not os.path.exists(css_file):
        print("❌ CSS file not found")
        return False
    
    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    # Check file size (should be much smaller now)
    if len(css_content) > 5000:  # 5KB limit for CloudPepper compatibility
        print(f"❌ CSS file too large: {len(css_content)} chars (should be < 5000)")
        return False
    
    # Check for problematic patterns
    problematic_patterns = ['!important', 'linear-gradient(', 'transform:', 'box-shadow:']
    issues = []
    
    for pattern in problematic_patterns:
        count = css_content.count(pattern)
        if count > 3:  # Allow minimal usage
            issues.append(f"Too many '{pattern}': {count}")
    
    if issues:
        print("❌ CSS still has problematic patterns:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    print("✅ CSS is CloudPepper compatible (minimal styling)")
    return True

def validate_workflow_buttons_admin_fallback():
    """Validate that workflow buttons have admin user fallback"""
    model_file = "order_status_override/models/sale_order.py"
    
    if not os.path.exists(model_file):
        print("❌ Model file not found")
        return False
    
    with open(model_file, 'r', encoding='utf-8') as f:
        model_content = f.read()
    
    # Check for admin fallback logic
    required_patterns = [
        'is_admin',
        'base.group_system',
        'base.group_erp_manager',
        'or is_admin'
    ]
    
    missing_patterns = []
    for pattern in required_patterns:
        if pattern not in model_content:
            missing_patterns.append(pattern)
    
    if missing_patterns:
        print("❌ Missing admin fallback patterns:")
        for pattern in missing_patterns:
            print(f"  - {pattern}")
        return False
    
    print("✅ Workflow buttons have admin user fallback")
    return True

def validate_manifest_includes_reports():
    """Validate that manifest includes all report files"""
    manifest_file = "order_status_override/__manifest__.py"
    
    if not os.path.exists(manifest_file):
        print("❌ Manifest file not found")
        return False
    
    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest_content = f.read()
    
    required_files = [
        'reports/enhanced_order_status_report_template.xml',
        'reports/enhanced_order_status_report_actions.xml',
        'views/order_views_assignment.xml'
    ]
    
    missing_files = []
    for file_path in required_files:
        if file_path not in manifest_content:
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files in manifest:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    print("✅ Manifest includes all required report files")
    return True

def validate_security_groups_exist():
    """Validate that security groups exist"""
    security_file = "order_status_override/security/security.xml"
    
    if not os.path.exists(security_file):
        print("❌ Security file not found")
        return False
    
    try:
        tree = ET.parse(security_file)
        root = tree.getroot()
        
        required_groups = [
            'group_order_documentation_reviewer',
            'group_order_commission_calculator',
            'group_order_allocation_manager',
            'group_order_approval_manager_enhanced',
            'group_order_posting_manager'
        ]
        
        found_groups = []
        for record in root.iter('record'):
            if record.get('model') == 'res.groups':
                group_id = record.get('id', '')
                if group_id in required_groups:
                    found_groups.append(group_id)
        
        missing_groups = [g for g in required_groups if g not in found_groups]
        if missing_groups:
            print("❌ Missing security groups:")
            for group in missing_groups:
                print(f"  - {group}")
            return False
        
        print("✅ All required security groups exist")
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML parsing error in security file: {e}")
        return False

def main():
    """Main validation function"""
    print("🔍 CloudPepper Production Fix Validation - Complete Check")
    print("=" * 60)
    
    # Change to module directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    validations = [
        ("Report Template Exists", validate_report_template_exists),
        ("CSS CloudPepper Compatible", validate_css_no_aggressive_styling),
        ("Workflow Buttons Admin Fallback", validate_workflow_buttons_admin_fallback),
        ("Manifest Includes Reports", validate_manifest_includes_reports),
        ("Security Groups Exist", validate_security_groups_exist),
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
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED - READY FOR CLOUDPEPPER!")
        print("\n🚀 Summary of fixes applied:")
        print("  ✅ Fixed missing QWeb report template")
        print("  ✅ Simplified CSS to prevent RPC errors")
        print("  ✅ Added admin fallback for workflow buttons")
        print("  ✅ Ensured manifest includes all files")
        print("  ✅ Validated security groups exist")
        print("\n📱 CloudPepper deployment should now work correctly!")
        print("🔗 Test at: https://brotest.cloudpepper.site/")
    else:
        print("❌ SOME VALIDATIONS FAILED")
        print("🔧 Please review and fix issues before deployment")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
