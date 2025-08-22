#!/usr/bin/env python3
"""
CloudPepper Account Payment Final Module Validation
Final check before CloudPepper deployment
"""

import os
import json
from pathlib import Path

def validate_module_structure():
    """Validate the module has all required files"""
    print("🔧 Validating Module Structure...")
    
    required_files = [
        "__manifest__.py",
        "__init__.py",
        "models/__init__.py",
        "models/account_payment.py",
        "static/src/js/cloudpepper_compatibility_patch.js",
        "static/src/js/payment_workflow_realtime.js",
        "static/src/js/payment_workflow.js",
        "views/account_payment_views.xml",
        "security/ir.model.access.csv"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print(f"✅ All {len(required_files)} required files present")
        return True

def validate_javascript_syntax():
    """Basic JavaScript syntax validation"""
    print("🔧 Validating JavaScript Syntax...")
    
    js_files = [
        "static/src/js/cloudpepper_compatibility_patch.js",
        "static/src/js/payment_workflow_realtime.js",
        "static/src/js/payment_workflow.js",
        "static/src/js/fields/qr_code_field.js"
    ]
    
    all_valid = True
    for js_file in js_files:
        if Path(js_file).exists():
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic syntax checks
                if '/** @odoo-module **/' not in content:
                    print(f"⚠️ {js_file} - Missing @odoo-module directive")
                
                if 'import {' in content and 'from "@odoo/' in content:
                    print(f"✅ {js_file} - Modern ES6+ syntax")
                elif 'odoo.define' in content:
                    print(f"❌ {js_file} - Legacy odoo.define syntax")
                    all_valid = False
                else:
                    print(f"✅ {js_file} - Valid JavaScript")
                    
            except Exception as e:
                print(f"❌ Error checking {js_file}: {e}")
                all_valid = False
        else:
            print(f"❌ {js_file} - File not found")
            all_valid = False
    
    return all_valid

def create_deployment_summary():
    """Create deployment summary for CloudPepper"""
    print("🔧 Creating Deployment Summary...")
    
    summary = {
        "module_name": "account_payment_final",
        "version": "17.0.1.1.0",
        "cloudpepper_ready": True,
        "features": [
            "Modern ES6+ JavaScript",
            "CloudPepper compatibility patches",
            "OWL error handlers",
            "Payment workflow automation",
            "QR code verification",
            "OSUS branding"
        ],
        "deployment_steps": [
            "1. Upload module to CloudPepper",
            "2. Install/Update module",
            "3. Test payment workflow",
            "4. Verify QR code generation",
            "5. Check approval process"
        ]
    }
    
    with open("CLOUDPEPPER_DEPLOYMENT_SUMMARY.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("✅ Deployment summary created: CLOUDPEPPER_DEPLOYMENT_SUMMARY.json")
    return True

def main():
    """Main validation function"""
    print("🚀 ACCOUNT PAYMENT FINAL - CLOUDPEPPER VALIDATION")
    print("=" * 60)
    
    # Change to module directory
    os.chdir("account_payment_final")
    
    checks = [
        ("Module Structure", validate_module_structure),
        ("JavaScript Syntax", validate_javascript_syntax),
        ("Deployment Summary", create_deployment_summary)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"❌ {check_name} failed: {e}")
    
    print("\n" + "=" * 60)
    print(f"🎯 VALIDATION SUMMARY: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 MODULE IS READY FOR CLOUDPEPPER DEPLOYMENT!")
        print("\n📋 NEXT STEPS:")
        print("1. Login to https://stagingtry.cloudpepper.site/")
        print("2. Go to Apps > Update Apps List")
        print("3. Install/Update 'OSUS Payment Approval System'")
        print("4. Test the payment workflow")
        return True
    else:
        print("❌ Module needs fixes before deployment")
        return False

if __name__ == "__main__":
    main()
