#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to validate Odoo model syntax and field definitions
"""

import os
import ast
import sys
import importlib.util

def validate_python_syntax(file_path):
    """Validate Python syntax of a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to check syntax
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def check_model_fields(file_path):
    """Check for common field definition issues"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for Monetary fields without currency_field
        if 'fields.Monetary(' in content:
            lines = content.split('\n')
            in_monetary_field = False
            field_lines = []
            
            for i, line in enumerate(lines):
                if 'fields.Monetary(' in line:
                    in_monetary_field = True
                    field_lines = [line]
                elif in_monetary_field:
                    field_lines.append(line)
                    if ')' in line and line.strip().endswith(')'):
                        # End of field definition
                        field_def = '\n'.join(field_lines)
                        if 'currency_field' not in field_def:
                            issues.append({
                                'file': file_path,
                                'line': i + 1,
                                'issue': 'Monetary field missing currency_field parameter',
                                'context': field_def.strip()
                            })
                        in_monetary_field = False
                        field_lines = []
                        
    except Exception as e:
        issues.append({
            'file': file_path,
            'line': 0,
            'issue': f'Error reading file: {e}',
            'context': ''
        })
        
    return issues

def validate_module(module_path):
    """Validate all Python files in an Odoo module"""
    syntax_errors = []
    field_issues = []
    
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Check syntax
                is_valid, error = validate_python_syntax(file_path)
                if not is_valid:
                    syntax_errors.append({
                        'file': file_path,
                        'error': error
                    })
                
                # Check field definitions
                issues = check_model_fields(file_path)
                field_issues.extend(issues)
                
    return syntax_errors, field_issues

def main():
    module_path = os.path.join(os.getcwd(), 'account_payment_final')
    
    if not os.path.exists(module_path):
        print("❌ account_payment_final module not found!")
        sys.exit(1)
        
    print("🔍 Validating account_payment_final module...")
    print("=" * 50)
    
    syntax_errors, field_issues = validate_module(module_path)
    
    # Report syntax errors
    if syntax_errors:
        print(f"❌ Found {len(syntax_errors)} syntax errors:")
        for error in syntax_errors:
            print(f"  - {error['file']}: {error['error']}")
        print()
    else:
        print("✅ No syntax errors found!")
        print()
    
    # Report field issues
    if field_issues:
        print(f"❌ Found {len(field_issues)} field issues:")
        for issue in field_issues:
            print(f"  - {issue['file']}:{issue['line']}")
            print(f"    Issue: {issue['issue']}")
            if issue['context']:
                print(f"    Context: {issue['context']}")
            print()
    else:
        print("✅ No field definition issues found!")
        print()
    
    # Overall status
    if syntax_errors or field_issues:
        print("❌ Module validation failed!")
        sys.exit(1)
    else:
        print("🎉 Module validation passed!")
        print("✅ The currency field issue should be resolved!")

if __name__ == '__main__':
    main()
