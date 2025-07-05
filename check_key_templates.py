#!/usr/bin/env python3
"""
Quick check for the key dynamic reports formatting
"""

import os
import re

def check_template(file_path):
    """Check if a template has proper formatting."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_format_lambda = 'format_number' in content and 'lambda' in content
        
        # Find unformatted patterns
        unformatted_patterns = [
            r't-esc="[^"]*(?:total|amount|debit|credit|balance|diff\d+)[^"]*"',
            r't-out="[^"]*(?:total|amount|debit|credit|balance|diff\d+)[^"]*"'
        ]
        
        unformatted_count = 0
        for pattern in unformatted_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if 'format_number' not in match and 'currency' not in match:
                    unformatted_count += 1
        
        return has_format_lambda, unformatted_count
        
    except Exception as e:
        return False, -1

def main():
    """Check key templates only."""
    root_dir = r"d:\RUNNING APPS\ready production\osus-main\odoo17_final"
    
    key_templates = [
        'dynamic_accounts_report/report/trial_balance.xml',
        'dynamic_accounts_report/report/balance_sheet_report_templates.xml',
        'dynamic_accounts_report/report/general_ledger_templates.xml',
        'dynamic_accounts_report/report/partner_ledger_templates.xml',
        'dynamic_accounts_report/report/aged_receivable_templates.xml',
        'dynamic_accounts_report/report/aged_payable_templates.xml'
    ]
    
    print("🔍 Checking key dynamic report templates...\n")
    
    all_good = True
    for template in key_templates:
        file_path = os.path.join(root_dir, template)
        if os.path.exists(file_path):
            has_lambda, unformatted_count = check_template(file_path)
            
            template_name = os.path.basename(template)
            print(f"📄 {template_name}")
            
            if has_lambda:
                print("   ✅ Has format_number lambda")
            else:
                print("   ❌ Missing format_number lambda")
                all_good = False
            
            if unformatted_count == 0:
                print("   ✅ All amounts appear formatted")
            elif unformatted_count > 0:
                print(f"   ⚠️  {unformatted_count} potentially unformatted amounts")
                all_good = False
            else:
                print("   ❌ Error checking file")
                all_good = False
            
            print()
        else:
            print(f"❌ Template not found: {template}")
            all_good = False
    
    if all_good:
        print("🎉 All key dynamic report templates are properly formatted!")
    else:
        print("⚠️  Some templates may need additional work.")

if __name__ == "__main__":
    main()
