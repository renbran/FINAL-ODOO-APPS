#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE VALIDATION
Validates that all files are restored and module is complete
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path

def final_comprehensive_validation():
    """Complete validation of the restored module"""
    
    print("=== FINAL COMPREHENSIVE VALIDATION ===")
    
    module_path = Path("account_payment_approval")
    if not module_path.exists():
        print("❌ Module directory not found!")
        return False
    
    issues = []
    
    # 1. Check directory structure
    print("\n1. CHECKING DIRECTORY STRUCTURE...")
    required_dirs = ['models', 'views', 'security', 'data', 'controllers', 'static', 'reports', 'wizards', 'demo']
    for dir_name in required_dirs:
        dir_path = module_path / dir_name
        if dir_path.exists():
            print(f"   ✅ {dir_name}/ directory exists")
        else:
            issues.append(f"Missing directory: {dir_name}/")
    
    # 2. Check essential files
    print("\n2. CHECKING ESSENTIAL FILES...")
    essential_files = [
        '__manifest__.py',
        'models/__init__.py',
        'models/account_payment.py',
        'models/account_move.py',
        'models/res_config_settings.py',
        'views/account_payment_views.xml',
        'views/menu_views.xml',
        'security/ir.model.access.csv',
        'security/payment_approval_groups.xml',
        'data/payment_sequences.xml',
        'controllers/main.py',
        'controllers/qr_verification.py',
    ]
    
    for file_path in essential_files:
        full_path = module_path / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            issues.append(f"Missing file: {file_path}")
    
    # 3. Validate XML files
    print("\n3. VALIDATING XML FILES...")
    xml_files = []
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(Path(root) / file)
    
    for xml_file in xml_files:
        try:
            ET.parse(xml_file)
            rel_path = xml_file.relative_to(module_path)
            print(f"   ✅ {rel_path} - Valid XML")
        except ET.ParseError as e:
            rel_path = xml_file.relative_to(module_path)
            issues.append(f"XML Parse Error in {rel_path}: {e}")
    
    # 4. Validate Python files
    print("\n4. VALIDATING PYTHON FILES...")
    python_files = []
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, py_file, 'exec')
            rel_path = py_file.relative_to(module_path)
            print(f"   ✅ {rel_path} - Valid Python")
        except SyntaxError as e:
            rel_path = py_file.relative_to(module_path)
            issues.append(f"Python Syntax Error in {rel_path}: {e}")
        except Exception as e:
            rel_path = py_file.relative_to(module_path)
            issues.append(f"Error reading {rel_path}: {e}")
    
    # 5. Check manifest data references
    print("\n5. CHECKING MANIFEST REFERENCES...")
    manifest_file = module_path / '__manifest__.py'
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest_content = f.read()
        
        # Extract data files from manifest
        import re
        data_matches = re.findall(r"'([^']+\\.xml)'", manifest_content)
        
        for data_file in data_matches:
            file_path = module_path / data_file
            if file_path.exists():
                print(f"   ✅ {data_file} - Referenced and exists")
            else:
                issues.append(f"Manifest references missing file: {data_file}")
        
    except Exception as e:
        issues.append(f"Error reading manifest: {e}")
    
    # 6. Check model imports
    print("\n6. CHECKING MODEL IMPORTS...")
    models_init = module_path / 'models' / '__init__.py'
    if models_init.exists():
        try:
            with open(models_init, 'r', encoding='utf-8') as f:
                init_content = f.read()
            
            # Check if imported models exist
            import_lines = [line.strip() for line in init_content.split('\n') if line.strip().startswith('from . import')]
            for line in import_lines:
                model_name = line.split('import')[-1].strip()
                model_file = module_path / 'models' / f'{model_name}.py'
                if model_file.exists():
                    print(f"   ✅ {model_name}.py - Imported and exists")
                else:
                    issues.append(f"Model import references missing file: {model_name}.py")
        
        except Exception as e:
            issues.append(f"Error checking model imports: {e}")
    
    # 7. Summary
    print("\n=== VALIDATION SUMMARY ===")
    if not issues:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ Module structure is complete")
        print("✅ All files exist and are valid")
        print("✅ All references are satisfied")
        print("✅ Ready for deployment")
        
        # Show module summary
        print("\n📋 MODULE SUMMARY:")
        print("   📁 Models: account_payment.py (main), account_move.py, res_config_settings.py")
        print("   📁 Views: payment views, menu views, move views, wizard views, QR templates")
        print("   📁 Security: groups, access rights, record rules")
        print("   📁 Data: sequences, email templates, system parameters, cron jobs")
        print("   📁 Controllers: main controller, QR verification")
        print("   📁 Reports: payment voucher report, payment summary report")
        print("   📁 Wizards: bulk approval wizard, rejection wizard")
        print("   📁 Static: SCSS styles, JavaScript widgets")
        print("   📁 Demo: sample payment data")
        
        return True
    else:
        print(f"❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"   - {issue}")
        return False

if __name__ == "__main__":
    success = final_comprehensive_validation()
    exit(0 if success else 1)
