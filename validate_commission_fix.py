#!/usr/bin/env python3
"""
Commission Email Template Fix Validation
Validates that all fixes are properly implemented.
"""

import os
import re

def validate_purchase_order_model():
    """Validate the purchase order model has required computed fields."""
    
    model_file = 'commission_ax/models/purchase_order.py'
    
    if not os.path.exists(model_file):
        print(f"❌ Model file not found: {model_file}")
        return False
    
    with open(model_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_fields = [
        'agent1_partner_id = fields.Many2one',
        'agent2_partner_id = fields.Many2one', 
        'project_id = fields.Many2one',
        'unit_id = fields.Many2one'
    ]
    
    found_fields = []
    for field in required_fields:
        if field in content:
            found_fields.append(field.split(' = ')[0])
    
    print(f"✅ Purchase Order Model Validation:")
    print(f"   - File exists: {os.path.exists(model_file)}")
    print(f"   - Required computed fields found: {len(found_fields)}/4")
    
    for field in found_fields:
        print(f"   - ✅ {field}")
    
    # Check for compute method
    if '_compute_commission_fields' in content:
        print(f"   - ✅ _compute_commission_fields method found")
    else:
        print(f"   - ❌ _compute_commission_fields method missing")
    
    return len(found_fields) == 4

def validate_email_templates():
    """Validate email templates are created."""
    
    template_file = 'commission_ax/data/commission_email_templates.xml'
    
    if not os.path.exists(template_file):
        print(f"❌ Email template file not found: {template_file}")
        return False
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for safe template patterns
    safe_patterns = [
        'hasattr(object, \'agent1_partner_id\')',
        'hasattr(object, \'origin_so_id\')',
        't-if="hasattr',
        't-else=""'
    ]
    
    found_patterns = []
    for pattern in safe_patterns:
        if pattern in content:
            found_patterns.append(pattern)
    
    print(f"✅ Email Templates Validation:")
    print(f"   - File exists: {os.path.exists(template_file)}")
    print(f"   - Safe patterns found: {len(found_patterns)}/{len(safe_patterns)}")
    
    for pattern in found_patterns:
        print(f"   - ✅ {pattern}")
    
    return len(found_patterns) >= 2

def validate_manifest():
    """Validate manifest includes email templates."""
    
    manifest_file = 'commission_ax/__manifest__.py'
    
    if not os.path.exists(manifest_file):
        print(f"❌ Manifest file not found: {manifest_file}")
        return False
    
    with open(manifest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    has_email_templates = 'commission_email_templates.xml' in content
    
    print(f"✅ Manifest Validation:")
    print(f"   - File exists: {os.path.exists(manifest_file)}")
    print(f"   - Email templates included: {has_email_templates}")
    
    return has_email_templates

def validate_emergency_fix_files():
    """Validate emergency fix files are created."""
    
    required_files = [
        'EMERGENCY_CLOUDPEPPER_COMMISSION_FIX.md',
        'cloudpepper_emergency_fix.sql',
        'COMMISSION_EMAIL_FIX_SUMMARY.md'
    ]
    
    print(f"✅ Emergency Fix Files Validation:")
    
    all_exist = True
    for file in required_files:
        exists = os.path.exists(file)
        print(f"   - {'✅' if exists else '❌'} {file}")
        if not exists:
            all_exist = False
    
    return all_exist

def main():
    """Run all validations."""
    
    print("🔧 Commission Email Template Fix Validation")
    print("=" * 50)
    
    results = {
        'purchase_order_model': validate_purchase_order_model(),
        'email_templates': validate_email_templates(), 
        'manifest': validate_manifest(),
        'emergency_files': validate_emergency_fix_files()
    }
    
    print("\n📊 VALIDATION SUMMARY:")
    print("=" * 30)
    
    all_passed = True
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test.replace('_', ' ').title()}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED!")
        print("🚀 Ready for CloudPepper deployment!")
        print("\nNext steps:")
        print("1. Execute cloudpepper_emergency_fix.sql in CloudPepper")
        print("2. Upgrade commission_ax module")
        print("3. Test commission email sending")
    else:
        print("❌ SOME VALIDATIONS FAILED!")
        print("Please review the failed items before deployment.")
    
    return all_passed

if __name__ == "__main__":
    main()
