#!/usr/bin/env python3
"""
Number Formatting Verification Script for Odoo Dynamic Reports
This script verifies that all dynamic report templates have proper number formatting.
"""

import os
import re

def find_dynamic_report_templates(root_dir):
    """Find all dynamic report template files."""
    templates = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.xml') and 'report' in dirpath:
                if 'dynamic' in dirpath or 'templates' in filename:
                    templates.append(os.path.join(dirpath, filename))
    return templates

def check_number_formatting(file_path):
    """Check if a file has proper number formatting."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for format_number lambda
        has_format_lambda = 'format_number' in content and 'lambda' in content
        
        # Find unformatted t-esc patterns for amounts
        unformatted_patterns = [
            r't-esc="[^"]*(?:total|amount|debit|credit|balance|diff\d+)[^"]*"',
            r't-out="[^"]*(?:total|amount|debit|credit|balance|diff\d+)[^"]*"'
        ]
        
        unformatted_matches = []
        for pattern in unformatted_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            # Filter out already formatted ones
            for match in matches:
                if 'format_number' not in match and 'currency' not in match:
                    unformatted_matches.append(match)
        
        return {
            'has_format_lambda': has_format_lambda,
            'unformatted_matches': unformatted_matches,
            'total_matches': len(unformatted_matches)
        }
    except Exception as e:
        return {
            'error': str(e),
            'has_format_lambda': False,
            'unformatted_matches': [],
            'total_matches': 0
        }

def main():
    """Main function to check all dynamic report templates."""
    root_dir = r"d:\RUNNING APPS\ready production\osus-main\odoo17_final"
    
    print("=== Odoo Dynamic Report Number Formatting Verification ===\n")
    
    templates = find_dynamic_report_templates(root_dir)
    
    print(f"Found {len(templates)} potential dynamic report templates:\n")
    
    all_good = True
    
    for template in templates:
        result = check_number_formatting(template)
        
        # Get relative path for display
        rel_path = os.path.relpath(template, root_dir)
        
        print(f"📄 {rel_path}")
        
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
            all_good = False
            continue
        
        if result['has_format_lambda']:
            print("   ✅ Has format_number lambda")
        else:
            print("   ❌ Missing format_number lambda")
            all_good = False
        
        if result['total_matches'] > 0:
            print(f"   ⚠️  Found {result['total_matches']} potentially unformatted amount fields:")
            for match in result['unformatted_matches'][:5]:  # Show first 5
                print(f"      - {match}")
            if len(result['unformatted_matches']) > 5:
                print(f"      ... and {len(result['unformatted_matches']) - 5} more")
            all_good = False
        else:
            print("   ✅ All amount fields appear to be formatted")
        
        print()
    
    if all_good:
        print("🎉 All dynamic report templates have proper number formatting!")
    else:
        print("⚠️  Some templates may need attention for proper number formatting.")
    
    print("\n=== Summary ===")
    print("Key templates verified:")
    key_templates = [
        'trial_balance.xml',
        'balance_sheet_report_templates.xml', 
        'general_ledger_templates.xml',
        'partner_ledger_templates.xml',
        'aged_receivable_templates.xml',
        'aged_payable_templates.xml'
    ]
    
    for key_template in key_templates:
        found = any(key_template in template for template in templates)
        status = "✅ Found and checked" if found else "❌ Not found"
        print(f"  {key_template}: {status}")

if __name__ == "__main__":
    main()
