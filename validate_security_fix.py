#!/usr/bin/env python3
"""
Emergency RPC Error Fix Validation Script
Validates the payment_approval_pro module security groups fix
"""

import os
import sys
import xml.etree.ElementTree as ET
import csv

def validate_security_xml():
    """Validate the security XML file structure"""
    try:
        file_path = 'payment_approval_pro/security/payment_security.xml'
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        print("✅ payment_security.xml - Valid XML syntax")
        
        # Check for required security groups
        required_groups = [
            'group_payment_user',
            'group_payment_reviewer', 
            'group_payment_approver',
            'group_payment_authorizer',
            'group_payment_manager',
            'group_payment_admin'
        ]
        
        found_groups = []
        for record in root.findall('.//record[@model="res.groups"]'):
            group_id = record.get('id')
            if group_id in required_groups:
                found_groups.append(group_id)
        
        missing_groups = set(required_groups) - set(found_groups)
        if missing_groups:
            print(f"❌ Missing security groups: {missing_groups}")
            return False
        else:
            print("✅ All required security groups found")
            
        # Check for module category
        categories = root.findall('.//record[@model="ir.module.category"]')
        if categories:
            print("✅ Module category defined")
        else:
            print("⚠️  No module category found")
            
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML Parse Error: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return False

def validate_access_csv():
    """Validate the access CSV file"""
    try:
        file_path = 'payment_approval_pro/security/ir.model.access.csv'
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        print(f"✅ ir.model.access.csv - {len(rows)} access rules found")
        
        # Check for external ID references
        required_groups = [
            'group_payment_user',
            'group_payment_reviewer', 
            'group_payment_approver',
            'group_payment_authorizer',
            'group_payment_manager',
            'group_payment_admin'
        ]
        
        groups_in_csv = set()
        for row in rows:
            group_ref = row.get('group_id:id', '')
            if group_ref:
                groups_in_csv.add(group_ref)
        
        missing_in_csv = set(required_groups) - groups_in_csv
        if missing_in_csv:
            print(f"⚠️  Groups not referenced in CSV: {missing_in_csv}")
        else:
            print("✅ All security groups properly referenced in access CSV")
            
        return True
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return False
    except Exception as e:
        print(f"❌ CSV validation error: {e}")
        return False

def validate_manifest():
    """Validate the manifest file includes security files"""
    try:
        file_path = 'payment_approval_pro/__manifest__.py'
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "'security/payment_security.xml'" in content:
            print("✅ payment_security.xml included in manifest")
        else:
            print("❌ payment_security.xml NOT included in manifest")
            return False
            
        if "'security/ir.model.access.csv'" in content:
            print("✅ ir.model.access.csv included in manifest")
        else:
            print("❌ ir.model.access.csv NOT included in manifest")
            return False
            
        return True
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return False

def main():
    """Main validation function"""
    print("🔧 PAYMENT APPROVAL PRO - RPC ERROR FIX VALIDATION")
    print("=" * 60)
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    all_valid = True
    
    print("\n📋 1. SECURITY XML VALIDATION:")
    if not validate_security_xml():
        all_valid = False
    
    print("\n📋 2. ACCESS CSV VALIDATION:")
    if not validate_access_csv():
        all_valid = False
        
    print("\n📋 3. MANIFEST VALIDATION:")
    if not validate_manifest():
        all_valid = False
    
    print("\n" + "=" * 60)
    if all_valid:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ Security groups properly defined")
        print("✅ External IDs should resolve correctly")
        print("✅ Module should install without RPC errors")
        print("\n🚀 READY FOR CLOUDPEPPER DEPLOYMENT!")
    else:
        print("❌ VALIDATION FAILED!")
        print("Please fix the reported issues before deployment")
        
    return 0 if all_valid else 1

if __name__ == "__main__":
    sys.exit(main())
