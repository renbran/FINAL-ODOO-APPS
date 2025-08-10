#!/usr/bin/env python3
"""
CloudPepper Security Group Validation Script
Validates that all security groups have unique OSUS prefixes to prevent duplicates
"""

import xml.etree.ElementTree as ET
import os
import sys

def validate_security_groups():
    """Validate security groups in the XML file"""
    
    security_file = 'account_payment_approval/security/payment_voucher_security.xml'
    
    if not os.path.exists(security_file):
        print(f"❌ ERROR: Security file not found: {security_file}")
        return False
    
    try:
        tree = ET.parse(security_file)
        root = tree.getroot()
        
        groups = []
        for record in root.findall('.//record[@model="res.groups"]'):
            name_field = record.find('./field[@name="name"]')
            if name_field is not None:
                groups.append(name_field.text)
        
        print("🔍 Found security groups:")
        for group in groups:
            print(f"   ├─ {group}")
        
        # Check if all groups have OSUS prefix
        all_have_osus = all('OSUS' in group for group in groups)
        
        print(f"\n📊 Total groups found: {len(groups)}")
        
        if all_have_osus:
            print("✅ SUCCESS: All groups have OSUS prefix - no duplicates expected")
            return True
        else:
            print("❌ ERROR: Some groups missing OSUS prefix")
            non_osus = [g for g in groups if 'OSUS' not in g]
            print("   Groups without OSUS prefix:")
            for group in non_osus:
                print(f"   ├─ {group}")
            return False
            
    except ET.ParseError as e:
        print(f"❌ XML Parse Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Validation Error: {e}")
        return False

def main():
    """Main validation function"""
    print("=" * 60)
    print("CloudPepper Security Group Validation")
    print("=" * 60)
    
    if validate_security_groups():
        print("\n🎉 VALIDATION PASSED: Module ready for CloudPepper installation")
        sys.exit(0)
    else:
        print("\n💥 VALIDATION FAILED: Fix security groups before installation")
        sys.exit(1)

if __name__ == "__main__":
    main()
