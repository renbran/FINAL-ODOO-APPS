#!/usr/bin/env python3
"""
Comprehensive validation script for account_payment_approval views and model alignment
Checks for field references, method existence, and view integrity
"""

import os
import sys
import xml.etree.ElementTree as ET
import re
from pathlib import Path

def validate_payment_module():
    """Validate the entire payment approval module for field and method consistency"""
    
    print("=== COMPREHENSIVE PAYMENT MODULE VALIDATION ===")
    
    module_path = Path("account_payment_approval")
    if not module_path.exists():
        print("❌ Module directory not found!")
        return False
    
    # 1. Check model fields
    model_file = module_path / "models" / "account_payment.py"
    if not model_file.exists():
        print("❌ Model file not found!")
        return False
    
    print("\n1. EXTRACTING MODEL FIELDS...")
    model_fields = extract_model_fields(model_file)
    print(f"   Found {len(model_fields)} fields in model")
    
    # 2. Check view field references
    views_file = module_path / "views" / "account_payment_views.xml"
    if not views_file.exists():
        print("❌ Views file not found!")
        return False
    
    print("\n2. CHECKING VIEW FIELD REFERENCES...")
    view_issues = check_view_fields(views_file, model_fields)
    
    # 3. Check model methods
    print("\n3. CHECKING MODEL METHODS...")
    model_methods = extract_model_methods(model_file)
    method_issues = check_view_methods(views_file, model_methods)
    
    # 4. Check XML syntax
    print("\n4. VALIDATING XML SYNTAX...")
    xml_issues = validate_xml_syntax(views_file)
    
    # 5. Summary
    print("\n=== VALIDATION SUMMARY ===")
    total_issues = len(view_issues) + len(method_issues) + len(xml_issues)
    
    if total_issues == 0:
        print("✅ ALL CHECKS PASSED - Module is valid!")
        return True
    else:
        print(f"❌ Found {total_issues} issues:")
        
        if view_issues:
            print("\nFIELD ISSUES:")
            for issue in view_issues:
                print(f"   - {issue}")
        
        if method_issues:
            print("\nMETHOD ISSUES:")
            for issue in method_issues:
                print(f"   - {issue}")
        
        if xml_issues:
            print("\nXML ISSUES:")
            for issue in xml_issues:
                print(f"   - {issue}")
        
        return False

def extract_model_fields(model_file):
    """Extract all field definitions from the model"""
    fields = set()
    
    try:
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find field definitions
        field_pattern = r'(\w+)\s*=\s*fields\.'
        matches = re.findall(field_pattern, content)
        fields.update(matches)
        
        print(f"   Model fields: {sorted(fields)}")
        
    except Exception as e:
        print(f"   Error reading model: {e}")
    
    return fields

def extract_model_methods(model_file):
    """Extract all method definitions from the model"""
    methods = set()
    
    try:
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find method definitions
        method_pattern = r'def\s+(\w+)\s*\('
        matches = re.findall(method_pattern, content)
        methods.update(matches)
        
        print(f"   Found {len(methods)} methods in model")
        
    except Exception as e:
        print(f"   Error reading model methods: {e}")
    
    return methods

def check_view_fields(views_file, model_fields):
    """Check if all fields referenced in views exist in model"""
    issues = []
    
    try:
        tree = ET.parse(views_file)
        root = tree.getroot()
        
        # Find all field references
        field_elements = root.findall('.//field[@name]')
        view_fields = set()
        
        for field_elem in field_elements:
            field_name = field_elem.get('name')
            if field_name:
                view_fields.add(field_name)
        
        print(f"   View fields: {sorted(view_fields)}")
        
        # Check for missing fields
        missing_fields = view_fields - model_fields
        for field in missing_fields:
            # Skip standard Odoo fields that should exist
            if field not in ['state', 'name', 'amount', 'partner_id', 'journal_id', 'date', 'ref']:
                issues.append(f"Field '{field}' referenced in view but not found in model")
        
        # Check invisible attributes for field references
        for elem in root.iter():
            invisible_attr = elem.get('invisible')
            if invisible_attr:
                # Extract field names from invisible conditions
                field_refs = re.findall(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:==|!=|=|in|not in)", invisible_attr)
                for field_ref in field_refs:
                    if field_ref not in model_fields and field_ref not in ['True', 'False']:
                        if field_ref not in ['state', 'name', 'amount', 'partner_id', 'journal_id', 'date', 'ref']:
                            issues.append(f"Field '{field_ref}' in invisible condition but not found in model")
        
    except Exception as e:
        issues.append(f"Error parsing views: {e}")
    
    return issues

def check_view_methods(views_file, model_methods):
    """Check if all methods referenced in views exist in model"""
    issues = []
    
    try:
        tree = ET.parse(views_file)
        root = tree.getroot()
        
        # Find all button actions
        button_elements = root.findall('.//button[@name]')
        view_methods = set()
        
        for button_elem in button_elements:
            method_name = button_elem.get('name')
            if method_name and button_elem.get('type') == 'object':
                view_methods.add(method_name)
        
        print(f"   View methods: {sorted(view_methods)}")
        
        # Check for missing methods
        missing_methods = view_methods - model_methods
        for method in missing_methods:
            issues.append(f"Method '{method}' referenced in view but not found in model")
        
    except Exception as e:
        issues.append(f"Error checking view methods: {e}")
    
    return issues

def validate_xml_syntax(xml_file):
    """Validate XML syntax"""
    issues = []
    
    try:
        ET.parse(xml_file)
        print("   ✅ XML syntax is valid")
    except ET.ParseError as e:
        issues.append(f"XML Parse Error: {e}")
    except Exception as e:
        issues.append(f"XML Validation Error: {e}")
    
    return issues

if __name__ == "__main__":
    success = validate_payment_module()
    sys.exit(0 if success else 1)
