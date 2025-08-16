#!/usr/bin/env python3
"""
Additional Odoo 17 specific validation for order_status_override module
"""

import os
import re
import xml.etree.ElementTree as ET

def check_security_groups():
    """Check if all referenced security groups are defined"""
    print("🔒 Checking Security Groups...")
    
    # Extract group references from Python files
    groups_referenced = set()
    python_files = ['models/sale_order.py']
    
    for file_path in python_files:
        full_path = f'order_status_override/{file_path}'
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find group references
            group_pattern = r"has_group\(['\"]([^'\"]+)['\"]\)"
            groups = re.findall(group_pattern, content)
            groups_referenced.update(groups)
    
    print(f"📝 Found {len(groups_referenced)} group references:")
    for group in sorted(groups_referenced):
        print(f"   - {group}")
    
    # Check if groups are defined in security.xml
    security_file = 'order_status_override/security/security.xml'
    if os.path.exists(security_file):
        try:
            tree = ET.parse(security_file)
            root = tree.getroot()
            
            defined_groups = []
            for record in root.findall('.//record[@model="res.groups"]'):
                group_id = record.get('id')
                if group_id:
                    full_id = f"order_status_override.{group_id}"
                    defined_groups.append(full_id)
            
            print(f"\n🛡️  Defined groups in security.xml: {len(defined_groups)}")
            for group in defined_groups:
                print(f"   - {group}")
            
            # Check for missing group definitions
            missing_groups = groups_referenced - set(defined_groups)
            if missing_groups:
                print(f"\n❌ Missing group definitions:")
                for group in missing_groups:
                    print(f"   - {group}")
                return False
            else:
                print(f"\n✅ All referenced groups are properly defined")
                return True
                
        except Exception as e:
            print(f"❌ Error reading security.xml: {e}")
            return False
    else:
        print(f"❌ security.xml not found")
        return False

def check_view_inheritance():
    """Check view inheritance is properly structured"""
    print("\n👁️  Checking View Inheritance...")
    
    view_files = [
        'views/order_status_views.xml',
        'views/order_views_assignment.xml',
        'views/email_template_views.xml',
        'views/report_wizard_views.xml'
    ]
    
    inheritance_issues = []
    
    for view_file in view_files:
        full_path = f'order_status_override/{view_file}'
        if os.path.exists(full_path):
            try:
                tree = ET.parse(full_path)
                root = tree.getroot()
                
                # Check view inheritance
                for record in root.findall('.//record[@model="ir.ui.view"]'):
                    view_id = record.get('id', 'Unknown')
                    
                    # Check for inherit_id
                    inherit_id_elem = record.find('field[@name="inherit_id"]')
                    if inherit_id_elem is not None:
                        inherit_id = inherit_id_elem.get('ref')
                        if inherit_id:
                            print(f"   ✅ View {view_id} inherits from {inherit_id}")
                        else:
                            inheritance_issues.append(f"View {view_id} has empty inherit_id")
                    
                    # Check arch structure
                    arch_elem = record.find('field[@name="arch"]')
                    if arch_elem is not None:
                        # Check for proper xpath or field positioning
                        xpath_elems = arch_elem.findall('.//xpath')
                        if xpath_elems:
                            for xpath in xpath_elems:
                                expr = xpath.get('expr')
                                position = xpath.get('position')
                                if expr and position:
                                    print(f"   ✅ XPath: {expr} ({position})")
                                else:
                                    inheritance_issues.append(f"Invalid xpath in {view_id}")
                        
            except ET.ParseError as e:
                inheritance_issues.append(f"XML parse error in {view_file}: {e}")
            except Exception as e:
                inheritance_issues.append(f"Error reading {view_file}: {e}")
        else:
            inheritance_issues.append(f"View file not found: {view_file}")
    
    if inheritance_issues:
        print(f"\n❌ View inheritance issues found:")
        for issue in inheritance_issues:
            print(f"   - {issue}")
        return False
    else:
        print(f"\n✅ View inheritance structure is valid")
        return True

