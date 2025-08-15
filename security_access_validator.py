#!/usr/bin/env python3
"""
Security Access Fix Validation Script
Specifically checks for missing model references in ir.model.access.csv
"""

import os
import csv
import ast

def extract_model_names_from_python_files():
    """Extract all _name declarations from Python model files"""
    models = []
    model_dir = "order_status_override/models"
    
    if not os.path.exists(model_dir):
        print(f"❌ Models directory not found: {model_dir}")
        return models
    
    for file_name in os.listdir(model_dir):
        if file_name.endswith('.py') and file_name != '__init__.py':
            file_path = os.path.join(model_dir, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for _name = 'model.name' patterns
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    if '_name =' in line and not line.strip().startswith('#'):
                        # Extract the model name
                        try:
                            # Simple extraction - look for quotes
                            if "'" in line:
                                start = line.find("'") + 1
                                end = line.find("'", start)
                                if start > 0 and end > start:
                                    model_name = line[start:end]
                                    models.append({
                                        'name': model_name,
                                        'file': file_name,
                                        'line': line_num
                                    })
                                    print(f"✅ Found model: {model_name} in {file_name}:{line_num}")
                        except Exception as e:
                            print(f"⚠️  Error parsing line in {file_name}:{line_num}: {str(e)}")
                            
            except Exception as e:
                print(f"❌ Error reading {file_path}: {str(e)}")
                
    return models

def validate_security_access():
    """Validate that all models in security file exist"""
    security_file = "order_status_override/security/ir.model.access.csv"
    
    if not os.path.exists(security_file):
        print(f"❌ Security file not found: {security_file}")
        return False
    
    print(f"📋 CHECKING SECURITY ACCESS FILE: {security_file}")
    
    # Get actual models from Python files
    actual_models = extract_model_names_from_python_files()
    actual_model_names = [model['name'] for model in actual_models]
    
    print(f"\n🔍 ACTUAL MODELS FOUND: {len(actual_models)}")
    for model in actual_models:
        print(f"   • {model['name']} ({model['file']})")
    
    # Read security access file
    issues = []
    try:
        with open(security_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, 2):  # Start at 2 to account for header
                model_id = row.get('model_id:id', '')
                
                # Extract model name from model_id (format: model_model_name)
                if model_id.startswith('model_'):
                    referenced_model = model_id[6:].replace('_', '.')  # Remove 'model_' prefix and convert underscores
                    
                    if referenced_model not in actual_model_names:
                        issues.append({
                            'row': row_num,
                            'model_id': model_id,
                            'referenced_model': referenced_model,
                            'access_name': row.get('name', 'Unknown')
                        })
                        print(f"❌ Row {row_num}: Model '{referenced_model}' (from {model_id}) not found in Python files")
                    else:
                        print(f"✅ Row {row_num}: Model '{referenced_model}' exists")
                else:
                    print(f"⚠️  Row {row_num}: Unusual model_id format: {model_id}")
                    
    except Exception as e:
        print(f"❌ Error reading security file: {str(e)}")
        return False
    
    return len(issues) == 0

def main():
    print("="*80)
    print("SECURITY ACCESS VALIDATION - MODEL REFERENCE CHECK")
    print("="*80)
    
    success = validate_security_access()
    
    print("\n" + "="*80)
    print("SECURITY VALIDATION SUMMARY") 
    print("="*80)
    
    if success:
        print("✅ ALL MODEL REFERENCES IN SECURITY FILE ARE VALID!")
        print("🚀 Module should load without model reference errors!")
    else:
        print("❌ MODEL REFERENCE ISSUES FOUND!")
        print("🔧 Fix the security file before attempting installation!")
    
    print("="*80)
    return success

if __name__ == "__main__":
    main()
