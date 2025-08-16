#!/usr/bin/env python3
"""
Payment Voucher Report Formatting Validator
Checks for potential formatting issues that could cause extra characters
"""

import xml.etree.ElementTree as ET
import re
import os

def check_formatting_issues(file_path):
    """Check for common formatting issues in QWeb templates"""
    
    print(f"🔍 Analyzing formatting in: {file_path}")
    print("=" * 60)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        issues = []
        warnings = []
        fixed_items = []
        
        # Check for line breaks in field references
        line_break_pattern = r't-field="[^"]+"\s*\n\s*[^\<]'
        line_break_matches = re.finditer(line_break_pattern, content, re.MULTILINE)
        
        for match in line_break_matches:
            line_num = content[:match.start()].count('\n') + 1
            issues.append(f"Line {line_num}: Field reference spans multiple lines")
        
        # Check for mixed field and conditional formatting
        mixed_pattern = r'<span[^>]*t-field="[^"]+"/>\s*\n\s*<t\s+t-if='
        mixed_matches = re.finditer(mixed_pattern, content, re.MULTILINE)
        
        for match in mixed_matches:
            line_num = content[:match.start()].count('\n') + 1
            warnings.append(f"Line {line_num}: Field and conditional on separate lines (potential whitespace)")
        
        # Check for Python format strings (should be replaced with % formatting)
        format_pattern = r'\.format\('
        format_matches = re.finditer(format_pattern, content)
        
        for match in format_matches:
            line_num = content[:match.start()].count('\n') + 1
            issues.append(f"Line {line_num}: Using .format() - should use % formatting for Odoo compatibility")
        
        # Check for complex Python expressions in t-esc
        complex_expr_pattern = r't-esc="[^"]*\[[^\]]*for[^\]]*\]'
        complex_matches = re.finditer(complex_expr_pattern, content)
        
        for match in complex_matches:
            line_num = content[:match.start()].count('\n') + 1
            issues.append(f"Line {line_num}: Complex Python expression in t-esc (may cause rendering issues)")
        
        # Check for properly formatted field references (these are good)
        good_field_pattern = r'<span[^>]*t-field="[^"]+"/><t\s+t-if[^>]*>[^<]*</t>'
        good_matches = re.finditer(good_field_pattern, content)
        
        for match in good_matches:
            line_num = content[:match.start()].count('\n') + 1
            fixed_items.append(f"Line {line_num}: Properly formatted field with inline conditional")
        
        # Check for single-line field references (these are good)
        single_line_pattern = r'<span[^>]*t-field="[^"]+"/>\s*\|'
        single_line_matches = re.finditer(single_line_pattern, content)
        
        for match in single_line_matches:
            line_num = content[:match.start()].count('\n') + 1
            fixed_items.append(f"Line {line_num}: Single-line field reference")
        
        # Check for % formatting (these are good)
        percent_pattern = r"'%[^']*'\s*%\s*[a-zA-Z_]"
        percent_matches = re.finditer(percent_pattern, content)
        
        for match in percent_matches:
            line_num = content[:match.start()].count('\n') + 1
            fixed_items.append(f"Line {line_num}: Using % formatting (Odoo compatible)")
        
        # Validate XML syntax
        try:
            ET.parse(file_path)
            xml_valid = True
        except ET.ParseError as e:
            xml_valid = False
            issues.append(f"XML Parse Error: {e}")
        
        # Report results
        print("📋 FORMATTING ANALYSIS RESULTS")
        print("-" * 40)
        
        if xml_valid:
            print("✅ XML Syntax: Valid")
        else:
            print("❌ XML Syntax: Invalid")
        
        print(f"\n🚨 Issues Found: {len(issues)}")
        for issue in issues:
            print(f"  ❌ {issue}")
        
        print(f"\n⚠️  Warnings: {len(warnings)}")
        for warning in warnings:
            print(f"  ⚠️  {warning}")
        
        print(f"\n✅ Fixed Items: {len(fixed_items)}")
        for fixed in fixed_items:
            print(f"  ✅ {fixed}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 FORMATTING SUMMARY")
        print("=" * 60)
        
        if len(issues) == 0:
            print("🎉 NO CRITICAL FORMATTING ISSUES FOUND!")
            print("The report should render without extra characters.")
        else:
            print(f"💥 {len(issues)} CRITICAL ISSUES NEED FIXING")
            print("These may cause extra characters in the rendered report.")
        
        if len(warnings) > 0:
            print(f"⚠️  {len(warnings)} warnings - review for potential whitespace issues")
        
        print(f"✅ {len(fixed_items)} items are properly formatted")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Error analyzing file: {e}")
        return False

def main():
    """Main validation function"""
    file_path = "account_payment_final/reports/payment_voucher_report.xml"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    success = check_formatting_issues(file_path)
    
    if success:
        print("\n🎯 FORMATTING VALIDATION PASSED!")
        print("The report template is properly formatted and should not")
        print("produce extra characters in the rendered output.")
    else:
        print("\n💥 FORMATTING VALIDATION FAILED!")
        print("Fix the issues above to prevent extra characters.")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
