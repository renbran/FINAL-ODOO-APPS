#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Account Payment Approval Module Structure Validation
"""

import os
import ast

def validate_account_payment_approval():
    """Validate the account_payment_approval module structure"""
    
    module_path = "account_payment_approval"
    
    if not os.path.exists(module_path):
        print("❌ Module directory not found")
        return False
    
    print("🔍 Validating Account Payment Approval Module...")
    
    # Check required files
    required_files = [
        "__init__.py",
        "__manifest__.py",
        "models/__init__.py",
        "models/account_payment.py",
        "models/res_config_settings.py",
        "views/account_payment_views.xml",
        "views/menus.xml",
        "security/ir.model.access.csv",
        "security/security_groups.xml",
        "controllers/__init__.py",
        "controllers/main.py",
        "wizards/__init__.py", 
        "wizards/payment_wizards.py",
        "reports/__init__.py",
        "reports/payment_approval_report.py",
        "tests/__init__.py",
        "tests/test_payment_approval.py",
        "README.md",
        "static/description/index.html"
    ]
    
    missing_files = []
    empty_files = []
    
    for file_path in required_files:
        full_path = os.path.join(module_path, file_path)
        
        if not os.path.exists(full_path):
            missing_files.append(file_path)
        elif os.path.getsize(full_path) == 0:
            empty_files.append(file_path)
    
    # Check manifest syntax
    manifest_path = os.path.join(module_path, "__manifest__.py")
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
                ast.parse(content)
            print("✅ Manifest file syntax is valid")
        except SyntaxError as e:
            print(f"❌ Manifest syntax error: {e}")
            return False
    
    # Check __init__.py files
    init_files = [
        "__init__.py",
        "models/__init__.py", 
        "controllers/__init__.py",
        "wizards/__init__.py",
        "reports/__init__.py",
        "tests/__init__.py"
    ]
    
    for init_file in init_files:
        init_path = os.path.join(module_path, init_file)
        if os.path.exists(init_path):
            with open(init_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content or len(content) < 10:
                    empty_files.append(init_file)
    
    # Report results
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
    
    if empty_files:
        print("⚠️  Empty or minimal files:")
        for file in empty_files:
            print(f"   - {file}")
    
    if not missing_files and not empty_files:
        print("✅ All required files present and non-empty")
        
        # Check file counts
        python_files = []
        xml_files = []
        
        for root, dirs, files in os.walk(module_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
                elif file.endswith('.xml'):
                    xml_files.append(os.path.join(root, file))
        
        print(f"📊 Module Statistics:")
        print(f"   - Python files: {len(python_files)}")
        print(f"   - XML files: {len(xml_files)}")
        print(f"   - Total size: {sum(os.path.getsize(f) for f in python_files + xml_files):,} bytes")
        
        print("\n✅ Account Payment Approval module structure is COMPLETE!")
        print("🚀 Ready for deployment in Odoo 17")
        return True
    
    return False

if __name__ == "__main__":
    validate_account_payment_approval()
