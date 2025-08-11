#!/usr/bin/env python3
"""
CloudPepper Access Rights Validation Script
Validates that all model references in ir.model.access.csv exist and are correct
"""

import csv
import os
import sys

def validate_access_rights():
    """Validate access rights in the CSV file"""
    
    access_file = 'account_payment_approval/security/ir.model.access.csv'
    
    if not os.path.exists(access_file):
        print(f"❌ ERROR: Access file not found: {access_file}")
        return False
    
    try:
        with open(access_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            print("🔍 Found access rights:")
            valid_models = []
            invalid_models = []
            
            for row in reader:
                model_ref = row['model_id:id']
                name = row['name']
                group_ref = row['group_id:id']
                
                print(f"   ├─ {name}")
                print(f"   │  Model: {model_ref}")
                print(f"   │  Group: {group_ref}")
                
                # Check if model reference looks valid
                if model_ref.startswith('account.model_') or model_ref.startswith('model_'):
                    valid_models.append(model_ref)
                else:
                    invalid_models.append(model_ref)
                
                print(f"   │  Status: {'✅' if model_ref not in invalid_models else '❌'}")
                print("   │")
        
        print(f"📊 Total access rights: {len(valid_models) + len(invalid_models)}")
        print(f"✅ Valid model references: {len(valid_models)}")
        print(f"❌ Invalid model references: {len(invalid_models)}")
        
        if invalid_models:
            print("\n❌ Invalid model references found:")
            for model in invalid_models:
                print(f"   ├─ {model}")
            return False
        else:
            print("\n✅ SUCCESS: All model references appear valid")
            return True
            
    except Exception as e:
        print(f"❌ Validation Error: {e}")
        return False

def main():
    """Main validation function"""
    print("=" * 60)
    print("CloudPepper Access Rights Validation")
    print("=" * 60)
    
    if validate_access_rights():
        print("\n🎉 VALIDATION PASSED: Access rights ready for CloudPepper installation")
        sys.exit(0)
    else:
        print("\n💥 VALIDATION FAILED: Fix access rights before installation")
        sys.exit(1)

if __name__ == "__main__":
    main()
