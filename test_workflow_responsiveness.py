#!/usr/bin/env python3
"""
Enhanced Workflow Logic and Responsiveness Test for account_payment_final module
Tests all workflow transitions, onchange methods, and UI responsiveness
"""

import sys
import os
import ast
import xml.etree.ElementTree as ET
from pathlib import Path

def check_workflow_responsiveness():
    """Comprehensive test of workflow logic and responsiveness"""
    
    print("🔄 TESTING WORKFLOW LOGIC AND RESPONSIVENESS")
    print("=" * 60)
    
    module_path = Path("account_payment_final")
    results = {
        'workflow_methods': 0,
        'onchange_methods': 0,
        'constraint_validations': 0,
        'ui_responsiveness': 0,
        'state_management': 0,
        'errors': []
    }
    
    # Test 1: Workflow Method Analysis
    print("\n1. 🔍 Analyzing Workflow Methods...")
    
    payment_model = module_path / "models" / "account_payment.py"
    if payment_model.exists():
        with open(payment_model, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            tree = ast.parse(content)
            
            workflow_methods = [
                'action_submit_for_approval',
                'action_approve_and_post', 
                'action_reject_payment'
            ]
            
            found_methods = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name in workflow_methods:
                        found_methods.append(node.name)
                        
                        # Check for enhanced validation
                        has_validation = any(
                            isinstance(child, ast.Raise) or 
                            (isinstance(child, ast.If) and 'ValidationError' in ast.dump(child))
                            for child in ast.walk(node)
                        )
                        
                        # Check for state management
                        has_state_mgmt = any(
                            'approval_state' in ast.dump(child)
                            for child in ast.walk(node)
                        )
                        
                        # Check for reload action
                        has_reload = 'reload' in ast.dump(node)
                        
                        print(f"   ✅ {node.name}")
                        print(f"      - Enhanced validation: {'✅' if has_validation else '❌'}")
                        print(f"      - State management: {'✅' if has_state_mgmt else '❌'}")  
                        print(f"      - UI reload action: {'✅' if has_reload else '❌'}")
                        
                        if has_validation and has_state_mgmt and has_reload:
                            results['workflow_methods'] += 1
            
            missing_methods = set(workflow_methods) - set(found_methods)
            if missing_methods:
                results['errors'].append(f"Missing workflow methods: {missing_methods}")
                
        except Exception as e:
            results['errors'].append(f"Error parsing workflow methods: {e}")
    
    # Test 2: Onchange Method Analysis
    print("\n2. 🔄 Analyzing Onchange Methods...")
    
    if payment_model.exists():
        with open(payment_model, 'r', encoding='utf-8') as f:
            content = f.read()
            
        onchange_methods = [
            '_onchange_payment_details',
            '_onchange_approval_state'
        ]
        
        for method in onchange_methods:
            if method in content:
                print(f"   ✅ {method} - Found")
                
                # Check for real-time validation
                if 'warning' in content and method in content:
                    print(f"      - Real-time warnings: ✅")
                    results['onchange_methods'] += 1
                else:
                    print(f"      - Real-time warnings: ❌")
            else:
                print(f"   ❌ {method} - Missing")
                results['errors'].append(f"Missing onchange method: {method}")
    
    # Test 3: Constraint Validation Analysis
    print("\n3. 🛡️ Analyzing Constraint Validations...")
    
    if payment_model.exists():
        with open(payment_model, 'r', encoding='utf-8') as f:
            content = f.read()
            
        constraints = [
            '@api.constrains',
            '_check_payment_requirements',
            'ValidationError'
        ]
        
        constraint_score = 0
        for constraint in constraints:
            if constraint in content:
                print(f"   ✅ {constraint} - Found")
                constraint_score += 1
            else:
                print(f"   ❌ {constraint} - Missing")
                
        if constraint_score >= 2:
            results['constraint_validations'] = 1
    
    # Test 4: UI Responsiveness Analysis
    print("\n4. 🎨 Analyzing UI Responsiveness...")
    
    view_file = module_path / "views" / "account_payment_views.xml"
    if view_file.exists():
        try:
            tree = ET.parse(view_file)
            root = tree.getroot()
            
            # Check for enhanced statusbar
            statusbar_elements = root.findall(".//field[@widget='statusbar']")
            for statusbar in statusbar_elements:
                if statusbar.get('readonly') == '0':
                    print("   ✅ Interactive statusbar - Found")
                    results['ui_responsiveness'] += 1
                    break
            
            # Check for dynamic button visibility
            buttons = root.findall(".//button")
            dynamic_buttons = 0
            for button in buttons:
                invisible_attr = button.get('invisible', '')
                if 'approval_state' in invisible_attr and ('!=' in invisible_attr or 'not in' in invisible_attr):
                    dynamic_buttons += 1
                    
            if dynamic_buttons >= 3:
                print(f"   ✅ Dynamic button visibility - {dynamic_buttons} responsive buttons")
                results['ui_responsiveness'] += 1
            else:
                print(f"   ⚠️ Limited button responsiveness - {dynamic_buttons} responsive buttons")
            
            # Check for real-time field attributes
            fields = root.findall(".//field")
            responsive_fields = 0
            for field in fields:
                readonly_attr = field.get('readonly', '')
                if 'approval_state' in readonly_attr:
                    responsive_fields += 1
                    
            if responsive_fields >= 3:
                print(f"   ✅ Responsive field states - {responsive_fields} fields")
                results['ui_responsiveness'] += 1
            else:
                print(f"   ⚠️ Limited field responsiveness - {responsive_fields} fields")
                
        except Exception as e:
            results['errors'].append(f"Error parsing view XML: {e}")
    
    # Test 5: State Management Analysis
    print("\n5. 🔄 Analyzing State Management...")
    
    if payment_model.exists():
        with open(payment_model, 'r', encoding='utf-8') as f:
            content = f.read()
            
        state_features = [
            '_approval_state_manual',  # Manual state flag
            '@api.depends.*approval_state',  # Computed dependencies
            'fields_view_get',  # Dynamic view rendering
            'write.*approval_state'  # Write method override
        ]
        
        state_score = 0
        for feature in state_features:
            if feature.replace('.*', '') in content or any(part in content for part in feature.split('.*')):
                print(f"   ✅ {feature.replace('.*', ' logic')} - Found")
                state_score += 1
            else:
                print(f"   ❌ {feature.replace('.*', ' logic')} - Missing")
                
        if state_score >= 3:
            results['state_management'] = 1
    
    # Final Results
    print("\n" + "=" * 60)
    print("📊 WORKFLOW RESPONSIVENESS TEST RESULTS")
    print("=" * 60)
    
    total_tests = 5
    passed_tests = sum([
        1 if results['workflow_methods'] >= 3 else 0,
        1 if results['onchange_methods'] >= 2 else 0,
        1 if results['constraint_validations'] >= 1 else 0,
        1 if results['ui_responsiveness'] >= 3 else 0,
        1 if results['state_management'] >= 1 else 0
    ])
    
    print(f"📈 Workflow Methods: {results['workflow_methods']}/3 ({'✅' if results['workflow_methods'] >= 3 else '❌'})")
    print(f"🔄 Onchange Methods: {results['onchange_methods']}/2 ({'✅' if results['onchange_methods'] >= 2 else '❌'})")
    print(f"🛡️ Constraint Validations: {results['constraint_validations']}/1 ({'✅' if results['constraint_validations'] >= 1 else '❌'})")
    print(f"🎨 UI Responsiveness: {results['ui_responsiveness']}/3 ({'✅' if results['ui_responsiveness'] >= 3 else '❌'})")
    print(f"🔄 State Management: {results['state_management']}/1 ({'✅' if results['state_management'] >= 1 else '❌'})")
    
    responsiveness_score = (passed_tests / total_tests) * 100
    
    print(f"\n🎯 Overall Responsiveness Score: {responsiveness_score:.1f}%")
    
    if responsiveness_score >= 90:
        print("🎉 EXCELLENT - Highly responsive workflow with real-time updates!")
        status = "PRODUCTION READY"
    elif responsiveness_score >= 75:
        print("✅ GOOD - Good responsiveness with minor improvements needed")
        status = "NEAR PRODUCTION READY"
    elif responsiveness_score >= 60:
        print("⚠️ FAIR - Basic responsiveness, needs enhancement")
        status = "DEVELOPMENT READY"
    else:
        print("❌ POOR - Limited responsiveness, major improvements needed")
        status = "NEEDS WORK"
        
    print(f"📋 Status: {status}")
    
    if results['errors']:
        print(f"\n⚠️ Issues Found:")
        for error in results['errors']:
            print(f"   - {error}")
    
    return responsiveness_score >= 75

if __name__ == "__main__":
    success = check_workflow_responsiveness()
    sys.exit(0 if success else 1)
