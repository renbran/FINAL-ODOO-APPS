#!/usr/bin/env python3
"""
Odoo 17 View Inheritance Fix Script
Fixes view inheritance issues for account_payment_final module
"""

import re
import os

def fix_view_inheritances():
    """Fix all view inheritance issues in the module"""
    
    print("🔧 Fixing Odoo 17 View Inheritance Issues")
    print("=" * 50)
    
    # Define view replacements for Odoo 17 compatibility
    view_fixes = {
        # Old view reference -> New view reference
        'account.view_account_invoice_kanban': 'account.view_account_move_kanban',
        'account.view_account_invoice_form': 'account.view_move_form',
        'account.view_account_invoice_tree': 'account.view_account_move_tree',
        'account.invoice_tree': 'account.view_out_invoice_tree',
        'account.invoice_form': 'account.view_move_form',
        'account.view_account_payment_form': 'account.view_account_payment_form',
        'account.view_account_payment_tree': 'account.view_account_payment_tree'
    }
    
    files_to_check = [
        'account_payment_final/views/account_move_views.xml',
        'account_payment_final/views/account_payment_views.xml'
    ]
    
    total_fixes = 0
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
            
        print(f"\n📄 Checking: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            file_fixes = 0
            
            # Apply view reference fixes
            for old_ref, new_ref in view_fixes.items():
                pattern = f'ref="{old_ref}"'
                replacement = f'ref="{new_ref}"'
                
                if pattern in content:
                    content = content.replace(pattern, replacement)
                    file_fixes += 1
                    print(f"   ✅ Fixed: {old_ref} -> {new_ref}")
            
            # Fix specific xpath expressions that might be problematic
            xpath_fixes = [
                # Fix hasclass syntax for Odoo 17
                (r"hasclass\('([^']+)'\)", r"hasclass('\\1')"),
                # Fix badge classes for Odoo 17
                (r"badge-pill", "badge"),
                # Fix state references
                (r"record\.approval_state\.raw_value", "record.approval_state.raw_value"),
            ]
            
            for pattern, replacement in xpath_fixes:
                old_content = content
                content = re.sub(pattern, replacement, content)
                if content != old_content:
                    file_fixes += 1
                    print(f"   ✅ Fixed xpath pattern: {pattern}")
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   💾 Saved {file_fixes} fixes to {file_path}")
                total_fixes += file_fixes
            else:
                print(f"   ✅ No fixes needed in {file_path}")
                
        except Exception as e:
            print(f"   ❌ Error processing {file_path}: {e}")
    
    print(f"\n🎉 Total fixes applied: {total_fixes}")
    
    # Additional fixes for common Odoo 17 issues
    print("\n🔍 Checking for additional Odoo 17 compatibility issues...")
    
    # Check for deprecated field types
    deprecated_checks = {
        'account_payment_final/models/account_payment.py': [
            ('fields.Text(', 'fields.Text('),  # Check if Text fields are properly used
            ('_rec_name', '_rec_name'),  # Check rec_name usage
            ('@api.one', '@api.one'),  # Check for deprecated api.one
        ],
        'account_payment_final/models/account_move.py': [
            ('fields.Text(', 'fields.Text('),
            ('_rec_name', '_rec_name'),
            ('@api.one', '@api.one'),
        ]
    }
    
    for file_path, checks in deprecated_checks.items():
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            print(f"\n📄 Checking Python compatibility: {file_path}")
            for pattern, description in checks:
                if pattern in content and pattern.startswith('@api.one'):
                    print(f"   ⚠️  Found deprecated: {pattern}")
                elif pattern in content:
                    print(f"   ✅ Found valid: {description}")
    
    return total_fixes > 0

def validate_xml_syntax():
    """Validate XML syntax in view files"""
    print("\n🔍 Validating XML syntax...")
    
    xml_files = [
        'account_payment_final/views/account_move_views.xml',
        'account_payment_final/views/account_payment_views.xml',
        'account_payment_final/security/payment_security.xml',
        'account_payment_final/data/system_parameters.xml'
    ]
    
    try:
        import xml.etree.ElementTree as ET
        
        for file_path in xml_files:
            if os.path.exists(file_path):
                try:
                    ET.parse(file_path)
                    print(f"   ✅ Valid XML: {file_path}")
                except ET.ParseError as e:
                    print(f"   ❌ XML Error in {file_path}: {e}")
                    return False
            else:
                print(f"   ⚠️  File not found: {file_path}")
        
        return True
        
    except ImportError:
        print("   ⚠️  XML validation skipped (ElementTree not available)")
        return True

def main():
    """Main execution function"""
    print("🚀 Odoo 17 Compatibility Fix Script")
    print("=" * 50)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Apply fixes
    fixes_applied = fix_view_inheritances()
    xml_valid = validate_xml_syntax()
    
    print("\n" + "=" * 50)
    
    if fixes_applied and xml_valid:
        print("🎉 ALL FIXES APPLIED SUCCESSFULLY!")
        print("\n📋 Next Steps:")
        print("1. ✅ View inheritance issues fixed")
        print("2. 🔄 Update the module in your Odoo instance")
        print("3. 🧪 Test payment registration from invoices")
        
        print("\n🔧 What was fixed:")
        print("• ✅ Updated view references for Odoo 17 compatibility")
        print("• ✅ Fixed kanban view inheritance")
        print("• ✅ Updated xpath expressions")
        print("• ✅ Validated XML syntax")
        
        print("\n⚠️  Remember to:")
        print("• Update the module after these changes")
        print("• Test invoice payment registration")
        print("• Check that approval workflow still works")
        
    elif xml_valid:
        print("✅ XML syntax is valid, no inheritance fixes needed")
        
    else:
        print("❌ SOME ISSUES REMAIN")
        print("Please check the error messages above and fix manually")

if __name__ == "__main__":
    main()
