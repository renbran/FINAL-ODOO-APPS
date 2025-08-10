#!/usr/bin/env python3
"""
Enhanced validation script for field references and search view compatibility
"""
import os
import xml.etree.ElementTree as ET
import re

def check_search_view_fields(module_dir):
    """Check if all fields referenced in search views exist and are searchable"""
    print("🔍 Validating Search View Field References...")
    
    # Get model file to extract field definitions
    model_file = os.path.join(module_dir, 'models', 'account_payment.py')
    if not os.path.exists(model_file):
        print("❌ Model file not found")
        return False
    
    # Extract field definitions from model
    model_content = open(model_file, 'r', encoding='utf-8').read()
    
    # Find field definitions with store=True or without compute (searchable fields)
    searchable_fields = set()
    
    # Standard fields that are always searchable
    standard_fields = {
        'id', 'name', 'state', 'partner_id', 'journal_id', 'company_id', 
        'payment_type', 'amount', 'date', 'ref', 'currency_id',
        'payment_method_line_id', 'requires_approval', 'voucher_type',
        'verification_token', 'create_date', 'write_date'
    }
    searchable_fields.update(standard_fields)
    
    # Find explicitly stored computed fields
    stored_computed_pattern = r'fields\.\w+\([^)]*compute[^)]*store=True[^)]*\)'
    stored_fields = re.findall(stored_computed_pattern, model_content)
    
    # Find regular fields (non-computed)
    field_pattern = r'(\w+)\s*=\s*fields\.\w+\([^)]*(?!compute)[^)]*\)'
    regular_fields = re.findall(field_pattern, model_content)
    searchable_fields.update(regular_fields)
    
    print(f"   Found {len(searchable_fields)} searchable fields")
    
    # Check search views
    search_views_valid = True
    view_files = []
    for root, dirs, files in os.walk(os.path.join(module_dir, 'views')):
        for file in files:
            if file.endswith('.xml'):
                view_files.append(os.path.join(root, file))
    
    for view_file in view_files:
        try:
            tree = ET.parse(view_file)
            root = tree.getroot()
            
            # Find search view records
            for record in root.findall('.//record[@model="ir.ui.view"]'):
                name = record.find('field[@name="name"]')
                if name is not None and 'search' in name.text.lower():
                    arch = record.find('field[@name="arch"]')
                    if arch is not None:
                        # Check all filter domains
                        for filter_elem in arch.findall('.//filter[@domain]'):
                            domain = filter_elem.get('domain', '')
                            filter_name = filter_elem.get('name', 'unnamed')
                            
                            # Extract field names from domain
                            field_refs = re.findall(r"\('(\w+)'", domain)
                            for field_ref in field_refs:
                                if field_ref not in searchable_fields:
                                    print(f"   ❌ Unsearchable field '{field_ref}' in filter '{filter_name}'")
                                    print(f"      File: {view_file}")
                                    search_views_valid = False
                                else:
                                    print(f"   ✅ Valid field '{field_ref}' in filter '{filter_name}'")
                                    
        except Exception as e:
            print(f"   ❌ Error processing {view_file}: {e}")
            search_views_valid = False
    
    return search_views_valid

def main():
    print("🚀 ENHANCED FIELD REFERENCE VALIDATION")
    print("="*50)
    
    module_dir = "account_payment_approval"
    
    if not os.path.exists(module_dir):
        print("❌ Module directory not found!")
        return False
    
    # Run the search view validation
    search_valid = check_search_view_fields(module_dir)
    
    # Final result
    print("\n" + "="*50)
    if search_valid:
        print("🎉 ALL FIELD REFERENCES VALID!")
        print("✅ No unsearchable fields found in search views")
        return True
    else:
        print("❌ FIELD REFERENCE ISSUES FOUND!")
        print("🔧 Fix required before deployment")
        return False

if __name__ == "__main__":
    main()
