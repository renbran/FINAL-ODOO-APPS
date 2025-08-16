#!/usr/bin/env python3
"""
JavaScript Syntax Error Fix Script
Fixes all stray semicolons and syntax errors in account_payment_final JavaScript files
"""

import os
import re
from pathlib import Path

def fix_javascript_syntax_errors():
    """Fix JavaScript syntax errors in all emergency fix files"""
    
    print("🔧 Fixing JavaScript syntax errors in account_payment_final...")
    
    js_files = [
        "account_payment_final/static/src/js/immediate_emergency_fix.js",
        "account_payment_final/static/src/js/cloudpepper_nuclear_fix.js", 
        "account_payment_final/static/src/js/cloudpepper_enhanced_handler.js",
        "account_payment_final/static/src/js/cloudpepper_critical_interceptor.js",
        "account_payment_final/static/src/js/cloudpepper_js_error_handler.js",
        "account_payment_final/static/src/js/emergency_error_fix.js"
    ]
    
    fixed_files = 0
    
    for file_path in js_files:
        if os.path.exists(file_path):
            print(f"🔍 Processing: {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Fix common syntax errors
                fixes_applied = []
                
                # 1. Fix stray semicolons in conditional statements
                # Pattern: condition ||\n; -> condition ||\n
                pattern1 = re.compile(r'(\|\|)\s*\n\s*;\s*\n', re.MULTILINE)
                if pattern1.search(content):
                    content = pattern1.sub(r'\1\n', content)
                    fixes_applied.append("Fixed stray semicolons in conditions")
                
                # 2. Fix stray semicolons in function calls
                # Pattern: addEventListener(\n;  -> addEventListener(\n
                pattern2 = re.compile(r'(\w+\()\s*\n\s*;\s*\n', re.MULTILINE)
                if pattern2.search(content):
                    content = pattern2.sub(r'\1\n', content)
                    fixes_applied.append("Fixed stray semicolons in function calls")
                
                # 3. Fix array elements ending with semicolon instead of comma
                # Pattern: /regex/; -> /regex/
                pattern3 = re.compile(r'(/[^/]+/);(\s*\n\s*\])', re.MULTILINE)
                if pattern3.search(content):
                    content = pattern3.sub(r'\1\2', content)
                    fixes_applied.append("Fixed regex array elements")
                
                # 4. Fix standalone semicolons on lines
                pattern4 = re.compile(r'^\s*;\s*$', re.MULTILINE)
                if pattern4.search(content):
                    content = pattern4.sub('', content)
                    fixes_applied.append("Removed standalone semicolons")
                
                # 5. Fix function parameters with stray semicolons
                pattern5 = re.compile(r'(\w+,)\s*\n\s*;\s*\n', re.MULTILINE)
                if pattern5.search(content):
                    content = pattern5.sub(r'\1\n', content)
                    fixes_applied.append("Fixed function parameter semicolons")
                
                # 6. Fix console.debug with stray semicolons
                pattern6 = re.compile(r'(console\.debug\()\s*\n\s*;\s*\n\s*("[^"]+",)', re.MULTILINE)
                if pattern6.search(content):
                    content = pattern6.sub(r'\1\n            \2', content)
                    fixes_applied.append("Fixed console.debug formatting")
                
                # Write the fixed content back
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"✅ Fixed {file_path}:")
                    for fix in fixes_applied:
                        print(f"   - {fix}")
                    fixed_files += 1
                else:
                    print(f"ℹ️  No fixes needed for {file_path}")
                
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n🎯 Summary: Fixed {fixed_files} JavaScript files")
    return fixed_files > 0

if __name__ == "__main__":
    fix_javascript_syntax_errors()
