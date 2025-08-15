#!/usr/bin/env python3
"""
Syntax Validation Script for OSUS Enhanced Workflow

This script validates Python syntax for all Python files in the module.
"""

import os
import ast
import sys

def validate_python_syntax(filepath):
    """Validate Python syntax for a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse the content
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except UnicodeDecodeError as e:
        return False, f"Unicode encoding error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

def check_module_syntax():
    """Check syntax for all Python files in the module."""
    print("🔍 Python Syntax Validation")
    print("=" * 50)
    
    module_path = "order_status_override"
    python_files = []
    
    # Find all Python files
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    all_valid = True
    
    for filepath in python_files:
        is_valid, error_msg = validate_python_syntax(filepath)
        
        if is_valid:
            print(f"✅ {filepath}")
        else:
            print(f"❌ {filepath}: {error_msg}")
            all_valid = False
    
    return all_valid

def check_manifest_specifically():
    """Specifically check the manifest file."""
    print("\n📋 Manifest File Validation")
    print("=" * 40)
    
    manifest_path = "order_status_override/__manifest__.py"
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for problematic Unicode characters
        problematic_chars = ['🎯', '→', '✨', '🔧']
        for char in problematic_chars:
            if char in content:
                print(f"⚠️  Found Unicode character: {char}")
                return False
        
        # Try to parse as Python dict
        ast.parse(content)
        print("✅ Manifest syntax is valid")
        
        # Try to evaluate as dict (what Odoo does)
        manifest_dict = ast.literal_eval(content)
        print("✅ Manifest can be evaluated as dictionary")
        
        return True
        
    except Exception as e:
        print(f"❌ Manifest validation failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Syntax Validation...")
    
    syntax_valid = check_module_syntax()
    manifest_valid = check_manifest_specifically()
    
    if syntax_valid and manifest_valid:
        print("\n✅ ALL SYNTAX VALIDATIONS PASSED!")
        print("The module is ready for installation.")
    else:
        print("\n❌ SYNTAX ERRORS DETECTED!")
        print("Please fix the syntax errors before installation.")
    
    sys.exit(0 if (syntax_valid and manifest_valid) else 1)
