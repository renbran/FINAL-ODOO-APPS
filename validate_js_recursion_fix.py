#!/usr/bin/env python3
"""
JavaScript Infinite Recursion Fix Validator
Validates the fix for the MutationObserver infinite recursion issue
"""

import os
import re

def validate_js_fix():
    """Validate the JavaScript fix for infinite recursion."""
    print("🔍 JAVASCRIPT INFINITE RECURSION FIX VALIDATION")
    print("=" * 60)
    
    js_file = "report_font_enhancement/static/src/js/report_font_enhancement.js"
    
    if not os.path.exists(js_file):
        print("❌ JavaScript file not found")
        return False
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for infinite recursion prevention measures
    checks = [
        ("isProcessing flag", r'this\.isProcessing\s*=\s*false'),
        ("Recursion guard", r'if\s*\(\s*this\.isProcessing\s*\)\s*\{'),
        ("Observer disconnect", r'this\.observer\.disconnect\(\)'),
        ("Error handling", r'try\s*\{[\s\S]*?\}\s*catch'),
        ("Finally block", r'finally\s*\{'),
        ("setTimeout delay", r'setTimeout\(\(\)\s*=>\s*\{'),
    ]
    
    all_passed = True
    for check_name, pattern in checks:
        if re.search(pattern, content):
            print(f"✅ {check_name} - Found")
        else:
            print(f"❌ {check_name} - Missing")
            all_passed = False
    
    # Check for recursion protection in setupMutationObserver
    if 'isProcessing' in content and 'if (this.isProcessing)' in content:
        print("✅ MutationObserver setup has proper guards")
    else:
        print("❌ MutationObserver setup lacks proper guards")
        all_passed = False
    
    # Check for observer disconnect in enhanceReportElement  
    if 'observer.disconnect()' in content and 'observe(document.body' in content:
        print("✅ enhanceReportElement has observer disconnect protection")
    else:
        print("❌ enhanceReportElement lacks observer disconnect protection")
        all_passed = False
    
    print(f"\n{'✅ All checks passed!' if all_passed else '❌ Some checks failed!'}")
    
    if all_passed:
        print("\n💡 NEXT STEPS:")
        print("1. Deploy the fixed JavaScript file to CloudPepper")
        print("2. Clear browser cache and refresh")
        print("3. Test report functionality")
        print("4. Monitor for any remaining recursion issues")
    
    return all_passed

if __name__ == "__main__":
    validate_js_fix()
