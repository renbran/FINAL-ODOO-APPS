#!/usr/bin/env python3
"""
Payment Approval Workflow Module Validation Script
==================================================

This script validates the installation and structure of the Payment Approval Workflow module.
Run this script to ensure all components are properly installed and configured.

Usage:
    python validate_payment_approval_module.py

Requirements:
    - Odoo 17 environment
    - Payment Approval Workflow module installed
"""

import os
import sys
import importlib.util

def check_file_exists(file_path, description):
    """Check if a file exists and print status"""
    exists = os.path.exists(file_path)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {file_path}")
    return exists

def check_python_dependencies():
    """Check if required Python dependencies are installed"""
    print("\n🔍 Checking Python Dependencies:")
    
    dependencies = ['qrcode', 'uuid', 'base64', 'io']
    all_deps_ok = True
    
    for dep in dependencies:
        try:
            if dep in ['base64', 'io', 'uuid']:
                # These are built-in modules
                importlib.import_module(dep)
            else:
                # External dependencies
                importlib.import_module(dep)
            print(f"✓ {dep}")
        except ImportError:
            print(f"✗ {dep} - MISSING! Install with: pip install {dep}")
            all_deps_ok = False
    
    return all_deps_ok

def validate_module_structure(module_path):
    """Validate the module structure"""
    print(f"\n🔍 Validating Module Structure in: {module_path}")
    
    required_files = [
        ("__manifest__.py", "Module manifest file"),
        ("__init__.py", "Module initialization file"),
        ("models/__init__.py", "Models package"),
        ("models/account_payment.py", "Extended payment model"),
        ("controllers/__init__.py", "Controllers package"),
        ("controllers/portal.py", "Portal controller"),
        ("wizards/__init__.py", "Wizards package"),
        ("wizards/payment_signature_wizard.py", "Signature wizard"),
        ("wizards/payment_rejection_wizard.py", "Rejection wizard"),
        ("views/account_payment_views.xml", "Payment views"),
        ("data/security_groups.xml", "Security groups"),
        ("data/mail_templates.xml", "Email templates"),
        ("security/ir.model.access.csv", "Access rights"),
        ("reports/payment_report.xml", "Payment reports"),
        ("templates/payment_verification_template.xml", "Verification templates"),
        ("static/src/css/payment_approval.css", "Backend CSS"),
        ("static/src/css/verification_portal.css", "Frontend CSS"),
    ]
    
    all_files_ok = True
    
    for file_path, description in required_files:
        full_path = os.path.join(module_path, file_path)
        if not check_file_exists(full_path, description):
            all_files_ok = False
    
    return all_files_ok

def check_manifest_content(module_path):
    """Check manifest file content"""
    print("\n🔍 Checking Manifest Content:")
    
    manifest_path = os.path.join(module_path, "__manifest__.py")
    if not os.path.exists(manifest_path):
        print("✗ Manifest file not found")
        return False
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_keys = [
            "'name'", "'version'", "'depends'", "'data'", 
            "'installable'", "'auto_install'", "'license'"
        ]
        
        for key in required_keys:
            if key in content:
                print(f"✓ {key} present in manifest")
            else:
                print(f"✗ {key} missing from manifest")
                return False
        
        # Check dependencies
        required_deps = ["'account'", "'mail'", "'web'", "'portal'", "'website'"]
        for dep in required_deps:
            if dep in content:
                print(f"✓ Dependency {dep} declared")
            else:
                print(f"✗ Missing dependency {dep}")
        
        return True
    
    except Exception as e:
        print(f"✗ Error reading manifest: {e}")
        return False

def check_security_files(module_path):
    """Check security configuration"""
    print("\n🔍 Checking Security Configuration:")
    
    # Check access CSV
    access_file = os.path.join(module_path, "security/ir.model.access.csv")
    if os.path.exists(access_file):
        print("✓ Access rights file exists")
        try:
            with open(access_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "payment_signature_wizard" in content and "payment_rejection_wizard" in content:
                    print("✓ Wizard access rights configured")
                else:
                    print("✗ Missing wizard access rights")
        except Exception as e:
            print(f"✗ Error reading access file: {e}")
    else:
        print("✗ Access rights file missing")
    
    # Check security groups
    groups_file = os.path.join(module_path, "data/security_groups.xml")
    if os.path.exists(groups_file):
        print("✓ Security groups file exists")
        try:
            with open(groups_file, 'r', encoding='utf-8') as f:
                content = f.read()
                required_groups = [
                    "group_payment_reviewer",
                    "group_payment_approver", 
                    "group_payment_authorizer"
                ]
                for group in required_groups:
                    if group in content:
                        print(f"✓ Security group {group} defined")
                    else:
                        print(f"✗ Missing security group {group}")
        except Exception as e:
            print(f"✗ Error reading groups file: {e}")
    else:
        print("✗ Security groups file missing")

def main():
    """Main validation function"""
    print("=" * 60)
    print("🚀 Payment Approval Workflow Module Validation")
    print("=" * 60)
    
    # Get module path
    if len(sys.argv) > 1:
        module_path = sys.argv[1]
    else:
        # Assume current directory
        module_path = os.path.dirname(os.path.abspath(__file__))
    
    print(f"📁 Module Path: {module_path}")
    
    # Run validation checks
    checks = [
        ("Python Dependencies", check_python_dependencies),
        ("Module Structure", lambda: validate_module_structure(module_path)),
        ("Manifest Content", lambda: check_manifest_content(module_path)),
        ("Security Configuration", lambda: check_security_files(module_path)),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"✗ Error in {check_name}: {e}")
            results.append((check_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check_name, result in results:
        status = "PASSED" if result else "FAILED"
        icon = "✅" if result else "❌"
        print(f"{icon} {check_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! Module is ready for use.")
        print("\nNext Steps:")
        print("1. Install the module in your Odoo instance")
        print("2. Configure security groups and assign users")
        print("3. Test the approval workflow")
        print("4. Customize email templates if needed")
    else:
        print("⚠️  SOME CHECKS FAILED! Please fix the issues above.")
        print("\nCommon solutions:")
        print("- Install missing Python dependencies: pip install qrcode")
        print("- Check file paths and permissions")
        print("- Verify XML syntax in data files")
        print("- Review manifest configuration")
    
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
