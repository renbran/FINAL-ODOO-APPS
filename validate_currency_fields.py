#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to validate all Monetary fields have proper currency_field parameters
"""

import os
import re
import sys

def check_monetary_fields(file_path):
    """Check if all Monetary fields in a Python file have currency_field parameter"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find all Monetary field definitions
        monetary_pattern = r'(\w+)\s*=\s*fields\.Monetary\s*\(((?:[^)]*\([^)]*\))*[^)]*)\)'
        matches = re.finditer(monetary_pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            field_name = match.group(1)
            field_def = match.group(2)
            
            # Check if currency_field is defined
            if 'currency_field' not in field_def:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    'file': file_path,
                    'field': field_name,
                    'line': line_num,
                    'issue': 'Missing currency_field parameter'
                })
                
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        
    return issues

def scan_directory(base_path):
    """Scan directory for Python files with Monetary fields"""
    all_issues = []
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                issues = check_monetary_fields(file_path)
                all_issues.extend(issues)
                
    return all_issues

def main():
    # Check account_payment_final module
    module_path = os.path.join(os.getcwd(), 'account_payment_final')
    
    if not os.path.exists(module_path):
        print("❌ account_payment_final module not found!")
        sys.exit(1)
        
    print("🔍 Scanning account_payment_final module for Monetary field issues...")
    issues = scan_directory(module_path)
    
    if issues:
        print(f"❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue['file']}:{issue['line']} - Field '{issue['field']}': {issue['issue']}")
        sys.exit(1)
    else:
        print("✅ All Monetary fields have proper currency_field parameters!")
        print("✅ Currency field validation passed!")

if __name__ == '__main__':
    main()
