#!/usr/bin/env python3
"""
Fix syntax errors in dashboard.js file caused by improper catch blocks.
"""
import re
import sys

def fix_dashboard_js(file_path):
    """
    Fix the dashboard.js file by:
    1. Remove extra catch blocks after if statements
    2. Fix string literals with catch snippets inserted
    3. Clean up any other catch-related syntax issues
    """
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace patterns

    # 1. Fix the double catch block issue in onMounted
    content = re.sub(
        r'catch \(error\) \{\s*this\._handleDashboardError\(error, \'mount\'\);\s*\}\s*catch \(error\) \{\s*console\.error\(\'Caught error:\', error\);\s*\}',
        r'catch (error) { this._handleDashboardError(error, \'mount\'); console.error(\'Caught error:\', error); }',
        content
    )
    
    # 2. Remove catch blocks after if/else statements (typically after return statements)
    content = re.sub(
        r'(if\s*\([^)]+\)\s*\{[^}]*return[^;]*;\s*\})\s*catch \(error\) \{\s*console\.error\(\'Caught error:\', error\);\s*\}',
        r'\1',
        content
    )
    
    # 3. Fix string literals with catch snippets inserted
    content = re.sub(
        r'(`[^`]*?) catch \(error\) \{\s*console\.error\(\'Caught error:\', error\);\s*\}([^`]*?`)',
        r'\1\2',
        content
    )
    
    # 4. Remove standalone catch blocks that don't match try blocks
    content = re.sub(
        r'\}\s*catch \(error\) \{\s*console\.error\(\'Caught error:\', error\);\s*\}(\s*(?:const|let|var|\/\/|\/\*|else|if|for|while))',
        r'}\1',
        content
    )

    # Write back the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Fixed {file_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fix_dashboard_js(sys.argv[1])
    else:
        fix_dashboard_js("d:/odoo17_final/oe_sale_dashboard_17/static/src/js/dashboard.js")
