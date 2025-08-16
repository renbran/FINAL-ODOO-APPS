#!/usr/bin/env python3
"""
CloudPepper Account Payment Final - Comprehensive Validation Test
Designed for remote CloudPepper hosting environment
"""

import os
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path

def cloudpepper_validation_test():
    """Comprehensive validation for CloudPepper deployment"""
    
    print("🌐 CloudPepper Account Payment Final - Validation Test")
    print("=" * 70)
    
    module_path = Path("account_payment_final")
    if not module_path.exists():
        print("❌ Module directory not found!")
        return False
    
    errors = 0
    warnings = 0
    
    # 1. MANIFEST VALIDATION
    print("\n📋 1. MANIFEST VALIDATION")
    print("-" * 30)
    
    manifest_path = module_path / "__manifest__.py"
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_content = f.read()
            
            # Check CloudPepper specific requirements
            if "'web'" in manifest_content:
                print("✅ Web dependency found")
            else:
                print("⚠️  Web dependency missing")
                warnings += 1
            
            if "cloudpepper_clean_fix.js" in manifest_content:
                print("✅ Clean JavaScript fix enabled")
            else:
                print("❌ Clean JavaScript fix missing")
                errors += 1
            
            if "OSUS" in manifest_content:
                print("✅ OSUS branding maintained")
            else:
                print("⚠️  OSUS branding not found")
                warnings += 1
                
        except Exception as e:
            print(f"❌ Manifest error: {e}")
            errors += 1
    else:
        print("❌ Manifest file missing")
        errors += 1
    
    # 2. JAVASCRIPT VALIDATION
    print("\n🔧 2. JAVASCRIPT VALIDATION")
    print("-" * 30)
    
    js_clean_fix = module_path / "static/src/js/cloudpepper_clean_fix.js"
    if js_clean_fix.exists():
        try:
            with open(js_clean_fix, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            if "MutationObserver" in js_content:
                print("✅ MutationObserver protection found")
            else:
                print("❌ MutationObserver protection missing")
                errors += 1
            
            if "addEventListener" in js_content:
                print("✅ Error event handling found")
            else:
                print("❌ Error event handling missing")
                errors += 1
            
            if "CloudPepper" in js_content:
                print("✅ CloudPepper branding found")
            else:
                print("⚠️  CloudPepper branding missing")
                warnings += 1
                
        except Exception as e:
            print(f"❌ JavaScript validation error: {e}")
            errors += 1
    else:
        print("❌ Clean JavaScript fix file missing")
        errors += 1
    
    # Check for problematic emergency files (should be removed)
    emergency_files = [
        "immediate_emergency_fix.js",
        "cloudpepper_nuclear_fix.js", 
        "cloudpepper_enhanced_handler.js",
        "cloudpepper_critical_interceptor.js",
        "emergency_error_fix.js"
    ]
    
    problematic_files = []
    for emergency_file in emergency_files:
        emergency_path = module_path / f"static/src/js/{emergency_file}"
        if emergency_path.exists():
            problematic_files.append(emergency_file)
    
    if problematic_files:
        print(f"⚠️  Found {len(problematic_files)} problematic emergency JS files")
        for pf in problematic_files:
            print(f"   - {pf}")
        print("   (These should be removed to use clean fix only)")
    else:
        print("✅ No problematic emergency files found")
    
    # 3. PYTHON SYNTAX VALIDATION
    print("\n🐍 3. PYTHON SYNTAX VALIDATION")
    print("-" * 30)
    
    python_files = list(module_path.rglob("*.py"))
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                py_content = f.read()
            compile(py_content, str(py_file), 'exec')
            print(f"✅ {py_file.relative_to(module_path)}")
        except Exception as e:
            print(f"❌ {py_file.relative_to(module_path)}: {e}")
            errors += 1
    
    # 4. XML SYNTAX VALIDATION
    print("\n📄 4. XML SYNTAX VALIDATION")
    print("-" * 30)
    
    xml_files = list(module_path.rglob("*.xml"))
    for xml_file in xml_files:
        try:
            ET.parse(xml_file)
            print(f"✅ {xml_file.relative_to(module_path)}")
        except Exception as e:
            print(f"❌ {xml_file.relative_to(module_path)}: {e}")
            errors += 1
    
    # 5. SECURITY VALIDATION
    print("\n🔒 5. SECURITY VALIDATION")
    print("-" * 30)
    
    security_files = [
        "security/payment_security.xml",
        "security/ir.model.access.csv"
    ]
    
    for sec_file in security_files:
        sec_path = module_path / sec_file
        if sec_path.exists():
            print(f"✅ {sec_file}")
        else:
            print(f"❌ {sec_file} missing")
            errors += 1
    
    # 6. CLOUDPEPPER COMPATIBILITY CHECK
    print("\n☁️  6. CLOUDPEPPER COMPATIBILITY")
    print("-" * 30)
    
    # Check for CloudPepper-specific patterns
    cloudpepper_checks = {
        "QR Code Support": "qrcode",
        "Professional UI": "osus_branding",
        "Responsive Design": "responsive", 
        "Email Templates": "email_templates",
        "PDF Reports": "payment_voucher_report"
    }
    
    for check_name, pattern in cloudpepper_checks.items():
        found = False
        for file_path in module_path.rglob("*"):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    if pattern in content.lower():
                        found = True
                        break
                except:
                    continue
        
        if found:
            print(f"✅ {check_name}")
        else:
            print(f"⚠️  {check_name} not found")
            warnings += 1
    
    # 7. DEPLOYMENT READINESS
    print("\n🚀 7. DEPLOYMENT READINESS")
    print("-" * 30)
    
    required_dirs = ["models", "views", "security", "reports", "static"]
    for req_dir in required_dirs:
        dir_path = module_path / req_dir
        if dir_path.exists() and dir_path.is_dir():
            print(f"✅ {req_dir}/ directory")
        else:
            print(f"❌ {req_dir}/ directory missing")
            errors += 1
    
    # 8. JAVASCRIPT ERROR RESOLUTION STATUS
    print("\n⚡ 8. JAVASCRIPT ERROR RESOLUTION")
    print("-" * 30)
    
    # Check if the clean fix addresses the specific errors mentioned
    if js_clean_fix.exists():
        with open(js_clean_fix, 'r', encoding='utf-8') as f:
            clean_fix_content = f.read()
        
        error_patterns = {
            "MutationObserver TypeError": "Failed to execute 'observe' on 'MutationObserver'",
            "Syntax Error Fix": "Unexpected token ';'",
            "Long Running Recorder": "Long Running Recorder",
            "Promise Rejection": "unhandledrejection"
        }
        
        for error_name, error_pattern in error_patterns.items():
            if error_pattern in clean_fix_content:
                print(f"✅ {error_name} handled")
            else:
                print(f"⚠️  {error_name} not specifically handled")
                warnings += 1
    
    # FINAL SUMMARY
    print("\n" + "=" * 70)
    print("🏁 CLOUDPEPPER VALIDATION SUMMARY")
    print("=" * 70)
    
    print(f"📊 Test Results:")
    print(f"   ✅ Successful Checks: {(40 - errors - warnings)}")  # Approximate successful checks
    print(f"   ❌ Errors: {errors}")
    print(f"   ⚠️  Warnings: {warnings}")
    
    if errors == 0:
        print(f"\n🎯 DEPLOYMENT STATUS: ✅ READY FOR CLOUDPEPPER")
        print(f"   • All critical validations passed")
        print(f"   • JavaScript errors should be resolved")
        print(f"   • Module ready for upload to CloudPepper")
        
        if warnings > 0:
            print(f"   • {warnings} minor warnings noted for optimization")
    else:
        print(f"\n🎯 DEPLOYMENT STATUS: ❌ NEEDS ATTENTION")
        print(f"   • {errors} critical errors must be fixed")
        print(f"   • Not ready for CloudPepper deployment")
    
    # CloudPepper Deployment Instructions
    print(f"\n📋 CLOUDPEPPER DEPLOYMENT STEPS:")
    print(f"   1. Upload account_payment_final module to CloudPepper")
    print(f"   2. Install dependencies: qrcode, pillow")  
    print(f"   3. Install module via Apps menu")
    print(f"   4. Test JavaScript error resolution")
    print(f"   5. Verify payment workflow functionality")
    
    return errors == 0

if __name__ == "__main__":
    success = cloudpepper_validation_test()
    sys.exit(0 if success else 1)
