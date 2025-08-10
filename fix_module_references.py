#!/usr/bin/env python3
"""
Fix all payment_voucher_enhanced references to account_payment_final
"""

import os
import re

def fix_module_references():
    # Define the module directory
    module_path = r"d:\RUNNING APPS\ready production\latest\odoo17_final\account_payment_final"
    
    # Pattern to find files
    patterns_to_fix = [
        (r'payment_voucher_enhanced\.', 'account_payment_final.'),
    ]
    
    # Walk through all files
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith(('.py', '.xml', '.js')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Apply fixes
                    original_content = content
                    for pattern, replacement in patterns_to_fix:
                        content = re.sub(pattern, replacement, content)
                    
                    # Write back if changed
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"Fixed: {file_path}")
                
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    fix_module_references()
    print("Module reference fix completed!")
