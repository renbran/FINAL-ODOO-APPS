#!/usr/bin/env python3
"""
Comprehensive Workflow Validation for order_status_override module
Validates all action methods, fields, and workflow consistency
"""

import os
import ast
import xml.etree.ElementTree as ET
import re

def validate_workflow_methods():
    """Validate all workflow action methods exist in sale_order.py"""
    
    print("🔍 Validating Workflow Methods...")
    
    model_file = 'order_status_override/models/sale_order.py'
    
    if not os.path.exists(model_file):
        print(f"❌ Model file not found: {model_file}")
        return False
    
    with open(model_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Expected workflow methods
    expected_methods = [
        'action_move_to_document_review',
        'action_move_to_commission_calculation', 
        'action_move_to_allocation',
        'action_move_to_final_review',
        'action_approve_order',
        'action_move_to_post'
    ]
    
    missing_methods = []
    found_methods = []
    
    for method in expected_methods:
        if f"def {method}(" in content:
            found_methods.append(method)
            print(f"✅ Found method: {method}")
        else:
            missing_methods.append(method)
            print(f"❌ Missing method: {method}")
    
    if missing_methods:
        print(f"\n❌ Missing {len(missing_methods)} workflow methods:")
        for method in missing_methods:
            print(f"   - {method}")
        return False
    
    print(f"\n✅ All {len(found_methods)} workflow methods found!")
    return True

def validate_workflow_fields():
    """Validate all workflow-related fields exist"""
    
    print("\n🔍 Validating Workflow Fields...")
    
    model_file = 'order_status_override/models/sale_order.py'
    
    with open(model_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Expected workflow fields
    expected_fields = [
        'order_status',
        'commission_user_id',
        'final_review_user_id',
        'show_document_review_button',
        'show_commission_calculation_button',
        'show_allocation_button', 
        'show_final_review_button',
        'show_approve_button',
        'show_post_button'
    ]
    
    missing_fields = []
    found_fields = []
    
    for field in expected_fields:
        if f"{field} = fields." in content:
            found_fields.append(field)
            print(f"✅ Found field: {field}")
        else:
            missing_fields.append(field)
            print(f"❌ Missing field: {field}")
    
    if missing_fields:
        print(f"\n❌ Missing {len(missing_fields)} workflow fields:")
        for field in missing_fields:
            print(f"   - {field}")
        return False
    
    print(f"\n✅ All {len(found_fields)} workflow fields found!")
    return True

def validate_workflow_stages():
    """Validate workflow stages consistency"""
    
    print("\n🔍 Validating Workflow Stages...")
    
    model_file = 'order_status_override/models/sale_order.py'
    
    with open(model_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Expected 7-stage workflow
    expected_stages = [
        'draft',
        'document_review', 
        'commission_calculation',
        'allocation',
        'final_review',
        'approved',
        'post'
    ]
    
    # Find order_status field definition
    stage_pattern = r"order_status = fields\.Selection\(\[(.*?)\]"
    match = re.search(stage_pattern, content, re.DOTALL)
    
    if not match:
        print("❌ order_status field definition not found")
        return False
    
    stages_text = match.group(1)
    found_stages = []
    
    for stage in expected_stages:
        if f"'{stage}'" in stages_text or f'"{stage}"' in stages_text:
            found_stages.append(stage)
            print(f"✅ Found stage: {stage}")
        else:
            print(f"❌ Missing stage: {stage}")
    
    if len(found_stages) != len(expected_stages):
        print(f"\n❌ Stage count mismatch. Expected {len(expected_stages)}, found {len(found_stages)}")
        return False
    
    print(f"\n✅ All {len(found_stages)} workflow stages found!")
    return True

def validate_view_buttons():
    """Validate view buttons match model methods"""
    
    print("\n🔍 Validating View Buttons...")
    
    view_file = 'order_status_override/views/order_views_assignment.xml'
    
    if not os.path.exists(view_file):
        print(f"❌ View file not found: {view_file}")
        return False
    
    try:
        tree = ET.parse(view_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"❌ XML parse error: {e}")
        return False
    
    # Find button elements
    buttons = root.findall('.//button[@name]')
    
    expected_buttons = [
        'action_move_to_document_review',
        'action_move_to_commission_calculation',
        'action_move_to_allocation', 
        'action_move_to_final_review',
        'action_approve_order',
        'action_move_to_post'
    ]
    
    found_buttons = []
    for button in buttons:
        button_name = button.get('name')
        if button_name in expected_buttons:
            found_buttons.append(button_name)
            print(f"✅ Found button: {button_name}")
    
    missing_buttons = [btn for btn in expected_buttons if btn not in found_buttons]
    
    if missing_buttons:
        print(f"\n❌ Missing {len(missing_buttons)} buttons:")
        for button in missing_buttons:
            print(f"   - {button}")
        return False
    
    print(f"\n✅ All {len(found_buttons)} workflow buttons found!")
    return True

def validate_python_syntax():
    """Validate Python syntax for all Python files"""
    
    print("\n🔍 Validating Python Syntax...")
    
    python_files = [
        'order_status_override/models/__init__.py',
        'order_status_override/models/sale_order.py',
        'order_status_override/__init__.py'
    ]
    
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
                print(f"✅ Python syntax valid: {file_path}")
            except SyntaxError as e:
                print(f"❌ Python syntax error in {file_path}: {e}")
                return False
        else:
            print(f"⚠️  File not found: {file_path}")
    
    return True

def main():
    """Run comprehensive workflow validation"""
    
    print("🚀 Starting Comprehensive Workflow Validation\n")
    print("=" * 60)
    
    validations = [
        ("Workflow Methods", validate_workflow_methods),
        ("Workflow Fields", validate_workflow_fields), 
        ("Workflow Stages", validate_workflow_stages),
        ("View Buttons", validate_view_buttons),
        ("Python Syntax", validate_python_syntax)
    ]
    
    all_passed = True
    results = []
    
    for name, validator in validations:
        try:
            result = validator()
            results.append((name, result))
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {name} validation failed with error: {e}")
            results.append((name, False))
            all_passed = False
        
        print("\n" + "-" * 60)
    
    # Summary
    print("\n🎯 VALIDATION SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:<20} {status}")
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ order_status_override module is ready for testing")
        return True
    else:
        print("❌ SOME VALIDATIONS FAILED!")
        print("⚠️  Please fix the issues above before proceeding")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
