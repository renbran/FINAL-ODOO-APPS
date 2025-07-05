#!/usr/bin/env python3
"""
Script to add proper number formatting to dynamic reports
"""

import re
import os

def fix_number_formatting_in_file(file_path, backup=True):
    """Fix number formatting in a report template file"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup original file
    if backup:
        backup_path = file_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Backup created: {backup_path}")
    
    # Patterns to match amount fields that need formatting
    patterns_to_fix = [
        # Balance/amount fields that should be formatted
        (r't-esc="([^"]*\[\'amount\'\][^"]*)"', r't-esc="format_number(\1)"'),
        (r't-esc="([^"]*\[\'total_[^\']*\'\][^"]*)"', r't-esc="format_number(\1)"'),
        (r't-esc="([^"]*\[\'balance\'\][^"]*)"', r't-esc="format_number(\1)"'),
        (r't-esc="([^"]*balance[^"]*)"(?![^<]*</)', r't-esc="format_number(\1)"'),
        (r't-esc="([^"]*_current_asset[^"]*)"', r't-esc="format_number(\1)"'),
        (r't-esc="([^"]*_non_current[^"]*)"', r't-esc="format_number(\1)"'),
    ]
    
    original_content = content
    
    # Apply formatting patterns
    for pattern, replacement in patterns_to_fix:
        # Skip if already formatted
        if 'format_number(' not in content:
            content = re.sub(pattern, replacement, content)
    
    # Add format_number function if not present
    if 'format_number' not in content and 't-set="format_number"' not in content:
        # Find the right place to insert the function
        if 't-call="web.html_container"' in content:
            insert_point = content.find('<t t-call="web.html_container">') + len('<t t-call="web.html_container">')
            format_function = '\n            <!-- Add number formatting function -->\n            <t t-set="format_number" t-value="lambda v: \'{:,.2f}\'.format(float(v)) if v and v != 0 else \'0.00\'"/>'
            content = content[:insert_point] + format_function + content[insert_point:]
    
    # Write back if changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {file_path}")
        return True
    else:
        print(f"No changes needed: {file_path}")
        return False

def main():
    """Main function to fix number formatting in dynamic reports"""
    
    # List of files to fix
    files_to_fix = [
        'd:/RUNNING APPS/ready production/osus-main/odoo17_final/dynamic_accounts_report/report/balance_sheet_report_templates.xml',
        'd:/RUNNING APPS/ready production/osus-main/odoo17_final/dynamic_accounts_report/report/general_ledger_templates.xml',
        'd:/RUNNING APPS/ready production/osus-main/odoo17_final/dynamic_accounts_report/report/partner_ledger_templates.xml',
        'd:/RUNNING APPS/ready production/osus-main/odoo17_final/dynamic_accounts_report/report/aged_receivable_templates.xml',
        'd:/RUNNING APPS/ready production/osus-main/odoo17_final/dynamic_accounts_report/report/aged_payable_templates.xml',
    ]
    
    print("Fixing number formatting in dynamic reports...")
    print("=" * 50)
    
    for file_path in files_to_fix:
        # Convert to Windows path format
        file_path = file_path.replace('/', '\\')
        fix_number_formatting_in_file(file_path)
    
    print("\nNote: Manual review may be needed for complex formatting cases.")
    print("Run this script from the project root directory.")

if __name__ == "__main__":
    main()
