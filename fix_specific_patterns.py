#!/usr/bin/env python3
"""
Fix specific patterns in the dashboard.js file that weren't caught by the first script.
"""

import re
import sys

def fix_specific_patterns(file_path):
    """Fix specific syntax patterns that weren't caught by the first script."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern 1: Catch block after return statement inside if block
    pattern = re.compile(r'(\s*if\s*\([^)]+\)\s*\{\s*[^{}]*?return[^;]*;\s*\})\s*catch \(error\) \{\s*console\.error\([^)]+\);\s*\}', re.DOTALL)
    content = pattern.sub(r'\1', content)
    
    # Pattern 2: Check for any remaining string literals with catch statements
    pattern = re.compile(r'(`[^`]*?)catch \(error\)(.*?`)', re.DOTALL)
    content = pattern.sub(r'\1\2', content)
    
    # Pattern 3: Check for any if-block followed by catch
    pattern = re.compile(r'(if\s*\([^)]+\)\s*\{[^}]*\})\s*catch \(error\)', re.DOTALL)
    content = pattern.sub(r'\1', content)

    # Write back the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Fixed specific patterns in {file_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fix_specific_patterns(sys.argv[1])
    else:
        fix_specific_patterns("d:/odoo17_final/oe_sale_dashboard_17/static/src/js/dashboard.js")
