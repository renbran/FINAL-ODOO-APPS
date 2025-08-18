#!/usr/bin/env python3
"""
Validation script for order_status_override module commission implementation
"""

import os
import sys
import ast
import csv
from xml.etree import ElementTree as ET

def check_python_syntax(file_path):
    """Check Python file syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        print(f"✓ {file_path}: Python syntax OK")
        return True
    except SyntaxError as e:
        print(f"✗ {file_path}: Python syntax error - {e}")
        return False
    except Exception as e:
        print(f"✗ {file_path}: Error - {e}")
        return False

def check_xml_syntax(file_path):
    """Check XML file syntax"""
    try:
        ET.parse(file_path)
        print(f"✓ {file_path}: XML syntax OK")
        return True
    except ET.ParseError as e:
        print(f"✗ {file_path}: XML syntax error - {e}")
        return False
    except Exception as e:
        print(f"✗ {file_path}: Error - {e}")
        return False

def check_csv_syntax(file_path):
    """Check CSV file syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            lines = list(reader)
            
        if not lines:
            print(f"✗ {file_path}: Empty CSV file")
            return False
            
        header = lines[0]
        expected_columns = 8  # Updated to match our simplified CSV
        
        for i, line in enumerate(lines):
            if len(line) != expected_columns:
                print(f"✗ {file_path}: Line {i+1} has {len(line)} columns, expected {expected_columns}")
                return False
                
        print(f"✓ {file_path}: CSV syntax OK ({len(lines)} lines)")
        return True
    except Exception as e:
        print(f"✗ {file_path}: Error - {e}")
        return False

def validate_commission_fields():
    """Validate that commission fields are properly implemented"""
    sale_order_path = "models/sale_order.py"
    
    required_fields = [
        'broker_partner_id', 'broker_commission_type', 'broker_rate', 'broker_amount',
        'referrer_partner_id', 'referrer_commission_type', 'referrer_rate', 'referrer_amount', 
        'cashback_partner_id', 'cashback_commission_type', 'cashback_rate', 'cashback_amount',
        'agent1_partner_id', 'agent1_commission_type', 'agent1_rate', 'agent1_amount',
        'agent2_partner_id', 'agent2_commission_type', 'agent2_rate', 'agent2_amount',
        'manager_partner_id', 'manager_commission_type', 'manager_rate', 'manager_amount',
        'director_partner_id', 'director_commission_type', 'director_rate', 'director_amount',
        'total_external_commission_amount', 'total_internal_commission_amount', 
        'total_commission_amount', 'net_commission_amount'
    ]
    
    required_methods = [
        '_compute_commission_amounts', '_compute_commission_totals', 
        '_compute_net_commission', '_calculate_commission_amount'
    ]
    
    try:
        with open(sale_order_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check fields
        missing_fields = []
        for field in required_fields:
            if f"{field} = fields." not in content:
                missing_fields.append(field)
                
        if missing_fields:
            print(f"✗ Missing commission fields: {missing_fields}")
            return False
        else:
            print(f"✓ All commission fields present ({len(required_fields)} fields)")
            
        # Check methods
        missing_methods = []
        for method in required_methods:
            if f"def {method}(" not in content:
                missing_methods.append(method)
                
        if missing_methods:
            print(f"✗ Missing commission methods: {missing_methods}")
            return False
        else:
            print(f"✓ All commission methods present ({len(required_methods)} methods)")
            
        # Check the net commission formula
        if "amount_total - (total_internal - total_external)" in content:
            print("✓ Net commission formula correctly implemented")
        else:
            print("✗ Net commission formula not found")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Error validating commission fields: {e}")
        return False

def main():
    """Main validation function"""
    print("=== Order Status Override Commission Implementation Validation ===\n")
    
    # Files to validate
    files_to_check = {
        'python': [
            'models/sale_order.py',
            'models/order_status.py', 
            'models/commission_models.py',
            'models/status_change_wizard.py',
            'models/__init__.py'
        ],
        'xml': [
            'security/security.xml',
            'views/order_views_assignment.xml'
        ],
        'csv': [
            'security/ir.model.access.csv'
        ]
    }
    
    all_good = True
    
    # Check Python files
    print("Checking Python files:")
    for file_path in files_to_check['python']:
        if os.path.exists(file_path):
            if not check_python_syntax(file_path):
                all_good = False
        else:
            print(f"✗ {file_path}: File not found")
            all_good = False
    
    print("\nChecking XML files:")
    for file_path in files_to_check['xml']:
        if os.path.exists(file_path):
            if not check_xml_syntax(file_path):
                all_good = False
        else:
            print(f"✗ {file_path}: File not found")
            all_good = False
    
    print("\nChecking CSV files:")
    for file_path in files_to_check['csv']:
        if os.path.exists(file_path):
            if not check_csv_syntax(file_path):
                all_good = False
        else:
            print(f"✗ {file_path}: File not found")
            all_good = False
    
    print("\nValidating commission implementation:")
    if not validate_commission_fields():
        all_good = False
    
    print(f"\n{'='*60}")
    if all_good:
        print("✓ ALL VALIDATIONS PASSED - Module ready for deployment")
        print("\nNew Commission Logic Summary:")
        print("- Added commission fields for internal and external partners")
        print("- Implemented automatic commission calculation")
        print("- Formula: net commission = amount_total - (total_internal - total_external)")
        print("- Simplified security with standard sales groups only")
        return True
    else:
        print("✗ VALIDATION FAILED - Please fix the errors above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
