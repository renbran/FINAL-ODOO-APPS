#!/usr/bin/env python3
"""
Account Statement Module Validation Script
This script validates the module structure and identifies potential issues.
"""

import os
import sys

def validate_module_structure(module_path):
    """Validate the module structure and files"""
    print("🔍 Validating Account Statement Module Structure...")
    print(f"📁 Module Path: {module_path}")
    
    issues = []
    recommendations = []
    
    # Check required files
    required_files = [
        '__manifest__.py',
        '__init__.py',
        'models/__init__.py',
        'models/account_statement.py', 
        'models/account_statement_wizard.py',
        'views/account_statement_views.xml',
        'views/account_statement_wizard_views.xml',
        'views/res_partner_views.xml',
        'security/account_statement_security.xml',
        'security/ir.model.access.csv'
    ]
    
    for file_path in required_files:
        full_path = os.path.join(module_path, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            issues.append(f"❌ Missing file: {file_path}")
    
    # Check optional files
    optional_files = [
        'data/report_paperformat.xml',
        'report/account_statement_report_action.xml',
        'report/account_statement_report_template.xml'
    ]
    
    for file_path in optional_files:
        full_path = os.path.join(module_path, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path} (optional)")
        else:
            recommendations.append(f"📝 Consider adding: {file_path}")
    
    # Print results
    print("\n" + "="*50)
    print("📋 VALIDATION RESULTS")
    print("="*50)
    
    if not issues:
        print("🎉 All required files are present!")
    else:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"   {issue}")
    
    if recommendations:
        print("\n💡 Recommendations:")
        for recommendation in recommendations:
            print(f"   {recommendation}")
    
    # Check manifest content
    manifest_path = os.path.join(module_path, '__manifest__.py')
    if os.path.exists(manifest_path):
        print("\n📄 Checking manifest file...")
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "'contacts'" in content:
            print("✅ Contacts app dependency found")
        else:
            issues.append("❌ Missing 'contacts' dependency")
            
        if "'account'" in content:
            print("✅ Account app dependency found")
        else:
            issues.append("❌ Missing 'account' dependency")
    
    print("\n" + "="*50)
    print("🏁 FINAL STATUS")
    print("="*50)
    
    if not issues:
        print("🟢 MODULE IS READY FOR INSTALLATION!")
        print("✨ The module should work in both Contacts and Accounting apps")
        return True
    else:
        print("🔴 MODULE HAS ISSUES THAT NEED TO BE FIXED:")
        for issue in issues:
            print(f"   {issue}")
        return False

if __name__ == "__main__":
    module_path = r"d:\RUNNING APPS\ready production\odoo_17_final\account_statement"
    
    if os.path.exists(module_path):
        is_valid = validate_module_structure(module_path)
        sys.exit(0 if is_valid else 1)
    else:
        print(f"❌ Module path not found: {module_path}")
        sys.exit(1)
