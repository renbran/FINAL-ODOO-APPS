#!/usr/bin/env python3
"""
Script to validate that all menu actions exist
"""

import xml.etree.ElementTree as ET
import os
import sys

def extract_actions_from_file(xml_file):
    """Extract all action IDs from an XML file"""
    actions = set()
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Find all records with model="ir.actions.act_window"
        for record in root.findall(".//record[@model='ir.actions.act_window']"):
            action_id = record.get('id')
            if action_id:
                actions.add(action_id)
                
    except ET.ParseError as e:
        print(f"❌ XML Parse Error in {xml_file}: {e}")
    except FileNotFoundError:
        print(f"❌ File not found: {xml_file}")
        
    return actions

def extract_referenced_actions(menus_file):
    """Extract all actions referenced in menu items"""
    referenced_actions = set()
    try:
        tree = ET.parse(menus_file)
        root = tree.getroot()
        
        # Find all menuitem elements with action attribute
        for menuitem in root.findall(".//menuitem[@action]"):
            action = menuitem.get('action')
            if action and not action.startswith('base.') and not action.startswith('account.'):
                referenced_actions.add(action)
                
    except ET.ParseError as e:
        print(f"❌ XML Parse Error in {menus_file}: {e}")
    except FileNotFoundError:
        print(f"❌ File not found: {menus_file}")
        
    return referenced_actions

def main():
    print("🔍 Validating Menu Actions...")
    print("=" * 50)
    
    # Files to check for action definitions
    action_files = [
        "account_payment_final/views/payment_actions_minimal.xml",
        "account_payment_final/reports/payment_voucher_actions.xml",
        "account_payment_final/views/res_company_views.xml"
    ]
    
    # File with menu references
    menus_file = "account_payment_final/views/menus.xml"
    
    # Extract all defined actions
    all_defined_actions = set()
    for action_file in action_files:
        if os.path.exists(action_file):
            actions = extract_actions_from_file(action_file)
            all_defined_actions.update(actions)
            print(f"✅ Found {len(actions)} actions in {action_file}")
        else:
            print(f"⚠️  File not found: {action_file}")
    
    print(f"📋 Total defined actions: {len(all_defined_actions)}")
    print(f"   Actions: {sorted(all_defined_actions)}")
    
    # Extract referenced actions
    referenced_actions = extract_referenced_actions(menus_file)
    print(f"📋 Referenced actions in menus: {len(referenced_actions)}")
    print(f"   Actions: {sorted(referenced_actions)}")
    
    # Check for missing actions
    missing_actions = referenced_actions - all_defined_actions
    
    print("\n" + "=" * 50)
    if missing_actions:
        print(f"❌ Missing actions: {sorted(missing_actions)}")
        return False
    else:
        print("✅ All menu actions are properly defined!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
