#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo.define Error Fix Validator
Tests if the JavaScript odoo.define compatibility fixes work correctly
"""

import os
import re
from pathlib import Path

def validate_js_modern_syntax():
    """Validate that JavaScript files use modern syntax or have proper compatibility shims"""
    print("🔍 Validating JavaScript Modern Syntax...")
    
    # Check commission_ax compatibility patch
    patch_file = Path("commission_ax/static/src/js/cloudpepper_compatibility_patch.js")
    if not patch_file.exists():
        print("❌ CloudPepper compatibility patch not found!")
        return False
    
    with open(patch_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for compatibility shim
    has_compatibility_shim = 'window.odoo.define' in content and 'function(name, dependencies, callback)' in content
    has_modern_syntax = '/** @odoo-module **/' in content and 'import' in content
    
    if has_compatibility_shim and has_modern_syntax:
        print("✅ Commission AX compatibility patch has proper odoo.define shim")
    else:
        print("❌ Commission AX compatibility patch missing proper shim")
        return False
    
    # Check if there are any direct odoo.define calls (not in comments)
    js_files = list(Path(".").rglob("*.js"))
    problematic_files = []
    
    for js_file in js_files:
        try:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove comments and strings to avoid false positives
            content_no_comments = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
            content_no_comments = re.sub(r'/\*.*?\*/', '', content_no_comments, flags=re.DOTALL)
            content_no_strings = re.sub(r'"[^"]*"', '', content_no_comments)
            content_no_strings = re.sub(r"'[^']*'", '', content_no_strings)
            
            # Check for actual odoo.define calls
            if re.search(r'\bodoo\.define\s*\(', content_no_strings):
                # Exclude compatibility files
                if ('compatibility' not in str(js_file).lower() and 
                    'shim' not in str(js_file).lower()):
                    problematic_files.append(str(js_file))
        
        except Exception as e:
            print(f"⚠️ Error reading {js_file}: {e}")
    
    if problematic_files:
        print("❌ Found files with legacy odoo.define calls:")
        for file_path in problematic_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ No problematic legacy odoo.define calls found")
    
    return True

def create_test_html():
    """Create a simple HTML test file to verify odoo.define compatibility"""
    test_html = """<!DOCTYPE html>
<html>
<head>
    <title>Odoo.define Compatibility Test</title>
    <script>
        // Simulate the odoo.define error scenario
        window.odoo = {};
        
        // Load commission_ax compatibility patch
        const script = document.createElement('script');
        script.src = 'commission_ax/static/src/js/cloudpepper_compatibility_patch.js';
        script.onload = function() {
            console.log('✅ Compatibility patch loaded');
            
            // Test if odoo.define is now available
            if (typeof window.odoo.define === 'function') {
                console.log('✅ odoo.define compatibility shim working');
                
                // Test a legacy call
                try {
                    window.odoo.define('test_module', function() {
                        console.log('✅ Legacy odoo.define call successful');
                    });
                } catch (error) {
                    console.error('❌ Legacy odoo.define call failed:', error);
                }
            } else {
                console.error('❌ odoo.define compatibility shim not working');
            }
        };
        script.onerror = function() {
            console.error('❌ Failed to load compatibility patch');
        };
        document.head.appendChild(script);
    </script>
</head>
<body>
    <h1>Odoo.define Compatibility Test</h1>
    <p>Check browser console for results</p>
</body>
</html>"""
    
    with open("odoo_define_test.html", 'w', encoding='utf-8') as f:
        f.write(test_html)
    
    print("📄 Created odoo_define_test.html - open in browser to test")

def main():
    """Main validation function"""
    print("🧪 Odoo.define Error Fix Validation")
    print("=" * 40)
    
    if not Path("commission_ax").exists():
        print("❌ commission_ax module not found!")
        return False
    
    # Run validations
    js_valid = validate_js_modern_syntax()
    
    # Create test file
    create_test_html()
    
    print("\n" + "=" * 40)
    if js_valid:
        print("🎉 VALIDATION PASSED!")
        print("✅ JavaScript compatibility fixes are correct")
        print("✅ No legacy odoo.define calls found")
        print("✅ CloudPepper compatibility patch has proper shim")
        print("\n📋 Next steps:")
        print("1. Clear browser cache")
        print("2. Restart Odoo server")
        print("3. Test in browser - should not see 'odoo.define is not a function'")
        print("4. Optional: Open odoo_define_test.html to verify locally")
    else:
        print("❌ VALIDATION FAILED!")
        print("🔧 Fix the issues above before testing")
    
    return js_valid

if __name__ == "__main__":
    main()
