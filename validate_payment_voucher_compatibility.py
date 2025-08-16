#!/usr/bin/env python3
"""
Payment Voucher Report Compatibility Validator
Checks if all field mappings and placeholders in the report template match actual model fields
"""

import xml.etree.ElementTree as ET
import re
import os
import sys

def extract_field_references_from_template(template_path):
    """Extract all t-field and t-esc references from the report template"""
    try:
        tree = ET.parse(template_path)
        root = tree.getroot()
        
        field_refs = set()
        method_refs = set()
        
        # Get the template content as string for regex analysis
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find t-field references
        t_field_pattern = r't-field="([^"]+)"'
        t_field_matches = re.findall(t_field_pattern, content)
        for match in t_field_matches:
            field_refs.add(match)
        
        # Find t-esc references (methods and expressions)
        t_esc_pattern = r't-esc="([^"]+)"'
        t_esc_matches = re.findall(t_esc_pattern, content)
        for match in t_esc_matches:
            if '(' in match:  # Method call
                method_refs.add(match.split('(')[0].replace('o.', ''))
            else:  # Field reference
                field_refs.add(match)
        
        # Find other field references in text
        field_pattern = r'<span[^>]*t-field="([^"]+)"'
        field_matches = re.findall(field_pattern, content)
        for match in field_matches:
            field_refs.add(match)
        
        return field_refs, method_refs
        
    except Exception as e:
        print(f"❌ Error parsing template: {e}")
        return set(), set()

def extract_model_fields_and_methods(model_path):
    """Extract field definitions and method names from the model file"""
    try:
        with open(model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find field definitions
        field_pattern = r'(\w+)\s*=\s*fields\.'
        field_matches = re.findall(field_pattern, content)
        
        # Find method definitions
        method_pattern = r'def\s+(\w+)\s*\('
        method_matches = re.findall(method_pattern, content)
        
        # Find inherited fields from base models (common fields)
        inherited_fields = {
            'name', 'partner_id', 'amount', 'date', 'ref', 'journal_id', 
            'payment_type', 'currency_id', 'create_uid', 'create_date', 
            'write_uid', 'write_date', 'company_id', 'state'
        }
        
        # Partner fields (via partner_id)
        partner_fields = {
            'partner_id.name', 'partner_id.mobile', 'partner_id.email',
            'partner_id.phone', 'partner_id.street', 'partner_id.city'
        }
        
        # Journal fields (via journal_id)
        journal_fields = {
            'journal_id.name', 'journal_id.code', 'journal_id.type'
        }
        
        # User fields (via create_uid, etc.)
        user_fields = {
            'create_uid.name', 'create_uid.signature', 'write_uid.name'
        }
        
        all_fields = set(field_matches) | inherited_fields | partner_fields | journal_fields | user_fields
        all_methods = set(method_matches)
        
        return all_fields, all_methods
        
    except Exception as e:
        print(f"❌ Error parsing model: {e}")
        return set(), set()

def validate_field_compatibility():
    """Main validation function"""
    print("🔍 Validating Payment Voucher Report Compatibility...")
    print("=" * 70)
    
    template_path = "account_payment_final/reports/payment_voucher_report.xml"
    model_path = "account_payment_final/models/account_payment.py"
    
    # Check if files exist
    if not os.path.exists(template_path):
        print(f"❌ Template file not found: {template_path}")
        return False
    
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        return False
    
    print(f"📄 Template: {template_path}")
    print(f"📄 Model: {model_path}")
    
    # Extract references from template
    print("\n🔍 Extracting field references from template...")
    template_fields, template_methods = extract_field_references_from_template(template_path)
    
    print(f"Found {len(template_fields)} field references and {len(template_methods)} method references")
    
    # Extract definitions from model
    print("\n🔍 Extracting field and method definitions from model...")
    model_fields, model_methods = extract_model_fields_and_methods(model_path)
    
    print(f"Found {len(model_fields)} fields and {len(model_methods)} methods in model")
    
    # Validate field mappings
    print("\n📋 FIELD COMPATIBILITY CHECK")
    print("-" * 40)
    
    missing_fields = []
    valid_fields = []
    
    for field_ref in template_fields:
        # Clean up the field reference
        clean_ref = field_ref.replace('o.', '').replace('doc.', '').replace('docs.', '')
        
        if clean_ref in model_fields:
            valid_fields.append(clean_ref)
            print(f"✅ {field_ref}")
        else:
            missing_fields.append(field_ref)
            print(f"❌ {field_ref} → Missing in model")
    
    # Validate method mappings
    print("\n📋 METHOD COMPATIBILITY CHECK")
    print("-" * 40)
    
    missing_methods = []
    valid_methods = []
    
    for method_ref in template_methods:
        # Clean up the method reference
        clean_ref = method_ref.replace('o.', '').replace('doc.', '').replace('docs.', '')
        
        if clean_ref in model_methods:
            valid_methods.append(clean_ref)
            print(f"✅ {method_ref}()")
        else:
            missing_methods.append(method_ref)
            print(f"❌ {method_ref}() → Missing in model")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 COMPATIBILITY SUMMARY")
    print("=" * 70)
    
    print(f"✅ Valid Fields:     {len(valid_fields)}/{len(template_fields)}")
    print(f"✅ Valid Methods:    {len(valid_methods)}/{len(template_methods)}")
    print(f"❌ Missing Fields:   {len(missing_fields)}")
    print(f"❌ Missing Methods:  {len(missing_methods)}")
    
    if missing_fields:
        print(f"\n🚨 MISSING FIELDS:")
        for field in missing_fields:
            print(f"  - {field}")
    
    if missing_methods:
        print(f"\n🚨 MISSING METHODS:")
        for method in missing_methods:
            print(f"  - {method}()")
    
    # Detailed field analysis
    print(f"\n📋 DETAILED FIELD ANALYSIS")
    print("-" * 40)
    
    print("Template Field References:")
    for field in sorted(template_fields):
        status = "✅" if field.replace('o.', '').replace('doc.', '').replace('docs.', '') in model_fields else "❌"
        print(f"  {status} {field}")
    
    print("\nTemplate Method References:")
    for method in sorted(template_methods):
        status = "✅" if method.replace('o.', '').replace('doc.', '').replace('docs.', '') in model_methods else "❌"
        print(f"  {status} {method}()")
    
    # Check for critical compatibility issues
    critical_issues = []
    
    # Check if essential methods exist
    essential_methods = ['get_related_document_info', 'get_payment_summary', 'get_voucher_description', '_get_amount_in_words']
    for method in essential_methods:
        if method not in model_methods:
            critical_issues.append(f"Missing essential method: {method}()")
    
    # Check if essential fields exist
    essential_fields = ['qr_code', 'name', 'date', 'partner_id', 'amount', 'journal_id', 'payment_type']
    for field in essential_fields:
        if field not in model_fields:
            critical_issues.append(f"Missing essential field: {field}")
    
    if critical_issues:
        print(f"\n🚨 CRITICAL COMPATIBILITY ISSUES:")
        for issue in critical_issues:
            print(f"  - {issue}")
        print(f"\n💥 Report may not render correctly!")
        return False
    else:
        print(f"\n🎉 REPORT IS COMPATIBLE!")
        print("All essential fields and methods are available.")
        return True

if __name__ == "__main__":
    success = validate_field_compatibility()
    sys.exit(0 if success else 1)
