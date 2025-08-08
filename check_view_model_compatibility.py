#!/usr/bin/env python3
"""
Comprehensive compatibility check between views and models for account_payment_final
"""

import os
import re
import xml.etree.ElementTree as ET

def extract_fields_from_model():
    """Extract all field definitions from the model"""
    model_file = "account_payment_final/models/account_payment.py"
    
    if not os.path.exists(model_file):
        print(f"❌ Model file not found: {model_file}")
        return set()
    
    with open(model_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract field definitions
    field_pattern = r'(\w+)\s*=\s*fields\.'
    fields = set(re.findall(field_pattern, content))
    
    print(f"📋 Found {len(fields)} fields in model:")
    for field in sorted(fields):
        print(f"  - {field}")
    
    return fields

def extract_action_methods_from_model():
    """Extract all action methods from the model"""
    model_file = "account_payment_final/models/account_payment.py"
    
    if not os.path.exists(model_file):
        print(f"❌ Model file not found: {model_file}")
        return set()
    
    with open(model_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract action method definitions
    action_pattern = r'def (action_\w+)\('
    actions = set(re.findall(action_pattern, content))
    
    print(f"🎯 Found {len(actions)} action methods in model:")
    for action in sorted(actions):
        print(f"  - {action}")
    
    return actions

def extract_fields_from_views():
    """Extract all field references from the views"""
    view_file = "account_payment_final/views/account_payment_views.xml"
    
    if not os.path.exists(view_file):
        print(f"❌ View file not found: {view_file}")
        return set()
    
    try:
        tree = ET.parse(view_file)
        root = tree.getroot()
        
        fields = set()
        for field_elem in root.iter('field'):
            field_name = field_elem.get('name')
            if field_name and not field_name.startswith('arch'):  # Skip technical fields
                fields.add(field_name)
        
        print(f"📄 Found {len(fields)} field references in views:")
        for field in sorted(fields):
            print(f"  - {field}")
        
        return fields
        
    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        return set()

def extract_action_methods_from_views():
    """Extract all action method references from the views"""
    view_file = "account_payment_final/views/account_payment_views.xml"
    
    if not os.path.exists(view_file):
        print(f"❌ View file not found: {view_file}")
        return set()
    
    with open(view_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract action method references from buttons
    action_pattern = r'name="(action_\w+)"'
    actions = set(re.findall(action_pattern, content))
    
    print(f"🎯 Found {len(actions)} action method references in views:")
    for action in sorted(actions):
        print(f"  - {action}")
    
    return actions

def check_field_compatibility():
    """Check compatibility between model fields and view field references"""
    print("\n" + "="*60)
    print("🔍 FIELD COMPATIBILITY CHECK")
    print("="*60)
    
    model_fields = extract_fields_from_model()
    view_fields = extract_fields_from_views()
    
    # Check for missing fields in model
    missing_in_model = view_fields - model_fields
    if missing_in_model:
        print(f"\n❌ Fields referenced in views but missing in model:")
        for field in sorted(missing_in_model):
            print(f"  - {field}")
    else:
        print(f"\n✅ All view field references found in model!")
    
    # Check for unused fields in model
    unused_in_views = model_fields - view_fields
    if unused_in_views:
        print(f"\n⚠️  Fields defined in model but not used in views:")
        for field in sorted(unused_in_views):
            print(f"  - {field}")
    
    return len(missing_in_model) == 0

def check_action_compatibility():
    """Check compatibility between model action methods and view action references"""
    print("\n" + "="*60)
    print("🎯 ACTION METHOD COMPATIBILITY CHECK")
    print("="*60)
    
    model_actions = extract_action_methods_from_model()
    view_actions = extract_action_methods_from_views()
    
    # Check for missing action methods in model
    missing_in_model = view_actions - model_actions
    if missing_in_model:
        print(f"\n❌ Action methods referenced in views but missing in model:")
        for action in sorted(missing_in_model):
            print(f"  - {action}")
    else:
        print(f"\n✅ All view action references found in model!")
    
    # Check for unused action methods in model
    unused_in_views = model_actions - view_actions
    if unused_in_views:
        print(f"\n⚠️  Action methods defined in model but not used in views:")
        for action in sorted(unused_in_views):
            print(f"  - {action}")
    
    return len(missing_in_model) == 0

def check_selection_field_values():
    """Check if selection field values used in views are defined in model"""
    print("\n" + "="*60)
    print("📋 SELECTION FIELD VALUES CHECK")
    print("="*60)
    
    # Extract approval_state values from model
    model_file = "account_payment_final/models/account_payment.py"
    if not os.path.exists(model_file):
        return False
    
    with open(model_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find approval_state field definition
    approval_state_match = re.search(r'approval_state\s*=\s*fields\.Selection\(\[(.*?)\]', content, re.DOTALL)
    if approval_state_match:
        # Extract selection values
        selection_text = approval_state_match.group(1)
        state_pattern = r"'(\w+)'"
        model_states = set(re.findall(state_pattern, selection_text))
        
        print(f"📋 Approval states defined in model: {sorted(model_states)}")
        
        # Extract states used in views
        view_file = "account_payment_final/views/account_payment_views.xml"
        if os.path.exists(view_file):
            with open(view_file, 'r', encoding='utf-8') as f:
                view_content = f.read()
            
            # Find states used in invisible conditions
            view_state_pattern = r"approval_state\s*[!=<>]+\s*'(\w+)'"
            view_states = set(re.findall(view_state_pattern, view_content))
            
            # Also check statusbar_visible
            statusbar_pattern = r'statusbar_visible="([^"]+)"'
            statusbar_match = re.search(statusbar_pattern, view_content)
            if statusbar_match:
                statusbar_states = set(statusbar_match.group(1).split(','))
                view_states.update(statusbar_states)
            
            print(f"📄 Approval states used in views: {sorted(view_states)}")
            
            # Check for mismatches
            undefined_states = view_states - model_states
            if undefined_states:
                print(f"\n❌ States used in views but not defined in model:")
                for state in sorted(undefined_states):
                    print(f"  - {state}")
                return False
            else:
                print(f"\n✅ All view states are properly defined in model!")
                return True
    
    return False

def main():
    """Main compatibility check function"""
    print("🔍 ACCOUNT PAYMENT FINAL - VIEW/MODEL COMPATIBILITY CHECK")
    print("=" * 70)
    
    # Change to the module directory
    if not os.path.exists("account_payment_final"):
        print("❌ Module directory 'account_payment_final' not found!")
        return False
    
    checks = [
        ("Field Compatibility", check_field_compatibility),
        ("Action Method Compatibility", check_action_compatibility),
        ("Selection Field Values", check_selection_field_values),
    ]
    
    all_passed = True
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Error in {check_name}: {str(e)}")
            results.append((check_name, False))
            all_passed = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 COMPATIBILITY CHECK SUMMARY")
    print("=" * 70)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check_name}")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL COMPATIBILITY CHECKS PASSED!")
        print("Views and model are properly aligned and compatible.")
    else:
        print("⚠️  SOME COMPATIBILITY ISSUES FOUND!")
        print("Please review and fix the issues above before deployment.")
    print("=" * 70)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
