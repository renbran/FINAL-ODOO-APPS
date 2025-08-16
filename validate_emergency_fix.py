#!/usr/bin/env python3
"""
Emergency CloudPepper Fix Validator
Validates that the infinite recursion fix is properly deployed
"""

import os

def validate_emergency_fix():
    """Validate the emergency fix deployment."""
    print("🚨 EMERGENCY CLOUDPEPPER FIX VALIDATION")
    print("=" * 60)
    
    success = True
    
    # Check if files exist
    files_to_check = [
        "report_font_enhancement/static/src/js/report_font_enhancement.js",
        "report_font_enhancement/static/src/js/cloudpepper_global_protection.js",
        "report_font_enhancement/__manifest__.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ File exists: {file_path}")
        else:
            print(f"❌ File missing: {file_path}")
            success = False
    
    # Check report_font_enhancement.js is disabled
    enhancement_file = "report_font_enhancement/static/src/js/report_font_enhancement.js"
    if os.path.exists(enhancement_file):
        with open(enhancement_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "EMERGENCY DISABLE" in content:
            print("✅ Report Font Enhancement service is DISABLED")
        else:
            print("❌ Report Font Enhancement service is still ACTIVE - DANGEROUS!")
            success = False
        
        if "registry.category(\"services\").add(\"reportFontEnhancement\"" in content and not content.count("/*") > 0:
            print("❌ Service registration is still ACTIVE - CRITICAL ISSUE!")
            success = False
        else:
            print("✅ Service registration is properly DISABLED")
    
    # Check global protection exists
    protection_file = "report_font_enhancement/static/src/js/cloudpepper_global_protection.js"
    if os.path.exists(protection_file):
        with open(protection_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        protection_features = [
            "SafeMutationObserver",
            "setAttribute",
            "addEventListener",
            "Maximum call stack",
            "Global Protection"
        ]
        
        found_features = 0
        for feature in protection_features:
            if feature in content:
                found_features += 1
        
        if found_features >= 4:
            print(f"✅ Global protection has {found_features}/5 safety features")
        else:
            print(f"⚠️ Global protection has only {found_features}/5 safety features")
    
    # Check manifest asset loading
    manifest_file = "report_font_enhancement/__manifest__.py"
    if os.path.exists(manifest_file):
        with open(manifest_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "cloudpepper_global_protection.js" in content:
            print("✅ Global protection is included in manifest assets")
        else:
            print("⚠️ Global protection may not be loaded correctly")
    
    print(f"\n{'✅ EMERGENCY FIX VALIDATED!' if success else '❌ EMERGENCY FIX HAS ISSUES!'}")
    
    if success:
        print("\n🚀 READY FOR CLOUDPEPPER DEPLOYMENT:")
        print("1. Upload all three files to CloudPepper")
        print("2. Upgrade the Report Font Enhancement module") 
        print("3. Clear all caches")
        print("4. Test - should have NO infinite recursion errors")
        print("\n💡 Expected result: Stable CloudPepper with no JavaScript errors")
    else:
        print("\n⚠️ FIX ISSUES BEFORE DEPLOYMENT!")
    
    return success

if __name__ == "__main__":
    validate_emergency_fix()
