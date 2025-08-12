#!/usr/bin/env python3
"""
Frontend Asset Organization Validation Script
Validates the reorganized static asset structure for the Payment Approval module
"""

import os
import sys
from pathlib import Path

def validate_directory_structure():
    """Validate the new directory structure exists"""
    base_path = Path("d:/RUNNING APPS/ready production/latest/odoo17_final/account_payment_approval/static/src")
    
    required_dirs = [
        "scss",
        "scss/components", 
        "css",
        "js",
        "js/components",
        "js/widgets", 
        "js/views",
        "js/fields",
        "js/lib",
        "xml",
        "tests"
    ]
    
    print("🔍 Validating Directory Structure...")
    missing_dirs = []
    
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if not full_path.exists():
            missing_dirs.append(str(full_path))
            print(f"❌ Missing: {dir_path}")
        else:
            print(f"✅ Found: {dir_path}")
    
    return len(missing_dirs) == 0, missing_dirs

def validate_scss_files():
    """Validate SCSS files and structure"""
    base_path = Path("d:/RUNNING APPS/ready production/latest/odoo17_final/account_payment_approval/static/src")
    
    required_scss_files = [
        "scss/_variables.scss",
        "scss/main.scss", 
        "scss/components/_dashboard.scss",
        "scss/components/_badges.scss",
        "scss/components/_signature.scss",
        "scss/components/_qr_code.scss"
    ]
    
    print("\n🎨 Validating SCSS Files...")
    missing_files = []
    
    for file_path in required_scss_files:
        full_path = base_path / file_path
        if not full_path.exists():
            missing_files.append(str(full_path))
            print(f"❌ Missing: {file_path}")
        else:
            # Check file size to ensure it's not empty
            if full_path.stat().st_size > 100:  # At least 100 bytes
                print(f"✅ Found: {file_path} ({full_path.stat().st_size} bytes)")
            else:
                print(f"⚠️  Found but small: {file_path} ({full_path.stat().st_size} bytes)")
    
    return len(missing_files) == 0, missing_files

def validate_css_compilation():
    """Validate compiled CSS exists"""
    css_path = Path("d:/RUNNING APPS/ready production/latest/odoo17_final/account_payment_approval/static/src/css/payment_approval.css")
    
    print("\n📦 Validating CSS Compilation...")
    
    if not css_path.exists():
        print("❌ Missing compiled CSS file")
        return False, ["payment_approval.css not found"]
    
    file_size = css_path.stat().st_size
    if file_size < 1000:  # Should be substantial for production
        print(f"⚠️  CSS file exists but seems small ({file_size} bytes)")
        return False, ["CSS file too small - compilation issue?"]
    
    print(f"✅ CSS file compiled successfully ({file_size} bytes)")
    return True, []

def validate_manifest_assets():
    """Validate manifest asset references"""
    manifest_path = Path("d:/RUNNING APPS/ready production/latest/odoo17_final/account_payment_approval/__manifest__.py")
    
    print("\n📋 Validating Manifest Assets...")
    
    if not manifest_path.exists():
        print("❌ Manifest file not found")
        return False, ["__manifest__.py not found"]
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_assets = [
        "payment_approval.css",
        "_variables.scss", 
        "main.scss",
        "payment_approval_dashboard.js",
        "digital_signature_widget.js",
        "qr_code_widget.js"
    ]
    
    missing_assets = []
    for asset in required_assets:
        if asset not in content:
            missing_assets.append(asset)
            print(f"❌ Missing asset reference: {asset}")
        else:
            print(f"✅ Asset referenced: {asset}")
    
    return len(missing_assets) == 0, missing_assets

def validate_import_structure():
    """Validate SCSS import structure"""
    main_scss = Path("d:/RUNNING APPS/ready production/latest/odoo17_final/account_payment_approval/static/src/scss/main.scss")
    
    print("\n🔗 Validating SCSS Import Structure...")
    
    if not main_scss.exists():
        print("❌ Main SCSS file not found")
        return False, ["main.scss not found"]
    
    with open(main_scss, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_imports = [
        "@import 'variables'",
        "@import 'components/dashboard'",
        "@import 'components/badges'", 
        "@import 'components/signature'",
        "@import 'components/qr_code'"
    ]
    
    missing_imports = []
    for import_stmt in required_imports:
        if import_stmt not in content:
            missing_imports.append(import_stmt)
            print(f"❌ Missing import: {import_stmt}")
        else:
            print(f"✅ Import found: {import_stmt}")
    
    return len(missing_imports) == 0, missing_imports

def check_variables_completeness():
    """Check if variables file has all required design tokens"""
    variables_path = Path("d:/RUNNING APPS/ready production/latest/odoo17_final/account_payment_approval/static/src/scss/_variables.scss")
    
    print("\n🎨 Validating Design System Variables...")
    
    if not variables_path.exists():
        print("❌ Variables file not found")
        return False, ["_variables.scss not found"]
    
    with open(variables_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_variable_groups = [
        "$osus-primary:",
        "$state-draft:",
        "$urgency-low:",
        "$font-family-base:",
        "$spacer-xs:",
        "$border-radius:",
        "$box-shadow:",
        "$transition-base:"
    ]
    
    missing_variables = []
    for var_group in required_variable_groups:
        if var_group not in content:
            missing_variables.append(var_group)
            print(f"❌ Missing variable group: {var_group}")
        else:
            print(f"✅ Variable group found: {var_group}")
    
    return len(missing_variables) == 0, missing_variables

def generate_summary_report(results):
    """Generate final validation summary"""
    print("\n" + "="*60)
    print("🎯 FRONTEND ASSET ORGANIZATION VALIDATION SUMMARY")
    print("="*60)
    
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result[0])
    
    print(f"📊 Overall Status: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("✅ ALL CHECKS PASSED - Frontend assets properly organized!")
        print("\n🚀 Ready for:")
        print("   • Development with modular SCSS")
        print("   • Production deployment")
        print("   • Easy customization and maintenance")
        print("   • Proper asset loading in Odoo 17")
        return True
    else:
        print("❌ SOME CHECKS FAILED - Issues need resolution")
        print("\n🔧 Issues to fix:")
        for check_name, (passed, issues) in results.items():
            if not passed and issues:
                print(f"\n   {check_name}:")
                for issue in issues:
                    print(f"     • {issue}")
        return False

def main():
    """Main validation function"""
    print("🔄 Starting Frontend Asset Organization Validation...")
    print("Module: OSUS Payment Approval System")
    print("Target: Enterprise-grade asset organization\n")
    
    # Run all validation checks
    results = {
        "Directory Structure": validate_directory_structure(),
        "SCSS Files": validate_scss_files(), 
        "CSS Compilation": validate_css_compilation(),
        "Manifest Assets": validate_manifest_assets(),
        "Import Structure": validate_import_structure(),
        "Design Variables": check_variables_completeness()
    }
    
    # Generate summary
    success = generate_summary_report(results)
    
    if success:
        print("\n🎉 Frontend reorganization completed successfully!")
        print("The payment approval module now has enterprise-grade")
        print("frontend asset organization with proper separation of")
        print("concerns, modular architecture, and maintainable code.")
        sys.exit(0)
    else:
        print("\n⚠️  Please resolve the identified issues before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main()
