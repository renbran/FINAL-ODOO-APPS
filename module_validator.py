#!/usr/bin/env python3
"""
Odoo Module Validation Script
Validates module structure, dependencies, and key components
"""

import os
import ast
import sys
from pathlib import Path

def validate_module(module_path):
    """Validate an Odoo module structure"""
    print(f"🔍 Validating module: {module_path}")
    
    # Check manifest file
    manifest_path = os.path.join(module_path, '__manifest__.py')
    if not os.path.exists(manifest_path):
        print(f"❌ Missing __manifest__.py file")
        return False
    
    try:
        with open(manifest_path, 'r') as f:
            manifest_content = f.read()
        manifest_data = ast.literal_eval(manifest_content)
        print(f"✅ Manifest file syntax is valid")
        print(f"   📦 Name: {manifest_data.get('name', 'Unknown')}")
        print(f"   📋 Version: {manifest_data.get('version', 'Unknown')}")
        print(f"   👥 Author: {manifest_data.get('author', 'Unknown')}")
        
        # Check dependencies
        depends = manifest_data.get('depends', [])
        print(f"   🔗 Dependencies: {', '.join(depends) if depends else 'None'}")
        
        # Check data files
        data_files = manifest_data.get('data', [])
        print(f"   📁 Data files: {len(data_files)} file(s)")
        
        # Validate data files exist
        missing_files = []
        for file_path in data_files:
            full_path = os.path.join(module_path, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Missing data files: {', '.join(missing_files)}")
            return False
        else:
            print(f"✅ All {len(data_files)} data files exist")
            
    except Exception as e:
        print(f"❌ Error reading manifest: {e}")
        return False
    
    # Check key directories
    expected_dirs = ['views', 'models', 'security']
    for dir_name in expected_dirs:
        dir_path = os.path.join(module_path, dir_name)
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            print(f"✅ {dir_name}/ directory: {len(files)} file(s)")
        else:
            print(f"ℹ️  {dir_name}/ directory: Not found (optional)")
    
    # Check __init__.py files
    init_file = os.path.join(module_path, '__init__.py')
    if os.path.exists(init_file):
        print(f"✅ __init__.py exists")
    else:
        print(f"❌ Missing __init__.py file")
        return False
    
    print(f"🎉 Module validation completed successfully!")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python module_validator.py <module_path>")
        sys.exit(1)
    
    module_path = sys.argv[1]
    if not os.path.exists(module_path):
        print(f"❌ Module path does not exist: {module_path}")
        sys.exit(1)
    
    if validate_module(module_path):
        print("\n✅ Module is valid and ready for deployment!")
        sys.exit(0)
    else:
        print("\n❌ Module validation failed!")
        sys.exit(1)
