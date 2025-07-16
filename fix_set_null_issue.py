#!/usr/bin/env python3
"""
Emergency fix script for SET_NULL foreign key constraint issue in Odoo.
This script searches for and fixes incorrect ondelete='set null' references.
"""

import os
import re
import sys

def fix_set_null_references(directory):
    """
    Search for and fix SET_NULL ondelete references in Python files
    """
    print("=" * 60)
    print("EMERGENCY FIX: SET_NULL Foreign Key Constraint Issue")
    print("=" * 60)
    
    fixes_made = 0
    files_checked = 0
    
    # Pattern to match problematic SET_NULL with underscore
    pattern = r"ondelete\s*=\s*['\"]SET_NULL['\"]"
    replacement = r"ondelete='set null'"
    
    print(f"\nScanning directory: {directory}")
    print(f"Looking for pattern: {pattern}")
    print(f"Will replace with: {replacement}")
    print("-" * 60)
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                files_checked += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if file contains the problematic pattern
                    if re.search(pattern, content, re.IGNORECASE):
                        print(f"❌ FOUND ISSUE: {file_path}")
                        
                        # Fix the issue
                        fixed_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                        
                        # Write back the fixed content
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(fixed_content)
                        
                        print(f"✅ FIXED: {file_path}")
                        fixes_made += 1
                    
                except Exception as e:
                    print(f"⚠️  Error processing {file_path}: {e}")
    
    print("-" * 60)
    print(f"SUMMARY:")
    print(f"Files checked: {files_checked}")
    print(f"Fixes made: {fixes_made}")
    
    if fixes_made > 0:
        print(f"\n✅ Fixed {fixes_made} files with SET_NULL issues.")
        print("You can now try installing the module again.")
    else:
        print(f"\n🔍 No SET_NULL issues found in Python files.")
        print("The issue might be in XML files or database level.")
    
    print("=" * 60)

if __name__ == "__main__":
    # Get current directory or use provided argument
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    fix_set_null_references(target_dir)
