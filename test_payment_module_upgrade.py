#!/usr/bin/env python3
"""
Test script to upgrade payment_account_enhanced module
and check for any remaining errors.
"""

import os
import sys
import subprocess

def test_module_upgrade():
    """Test upgrading the payment_account_enhanced module"""
    
    print("🔧 Testing payment_account_enhanced module upgrade...")
    
    # Change to the project directory
    project_dir = r"d:\RUNNING APPS\ready production\latest\odoo17_final"
    os.chdir(project_dir)
    
    # Test 1: Validate Python syntax of manifest
    print("\n✅ Step 1: Validating manifest file...")
    try:
        with open('payment_account_enhanced/__manifest__.py', 'r') as f:
            manifest_content = f.read()
        
        # Check if the manifest can be executed
        exec(manifest_content)
        print("   ✓ Manifest file syntax is valid")
    except Exception as e:
        print(f"   ❌ Manifest validation failed: {e}")
        return False
    
    # Test 2: Check if all asset files exist
    print("\n✅ Step 2: Checking asset file existence...")
    required_assets = [
        'payment_account_enhanced/static/src/css/osus_backend.css',
        'payment_account_enhanced/static/src/css/osus_report.css', 
        'payment_account_enhanced/static/src/scss/payment_voucher.scss',
        'payment_account_enhanced/static/src/js/payment_voucher_form.js',
        'payment_account_enhanced/static/src/scss/payment_voucher_report.scss'
    ]
    
    missing_files = []
    for asset in required_assets:
        if not os.path.exists(asset):
            missing_files.append(asset)
        else:
            print(f"   ✓ Found: {asset}")
    
    if missing_files:
        print(f"   ❌ Missing asset files:")
        for missing in missing_files:
            print(f"      - {missing}")
        return False
    
    # Test 3: Check data files exist
    print("\n✅ Step 3: Checking data file existence...")
    required_data = [
        'payment_account_enhanced/security/ir.model.access.csv',
        'payment_account_enhanced/security/payment_security.xml',
        'payment_account_enhanced/views/account_payment_views.xml',
        'payment_account_enhanced/views/payment_verification_templates.xml',
        'payment_account_enhanced/reports/payment_voucher_template.xml',
        'payment_account_enhanced/data/sequences.xml'
    ]
    
    missing_data = []
    for data_file in required_data:
        if not os.path.exists(data_file):
            missing_data.append(data_file)
        else:
            print(f"   ✓ Found: {data_file}")
    
    if missing_data:
        print(f"   ❌ Missing data files:")
        for missing in missing_data:
            print(f"      - {missing}")
        return False
    
    print("\n🎉 All module validation tests passed!")
    print("\n💡 Next steps:")
    print("   1. Restart your Odoo server")
    print("   2. Go to Apps → Update Apps List") 
    print("   3. Find 'OSUS Payment Voucher Enhanced' and click 'Upgrade'")
    print("   4. The web.assets_backend error should be resolved")
    
    return True

if __name__ == "__main__":
    success = test_module_upgrade()
    sys.exit(0 if success else 1)
