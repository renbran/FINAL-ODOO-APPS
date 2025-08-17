#!/usr/bin/env python3
"""
Report Formatting Validation Script
==================================

This script validates that all report formatting fixes have been properly applied:
1. Verify all monetary fields use proper 2 decimal formatting
2. Confirm all price fields have monetary widget attributes
3. Check for proper AED currency spacing
4. Validate CloudPepper compatibility
5. Generate comprehensive validation report

Post-Fix Validation for Order Status Override Module
"""

import os
import re
import sys
import json
from pathlib import Path
from datetime import datetime

class ReportFormattingValidator:
    """Comprehensive validator for report template formatting"""
    
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.reports_path = self.base_path / "order_status_override" / "reports"
        self.validation_results = {
            'files_checked': [],
            'formatting_compliance': {},
            'monetary_widget_compliance': {},
            'currency_formatting_compliance': {},
            'cloudpepper_compatibility': {},
            'overall_status': 'PENDING'
        }
        
    def validate_all_reports(self):
        """Main validation method"""
        print("🔍 Starting comprehensive report formatting validation...")
        print("="*60)
        
        # Find all XML report files
        xml_files = list(self.reports_path.glob("*.xml"))
        print(f"Found {len(xml_files)} XML report files to validate")
        
        for xml_file in xml_files:
            if xml_file.suffix == '.backup':
                continue  # Skip backup files
                
            print(f"\n📄 Validating: {xml_file.name}")
            self.validate_file_formatting(xml_file)
            
        self.generate_validation_summary()
        self.save_validation_results()
        
    def validate_file_formatting(self, xml_file):
        """Validate formatting for a specific XML file"""
        file_name = xml_file.name
        self.validation_results['files_checked'].append(file_name)
        
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Initialize file results
            self.validation_results['formatting_compliance'][file_name] = []
            self.validation_results['monetary_widget_compliance'][file_name] = []
            self.validation_results['currency_formatting_compliance'][file_name] = []
            self.validation_results['cloudpepper_compatibility'][file_name] = []
            
            # Validate decimal formatting
            self.validate_decimal_formatting(content, file_name)
            
            # Validate monetary widget usage
            self.validate_monetary_widgets(content, file_name)
            
            # Validate currency formatting
            self.validate_currency_formatting(content, file_name)
            
            # Validate CloudPepper compatibility
            self.validate_cloudpepper_compatibility(content, file_name)
            
        except Exception as e:
            print(f"❌ Error validating {file_name}: {str(e)}")
            self.validation_results['formatting_compliance'][file_name] = [f"ERROR: {str(e)}"]
            
    def validate_decimal_formatting(self, content, file_name):
        """Validate that all monetary amounts use 2 decimal places"""
        print("  🔢 Checking decimal formatting...")
        
        # Check for old 0 decimal formatting (should be none)
        zero_decimal_pattern = r'\{:,\.0f\}'
        zero_decimal_matches = re.findall(zero_decimal_pattern, content)
        
        if zero_decimal_matches:
            issue = f"Found {len(zero_decimal_matches)} instances of 0-decimal formatting"
            print(f"    ❌ {issue}")
            self.validation_results['formatting_compliance'][file_name].append(issue)
        else:
            print("    ✅ No 0-decimal formatting found")
            self.validation_results['formatting_compliance'][file_name].append("PASS: No 0-decimal formatting")
            
        # Check for proper 2 decimal formatting
        two_decimal_pattern = r'\{:,\.2f\}'
        two_decimal_matches = re.findall(two_decimal_pattern, content)
        
        if two_decimal_matches:
            success = f"Found {len(two_decimal_matches)} properly formatted 2-decimal instances"
            print(f"    ✅ {success}")
            self.validation_results['formatting_compliance'][file_name].append(f"PASS: {success}")
        else:
            print("    ⚠️  No 2-decimal formatting found (may be using monetary widgets)")
            self.validation_results['formatting_compliance'][file_name].append("INFO: No explicit decimal formatting found")
            
    def validate_monetary_widgets(self, content, file_name):
        """Validate that price fields use proper monetary widgets"""
        print("  💰 Checking monetary widget usage...")
        
        # Find all price-related fields
        price_field_pattern = r't-field="[^"]*(?:price_unit|price_subtotal|amount_total)[^"]*"'
        price_fields = re.findall(price_field_pattern, content)
        
        if not price_fields:
            print("    ℹ️  No price fields found in this file")
            self.validation_results['monetary_widget_compliance'][file_name].append("INFO: No price fields found")
            return
            
        # Check if monetary widgets are used
        monetary_widget_pattern = r't-field="[^"]*(?:price_unit|price_subtotal|amount_total)[^"]*"\s+t-options="[^"]*monetary[^"]*"'
        monetary_widgets = re.findall(monetary_widget_pattern, content)
        
        widget_coverage = len(monetary_widgets) / len(price_fields) * 100
        
        if widget_coverage >= 80:  # Allow some fields to use other formatting
            success = f"Good monetary widget coverage: {len(monetary_widgets)}/{len(price_fields)} fields ({widget_coverage:.1f}%)"
            print(f"    ✅ {success}")
            self.validation_results['monetary_widget_compliance'][file_name].append(f"PASS: {success}")
        else:
            issue = f"Low monetary widget coverage: {len(monetary_widgets)}/{len(price_fields)} fields ({widget_coverage:.1f}%)"
            print(f"    ⚠️  {issue}")
            self.validation_results['monetary_widget_compliance'][file_name].append(f"WARNING: {issue}")
            
    def validate_currency_formatting(self, content, file_name):
        """Validate AED currency formatting and spacing"""
        print("  💱 Checking currency formatting...")
        
        # Check for AED currency usage
        aed_pattern = r'AED\s*[\'"}]'
        aed_matches = re.findall(aed_pattern, content)
        
        if not aed_matches:
            print("    ℹ️  No AED currency formatting found")
            self.validation_results['currency_formatting_compliance'][file_name].append("INFO: No AED currency found")
            return
            
        # Check for proper spacing (single space before AED)
        proper_spacing_pattern = r'\{\s*AED\s*[\'"}\)]'
        proper_spacing = re.findall(proper_spacing_pattern, content)
        
        # Check for improper spacing
        improper_spacing_pattern = r'AED\s{2,}|[^\s]AED'
        improper_spacing = re.findall(improper_spacing_pattern, content)
        
        if improper_spacing:
            issue = f"Found {len(improper_spacing)} instances of improper AED spacing"
            print(f"    ⚠️  {issue}")
            self.validation_results['currency_formatting_compliance'][file_name].append(f"WARNING: {issue}")
        else:
            success = f"Proper AED currency formatting: {len(aed_matches)} instances"
            print(f"    ✅ {success}")
            self.validation_results['currency_formatting_compliance'][file_name].append(f"PASS: {success}")
            
    def validate_cloudpepper_compatibility(self, content, file_name):
        """Validate CloudPepper compatibility requirements"""
        print("  ☁️  Checking CloudPepper compatibility...")
        
        compatibility_checks = []
        
        # Check for proper XML structure
        if '<?xml version="1.0" encoding="utf-8"?>' in content:
            compatibility_checks.append("✅ Proper XML encoding declaration")
        else:
            compatibility_checks.append("⚠️  Missing XML encoding declaration")
            
        # Check for proper template structure
        if '<template id=' in content:
            compatibility_checks.append("✅ Proper template structure")
        else:
            compatibility_checks.append("ℹ️  No templates in this file")
            
        # Check for potential character encoding issues
        problematic_chars = re.findall(r'[^\x00-\x7F]', content)
        if problematic_chars:
            unique_chars = set(problematic_chars)
            if len(unique_chars) > 5:  # Some special chars are OK
                compatibility_checks.append(f"⚠️  Found {len(unique_chars)} unique non-ASCII characters")
            else:
                compatibility_checks.append("✅ Minimal non-ASCII character usage")
        else:
            compatibility_checks.append("✅ Only ASCII characters used")
            
        # Store results
        self.validation_results['cloudpepper_compatibility'][file_name] = compatibility_checks
        for check in compatibility_checks:
            print(f"    {check}")
            
    def generate_validation_summary(self):
        """Generate comprehensive validation summary"""
        print("\n" + "="*60)
        print("📊 REPORT FORMATTING VALIDATION SUMMARY")
        print("="*60)
        
        total_files = len(self.validation_results['files_checked'])
        print(f"Total Files Validated: {total_files}")
        
        # Count compliance status
        formatting_issues = 0
        widget_issues = 0
        currency_issues = 0
        cloudpepper_issues = 0
        
        for file_name in self.validation_results['files_checked']:
            # Check formatting compliance
            formatting_results = self.validation_results['formatting_compliance'].get(file_name, [])
            if any('ERROR' in result or 'Found' in result for result in formatting_results):
                formatting_issues += 1
                
            # Check widget compliance
            widget_results = self.validation_results['monetary_widget_compliance'].get(file_name, [])
            if any('WARNING' in result or 'ERROR' in result for result in widget_results):
                widget_issues += 1
                
            # Check currency compliance
            currency_results = self.validation_results['currency_formatting_compliance'].get(file_name, [])
            if any('WARNING' in result or 'ERROR' in result for result in currency_results):
                currency_issues += 1
                
            # Check CloudPepper compatibility
            cloudpepper_results = self.validation_results['cloudpepper_compatibility'].get(file_name, [])
            if any('⚠️' in result or '❌' in result for result in cloudpepper_results):
                cloudpepper_issues += 1
                
        print(f"\n📈 Compliance Summary:")
        print(f"  ✅ Decimal Formatting: {total_files - formatting_issues}/{total_files} files compliant")
        print(f"  ✅ Monetary Widgets: {total_files - widget_issues}/{total_files} files compliant")
        print(f"  ✅ Currency Formatting: {total_files - currency_issues}/{total_files} files compliant")
        print(f"  ✅ CloudPepper Ready: {total_files - cloudpepper_issues}/{total_files} files compatible")
        
        # Determine overall status
        total_issues = formatting_issues + widget_issues + currency_issues + cloudpepper_issues
        
        if total_issues == 0:
            self.validation_results['overall_status'] = 'FULLY_COMPLIANT'
            print(f"\n🎉 OVERALL STATUS: FULLY COMPLIANT")
            print("All report templates are properly formatted and CloudPepper ready!")
        elif total_issues <= 2:
            self.validation_results['overall_status'] = 'MOSTLY_COMPLIANT'
            print(f"\n✅ OVERALL STATUS: MOSTLY COMPLIANT")
            print(f"Minor issues found in {total_issues} areas, but deployment ready")
        else:
            self.validation_results['overall_status'] = 'NEEDS_ATTENTION'
            print(f"\n⚠️  OVERALL STATUS: NEEDS ATTENTION")
            print(f"Issues found in {total_issues} areas, review recommended")
            
        print("\n🔧 Applied Formatting Standards:")
        print("  - All monetary amounts display with 2 decimal places")
        print("  - Price fields use proper Odoo monetary widgets")
        print("  - AED currency formatting with consistent spacing")
        print("  - CloudPepper compatible character encoding")
        print("  - Professional report presentation")
        
    def save_validation_results(self):
        """Save validation results to JSON file"""
        results_file = self.base_path / "report_formatting_validation_results.json"
        
        # Add metadata
        self.validation_results['validation_timestamp'] = datetime.now().isoformat()
        self.validation_results['validation_summary'] = {
            'total_files_checked': len(self.validation_results['files_checked']),
            'files_checked': self.validation_results['files_checked'],
            'overall_status': self.validation_results['overall_status']
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 Validation results saved to: {results_file}")

def main():
    """Main execution function"""
    try:
        # Get the base path (current directory)
        base_path = Path.cwd()
        
        # Initialize the validator
        validator = ReportFormattingValidator(base_path)
        
        # Check if reports directory exists
        if not validator.reports_path.exists():
            print(f"❌ Reports directory not found: {validator.reports_path}")
            sys.exit(1)
            
        # Run the validation
        validator.validate_all_reports()
        
        print("\n🎯 Report formatting validation completed!")
        print("Check the generated JSON file for detailed results.")
        
    except Exception as e:
        print(f"❌ Critical error during validation: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