def check_model_references():
    """Check all model references are valid"""
    print("\n📊 Checking Model References...")
    
    # Models that should exist
    expected_models = [
        'sale.order',  # Extended model
        'order.status',  # Custom model
        'order.status.history',  # Custom model
        'res.users',  # Standard Odoo model
        'res.partner',  # Standard Odoo model
    ]
    
    issues = []
    
    # Check model files exist
    model_files = [
        'models/sale_order.py',
        'models/order_status.py',
        'models/commission_models.py',
        'models/status_change_wizard.py'
    ]
    
    for model_file in model_files:
        full_path = f'order_status_override/{model_file}'
        if os.path.exists(full_path):
            print(f"   ✅ Model file exists: {model_file}")
        else:
            issues.append(f"Model file missing: {model_file}")
    
    # Check model imports in __init__.py
    init_file = 'order_status_override/models/__init__.py'
    if os.path.exists(init_file):
        with open(init_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        expected_imports = ['order_status', 'commission_models', 'sale_order', 'status_change_wizard']
        for import_name in expected_imports:
            if f"from . import {import_name}" in content:
                print(f"   ✅ Model import found: {import_name}")
            else:
                issues.append(f"Missing model import: {import_name}")
    else:
        issues.append("models/__init__.py not found")
    
    if issues:
        print(f"\n❌ Model reference issues:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print(f"\n✅ All model references are valid")
        return True

def check_data_file_references():
    """Check data file structure and references"""
    print("\n📁 Checking Data File References...")
    
    data_files = [
        'data/order_status_data.xml',
        'data/email_templates.xml',
        'data/paperformat.xml'
    ]
    
    issues = []
    
    for data_file in data_files:
        full_path = f'order_status_override/{data_file}'
        if os.path.exists(full_path):
            try:
                tree = ET.parse(full_path)
                print(f"   ✅ Data file valid: {data_file}")
            except ET.ParseError as e:
                issues.append(f"XML parse error in {data_file}: {e}")
        else:
            print(f"   ⚠️  Data file not found: {data_file}")
    
    if issues:
        print(f"\n❌ Data file issues:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print(f"\n✅ Data files are valid")
        return True

def check_report_structure():
    """Check report structure and references"""
    print("\n📄 Checking Report Structure...")
    
    report_files = [
        'reports/order_status_reports.xml',
        'reports/commission_report_enhanced.xml',
        'reports/sale_commission_report.xml',
        'reports/sale_commission_template.xml',
        'reports/enhanced_order_status_report_template.xml',
        'reports/enhanced_order_status_report_template_updated.xml',
        'reports/enhanced_order_status_report_actions.xml'
    ]
    
    existing_reports = []
    missing_reports = []
    
    for report_file in report_files:
        full_path = f'order_status_override/{report_file}'
        if os.path.exists(full_path):
            try:
                tree = ET.parse(full_path)
                existing_reports.append(report_file)
                print(f"   ✅ Report file valid: {report_file}")
            except ET.ParseError as e:
                print(f"   ❌ XML parse error in {report_file}: {e}")
        else:
            missing_reports.append(report_file)
            print(f"   ⚠️  Report file not found: {report_file}")
    
    print(f"\n📊 Report Summary:")
    print(f"   - Existing reports: {len(existing_reports)}")
    print(f"   - Missing reports: {len(missing_reports)}")
    
    return len(existing_reports) > 0

def main():
    """Run additional validation checks"""
    print("🔍 Running Additional Odoo 17 Validation Checks")
    print("="*60)
    
    checks = [
        ("Security Groups", check_security_groups),
        ("View Inheritance", check_view_inheritance),
        ("Model References", check_model_references),
        ("Data File References", check_data_file_references),
        ("Report Structure", check_report_structure)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Error during {check_name} check: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📋 ADDITIONAL VALIDATION SUMMARY")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for check_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{check_name:<20} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Overall Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    
    if failed == 0:
        print(f"\n🎉 ALL ADDITIONAL CHECKS PASSED!")
        print(f"✅ Module passes advanced Odoo 17 validation")
    else:
        print(f"\n⚠️  SOME CHECKS FAILED")
        print(f"🔧 Review failed checks before deployment")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
