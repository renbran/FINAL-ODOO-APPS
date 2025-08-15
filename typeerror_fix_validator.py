#!/usr/bin/env python3
"""
TypeError Fix Validation Script
Specifically checks for the Monetary field @ function operator issue
"""

import os
import re

def check_monetary_decorator_issue():
    """Check for the specific @ operator issue with Monetary fields"""
    
    print("🔍 CHECKING FOR MONETARY FIELD @ DECORATOR ISSUES...")
    
    sale_order_file = "order_status_override/models/sale_order.py"
    
    if not os.path.exists(sale_order_file):
        print(f"❌ File not found: {sale_order_file}")
        return False
    
    with open(sale_order_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for the specific issue pattern
    # Look for fields.Monetary( followed immediately by @api
    pattern = r'fields\.Monetary\([^)]*\)\s*@api'
    
    matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
    
    issue_found = False
    for match in matches:
        issue_found = True
        start_line = content[:match.start()].count('\n') + 1
        print(f"❌ ISSUE FOUND at line {start_line}: Monetary field immediately followed by @api decorator")
    
    if not issue_found:
        print("✅ NO MONETARY @ DECORATOR ISSUES FOUND")
    
    # Also check for proper line breaks after field definitions
    field_patterns = [
        r'fields\.Monetary\([^)]*\)[\s]*@',
        r'fields\.One2many\([^)]*\)[\s]*@',
        r'fields\.Many2one\([^)]*\)[\s]*@'
    ]
    
    for pattern in field_patterns:
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        for match in matches:
            start_line = content[:match.start()].count('\n') + 1
            print(f"❌ POTENTIAL ISSUE at line {start_line}: Field definition immediately followed by @")
            issue_found = True
    
    return not issue_found

def main():
    print("="*70)
    print("TYPEERROR FIX VALIDATION - MONETARY @ FUNCTION OPERATOR")
    print("="*70)
    
    success = check_monetary_decorator_issue()
    
    print("\n" + "="*70)
    print("FIX VALIDATION SUMMARY")
    print("="*70)
    
    if success:
        print("✅ TYPEERROR FIX SUCCESSFUL!")
        print("🚀 Monetary field @ decorator issue resolved!")
        print("📋 Module should now load without the TypeError!")
    else:
        print("❌ TYPEERROR STILL PRESENT!")
        print("🔧 Manual intervention required!")
    
    print("="*70)
    return success

if __name__ == "__main__":
    main()
