# -*- coding: utf-8 -*-
"""
XPath and Field Reference Validator
===================================
This script validates XPath expressions and field references in Odoo views
without requiring a running Odoo instance.
"""

import os
import xml.etree.ElementTree as ET
import re
from collections import defaultdict


class OdooViewValidator:
    """Validator for Odoo view XPath expressions and field references"""
    
    # Common standard fields in Odoo base models
    STANDARD_ACCOUNT_PAYMENT_FIELDS = {
        'name', 'partner_id', 'amount', 'currency_id', 'date', 'state', 
        'payment_type', 'partner_type', 'journal_id', 'company_id',
        'payment_method_id', 'payment_method_line_id', 'ref', 'memo'
    }
    
    STANDARD_ACCOUNT_MOVE_FIELDS = {
        'name', 'partner_id', 'date', 'state', 'move_type', 'amount_total',
        'amount_untaxed', 'amount_tax', 'currency_id', 'journal_id', 
        'company_id', 'ref', 'invoice_date', 'invoice_date_due'
    }
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def validate_xpath_expressions(self, xml_file):
        """Validate XPath expressions in XML view files"""
        print(f"\n🔍 Validating XPath expressions in: {xml_file}")
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Find all xpath elements
            xpath_elements = root.findall('.//xpath')
            
            for xpath_elem in xpath_elements:
                expr = xpath_elem.get('expr', '')
                position = xpath_elem.get('position', 'inside')
                
                print(f"  📍 XPath: {expr} (position: {position})")
                
                # Validate common problematic patterns
                if self._is_problematic_xpath(expr):
                    error_msg = f"Potentially problematic XPath in {xml_file}: {expr}"
                    self.errors.append(error_msg)
                    print(f"    ❌ {error_msg}")
                else:
                    print(f"    ✅ XPath looks valid")
                    
        except Exception as e:
            error_msg = f"Error parsing {xml_file}: {e}"
            self.errors.append(error_msg)
            print(f"  ❌ {error_msg}")
    
    def _is_problematic_xpath(self, expr):
        """Check if XPath expression might be problematic"""
        problematic_patterns = [
            r"//field\[@name='amount'\]",  # amount field might not exist in base views
            r"//field\[@name='voucher_number'\]",  # custom fields in base views
            r"//group\[@name='[^']*'\]",  # group names are often unreliable
            r"//page\[@name='[^']*'\]",   # page names might not exist
        ]
        
        for pattern in problematic_patterns:
            if re.search(pattern, expr):
                return True
        return False
    
    def suggest_xpath_alternatives(self, xml_file):
        """Suggest better XPath alternatives"""
        print(f"\n💡 Suggesting XPath alternatives for: {xml_file}")
        
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find problematic XPath patterns and suggest alternatives
            xpath_patterns = re.findall(r'<xpath\s+expr="([^"]*)"[^>]*>', content)
            
            for xpath in xpath_patterns:
                if "field[@name='amount']" in xpath:
                    print(f"  🔄 Replace: {xpath}")
                    print(f"    ✅ Suggested: //field[@name='partner_id']")
                elif "field[@name='voucher_number']" in xpath:
                    print(f"  🔄 Replace: {xpath}")
                    print(f"    ✅ Suggested: //field[@name='ref']")
                elif "group[@name=" in xpath:
                    print(f"  🔄 Replace: {xpath}")
                    print(f"    ✅ Suggested: Use field-based positioning instead")
                    
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
    
    def validate_field_references(self, xml_file, model_name):
        """Validate field references in view files"""
        print(f"\n🔍 Validating field references in: {xml_file} (model: {model_name})")
        
        # Get standard fields for the model
        if model_name == 'account.payment':
            standard_fields = self.STANDARD_ACCOUNT_PAYMENT_FIELDS
        elif model_name == 'account.move':
            standard_fields = self.STANDARD_ACCOUNT_MOVE_FIELDS
        else:
            print(f"  ⚠️ Unknown model: {model_name}")
            return
        
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find field references
            field_refs = re.findall(r'<field\s+name="([^"]*)"', content)
            xpath_field_refs = re.findall(r'field\[@name=\'([^\']*)\'\]', content)
            xpath_field_refs += re.findall(r'field\[@name="([^"]*)"\]', content)
            
            all_field_refs = set(field_refs + xpath_field_refs)
            
            print(f"  📊 Found {len(all_field_refs)} field references")
            
            for field_name in sorted(all_field_refs):
                if field_name in standard_fields:
                    print(f"    ✅ {field_name} (standard)")
                else:
                    print(f"    ⚠️ {field_name} (custom - ensure it exists)")
                    
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    def generate_safe_xpath_alternatives(self):
        """Generate safe XPath alternatives"""
        print("\n📋 Safe XPath Patterns for Odoo Views:")
        print("=" * 50)
        
        safe_patterns = {
            "Position after partner field": "//field[@name='partner_id']",
            "Position after amount field": "//field[@name='currency_id']",
            "Position after date field": "//field[@name='date']",
            "Position after reference field": "//field[@name='ref']",
            "Add to sheet element": "//sheet",
            "Add to form element": "//form",
            "Add to header element": "//header",
            "Position in tree": "//tree",
        }
        
        for description, xpath in safe_patterns.items():
            print(f"  ✅ {description}: {xpath}")
    
    def fix_account_payment_views(self):
        """Provide specific fixes for account payment views"""
        print("\n🔧 Specific Fixes for Account Payment Views:")
        print("=" * 50)
        
        fixes = {
            "//field[@name='amount']": "//field[@name='partner_id']",
            "//field[@name='voucher_number']": "//field[@name='ref']", 
            "//group[@name='group_main']": "//field[@name='partner_id']",
            "//page[@name='voucher_details']": "//field[@name='memo']",
        }
        
        for old_xpath, new_xpath in fixes.items():
            print(f"  🔄 {old_xpath} → {new_xpath}")
    
    def run_validation(self):
        """Run complete validation"""
        print("🚀 Starting XPath and Field Validation")
        print("=" * 60)
        
        # Validate view files
        view_files = [
            ('account_payment_final/views/account_payment_views.xml', 'account.payment'),
            ('account_payment_final/views/account_move_views.xml', 'account.move'),
            ('account_payment_final/views/payment_verification_views.xml', 'payment.verification.log'),
        ]
        
        for xml_file, model_name in view_files:
            if os.path.exists(xml_file):
                self.validate_xpath_expressions(xml_file)
                self.validate_field_references(xml_file, model_name)
                self.suggest_xpath_alternatives(xml_file)
        
        # Generate recommendations
        self.generate_safe_xpath_alternatives()
        self.fix_account_payment_views()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 VALIDATION SUMMARY")
        print("=" * 60)
        
        if self.errors:
            print(f"❌ Found {len(self.errors)} errors:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        else:
            print("✅ No critical errors found!")
        
        if self.warnings:
            print(f"\n⚠️ Found {len(self.warnings)} warnings:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")


def main():
    """Main validation function"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    validator = OdooViewValidator()
    validator.run_validation()


if __name__ == "__main__":
    main()
