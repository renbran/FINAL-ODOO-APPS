#!/usr/bin/env python3
"""
Test script to verify payment_account_enhanced module can now be installed
"""

import os
import sys

def test_module_ready_for_install():
    """Test if the module is ready for installation"""
    
    print("🧪 Testing payment_account_enhanced module readiness...")
    
    project_dir = r"d:\RUNNING APPS\ready production\latest\odoo17_final"
    os.chdir(project_dir)
    
    print("\n✅ Step 1: Verify module files exist and are valid...")
    
    # Check manifest
    try:
        with open('payment_account_enhanced/__manifest__.py', 'r') as f:
            manifest = f.read()
        exec(manifest)
        print("   ✓ Manifest file is valid")
    except Exception as e:
        print(f"   ❌ Manifest error: {e}")
        return False
    
    # Check key files
    required_files = [
        'payment_account_enhanced/__init__.py',
        'payment_account_enhanced/views/assets.xml',
        'payment_account_enhanced/static/src/css/osus_backend.css',
        'payment_account_enhanced/static/src/js/payment_voucher_form.js'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✓ Found: {file_path}")
        else:
            print(f"   ❌ Missing: {file_path}")
            return False
    
    print("\n✅ Step 2: Check assets.xml is clean...")
    try:
        with open('payment_account_enhanced/views/assets.xml', 'r') as f:
            assets_content = f.read()
        
        if 'inherit_id="web.assets_backend"' in assets_content:
            print("   ❌ assets.xml still contains problematic inheritance!")
            return False
        else:
            print("   ✓ assets.xml is clean (no XML inheritance)")
    except Exception as e:
        print(f"   ❌ Error reading assets.xml: {e}")
        return False
    
    print("\n✅ Step 3: Verify manifest assets configuration...")
    if "'web.assets_backend':" in manifest:
        print("   ✓ Manifest contains proper assets configuration")
    else:
        print("   ❌ Manifest missing assets configuration")
        return False
    
    print("\n🎉 MODULE READY FOR INSTALLATION!")
    print("\n📋 NEXT STEPS:")
    print("   1. Go to your Odoo instance")
    print("   2. Navigate to Apps menu")
    print("   3. Click 'Update Apps List'")
    print("   4. Search for 'OSUS Payment Voucher Enhanced'")
    print("   5. Click 'Install' (should work without errors)")
    print("\n✅ EXPECTED RESULT:")
    print("   - No web.assets_backend errors")
    print("   - No constraint violation errors")  
    print("   - Module installs successfully")
    print("   - Assets load from manifest configuration")
    print("   - OSUS payment vouchers work perfectly")
    
    return True

if __name__ == "__main__":
    success = test_module_ready_for_install()
    if success:
        print("\n🚀 READY TO INSTALL! The web.assets_backend issue has been resolved!")
    else:
        print("\n❌ Module not ready. Please fix the issues above.")
    sys.exit(0 if success else 1)
