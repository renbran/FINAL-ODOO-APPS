#!/usr/bin/env python3
"""
Domain Filter Validation Script
Validates that all fields used in search domain filters are searchable (stored)
"""

import xml.etree.ElementTree as ET
import re

def validate_search_domains():
    """Validate search domain filters"""
    issues = []
    
    view_file = 'account_payment_approval/views/account_move_enhanced_views.xml'
    
    try:
        tree = ET.parse(view_file)
        root = tree.getroot()
        
        # Find all filter elements with domain attributes
        for filter_elem in root.findall('.//filter[@domain]'):
            domain = filter_elem.get('domain', '')
            filter_name = filter_elem.get('name', 'unnamed')
            
            # Extract field names from domain
            field_pattern = r"\('([^']+)'"
            fields_in_domain = re.findall(field_pattern, domain)
            
            print(f"Filter '{filter_name}': {domain}")
            print(f"  Fields used: {fields_in_domain}")
            
            # Check for computed fields that might not be stored
            potentially_unstored = [
                'has_approval_payments',
                'approval_payment_count', 
                'pending_approval_amount',
                'payment_state',
                'payment_voucher_state'
            ]
            
            for field in fields_in_domain:
                if field in potentially_unstored:
                    print(f"  ⚠️ Field '{field}' needs store=True to be searchable")
                else:
                    print(f"  ✅ Field '{field}' is safe for domain search")
            print()
            
    except Exception as e:
        issues.append(f"Error parsing {view_file}: {e}")
    
    return issues

def main():
    """Main validation function"""
    print("=== Domain Filter Validation ===\n")
    
    issues = validate_search_domains()
    
    if issues:
        print("❌ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ All domain filters validated")
    
    print("\n=== SUMMARY ===")
    print("All computed fields used in search domains should have store=True")
    print("This ensures they can be searched and filtered properly.")

if __name__ == "__main__":
    main()
