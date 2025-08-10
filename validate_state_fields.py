#!/usr/bin/env python3
"""
Validation script for state field definitions and references
"""
import os
import re

def validate_state_field_definitions():
    """Check state field definitions for proper syntax"""
    print("🔍 Validating State Field Definitions...")
    
    # Check account_payment.py
    payment_file = "account_payment_approval/models/account_payment.py"
    if os.path.exists(payment_file):
        content = open(payment_file, 'r', encoding='utf-8').read()
        
        # Check for proper selection_add usage
        if 'selection_add=' in content:
            print("   ✅ account_payment.py uses selection_add (correct)")
        elif 'selection=[' in content and 'state = fields.Selection' in content:
            print("   ❌ account_payment.py overrides selection completely (problematic)")
            return False
        else:
            print("   ✅ account_payment.py state field looks good")
            
        # Check for ondelete parameter
        if 'ondelete=' in content:
            print("   ✅ account_payment.py has ondelete parameter")
        else:
            print("   ⚠️  account_payment.py missing ondelete parameter")
    
    # Check account_move.py
    move_file = "account_payment_approval/models/account_move.py"
    if os.path.exists(move_file):
        content = open(move_file, 'r', encoding='utf-8').read()
        
        if 'selection_add=' in content and 'state = fields.Selection' in content:
            print("   ✅ account_move.py uses selection_add (correct)")
        else:
            print("   ❌ account_move.py state field issue")
    
    return True

def check_state_references():
    """Check for any hardcoded state references that might be invalid"""
    print("\n🔍 Checking State References in Views and Code...")
    
    # States that should exist in base Odoo
    base_states = {'draft', 'posted', 'sent', 'reconciled', 'cancelled'}
    
    # States we're adding
    added_payment_states = {'submitted', 'under_review', 'approved', 'authorized', 'rejected'}
    added_move_states = {'submit_review', 'waiting_approval', 'approved', 'rejected'}
    
    all_valid_payment_states = base_states | added_payment_states
    all_valid_move_states = {'draft', 'posted', 'cancel'} | added_move_states
    
    # Check XML files for state references
    xml_files = []
    for root, dirs, files in os.walk('account_payment_approval'):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    
    issues_found = False
    for xml_file in xml_files:
        try:
            content = open(xml_file, 'r', encoding='utf-8').read()
            
            # Find state references in domain filters
            state_refs = re.findall(r"state['\"]?\s*[=!]+\s*['\"](\w+)['\"]", content)
            
            for state_ref in state_refs:
                if 'payment' in xml_file.lower():
                    if state_ref not in all_valid_payment_states:
                        print(f"   ❌ Invalid payment state '{state_ref}' in {xml_file}")
                        issues_found = True
                elif 'move' in xml_file.lower():
                    if state_ref not in all_valid_move_states:
                        print(f"   ❌ Invalid move state '{state_ref}' in {xml_file}")
                        issues_found = True
                else:
                    print(f"   ✅ State '{state_ref}' found in {xml_file}")
                    
        except Exception as e:
            print(f"   ❌ Error checking {xml_file}: {e}")
            issues_found = True
    
    if not issues_found:
        print("   ✅ All state references appear valid")
    
    return not issues_found

def main():
    print("🚀 STATE FIELD VALIDATION")
    print("="*50)
    
    # Run validations
    definitions_ok = validate_state_field_definitions()
    references_ok = check_state_references()
    
    print("\n" + "="*50)
    if definitions_ok and references_ok:
        print("🎉 STATE FIELD VALIDATION PASSED!")
        print("✅ State fields properly defined with selection_add")
        print("✅ All state references valid")
        return True
    else:
        print("❌ STATE FIELD VALIDATION FAILED!")
        print("🔧 Fix required before deployment")
        return False

if __name__ == "__main__":
    main()
