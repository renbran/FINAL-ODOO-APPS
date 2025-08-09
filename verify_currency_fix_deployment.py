#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Currency Field Fix - Deployment Verification Script
===================================================

This script helps verify that the currency field fix is ready for deployment.
"""

import os
import sys
import subprocess

def check_file_exists(file_path):
    """Check if a file exists and return status"""
    return os.path.exists(file_path)

def check_currency_field_fix(file_path, expected_patterns):
    """Check if currency field fixes are present in a file"""
    if not os.path.exists(file_path):
        return False, "File not found"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_patterns = []
        for pattern in expected_patterns:
            if pattern not in content:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            return False, f"Missing patterns: {missing_patterns}"
        else:
            return True, "All fixes present"
            
    except Exception as e:
        return False, f"Error reading file: {e}"

def main():
    print("🔍 Currency Field Fix - Deployment Verification")
    print("=" * 50)
    
    # Define the files and expected fixes
    verification_checks = [
        {
            'file': 'account_payment_final/controllers/payment_verification.py',
            'patterns': ["currency_field='payment_currency_id'"],
            'description': 'Payment verification controller'
        },
        {
            'file': 'account_payment_final/models/res_company.py',
            'patterns': ["currency_field='currency_id'"],
            'description': 'Company model extensions'
        },
        {
            'file': 'account_payment_final/models/res_config_settings.py', 
            'patterns': ["currency_field='company_currency_id'"],
            'description': 'Configuration settings'
        }
    ]
    
    all_passed = True
    
    for check in verification_checks:
        file_path = os.path.join(os.getcwd(), check['file'])
        print(f"\n📁 Checking: {check['description']}")
        print(f"   File: {check['file']}")
        
        if not check_file_exists(file_path):
            print(f"   ❌ File not found!")
            all_passed = False
            continue
            
        success, message = check_currency_field_fix(file_path, check['patterns'])
        
        if success:
            print(f"   ✅ {message}")
        else:
            print(f"   ❌ {message}")
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 VERIFICATION PASSED!")
        print("✅ All currency field fixes are properly applied")
        print("✅ Module is ready for deployment")
        print("\n📋 Next Steps:")
        print("   1. Restart your Odoo server")
        print("   2. Update the module: odoo -u account_payment_final")
        print("   3. Test the module functionality")
        
        # Create deployment ready marker
        try:
            with open('CURRENCY_FIX_DEPLOYMENT_READY.txt', 'w') as f:
                f.write("Currency field fix validation passed\n")
                f.write(f"Verified on: {__import__('datetime').datetime.now()}\n")
            print("   4. ✅ Deployment ready marker created")
        except:
            pass
            
    else:
        print("❌ VERIFICATION FAILED!")
        print("Some currency field fixes are missing or incomplete")
        print("Please review the errors above and reapply the fixes")
        sys.exit(1)

if __name__ == '__main__':
    main()
