#!/usr/bin/env python3
"""
Validation script for the report action reference fix
"""
import os
import xml.etree.ElementTree as ET
import re

def validate_xml_syntax(file_path):
    """Validate XML syntax"""
    try:
        ET.parse(file_path)
        return True, "Valid XML syntax"
    except ET.ParseError as e:
        return False, f"XML syntax error: {e}"

def check_external_id_references(module_dir):
    """Check if all external ID references exist"""
    print("🔍 Checking External ID References...")
    
    # Find all XML files
    xml_files = []
    for root, dirs, files in os.walk(module_dir):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    
    # Extract all record IDs
    defined_ids = set()
    referenced_ids = set()
    
    for xml_file in xml_files:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Find defined IDs
            for record in root.findall('.//record'):
                record_id = record.get('id')
                if record_id:
                    defined_ids.add(f"account_payment_approval.{record_id}")
            
            # Find referenced IDs in ref attributes
            content = open(xml_file, 'r', encoding='utf-8').read()
            ref_pattern = r'ref="([^"]+)"'
            refs = re.findall(ref_pattern, content)
            for ref in refs:
                if ref.startswith('account_payment_approval.'):
                    referenced_ids.add(ref)
            
            # Find referenced IDs in %(...)d patterns
            action_pattern = r'%\(([^)]+)\)d'
            actions = re.findall(action_pattern, content)
            for action in actions:
                if '.' in action:
                    referenced_ids.add(action)
                else:
                    referenced_ids.add(f"account_payment_approval.{action}")
                    
        except Exception as e:
            print(f"❌ Error processing {xml_file}: {e}")
    
    # Check for missing references
    missing_refs = referenced_ids - defined_ids
    
    print(f"✅ Defined IDs: {len(defined_ids)}")
    print(f"🔗 Referenced IDs: {len(referenced_ids)}")
    
    if missing_refs:
        print(f"❌ Missing External IDs:")
        for missing in missing_refs:
            print(f"   - {missing}")
        return False
    else:
        print("✅ All external ID references are valid!")
        return True

def main():
    print("🚀 REPORT ACTION FIX VALIDATION")
    print("="*50)
    
    module_dir = "account_payment_approval"
    
    if not os.path.exists(module_dir):
        print("❌ Module directory not found!")
        return False
    
    # 1. Validate XML syntax
    print("\n1. 🔍 XML Syntax Validation...")
    xml_files = []
    for root, dirs, files in os.walk(module_dir):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    
    xml_valid = True
    for xml_file in xml_files:
        valid, message = validate_xml_syntax(xml_file)
        if valid:
            print(f"   ✅ {xml_file}")
        else:
            print(f"   ❌ {xml_file}: {message}")
            xml_valid = False
    
    # 2. Check external ID references
    print("\n2. 🔗 External ID Reference Validation...")
    refs_valid = check_external_id_references(module_dir)
    
    # 3. Specific check for the fixed action
    print("\n3. 🎯 Specific Fix Validation...")
    
    # Check that action_report_voucher_verification_web exists in report_actions.xml
    report_actions_file = os.path.join(module_dir, 'reports', 'report_actions.xml')
    if os.path.exists(report_actions_file):
        content = open(report_actions_file, 'r', encoding='utf-8').read()
        if 'action_report_voucher_verification_web' in content:
            print("   ✅ action_report_voucher_verification_web found in report_actions.xml")
            fix_applied = True
        else:
            print("   ❌ action_report_voucher_verification_web NOT found in report_actions.xml")
            fix_applied = False
    else:
        print("   ❌ report_actions.xml file not found")
        fix_applied = False
    
    # Check that the action is NOT duplicated in menu_items.xml
    menu_items_file = os.path.join(module_dir, 'views', 'menu_items.xml')
    if os.path.exists(menu_items_file):
        content = open(menu_items_file, 'r', encoding='utf-8').read()
        # Count occurrences
        count = content.count('action_report_voucher_verification_web')
        if count <= 2:  # Should only appear in references, not definitions
            print("   ✅ No duplicate definition found in menu_items.xml")
        else:
            print(f"   ⚠️  Found {count} occurrences in menu_items.xml (might be duplicated)")
    
    # Final result
    print("\n" + "="*50)
    if xml_valid and refs_valid and fix_applied:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ Module should deploy successfully to CloudPepper")
        return True
    else:
        print("❌ VALIDATION FAILED!")
        print("🔧 Fix required before deployment")
        return False

if __name__ == "__main__":
    main()
