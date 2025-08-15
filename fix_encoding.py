#!/usr/bin/env python3
"""
ODOO MODULE ENCODING FIXER
Fixes Unicode encoding issues in Python files
"""

import os
from pathlib import Path
import chardet

def fix_file_encoding(file_path):
    """Fix encoding issues in a file"""
    try:
        # Detect encoding
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        detected = chardet.detect(raw_data)
        encoding = detected['encoding']
        
        if encoding and encoding.lower() not in ['utf-8', 'ascii']:
            print(f"üîß Fixing encoding in {file_path} (detected: {encoding})")
            
            # Read with detected encoding
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Write back as UTF-8
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        return False
        
    except Exception as e:
        print(f"‚ùå Could not fix {file_path}: {e}")
        return False

def main():
    workspace = Path(r"d:\GitHub\osus_main\cleanup osus\odoo17_final")
    
    print("üîß Fixing encoding issues in Python files...")
    
    fixed_count = 0
    for py_file in workspace.rglob("*.py"):
        if fix_file_encoding(py_file):
            fixed_count += 1
    
    print(f"‚úÖ Fixed encoding in {fixed_count} files")

if __name__ == "__main__":
    main()
