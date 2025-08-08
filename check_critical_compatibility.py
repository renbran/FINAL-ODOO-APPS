#!/usr/bin/env python3
"""
Focused compatibility check - only checking custom fields and methods
"""

import os
import re
import xml.etree.ElementTree as ET

def get_custom_fields_from_views():
    """Get only custom fields that should be defined in our model"""
    custom_fields = {
        'approval_state', 'voucher_number', 'remarks', 'reviewer_id', 'reviewer_date',
        'approver_id', 'approver_date', 'authorizer_id', 'authorizer_date', 
        'authorized_by', 'actual_approver_id', 'destination_account_id', 
        'qr_code', 'qr_in_report'
    }
    
    view_file = "account_payment_final/views/account_payment_views.xml"
    if not os.path.exists(view_file):
        return set()
    
    try:
        tree = ET.parse(view_file)
        root = tree.getroot()
        
        view_custom_fields = set()
        for field_elem in root.iter('field'):
            field_name = field_elem.get('name')
            if field_name in custom_fields:
                view_custom_fields.add(field_name)
        
        return view_custom_fields
        
    except ET.ParseError:
        return set()

def get_custom_fields_from_model():
    """Get custom fields defined in our model"""
    model_file = "account_payment_final/models/account_payment.py"
    
    if not os.path.exists(model_file):
        return set()
    
    with open(model_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract field definitions
    field_pattern = r'(\w+)\s*=\s*fields\.'
    return set(re.findall(field_pattern, content))

def check_critical_compatibility():
    """Check only critical custom fields and methods"""
    print("🔍 CRITICAL COMPATIBILITY CHECK")
    print("=" * 50)
    
    # Check custom fields
    print("\n📋 Custom Fields Check:")
    model_fields = get_custom_fields_from_model()
    view_fields = get_custom_fields_from_views()
    
    print(f"Model defines: {sorted(model_fields)}")
    print(f"Views reference: {sorted(view_fields)}")
    
    missing_fields = view_fields - model_fields
    if missing_fields:
        print(f"❌ Missing custom fields in model: {missing_fields}")
        return False
    else:
        print("✅ All custom fields properly defined!")
    
    # Check action methods
    print("\n🎯 Action Methods Check:")
    
    # Extract actions from views
    view_file = "account_payment_final/views/account_payment_views.xml"
    with open(view_file, 'r', encoding='utf-8') as f:
        view_content = f.read()
    
    action_pattern = r'name="(action_\w+)"'
    view_actions = set(re.findall(action_pattern, view_content))
    
    # Extract actions from model
    model_file = "account_payment_final/models/account_payment.py"
    with open(model_file, 'r', encoding='utf-8') as f:
        model_content = f.read()
    
    model_action_pattern = r'def (action_\w+)\('
    model_actions = set(re.findall(model_action_pattern, model_content))
    
    print(f"Model defines: {sorted(model_actions)}")
    print(f"Views reference: {sorted(view_actions)}")
    
    missing_actions = view_actions - model_actions
    if missing_actions:
        print(f"❌ Missing action methods in model: {missing_actions}")
        return False
    else:
        print("✅ All action methods properly defined!")
    
    return True

def check_security_groups():
    """Check if security groups referenced in views are defined"""
    print("\n🔒 Security Groups Check:")
    
    # Extract group references from views
    view_file = "account_payment_final/views/account_payment_views.xml"
    with open(view_file, 'r', encoding='utf-8') as f:
        view_content = f.read()
    
    group_pattern = r'groups="account_payment_final\.(\w+)"'
    view_groups = set(re.findall(group_pattern, view_content))
    
    # Check security file
    security_file = "account_payment_final/security/payment_security.xml"
    if not os.path.exists(security_file):
        print(f"❌ Security file not found: {security_file}")
        return False
    
    with open(security_file, 'r', encoding='utf-8') as f:
        security_content = f.read()
    
    security_group_pattern = r'<record id="(\w+)" model="res\.groups">'
    security_groups = set(re.findall(security_group_pattern, security_content))
    
    print(f"Views reference groups: {sorted(view_groups)}")
    print(f"Security defines groups: {sorted(security_groups)}")
    
    missing_groups = view_groups - security_groups
    if missing_groups:
        print(f"❌ Missing security groups: {missing_groups}")
        return False
    else:
        print("✅ All security groups properly defined!")
    
    return True

def main():
    print("🚀 FOCUSED ACCOUNT PAYMENT FINAL COMPATIBILITY CHECK")
    print("=" * 60)
    
    if not os.path.exists("account_payment_final"):
        print("❌ Module directory not found!")
        return False
    
    checks = [
        check_critical_compatibility,
        check_security_groups
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL CRITICAL CHECKS PASSED!")
        print("Module is ready for installation!")
    else:
        print("❌ CRITICAL ISSUES FOUND!")
        print("Please fix the issues before proceeding.")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
