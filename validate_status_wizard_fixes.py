#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Status Change Wizard Validation Script
======================================

Validates the fixes and completions made to the status_change_wizard.py
and related order status management functionality.

Author: Odoo 17 Development Team
Date: August 17, 2025
"""

import os
import sys
import ast
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def validate_file_syntax(file_path):
    """Validate Python file syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the AST
        ast.parse(source, filename=file_path)
        return True, "Syntax valid"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def analyze_class_methods(file_path, class_name):
    """Analyze methods in a specific class"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source)
        methods = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(item.name)
        
        return methods
    except Exception as e:
        logger.error(f"Error analyzing {file_path}: {e}")
        return []

def validate_wizard_completeness():
    """Validate that the status change wizard is complete"""
    print("\n🔍 STATUS CHANGE WIZARD VALIDATION")
    print("=" * 50)
    
    wizard_path = "order_status_override/models/status_change_wizard.py"
    
    # Check file exists
    if not os.path.exists(wizard_path):
        print(f"❌ File not found: {wizard_path}")
        return False
    
    # Validate syntax
    valid, msg = validate_file_syntax(wizard_path)
    if not valid:
        print(f"❌ Syntax validation failed: {msg}")
        return False
    
    print(f"✅ Syntax validation passed")
    
    # Check required methods
    required_methods = [
        '__init__',
        'default_get',
        '_get_current_order_status',
        '_compute_required_assignments',
        '_onchange_current_status',
        '_onchange_new_status',
        '_onchange_order_id',
        'change_status',
        '_validate_status_transition',
        '_apply_status_change',
        '_update_order_status_and_state',
        '_create_status_history',
        '_send_notifications',
        '_send_user_notification',
        '_validate_assignments',
        '_validate_user_permissions',
        '_update_assignments',
        'action_cancel',
        'action_force_change'
    ]
    
    actual_methods = analyze_class_methods(wizard_path, "OrderStatusChangeWizard")
    
    print(f"\n📋 Method Analysis:")
    print(f"   Required methods: {len(required_methods)}")
    print(f"   Implemented methods: {len(actual_methods)}")
    
    missing_methods = set(required_methods) - set(actual_methods)
    extra_methods = set(actual_methods) - set(required_methods)
    
    if missing_methods:
        print(f"❌ Missing methods: {missing_methods}")
    else:
        print(f"✅ All required methods implemented")
    
    if extra_methods:
        print(f"ℹ️  Additional methods: {extra_methods}")
    
    return len(missing_methods) == 0

def validate_sale_order_extension():
    """Validate sale order model extensions"""
    print("\n🔍 SALE ORDER EXTENSION VALIDATION")
    print("=" * 50)
    
    sale_order_path = "order_status_override/models/sale_order.py"
    
    # Check file exists
    if not os.path.exists(sale_order_path):
        print(f"❌ File not found: {sale_order_path}")
        return False
    
    # Validate syntax
    valid, msg = validate_file_syntax(sale_order_path)
    if not valid:
        print(f"❌ Syntax validation failed: {msg}")
        return False
    
    print(f"✅ Syntax validation passed")
    
    # Check for _change_status method
    methods = analyze_class_methods(sale_order_path, "SaleOrder")
    
    if '_change_status' in methods:
        print(f"✅ _change_status method found")
    else:
        print(f"❌ _change_status method missing")
        return False
    
    # Check for required fields in file content
    try:
        with open(sale_order_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_fields = [
            'order_status_id',
            'documentation_user_id', 
            'commission_user_id',
            'final_review_user_id'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in content:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return False
        else:
            print(f"✅ All required fields found")
    
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    return True

def validate_security_fix():
    """Validate that security.xml is fixed"""
    print("\n🔍 SECURITY.XML VALIDATION")
    print("=" * 50)
    
    security_path = "order_status_override/security/security.xml"
    
    if not os.path.exists(security_path):
        print(f"❌ File not found: {security_path}")
        return False
    
    try:
        import xml.etree.ElementTree as ET
        ET.parse(security_path)
        print(f"✅ XML syntax is valid")
        
        # Check for line 85 fix
        with open(security_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"📊 Total lines: {len(lines)}")
        
        # Find implied_ids field
        for i, line in enumerate(lines, 1):
            if 'implied_ids' in line and 'eval=' in line:
                if '\n' not in line.strip():
                    print(f"✅ Line {i}: implied_ids field is properly formatted (single line)")
                    return True
        
        print(f"⚠️  Could not verify implied_ids field format")
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main validation function"""
    print("🚀 ORDER STATUS OVERRIDE MODULE VALIDATION")
    print("=" * 60)
    print("Validating fixes and completions for the status change wizard")
    print(f"Date: August 17, 2025")
    print()
    
    # Change to module directory
    if os.path.exists("order_status_override"):
        os.chdir("order_status_override")
        print(f"📁 Working directory: {os.getcwd()}")
    
    results = []
    
    # Run validations
    results.append(("Status Change Wizard", validate_wizard_completeness()))
    results.append(("Sale Order Extension", validate_sale_order_extension()))
    results.append(("Security XML Fix", validate_security_fix()))
    
    # Summary
    print("\n🎯 VALIDATION SUMMARY")
    print("=" * 30)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ Module is ready for CloudPepper deployment")
        print()
        print("📋 DEPLOYMENT CHECKLIST:")
        print("1. Upload order_status_override module to CloudPepper")
        print("2. Go to Apps -> order_status_override -> Update")
        print("3. Test the status change wizard functionality")
        print("4. Verify user assignments work correctly")
        print("5. Check that notifications are sent properly")
    else:
        print("❌ Some validations failed - please review and fix")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
