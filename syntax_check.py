#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import ast
import os

def check_python_syntax(file_path):
    """Check if a Python file has valid syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def scan_module(module_path):
    """Scan a module for Python syntax errors"""
    errors = []
    
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                is_valid, error = check_python_syntax(file_path)
                if not is_valid:
                    errors.append(f"{file_path}: {error}")
    
    return errors

if __name__ == "__main__":
    # Check white_label_branding module
    white_label_path = "white_label_branding"
    print(f"Checking {white_label_path} module...")
    
    errors = scan_module(white_label_path)
    
    if errors:
        print("❌ Syntax errors found:")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print("✅ No syntax errors found!")
        
    # Check payment_account_enhanced as well
    payment_path = "payment_account_enhanced"
    print(f"Checking {payment_path} module...")
    
    errors = scan_module(payment_path)
    
    if errors:
        print("❌ Syntax errors found:")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print("✅ No syntax errors found!")
