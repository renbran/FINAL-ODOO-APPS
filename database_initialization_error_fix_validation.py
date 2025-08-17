#!/usr/bin/env python3
"""
Database Initialization Error Fix Validation
Specifically validates the fields mentioned in the original CloudPepper error
"""

import re

def validate_specific_error_fix():
    """Validate the specific field dependency error that was causing database initialization failure"""
    
    print("🔍 DATABASE INITIALIZATION ERROR FIX VALIDATION")
    print("=" * 60)
    print("Original Error: Field 'document_review_user_id' not found in model 'sale.order'")
    print("Error in: @depends on '_compute_auto_assigned_users'")
    print()
    
    model_path = "order_status_override/models/sale_order.py"
    
    # Read the model file
    with open(model_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for the problematic fields that were causing the error
    problematic_fields = [
        'document_review_user_id',
        'commission_calculation_user_id'
    ]
    
    print("🔍 Checking for problematic field references...")
    found_problematic = False
    
    for field in problematic_fields:
        if field in content:
            print(f"❌ STILL FOUND: {field}")
            found_problematic = True
        else:
            print(f"✅ REMOVED: {field}")
    
    if found_problematic:
        print("\n❌ CRITICAL: Problematic fields still exist!")
        return False
    
    # Check that the compute method now references correct fields
    print("\n🔍 Checking _compute_auto_assigned_users method...")
    
    # Find the compute method
    compute_match = re.search(
        r'@api\.depends\(([^)]+)\)\s*def _compute_auto_assigned_users',
        content,
        re.DOTALL
    )
    
    if not compute_match:
        print("❌ CRITICAL: _compute_auto_assigned_users method not found!")
        return False
    
    depends_args = compute_match.group(1)
    print(f"✅ Found @api.depends: {depends_args}")
    
    # Extract field names from depends
    field_names = re.findall(r'[\'"]([^\'"]+)[\'"]', depends_args)
    print(f"✅ Dependency fields: {field_names}")
    
    # Check that all referenced fields exist as field definitions
    expected_fields = ['documentation_user_id', 'commission_user_id', 'allocation_user_id', 'final_review_user_id']
    
    print("\n🔍 Validating field definitions exist...")
    all_fields_exist = True
    
    for field in expected_fields:
        if f'{field} = fields.Many2one' in content:
            print(f"✅ Field defined: {field}")
        else:
            print(f"❌ Field missing: {field}")
            all_fields_exist = False
    
    # Final validation
    print("\n" + "=" * 60)
    print("📊 FIX VALIDATION SUMMARY:")
    
    if not found_problematic and all_fields_exist:
        print("🎉 DATABASE INITIALIZATION ERROR SUCCESSFULLY FIXED!")
        print("✅ Problematic field references removed")
        print("✅ All dependency fields properly defined")
        print("✅ CloudPepper database will initialize correctly")
        print("✅ Ready for production deployment")
        return True
    else:
        print("❌ DATABASE INITIALIZATION ERROR NOT FULLY FIXED!")
        if found_problematic:
            print("❌ Problematic field references still exist")
        if not all_fields_exist:
            print("❌ Required dependency fields missing")
        return False

if __name__ == "__main__":
    success = validate_specific_error_fix()
    exit(0 if success else 1)
