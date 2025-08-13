#!/usr/bin/env python3
"""
Payment Approval Workflow - Module Validation Script
This script validates the module structure and dependencies for Odoo 17 compatibility
"""

import os
import sys
import re
import csv
from pathlib import Path

def validate_module():
    """Validate the payment_approval_workflow module"""
    
    print("=== PAYMENT APPROVAL WORKFLOW - MODULE VALIDATION ===")
    print()
    
    base_path = Path(__file__).parent / "payment_approval_workflow"
    if not base_path.exists():
        base_path = Path("payment_approval_workflow")
    
    if not base_path.exists():
        print("❌ Module directory not found!")
        return False
    
    print("✅ Module directory found")
    
    # 1. Check manifest file
    manifest_path = base_path / "__manifest__.py"
    if not manifest_path.exists():
        print("❌ __manifest__.py not found!")
        return False
    
    print("✅ Manifest file exists")
    
    # 2. Check data loading order
    with open(manifest_path, 'r') as f:
        manifest_content = f.read()
    
    # Extract data list
    data_match = re.search(r"'data':\s*\[(.*?)\]", manifest_content, re.DOTALL)
    if not data_match:
        print("❌ No data section found in manifest!")
        return False
    
    data_files = re.findall(r"'([^']+)'", data_match.group(1))
    print(f"📦 Found {len(data_files)} data files in manifest")
    
    # Check if security groups come before access CSV
    security_groups_idx = None
    access_csv_idx = None
    
    for i, file_path in enumerate(data_files):
        if 'security_groups.xml' in file_path:
            security_groups_idx = i
        if 'ir.model.access.csv' in file_path:
            access_csv_idx = i
    
    if security_groups_idx is None:
        print("❌ security_groups.xml not found in data files!")
        return False
    
    if access_csv_idx is None:
        print("❌ ir.model.access.csv not found in data files!")
        return False
    
    if security_groups_idx >= access_csv_idx:
        print("❌ security_groups.xml must be loaded before ir.model.access.csv!")
        print(f"   Current order: security_groups at {security_groups_idx}, access_csv at {access_csv_idx}")
        return False
    
    print("✅ Data loading order is correct")
    
    # 3. Check security groups file
    security_groups_path = base_path / "data" / "security_groups.xml"
    if not security_groups_path.exists():
        print("❌ data/security_groups.xml not found!")
        return False
    
    with open(security_groups_path, 'r') as f:
        security_content = f.read()
    
    # Check for required groups
    required_groups = [
        'group_payment_reviewer',
        'group_payment_approver', 
        'group_payment_authorizer'
    ]
    
    found_groups = []
    for group in required_groups:
        if f'id="{group}"' in security_content:
            found_groups.append(group)
    
    if len(found_groups) != len(required_groups):
        print(f"❌ Missing security groups: {set(required_groups) - set(found_groups)}")
        return False
    
    print("✅ All required security groups found")
    
    # 4. Check access CSV file
    access_csv_path = base_path / "security" / "ir.model.access.csv"
    if not access_csv_path.exists():
        print("❌ security/ir.model.access.csv not found!")
        return False
    
    # Read and validate CSV
    try:
        with open(access_csv_path, 'r') as f:
            csv_reader = csv.DictReader(f)
            csv_rows = list(csv_reader)
        
        print(f"📊 Found {len(csv_rows)} access rules in CSV")
        
        # Check group references
        for row in csv_rows:
            group_id = row.get('group_id:id', '')
            if 'payment_approval_workflow.group_' in group_id:
                group_name = group_id.split('.')[-1]
                if group_name not in required_groups:
                    print(f"❌ Invalid group reference: {group_id}")
                    return False
        
        print("✅ All group references in CSV are valid")
        
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return False
    
    # 5. Check wizard models
    wizard_path = base_path / "wizards"
    if not wizard_path.exists():
        print("❌ wizards directory not found!")
        return False
    
    wizard_files = ['payment_signature_wizard.py', 'payment_rejection_wizard.py']
    for wizard_file in wizard_files:
        wizard_file_path = wizard_path / wizard_file
        if not wizard_file_path.exists():
            print(f"❌ {wizard_file} not found!")
            return False
        
        with open(wizard_file_path, 'r') as f:
            wizard_content = f.read()
        
        if '_name =' not in wizard_content:
            print(f"❌ {wizard_file} missing _name declaration!")
            return False
    
    print("✅ All wizard models are properly declared")
    
    # 6. Check imports
    controller_path = base_path / "controllers" / "portal.py"
    if controller_path.exists():
        with open(controller_path, 'r') as f:
            controller_content = f.read()
        
        if 'from werkzeug.security import safe_str_cmp' in controller_content:
            print("❌ Deprecated werkzeug import found!")
            return False
        
        if 'from odoo.tools import consteq' not in controller_content:
            print("❌ Missing odoo.tools.consteq import!")
            return False
        
        print("✅ Controller imports are Odoo 17 compatible")
    
    print()
    print("🎉 MODULE VALIDATION PASSED!")
    print("The payment_approval_workflow module is ready for installation.")
    return True

if __name__ == "__main__":
    success = validate_module()
    sys.exit(0 if success else 1)
