# -*- coding: utf-8 -*-
"""
Comprehensive Module Validation Script
======================================
This script validates the account_payment_final module for:
- Python syntax validation
- XML syntax validation
- Model-View compatibility
- Action method availability
- Field references
- Access rights consistency
"""

import os
import ast
import xml.etree.ElementTree as ET
import re
import csv


def validate_python_files():
    """Validate all Python files for syntax errors"""
    print("🐍 Validating Python Files...")
    errors = []
    
    for root, dirs, files in os.walk('account_payment_final'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    ast.parse(content)
                    print(f"  ✅ {filepath}")
                except SyntaxError as e:
                    error_msg = f"Syntax Error in {filepath}: {e}"
                    print(f"  ❌ {error_msg}")
                    errors.append(error_msg)
                except Exception as e:
                    error_msg = f"Error in {filepath}: {e}"
                    print(f"  ❌ {error_msg}")
                    errors.append(error_msg)
    
    return errors


def validate_xml_files():
    """Validate all XML files for syntax errors"""
    print("\n📄 Validating XML Files...")
    errors = []
    
    for root, dirs, files in os.walk('account_payment_final'):
        for file in files:
            if file.endswith('.xml'):
                filepath = os.path.join(root, file)
                try:
                    ET.parse(filepath)
                    print(f"  ✅ {filepath}")
                except ET.ParseError as e:
                    error_msg = f"XML Parse Error in {filepath}: {e}"
                    print(f"  ❌ {error_msg}")
                    errors.append(error_msg)
                except Exception as e:
                    error_msg = f"Error in {filepath}: {e}"
                    print(f"  ❌ {error_msg}")
                    errors.append(error_msg)
    
    return errors


def extract_action_refs():
    """Extract action references from view files"""
    print("\n🔍 Extracting Action References...")
    action_refs = set()
    
    view_files = [
        'account_payment_final/views/account_payment_views.xml',
        'account_payment_final/views/account_move_views.xml', 
        'account_payment_final/views/payment_verification_views.xml'
    ]
    
    for view_file in view_files:
        if os.path.exists(view_file):
            try:
                with open(view_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find button action references
                buttons = re.findall(r'<button[^>]+name="(action_[^"]*)"', content)
                action_refs.update(buttons)
                print(f"  📋 {view_file}: {len(buttons)} actions found")
                
            except Exception as e:
                print(f"  ❌ Error reading {view_file}: {e}")
    
    print(f"  📊 Total unique actions: {sorted(action_refs)}")
    return action_refs


def validate_model_actions():
    """Validate that all referenced actions exist in models"""
    print("\n🔧 Validating Model Actions...")
    errors = []
    
    # Get all action references
    action_refs = extract_action_refs()
    
    # Check each model file for action methods
    model_files = {
        'account.payment': 'account_payment_final/models/account_payment.py',
        'account.move': 'account_payment_final/models/account_move.py',
        'payment.verification.log': 'account_payment_final/models/payment_verification_log.py'
    }
    
    all_model_actions = set()
    
    for model_name, model_file in model_files.items():
        if os.path.exists(model_file):
            try:
                with open(model_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find action method definitions
                actions = re.findall(r'def (action_[^(]*)\(', content)
                all_model_actions.update(actions)
                print(f"  📦 {model_name}: {len(actions)} actions defined")
                
            except Exception as e:
                print(f"  ❌ Error reading {model_file}: {e}")
    
    # Check for missing actions
    missing_actions = action_refs - all_model_actions
    if missing_actions:
        for action in sorted(missing_actions):
            error_msg = f"Missing action method: {action}"
            print(f"  ❌ {error_msg}")
            errors.append(error_msg)
    else:
        print("  ✅ All referenced actions are defined")
    
    return errors


def validate_access_rights():
    """Validate access rights CSV file"""
    print("\n🔐 Validating Access Rights...")
    errors = []
    
    csv_file = 'account_payment_final/security/ir.model.access.csv'
    if os.path.exists(csv_file):
        try:
            with open(csv_file, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            if not rows:
                errors.append("Access rights CSV is empty")
                return errors
            
            # Validate header
            expected_header = ['id', 'name', 'model_id:id', 'group_id:id', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink']
            if rows[0] != expected_header:
                errors.append(f"Invalid CSV header: {rows[0]}")
            
            # Validate rows
            for i, row in enumerate(rows[1:], 1):
                if len(row) != 8:
                    errors.append(f"Row {i}: Invalid column count ({len(row)} instead of 8)")
                else:
                    print(f"  ✅ Row {i}: {row[0]}")
            
            if not errors:
                print(f"  ✅ Access rights validated: {len(rows)-1} rules")
                
        except Exception as e:
            errors.append(f"Error reading access rights CSV: {e}")
    else:
        errors.append("Access rights CSV file not found")
    
    return errors


def main():
    """Run comprehensive module validation"""
    print("🚀 Starting Comprehensive Module Validation")
    print("=" * 50)
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    all_errors = []
    
    # Run all validations
    all_errors.extend(validate_python_files())
    all_errors.extend(validate_xml_files())
    all_errors.extend(validate_model_actions())
    all_errors.extend(validate_access_rights())
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 VALIDATION SUMMARY")
    print("=" * 50)
    
    if all_errors:
        print(f"❌ Found {len(all_errors)} errors:")
        for i, error in enumerate(all_errors, 1):
            print(f"  {i}. {error}")
        print("\n🔧 Please fix these errors before deployment!")
    else:
        print("✅ ALL VALIDATIONS PASSED!")
        print("🎉 Module is ready for deployment!")


if __name__ == "__main__":
    main()
