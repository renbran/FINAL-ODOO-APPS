#!/usr/bin/env python3
"""
Final Validation Script for Account Statement Module
Tests all components before production deployment
"""

import os
import sys
import ast
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_module_structure():
    """Validate the module has all required files"""
    print("🔍 Validating Module Structure...")
    
    base_path = Path("account_statement")
    required_files = [
        "__init__.py",
        "__manifest__.py",
        "models/__init__.py",
        "models/account_statement.py", 
        "models/account_statement_wizard.py",
        "views/account_statement_views.xml",
        "views/account_statement_wizard_views.xml",
        "views/res_partner_views.xml",
        "security/account_statement_security.xml",
        "security/ir.model.access.csv",
        "data/report_paperformat.xml",
        "report/__init__.py",
        "report/account_statement_report_action.xml",
        "report/account_statement_report_template.xml"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = base_path / file_path
        if not full_path.exists():
            missing_files.append(str(file_path))
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def validate_python_syntax():
    """Validate Python files for syntax errors"""
    print("\n🐍 Validating Python Syntax...")
    
    python_files = [
        "account_statement/__init__.py",
        "account_statement/__manifest__.py", 
        "account_statement/models/__init__.py",
        "account_statement/models/account_statement.py",
        "account_statement/models/account_statement_wizard.py",
        "account_statement/report/__init__.py"
    ]
    
    errors = []
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
                print(f"✅ {file_path}")
            except SyntaxError as e:
                errors.append(f"{file_path}: {e}")
                print(f"❌ {file_path}: {e}")
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return len(errors) == 0

def validate_xml_syntax():
    """Validate XML files for syntax errors"""
    print("\n📄 Validating XML Syntax...")
    
    xml_files = [
        "account_statement/views/account_statement_views.xml",
        "account_statement/views/account_statement_wizard_views.xml", 
        "account_statement/views/res_partner_views.xml",
        "account_statement/security/account_statement_security.xml",
        "account_statement/data/report_paperformat.xml",
        "account_statement/report/account_statement_report_action.xml",
        "account_statement/report/account_statement_report_template.xml"
    ]
    
    errors = []
    for file_path in xml_files:
        if os.path.exists(file_path):
            try:
                ET.parse(file_path)
                print(f"✅ {file_path}")
            except ET.ParseError as e:
                errors.append(f"{file_path}: {e}")
                print(f"❌ {file_path}: {e}")
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return len(errors) == 0

def validate_manifest():
    """Validate manifest file"""
    print("\n📋 Validating Manifest...")
    
    manifest_path = "account_statement/__manifest__.py"
    if not os.path.exists(manifest_path):
        print("❌ Manifest file not found")
        return False
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse manifest
        manifest_dict = eval(content)
        
        required_keys = ['name', 'version', 'depends', 'data', 'installable']
        missing_keys = [key for key in required_keys if key not in manifest_dict]
        
        if missing_keys:
            print(f"❌ Missing manifest keys: {missing_keys}")
            return False
        
        # Check version format
        version = manifest_dict.get('version', '')
        if not version.startswith('17.0'):
            print(f"⚠️  Version should start with '17.0', found: {version}")
        
        # Check dependencies
        depends = manifest_dict.get('depends', [])
        expected_depends = ['base', 'account', 'contacts']
        for dep in expected_depends:
            if dep not in depends:
                print(f"⚠️  Missing dependency: {dep}")
        
        print("✅ Manifest validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Error validating manifest: {e}")
        return False

def validate_security_files():
    """Validate security configuration"""
    print("\n🔒 Validating Security Files...")
    
    # Check security XML
    security_xml = "account_statement/security/account_statement_security.xml"
    if os.path.exists(security_xml):
        try:
            tree = ET.parse(security_xml)
            root = tree.getroot()
            
            # Check for security groups
            groups = root.findall(".//record[@model='res.groups']")
            if groups:
                print(f"✅ Found {len(groups)} security groups")
            else:
                print("⚠️  No security groups found")
            
        except Exception as e:
            print(f"❌ Error parsing security XML: {e}")
            return False
    
    # Check access CSV
    access_csv = "account_statement/security/ir.model.access.csv"
    if os.path.exists(access_csv):
        try:
            with open(access_csv, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if len(lines) > 1:  # Header + data
                print(f"✅ Found {len(lines)-1} access rules")
            else:
                print("⚠️  No access rules found")
                
        except Exception as e:
            print(f"❌ Error reading access CSV: {e}")
            return False
    
    return True

def check_odoo17_compatibility():
    """Check for Odoo 17.0 compatibility issues"""
    print("\n🔧 Checking Odoo 17.0 Compatibility...")
    
    # Check for deprecated attributes in XML files
    xml_files = [
        "account_statement/views/account_statement_views.xml",
        "account_statement/views/account_statement_wizard_views.xml",
        "account_statement/views/res_partner_views.xml"
    ]
    
    deprecated_attrs = ['states', 'attrs']
    issues = []
    
    for file_path in xml_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for attr in deprecated_attrs:
                    if f'{attr}=' in content:
                        issues.append(f"{file_path}: Contains deprecated '{attr}' attribute")
                
            except Exception as e:
                issues.append(f"{file_path}: Error reading file - {e}")
    
    if issues:
        print("❌ Odoo 17.0 compatibility issues found:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ No deprecated attributes found")
        return True

def run_full_validation():
    """Run all validation tests"""
    print("🚀 Starting Full Module Validation...")
    print("=" * 50)
    
    tests = [
        ("Module Structure", validate_module_structure),
        ("Python Syntax", validate_python_syntax),
        ("XML Syntax", validate_xml_syntax),
        ("Manifest", validate_manifest),
        ("Security Files", validate_security_files),
        ("Odoo 17.0 Compatibility", check_odoo17_compatibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: Error during validation - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 MODULE IS READY FOR PRODUCTION!")
        print("\nNext steps:")
        print("1. Restart your Odoo service")
        print("2. Update Apps List")
        print("3. Install the Account Statement module")
        print("4. Test in both Contacts and Accounting apps")
        return True
    else:
        print("⚠️  Some issues need to be resolved before deployment")
        return False

if __name__ == "__main__":
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        success = run_full_validation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"💥 Validation script failed: {e}")
        sys.exit(1)
