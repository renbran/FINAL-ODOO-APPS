#!/usr/bin/env python3
"""
Field Reference Validator - Check for missing field references
"""

import os
import xml.etree.ElementTree as ET
import ast
import re

def check_field_references(base_path):
    """Check if all field references in views exist in models"""
    print("🔍 FIELD REFERENCE VALIDATION")
    print("-" * 40)
    
    issues = []
    
    # Get all field definitions from Python files
    model_fields = {}
    models_path = os.path.join(base_path, 'models')
    
    if os.path.exists(models_path):
        for file in os.listdir(models_path):
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(models_path, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract class names and field definitions
                    class_pattern = r'class\s+(\w+)\(.*\):'
                    field_pattern = r'(\w+)\s*=\s*fields\.'
                    
                    current_class = None
                    for line in content.split('\n'):
                        class_match = re.search(class_pattern, line)
                        if class_match:
                            current_class = class_match.group(1)
                            if current_class not in model_fields:
                                model_fields[current_class] = []
                        
                        field_match = re.search(field_pattern, line)
                        if field_match and current_class:
                            field_name = field_match.group(1)
                            model_fields[current_class].append(field_name)
                            print(f"✅ Found field: {current_class}.{field_name}")
                
                except Exception as e:
                    print(f"❌ Error reading {file}: {e}")
    
    # Check XML view files for field references
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(root, file)
                try:
                    tree = ET.parse(file_path)
                    for elem in tree.iter():
                        if elem.tag == 'field' and 'name' in elem.attrib:
                            field_name = elem.attrib['name']
                            # Check if field exists in any model (simplified check)
                            field_found = False
                            for model_class, fields in model_fields.items():
                                if field_name in fields:
                                    field_found = True
                                    break
                            
                            # Special case for common Odoo fields
                            common_fields = ['state', 'name', 'id', 'create_date', 'write_date', 'create_uid', 'write_uid']
                            if field_name in common_fields:
                                field_found = True
                            
                            if not field_found and not field_name.startswith('__'):
                                issues.append(f"Field '{field_name}' referenced in {file} but not found in models")
                                print(f"⚠️  Field '{field_name}' referenced in {file} but not found in models")
                
                except Exception as e:
                    print(f"❌ Error parsing XML {file}: {e}")
    
    return issues

def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    print("🔍 FIELD REFERENCE VALIDATION")
    print("=" * 50)
    print(f"Module: {os.path.basename(base_path)}")
    print("=" * 50)
    
    issues = check_field_references(base_path)
    
    print("\n" + "=" * 50)
    print("🎯 VALIDATION RESULTS")
    print("=" * 50)
    
    if not issues:
        print("🎉 ALL FIELD REFERENCES ARE VALID!")
        print("✅ No missing field references found")
        return True
    else:
        print(f"⚠️  FOUND {len(issues)} FIELD REFERENCE ISSUES:")
        for issue in issues:
            print(f"  • {issue}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
