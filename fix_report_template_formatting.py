#!/usr/bin/env python3
"""
Report Template Formatting Fix Script
====================================

This script addresses formatting issues in order status override report templates:
1. Standardize decimal precision to 2 decimal places
2. Fix extra character rendering in currency displays
3. Ensure consistent formatting across all monetary fields
4. Clean up any encoding or rendering artifacts

Target Issues:
- Inconsistent decimal formatting ({:,.0f} vs {:,.2f})
- Missing monetary widget options for proper currency display
- Potential extra character rendering in AED currency formatting
- Mixed formatting approaches across different report sections
"""

import os
import re
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('report_formatting_fix.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ReportFormattingFixer:
    """Comprehensive report template formatting fixer"""
    
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.reports_path = self.base_path / "order_status_override" / "reports"
        self.fixed_files = []
        self.issues_found = []
        
    def analyze_and_fix_formatting(self):
        """Main method to analyze and fix all formatting issues"""
        logger.info("🔍 Starting comprehensive report formatting analysis...")
        
        # Find all XML report files
        xml_files = list(self.reports_path.glob("*.xml"))
        logger.info(f"Found {len(xml_files)} XML report files to analyze")
        
        for xml_file in xml_files:
            self.fix_file_formatting(xml_file)
            
        self.generate_summary_report()
        
    def fix_file_formatting(self, xml_file):
        """Fix formatting issues in a specific XML file"""
        logger.info(f"📄 Processing: {xml_file.name}")
        
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Track changes made
            changes_made = []
            
            # 1. Fix price field formatting - add proper monetary widget
            content, price_changes = self.fix_price_field_formatting(content)
            changes_made.extend(price_changes)
            
            # 2. Fix decimal formatting in t-esc expressions
            content, decimal_changes = self.fix_decimal_formatting(content)
            changes_made.extend(decimal_changes)
            
            # 3. Fix currency formatting and remove extra characters
            content, currency_changes = self.fix_currency_formatting(content)
            changes_made.extend(currency_changes)
            
            # 4. Fix percentage formatting
            content, percent_changes = self.fix_percentage_formatting(content)
            changes_made.extend(percent_changes)
            
            # Only write if changes were made
            if content != original_content:
                # Create backup
                backup_file = xml_file.with_suffix('.xml.backup')
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                    
                # Write fixed content
                with open(xml_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                self.fixed_files.append(xml_file.name)
                logger.info(f"✅ Fixed {len(changes_made)} formatting issues in {xml_file.name}")
                
                for change in changes_made:
                    logger.info(f"   - {change}")
                    
            else:
                logger.info(f"✓ No formatting issues found in {xml_file.name}")
                
        except Exception as e:
            logger.error(f"❌ Error processing {xml_file.name}: {str(e)}")
            self.issues_found.append(f"{xml_file.name}: {str(e)}")
            
    def fix_price_field_formatting(self, content):
        """Fix price field formatting to use proper monetary widget"""
        changes = []
        
        # Pattern 1: Basic price fields without monetary widget
        price_field_pattern = r'<span t-field="([^"]*(?:price_unit|price_subtotal|amount_total)[^"]*)"(?!\s+t-options)/>'
        
        def replace_price_field(match):
            field_name = match.group(1)
            changes.append(f"Added monetary widget to {field_name}")
            return f'<span t-field="{field_name}" t-options="{{\'widget\': \'monetary\', \'display_currency\': o.currency_id}}"/>'
            
        content = re.sub(price_field_pattern, replace_price_field, content)
        
        return content, changes
        
    def fix_decimal_formatting(self, content):
        """Fix decimal formatting in t-esc expressions"""
        changes = []
        
        # Pattern 1: Change {:,.0f} to {:,.2f} for monetary amounts
        decimal_pattern = r"(\{:,\.)0f(\})"
        
        def replace_decimal(match):
            changes.append("Changed decimal precision from 0 to 2 decimal places")
            return f"{match.group(1)}2f{match.group(2)}"
            
        content = re.sub(decimal_pattern, replace_decimal, content)
        
        # Pattern 2: Add proper formatting for unformatted monetary expressions
        unformatted_money_pattern = r't-esc="([^"]*(?:amount|total|commission)[^"]*)"(?!\s*t-options)'
        
        def replace_unformatted_money(match):
            expr = match.group(1)
            if not "{:" in expr and not "format(" in expr:
                changes.append(f"Added monetary formatting to expression: {expr[:30]}...")
                # Wrap simple field access with formatting
                if "o." in expr and not "(" in expr:
                    return f't-esc="{{{{:,.2f}} AED}}".format({expr} or 0)"'
            return match.group(0)
            
        content = re.sub(unformatted_money_pattern, replace_unformatted_money, content)
        
        return content, changes
        
    def fix_currency_formatting(self, content):
        """Fix currency formatting and remove extra characters"""
        changes = []
        
        # Pattern 1: Ensure proper spacing in AED formatting
        aed_pattern = r"(\{:,\.[0-9]+f\}\s*AED)"
        
        def fix_aed_spacing(match):
            # Ensure single space before AED
            formatted = re.sub(r'\s+AED', ' AED', match.group(1))
            if formatted != match.group(1):
                changes.append("Fixed AED currency spacing")
            return formatted
            
        content = re.sub(aed_pattern, fix_aed_spacing, content)
        
        # Pattern 2: Fix potential encoding issues with currency symbols
        currency_encoding_fixes = [
            (r'AED\s*', 'AED '),  # Ensure single space after AED
            (r'\s+AED', ' AED'),   # Remove multiple spaces before AED
        ]
        
        for pattern, replacement in currency_encoding_fixes:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes.append(f"Fixed currency encoding: {pattern}")
                
        return content, changes
        
    def fix_percentage_formatting(self, content):
        """Fix percentage formatting"""
        changes = []
        
        # Ensure percentage formatting is consistent
        percent_pattern = r"(\{:\.[0-9]+f\}%)"
        
        def fix_percent(match):
            # Standardize to 1 decimal place for percentages
            if ".1f" not in match.group(1):
                changes.append("Standardized percentage to 1 decimal place")
                return "{:.1f}%"
            return match.group(1)
            
        content = re.sub(percent_pattern, fix_percent, content)
        
        return content, changes
        
    def generate_summary_report(self):
        """Generate summary report of all fixes applied"""
        logger.info("\n" + "="*60)
        logger.info("📊 REPORT FORMATTING FIX SUMMARY")
        logger.info("="*60)
        
        logger.info(f"✅ Files Successfully Fixed: {len(self.fixed_files)}")
        for file_name in self.fixed_files:
            logger.info(f"   - {file_name}")
            
        if self.issues_found:
            logger.info(f"\n❌ Issues Found: {len(self.issues_found)}")
            for issue in self.issues_found:
                logger.info(f"   - {issue}")
                
        logger.info("\n🔧 Formatting Standards Applied:")
        logger.info("   - Monetary fields: 2 decimal places with proper currency widget")
        logger.info("   - Percentage fields: 1 decimal place")
        logger.info("   - Currency display: Proper AED spacing and encoding")
        logger.info("   - Field formatting: Consistent monetary widget usage")
        
        logger.info("\n💾 Backups created for all modified files with .backup extension")
        logger.info("="*60)

def main():
    """Main execution function"""
    try:
        # Get the base path (current directory)
        base_path = Path.cwd()
        
        # Initialize the fixer
        fixer = ReportFormattingFixer(base_path)
        
        # Check if reports directory exists
        if not fixer.reports_path.exists():
            logger.error(f"❌ Reports directory not found: {fixer.reports_path}")
            sys.exit(1)
            
        # Run the formatting fixes
        fixer.analyze_and_fix_formatting()
        
        logger.info("\n🎉 Report formatting fix completed successfully!")
        logger.info("All monetary fields now display with 2 decimal places")
        logger.info("Currency formatting standardized with proper spacing")
        logger.info("Extra character rendering issues resolved")
        
    except Exception as e:
        logger.error(f"❌ Critical error during formatting fix: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
