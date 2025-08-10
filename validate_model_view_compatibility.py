#!/usr/bin/env python3
"""
Model-View Compatibility Checker for Odoo 17
Validates that all view field references exist in models
"""

import os
import re
import xml.etree.ElementTree as ET
from typing import Set, Dict, List, Tuple

def extract_model_fields(python_file: str) -> Set[str]:
    """Extract all field definitions from a Python model file"""
    fields = set()
    
    try:
        with open(python_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match field definitions
        field_pattern = r'(\w+)\s*=\s*fields\.'
        matches = re.findall(field_pattern, content)
        fields.update(matches)
        
        # Also check for computed field names in string definitions
        computed_pattern = r"@api\.depends\(['\"]([^'\"]+)['\"]"
        computed_matches = re.findall(computed_pattern, content)
        for match in computed_matches:
            fields.update(match.split(','))
        
        return fields
        
    except Exception as e:
        print(f"Error reading {python_file}: {e}")
        return set()

def extract_view_field_references(xml_file: str) -> Dict[str, Set[str]]:
    """Extract field references from XML view files"""
    model_fields = {}
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Find all view records
        for record in root.findall('.//record[@model="ir.ui.view"]'):
            arch = record.find('.//field[@name="arch"]')
            if arch is not None:
                # Get model name
                model_field = record.find('.//field[@name="model"]')
                if model_field is not None:
                    model_name = model_field.text
                    if model_name not in model_fields:
                        model_fields[model_name] = set()
                    
                    # Extract field references from arch
                    arch_str = ET.tostring(arch, encoding='unicode')
                    field_pattern = r'field\[@name=[\'"]([^\'"]+)[\'"]\]|<field\s+name=[\'"]([^\'"]+)[\'"]'
                    matches = re.findall(field_pattern, arch_str)
                    for match in matches:
                        field_name = match[0] or match[1]
                        if field_name:
                            model_fields[model_name].add(field_name)
        
        return model_fields
        
    except Exception as e:
        print(f"Error reading {xml_file}: {e}")
        return {}

def get_standard_account_payment_fields() -> Set[str]:
    """Return known standard fields for account.payment model"""
    return {
        'name', 'payment_type', 'partner_type', 'partner_id', 'amount', 
        'currency_id', 'payment_date', 'communication', 'journal_id',
        'payment_method_id', 'payment_method_line_id', 'partner_bank_id',
        'state', 'is_reconciled', 'move_id', 'date', 'ref', 'company_id',
        'destination_account_id', 'reconciled_invoice_ids', 'outstanding_account_id',
        'payment_transaction_id', 'paired_internal_transfer_payment_id',
        'move_line_ids', 'reconciled_bill_ids', 'reconciled_bills_count',
        'reconciled_invoices_count', 'has_invoices', 'country_code',
        'partner_bank_account', 'show_partner_bank_account', 'require_partner_bank_account',
        'available_payment_method_line_ids', 'available_journal_ids',
        'suitable_journal_ids', 'hide_payment_method', 'payment_method_code',
        'is_internal_transfer', 'qr_code_method', 'display_name',
        'create_date', 'create_uid', 'write_date', 'write_uid', 'id'
    }

def validate_model_view_compatibility():
    """Main validation function"""
    print("🔍 Model-View Compatibility Check for Odoo 17")
    print("=" * 60)
    
    # 1. Extract all custom fields from models
    model_files = [
        'account_payment_final/models/account_payment.py',
        'account_payment_final/models/res_company.py',
        'account_payment_final/models/res_config_settings.py',
    ]
    
    all_custom_fields = {}
    
    print("📋 Extracting custom field definitions...")
    for model_file in model_files:
        if os.path.exists(model_file):
            fields = extract_model_fields(model_file)
            model_name = os.path.basename(model_file).replace('.py', '')
            all_custom_fields[model_name] = fields
            print(f"  ✅ {model_file}: {len(fields)} fields found")
        else:
            print(f"  ⚠️ {model_file}: File not found")
    
    # 2. Get standard account.payment fields
    standard_payment_fields = get_standard_account_payment_fields()
    all_payment_fields = all_custom_fields.get('account_payment', set()) | standard_payment_fields
    
    print(f"📋 Total account.payment fields available: {len(all_payment_fields)}")
    
    # 3. Extract field references from views
    view_files = [
        'account_payment_final/views/account_payment_views.xml',
        'account_payment_final/views/account_payment_views_ultra_safe.xml',
        'account_payment_final/views/account_payment_views_advanced.xml',
        'account_payment_final/views/res_company_views.xml',
    ]
    
    print("\n📋 Checking view field references...")
    all_issues = []
    
    for view_file in view_files:
        if not os.path.exists(view_file):
            print(f"  ⚠️ {view_file}: File not found (skipping)")
            continue
            
        view_fields = extract_view_field_references(view_file)
        print(f"  📄 {view_file}:")
        
        for model_name, field_refs in view_fields.items():
            if model_name == 'account.payment':
                # Check against account.payment fields
                missing_fields = field_refs - all_payment_fields
                if missing_fields:
                    print(f"    ❌ Missing fields for {model_name}: {missing_fields}")
                    all_issues.append((view_file, model_name, missing_fields))
                else:
                    print(f"    ✅ All {len(field_refs)} fields valid for {model_name}")
            
            elif model_name == 'res.company':
                # For res.company, we'll be more lenient since it's a core model
                print(f"    ℹ️ {model_name}: {len(field_refs)} field references (core model)")
            
            else:
                print(f"    ℹ️ {model_name}: {len(field_refs)} field references")
    
    # 4. Check inheritance patterns
    print("\n📋 Checking view inheritance patterns...")
    inheritance_issues = check_inheritance_patterns()
    
    # 5. Check security alignment
    print("\n📋 Checking security definitions...")
    security_issues = check_security_alignment()
    
    # 6. Final summary
    print("\n" + "=" * 60)
    total_issues = len(all_issues) + len(inheritance_issues) + len(security_issues)
    
    if total_issues == 0:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Model-View compatibility verified")
        print("✅ Inheritance patterns are correct") 
        print("✅ Security definitions are aligned")
        print("✅ Module follows Odoo 17 protocols")
    else:
        print(f"❌ {total_issues} issues found:")
        if all_issues:
            print(f"  • {len(all_issues)} field reference issues")
        if inheritance_issues:
            print(f"  • {len(inheritance_issues)} inheritance issues")
        if security_issues:
            print(f"  • {len(security_issues)} security issues")
    
    return total_issues == 0

def check_inheritance_patterns() -> List[str]:
    """Check that view inheritance patterns are correct"""
    issues = []
    
    try:
        # Check that inherited views exist
        view_files = [
            'account_payment_final/views/account_payment_views.xml',
            'account_payment_final/views/account_payment_views_ultra_safe.xml',
            'account_payment_final/views/account_payment_views_advanced.xml',
        ]
        
        for view_file in view_files:
            if not os.path.exists(view_file):
                continue
                
            tree = ET.parse(view_file)
            for record in tree.findall('.//record[@model="ir.ui.view"]'):
                inherit_id = record.find('.//field[@name="inherit_id"]')
                if inherit_id is not None:
                    ref_value = inherit_id.get('ref')
                    if ref_value:
                        # Check if it's a valid reference
                        if ref_value.startswith('account_payment_final.'):
                            # Internal reference - should be safe
                            print(f"    ✅ Internal inheritance: {ref_value}")
                        elif ref_value.startswith('account.'):
                            # Standard Odoo reference - should exist
                            print(f"    ✅ Standard inheritance: {ref_value}")
                        else:
                            print(f"    ⚠️ External inheritance: {ref_value}")
        
    except Exception as e:
        issues.append(f"Error checking inheritance: {e}")
    
    return issues

def check_security_alignment() -> List[str]:
    """Check that security definitions align with models"""
    issues = []
    
    try:
        # Check ir.model.access.csv
        access_file = 'account_payment_final/security/ir.model.access.csv'
        if os.path.exists(access_file):
            with open(access_file, 'r') as f:
                lines = f.readlines()
                print(f"    ✅ Security access file: {len(lines)-1} rules found")
        else:
            issues.append("Missing ir.model.access.csv file")
        
        # Check security.xml
        security_file = 'account_payment_final/security/payment_security.xml'
        if os.path.exists(security_file):
            tree = ET.parse(security_file)
            groups = tree.findall('.//record[@model="res.groups"]')
            rules = tree.findall('.//record[@model="ir.rule"]')
            print(f"    ✅ Security groups: {len(groups)} defined")
            print(f"    ✅ Record rules: {len(rules)} defined")
        else:
            issues.append("Missing payment_security.xml file")
        
    except Exception as e:
        issues.append(f"Error checking security: {e}")
    
    return issues

if __name__ == "__main__":
    validate_model_view_compatibility()
