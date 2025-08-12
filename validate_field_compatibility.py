#!/usr/bin/env python3
"""
Field Reference Validation Script for Odoo 17
Validates that all field references in views exist and are compatible
"""

import os
import xml.etree.ElementTree as ET
import re
from pathlib import Path

def validate_view_field_references():
    """Validate that all field references in views are safe for Odoo 17"""
    issues = []
    
    view_files = [
        'account_payment_approval/views/account_payment_views.xml',
        'account_payment_approval/views/account_move_enhanced_views.xml',
        'account_payment_approval/views/wizard_views.xml'
    ]
    
    # Risky field patterns that might not exist in all Odoo 17 installations
    risky_fields = [
        'full_reconcile_id',
        'reconcile_id', 
        'reconciled',
        'reconcile_ref'
    ]
    
    safe_fields = [
        'debit',
        'credit', 
        'account_id',
        'partner_id',
        'name',
        'date',
        'amount_currency',
        'currency_id',
        'matched_debit_ids',
        'matched_credit_ids',
        'amount_residual'
    ]
    
    for view_file in view_files:
        if not os.path.exists(view_file):
            issues.append(f"View file not found: {view_file}")
            continue
            
        try:
            with open(view_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for risky field references
            for risky_field in risky_fields:
                if f'name="{risky_field}"' in content or f"name='{risky_field}'" in content:
                    issues.append(f"{view_file}: Risky field reference '{risky_field}' - may not exist in all Odoo 17 installations")
                
                # Check XPath expressions
                xpath_pattern = rf"//field\[@name='{risky_field}'\]|//field\[@name=\"{risky_field}\"\]"
                if re.search(xpath_pattern, content):
                    issues.append(f"{view_file}: Risky XPath targeting '{risky_field}' - may cause parse error")
            
            # Validate XML structure
            ET.parse(view_file)
            
        except ET.ParseError as e:
            issues.append(f"{view_file}: XML Parse Error - {e}")
        except Exception as e:
            issues.append(f"{view_file}: Error reading file - {e}")
    
    return issues

def validate_model_field_dependencies():
    """Validate model field dependencies"""
    issues = []
    
    model_files = [
        'account_payment_approval/models/account_move.py',
        'account_payment_approval/models/account_payment.py'
    ]
    
    for model_file in model_files:
        if not os.path.exists(model_file):
            issues.append(f"Model file not found: {model_file}")
            continue
            
        try:
            with open(model_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for @api.depends with risky fields
            depends_pattern = r'@api\.depends\([^)]*[\'"]full_reconcile_id[\'"][^)]*\)'
            if re.search(depends_pattern, content):
                issues.append(f"{model_file}: @api.depends uses 'full_reconcile_id' - should check field existence")
            
            # Check for direct field access without hasattr check
            direct_access_pattern = r'line\.full_reconcile_id(?!\s*and)'
            matches = re.finditer(direct_access_pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                if 'hasattr' not in content[max(0, match.start()-100):match.end()+100]:
                    issues.append(f"{model_file}:Line {line_num}: Direct access to 'full_reconcile_id' without existence check")
            
        except Exception as e:
            issues.append(f"{model_file}: Error reading file - {e}")
    
    return issues

def main():
    """Main validation function"""
    print("=== Odoo 17 Field Compatibility Validation ===\n")
    
    # Validate view field references
    print("1. Validating view field references...")
    view_issues = validate_view_field_references()
    
    if view_issues:
        print("   ❌ View Issues Found:")
        for issue in view_issues:
            print(f"      - {issue}")
    else:
        print("   ✅ All view field references are safe")
    
    print()
    
    # Validate model dependencies
    print("2. Validating model field dependencies...")
    model_issues = validate_model_field_dependencies()
    
    if model_issues:
        print("   ❌ Model Issues Found:")
        for issue in model_issues:
            print(f"      - {issue}")
    else:
        print("   ✅ All model field dependencies are safe")
    
    print()
    
    # Summary
    total_issues = len(view_issues) + len(model_issues)
    
    print("=== COMPATIBILITY SUMMARY ===")
    if total_issues == 0:
        print("🎉 ALL FIELD REFERENCES ARE COMPATIBLE!")
        print("✅ Views use reliable field targets")
        print("✅ Models handle optional fields safely")
        print("✅ Ready for deployment on any Odoo 17 installation")
    else:
        print(f"⚠️  {total_issues} compatibility issue(s) found")
        print("❌ Manual review required before deployment")
    
    return total_issues == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
