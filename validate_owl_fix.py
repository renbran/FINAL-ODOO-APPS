#!/usr/bin/env python3
"""
OWL Error Fix Validation
Tests the reconciled_invoice_ids field fix
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_field_references(xml_file):
    """Check for field references in XML and verify they're properly defined"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Find all field references in invisible conditions
        invisible_fields = []
        for elem in root.iter():
            if 'invisible' in elem.attrib:
                invisible_condition = elem.attrib['invisible']
                if 'reconciled_invoice_ids' in invisible_condition:
                    invisible_fields.append(invisible_condition)
        
        # Find all field declarations
        declared_fields = []
        for field in root.findall(".//field"):
            if 'name' in field.attrib:
                declared_fields.append(field.attrib['name'])
        
        print(f"  📋 Invisible conditions using reconciled_invoice_ids: {len(invisible_fields)}")
        for condition in invisible_fields:
            print(f"      - {condition}")
        
        print(f"  📋 Field declarations found: {len(declared_fields)}")
        
        # Check if reconciled_invoice_ids is declared
        required_fields = ['reconciled_invoice_ids', 'reconciled_bill_ids']
        missing_fields = [field for field in required_fields if field not in declared_fields]
        
        if missing_fields:
            return False, f"Missing field declarations: {missing_fields}"
        
        return True, "All required fields are declared"
        
    except Exception as e:
        return False, f"Error checking field references: {e}"

def validate_model_fields(py_file):
    """Check if the model has the required field definitions"""
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for field definitions
        required_fields = ['reconciled_invoice_ids', 'reconciled_bill_ids']
        found_fields = []
        
        for field in required_fields:
            if f"{field} = fields." in content:
                found_fields.append(field)
        
        print(f"  📋 Model field definitions found: {found_fields}")
        
        # Check for compute methods
        compute_methods = ['_compute_reconciled_invoices', '_compute_reconciled_bills']
        found_methods = []
        
        for method in compute_methods:
            if f"def {method}(" in content:
                found_methods.append(method)
        
        print(f"  📋 Compute methods found: {found_methods}")
        
        missing_fields = [field for field in required_fields if field not in found_fields]
        missing_methods = [method for method in compute_methods if method not in found_methods]
        
        if missing_fields or missing_methods:
            return False, f"Missing fields: {missing_fields}, Missing methods: {missing_methods}"
        
        return True, "All model components are present"
        
    except Exception as e:
        return False, f"Error checking model: {e}"

def main():
    """Main validation function"""
    print("🔍 OWL Error Fix Validation\n")
    print("Issue: EvalError - Name 'reconciled_invoice_ids' is not defined")
    print("Fix: Added missing field definitions and compute methods\n")
    
    base_path = Path(__file__).parent
    module_path = base_path / "account_payment_final"
    
    # Files to validate
    files_to_check = {
        "Payment Views": module_path / "views" / "account_payment_views.xml",
        "Payment Model": module_path / "models" / "account_payment.py",
    }
    
    all_valid = True
    
    for name, file_path in files_to_check.items():
        print(f"📄 Checking {name}:")
        
        if not file_path.exists():
            print(f"  ❌ File not found: {file_path}")
            all_valid = False
            continue
        
        if "views" in str(file_path):
            valid, message = validate_field_references(file_path)
            if valid:
                print(f"  ✅ Field References: {message}")
            else:
                print(f"  ❌ Field References: {message}")
                all_valid = False
        
        elif "models" in str(file_path):
            valid, message = validate_model_fields(file_path)
            if valid:
                print(f"  ✅ Model Fields: {message}")
            else:
                print(f"  ❌ Model Fields: {message}")
                all_valid = False
        
        print()
    
    print("="*50)
    if all_valid:
        print("🎉 OWL Error Fix Validation Passed!")
        print("\n📋 Summary of fixes:")
        print("✅ Added reconciled_invoice_ids field definition")
        print("✅ Added reconciled_bill_ids field definition") 
        print("✅ Added _compute_reconciled_invoices method")
        print("✅ Added _compute_reconciled_bills method")
        print("✅ Added hidden fields to XML view")
        print("\n🚀 The OWL evaluation error should now be resolved!")
    else:
        print("❌ Some validations failed!")
    
    print("\n💡 What this fixes:")
    print("- Prevents 'reconciled_invoice_ids' not defined errors")
    print("- Enables proper invoice reconciliation tracking")
    print("- Allows smart buttons to show/hide correctly")
    print("- Resolves OWL lifecycle evaluation errors")

if __name__ == "__main__":
    main()
