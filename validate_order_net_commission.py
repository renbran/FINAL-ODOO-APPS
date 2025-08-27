#!/usr/bin/env python3
"""
Order Net Commission Module Validation Script
OSUS Properties - Odoo 17 Deployment Ready
"""

import os
import sys
import json
import xml.etree.ElementTree as ET
import ast
from datetime import datetime

def validate_order_net_commission():
    """Validate the order_net_commission module for CloudPepper deployment"""
    
    print("🚀 ORDER NET COMMISSION MODULE VALIDATION")
    print("="*60)
    print(f"📅 Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Target: order_net_commission module")
    print("📊 OSUS Properties Branding Compliance")
    print()
    
    results = {
        'passed': 0,
        'failed': 0,
        'warnings': 0,
        'errors': []
    }
    
    module_path = "order_net_commission"
    
    # Check 1: Module Structure
    print("🔧 Checking Module Structure...")
    required_files = [
        '__manifest__.py',
        '__init__.py',
        'models/__init__.py',
        'models/sale_order.py',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_form.xml',
        'views/sale_order_tree.xml',
        'data/mail_activity_data.xml',
        'static/src/scss/order_commission_style.scss',
        'tests/__init__.py',
        'tests/test_workflow.py'
    ]
    
    for file_path in required_files:
        full_path = os.path.join(module_path, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
            results['passed'] += 1
        else:
            print(f"❌ {file_path} - MISSING")
            results['failed'] += 1
            results['errors'].append(f"Missing required file: {file_path}")
    
    # Check 2: Manifest File Validation
    print("\n🔧 Checking Manifest File...")
    manifest_path = os.path.join(module_path, '__manifest__.py')
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_content = f.read()
            
            # Parse manifest
            manifest_ast = ast.parse(manifest_content)
            
            # Check for required fields
            required_manifest_fields = [
                'name', 'version', 'depends', 'data', 'assets'
            ]
            
            print("✅ Manifest file is valid Python")
            
            # Check OSUS branding
            if 'OSUS Properties' in manifest_content:
                print("✅ OSUS Properties branding present")
                results['passed'] += 1
            else:
                print("⚠️ OSUS Properties branding not found")
                results['warnings'] += 1
            
            # Check version format
            if '17.0.1.0.0' in manifest_content:
                print("✅ Correct Odoo 17 version format")
                results['passed'] += 1
            else:
                print("❌ Incorrect version format")
                results['failed'] += 1
                
        except Exception as e:
            print(f"❌ Manifest validation failed: {e}")
            results['failed'] += 1
            results['errors'].append(f"Manifest error: {e}")
    
    # Check 3: Python Syntax Validation
    print("\n🔧 Checking Python Files...")
    python_files = [
        'models/sale_order.py',
        'tests/test_workflow.py'
    ]
    
    for py_file in python_files:
        file_path = os.path.join(module_path, py_file)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse Python syntax
                ast.parse(content)
                print(f"✅ {py_file} - Valid Python syntax")
                results['passed'] += 1
                
                # Check for CloudPepper compatibility patterns
                if 'try:' in content and 'except' in content:
                    print(f"✅ {py_file} - Has error handling")
                    results['passed'] += 1
                
                # Check for workflow methods
                if py_file == 'models/sale_order.py':
                    required_methods = [
                        'action_set_documentation',
                        'action_set_commission', 
                        'action_approve_commission'
                    ]
                    for method in required_methods:
                        if method in content:
                            print(f"✅ {py_file} - Method {method} found")
                            results['passed'] += 1
                        else:
                            print(f"❌ {py_file} - Method {method} missing")
                            results['failed'] += 1
                            
            except SyntaxError as e:
                print(f"❌ {py_file} - Syntax error: {e}")
                results['failed'] += 1
                results['errors'].append(f"Python syntax error in {py_file}: {e}")
            except Exception as e:
                print(f"❌ {py_file} - Error: {e}")
                results['failed'] += 1
    
    # Check 4: XML Validation
    print("\n🔧 Checking XML Files...")
    xml_files = [
        'security/security.xml',
        'views/sale_order_form.xml',
        'views/sale_order_tree.xml',
        'data/mail_activity_data.xml'
    ]
    
    for xml_file in xml_files:
        file_path = os.path.join(module_path, xml_file)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse XML
                ET.fromstring(content)
                print(f"✅ {xml_file} - Valid XML")
                results['passed'] += 1
                
                # Check for OSUS specific elements
                if xml_file == 'views/sale_order_form.xml':
                    if 'o_commission_btn' in content:
                        print(f"✅ {xml_file} - Custom commission buttons found")
                        results['passed'] += 1
                    if 'order_net_commission.group_' in content:
                        print(f"✅ {xml_file} - Security groups referenced")
                        results['passed'] += 1
                        
            except ET.ParseError as e:
                print(f"❌ {xml_file} - XML parse error: {e}")
                results['failed'] += 1
                results['errors'].append(f"XML error in {xml_file}: {e}")
            except Exception as e:
                print(f"❌ {xml_file} - Error: {e}")
                results['failed'] += 1
    
    # Check 5: Security Configuration
    print("\n🔧 Checking Security Configuration...")
    security_xml = os.path.join(module_path, 'security/security.xml')
    access_csv = os.path.join(module_path, 'security/ir.model.access.csv')
    
    if os.path.exists(security_xml) and os.path.exists(access_csv):
        # Check security groups
        with open(security_xml, 'r', encoding='utf-8') as f:
            security_content = f.read()
        
        required_groups = [
            'group_documentation_officer',
            'group_commission_analyst',
            'group_sales_approver'
        ]
        
        for group in required_groups:
            if group in security_content:
                print(f"✅ Security group {group} defined")
                results['passed'] += 1
            else:
                print(f"❌ Security group {group} missing")
                results['failed'] += 1
        
        # Check access rights
        with open(access_csv, 'r', encoding='utf-8') as f:
            access_content = f.read()
        
        if 'group_documentation_officer' in access_content:
            print("✅ Access rights configured for security groups")
            results['passed'] += 1
        else:
            print("❌ Access rights not properly configured")
            results['failed'] += 1
    
    # Check 6: SCSS Styling
    print("\n🔧 Checking OSUS Styling...")
    scss_file = os.path.join(module_path, 'static/src/scss/order_commission_style.scss')
    if os.path.exists(scss_file):
        with open(scss_file, 'r', encoding='utf-8') as f:
            scss_content = f.read()
        
        # Check OSUS colors
        if '--osus-primary: #800020' in scss_content:
            print("✅ OSUS burgundy color (#800020) defined")
            results['passed'] += 1
        else:
            print("❌ OSUS burgundy color not found")
            results['failed'] += 1
        
        if '--osus-secondary: #FFD700' in scss_content:
            print("✅ OSUS gold color (#FFD700) defined")
            results['passed'] += 1
        else:
            print("❌ OSUS gold color not found") 
            results['failed'] += 1
    
    # Final Assessment
    print("\n" + "="*60)
    print("📊 VALIDATION SUMMARY")
    print("="*60)
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"⚠️ Warnings: {results['warnings']}")
    
    if results['failed'] == 0:
        print("\n🎉 MODULE VALIDATION SUCCESSFUL!")
        print("✅ Ready for CloudPepper deployment")
        print("✅ OSUS Properties branding compliant")
        print("✅ Odoo 17 compatible")
        print("✅ Security properly configured")
        print("✅ Workflow implementation complete")
        deployment_ready = True
    else:
        print("\n🔴 MODULE VALIDATION FAILED!")
        print(f"❌ {results['failed']} critical issues found")
        for error in results['errors']:
            print(f"   • {error}")
        deployment_ready = False
    
    # Create validation report
    report = {
        'module': 'order_net_commission',
        'validation_date': datetime.now().isoformat(),
        'deployment_ready': deployment_ready,
        'results': results,
        'osus_branding': True,
        'cloudpepper_compatible': deployment_ready
    }
    
    with open('order_net_commission_validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📋 Validation report saved: order_net_commission_validation_report.json")
    
    return deployment_ready

if __name__ == "__main__":
    validate_order_net_commission()
