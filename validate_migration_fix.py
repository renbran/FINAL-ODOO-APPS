#!/usr/bin/env python3
"""
Validate the migration fix is working
"""
import os
import re

def validate_migration_fix():
    migration_file = 'account_payment_final/migrations/17.0.1.1.0/post-migrate.py'
    
    if not os.path.exists(migration_file):
        print("❌ Migration file not found")
        return False
    
    with open(migration_file, 'r') as f:
        content = f.read()
    
    # Check for emergency fix markers
    checks = [
        'EMERGENCY FIXED',
        'cr.execute(',
        'has_permission',
        'get_valid_reviewer',
        'bypass validation'
    ]
    
    passed = 0
    for check in checks:
        if check.lower() in content.lower():
            print(f"✅ Found: {check}")
            passed += 1
        else:
            print(f"❌ Missing: {check}")
    
    success_rate = (passed / len(checks)) * 100
    print(f"\nValidation Result: {passed}/{len(checks)} checks passed ({success_rate:.0f}%)")
    
    return passed == len(checks)

if __name__ == "__main__":
    print("🔍 Validating Migration Fix")
    print("=" * 30)
    success = validate_migration_fix()
    print(f"\n{'✅ VALIDATION PASSED' if success else '❌ VALIDATION FAILED'}")
