#!/usr/bin/env python3
"""
RPC Error Fix Validation for account_payment_final
"""

import os
import xml.etree.ElementTree as ET

def test_rpc_error_fix():
    """Test that the RPC error fix is working"""
    print("🔍 Testing RPC Error Fix...")
    print("=" * 50)
    
    # Test 1: Check that actions file exists and is included in manifest
    print("Test 1: Actions file existence and inclusion...")
    
    actions_file = 'account_payment_final/views/payment_actions_minimal.xml'
    if not os.path.exists(actions_file):
        print(f"  ❌ Actions file missing: {actions_file}")
        return False
    
    with open('account_payment_final/__manifest__.py', 'r') as f:
        manifest = f.read()
    
    if 'payment_actions_minimal.xml' not in manifest:
        print("  ❌ Actions file not included in manifest")
        return False
    
    print("  ✅ Actions file exists and is included in manifest")
    
    # Test 2: Check all menu actions are defined
    print("\nTest 2: All menu actions are defined...")
    
    # Get referenced actions from menus
    referenced_actions = set()
    try:
        tree = ET.parse('account_payment_final/views/menus.xml')
        for menuitem in tree.findall('.//menuitem[@action]'):
            action = menuitem.get('action')
            if action and not action.startswith(('base.', 'account.')):
                referenced_actions.add(action)
    except Exception as e:
        print(f"  ❌ Error reading menus.xml: {e}")
        return False
    
    # Get defined actions
    defined_actions = set()
    action_files = [
        'account_payment_final/views/payment_actions_minimal.xml',
        'account_payment_final/views/res_company_views.xml'
    ]
    
    for file_path in action_files:
        if os.path.exists(file_path):
            try:
                tree = ET.parse(file_path)
                for record in tree.findall('.//record[@model="ir.actions.act_window"]'):
                    action_id = record.get('id')
                    if action_id:
                        defined_actions.add(action_id)
            except Exception as e:
                print(f"  ❌ Error reading {file_path}: {e}")
                return False
    
    missing_actions = referenced_actions - defined_actions
    
    if missing_actions:
        print(f"  ❌ Missing actions: {missing_actions}")
        return False
    
    print(f"  ✅ All {len(referenced_actions)} menu actions are properly defined")
    
    # Test 3: Validate action structure
    print("\nTest 3: Action structure validation...")
    
    try:
        tree = ET.parse(actions_file)
        actions = tree.findall('.//record[@model="ir.actions.act_window"]')
        
        for action in actions:
            action_id = action.get('id')
            
            # Check required fields
            required_fields = ['name', 'type', 'res_model', 'view_mode']
            missing_fields = []
            
            for field_name in required_fields:
                field = action.find(f'.//field[@name="{field_name}"]')
                if field is None:
                    missing_fields.append(field_name)
            
            if missing_fields:
                print(f"  ❌ Action {action_id} missing fields: {missing_fields}")
                return False
        
        print(f"  ✅ All {len(actions)} actions have proper structure")
        
    except Exception as e:
        print(f"  ❌ Error validating action structure: {e}")
        return False
    
    # Test 4: XML syntax validation
    print("\nTest 4: XML syntax validation...")
    
    critical_files = [
        'account_payment_final/views/payment_actions_minimal.xml',
        'account_payment_final/views/menus.xml'
    ]
    
    for xml_file in critical_files:
        try:
            ET.parse(xml_file)
            print(f"  ✅ {xml_file}")
        except ET.ParseError as e:
            print(f"  ❌ {xml_file}: {e}")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 RPC ERROR FIX VALIDATION PASSED!")
    print("=" * 50)
    print("✅ The missing action 'action_payment_dashboard' has been created")
    print("✅ All menu actions are properly defined")
    print("✅ Action structure is valid")
    print("✅ XML syntax is correct")
    print("\n🚀 The RPC error should now be resolved!")
    
    return True

if __name__ == "__main__":
    test_rpc_error_fix()
