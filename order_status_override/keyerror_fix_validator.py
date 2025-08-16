#!/usr/bin/env python3
"""
Core Field Fix Validation - Check the KeyError fix
"""

import os
import re

def check_core_fields():
    """Check if the missing fields have been added"""
    print("🔍 CORE FIELD VALIDATION")
    print("-" * 30)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    sale_order_file = os.path.join(base_path, 'models', 'sale_order.py')
    
    if not os.path.exists(sale_order_file):
        print("❌ sale_order.py not found")
        return False
    
    with open(sale_order_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for the missing fields
    missing_fields = ['commission_user_id', 'final_review_user_id']
    found_fields = []
    
    for field in missing_fields:
        pattern = rf'{field}\s*=\s*fields\.'
        if re.search(pattern, content):
            found_fields.append(field)
            print(f"✅ Found field definition: {field}")
        else:
            print(f"❌ Missing field definition: {field}")
    
    # Check if both fields are found
    if len(found_fields) == len(missing_fields):
        print("\n🎉 ALL REQUIRED FIELDS ARE PRESENT!")
        print("✅ commission_user_id field added")
        print("✅ final_review_user_id field added")
        print("✅ KeyError should be resolved")
        return True
    else:
        print(f"\n❌ Missing {len(missing_fields) - len(found_fields)} field(s)")
        return False

def main():
    print("🔧 KEYERROR FIX VALIDATION")
    print("=" * 40)
    
    success = check_core_fields()
    
    print("\n" + "=" * 40)
    if success:
        print("🎯 FIX VALIDATION: SUCCESS")
        print("Module should now install without KeyError")
    else:
        print("🎯 FIX VALIDATION: FAILED")
        print("Additional fixes required")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
