#!/usr/bin/env python3
"""
Final Module Validation Script for account_payment_final
Validates all critical aspects before production deployment
"""

import os
import ast
import xml.etree.ElementTree as ET
from pathlib import Path

MODULE_PATH = Path("d:/RUNNING APPS/ready production/latest/odoo17_final/account_payment_final")

def validate_manifest():
    """Validate manifest file"""
    manifest_path = MODULE_PATH / "__manifest__.py"
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        print("✅ Manifest syntax: VALID")
        
        # Check for required fields
        if "'name':" in content and "'version':" in content:
            print("✅ Manifest metadata: COMPLETE")
        else:
            print("❌ Manifest metadata: MISSING required fields")
            
        return True
    except Exception as e:
        print(f"❌ Manifest validation failed: {e}")
        return False

def validate_xml_files():
    """Validate all XML files"""
    xml_files = list(MODULE_PATH.rglob("*.xml"))
    valid_count = 0
    
    for xml_file in xml_files:
        try:
            ET.parse(xml_file)
            valid_count += 1
        except Exception as e:
            print(f"❌ XML Error in {xml_file.name}: {e}")
            return False
    
    print(f"✅ XML Validation: {valid_count}/{len(xml_files)} files valid")
    return True

def validate_python_files():
    """Validate all Python files"""
    py_files = list(MODULE_PATH.rglob("*.py"))
    valid_count = 0
    
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            valid_count += 1
        except Exception as e:
            print(f"❌ Python Error in {py_file.name}: {e}")
            return False
    
    print(f"✅ Python Validation: {valid_count}/{len(py_files)} files valid")
    return True

def validate_file_references():
    """Check if all files referenced in manifest exist"""
    manifest_path = MODULE_PATH / "__manifest__.py"
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    missing_files = []
    
    # Extract data files
    if "'data':" in content:
        data_start = content.find("'data':") + 8
        data_end = content.find("]", data_start) + 1
        data_section = content[data_start:data_end]
        
        # Find all quoted file paths
        import re
        file_refs = re.findall(r"'([^']*\.xml)'", data_section)
        
        for file_ref in file_refs:
            if not file_ref.startswith('#'):  # Skip comments
                file_path = MODULE_PATH / file_ref
                if not file_path.exists():
                    missing_files.append(file_ref)
    
    if missing_files:
        print(f"❌ Missing referenced files: {missing_files}")
        return False
    else:
        print("✅ File References: All referenced files exist")
        return True

def validate_asset_files():
    """Check if all asset files referenced in manifest exist"""
    manifest_path = MODULE_PATH / "__manifest__.py"
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    missing_assets = []
    
    if "'assets':" in content:
        # Extract asset file references
        import re
        asset_refs = re.findall(r"'account_payment_final/([^']*)'", content)
        
        for asset_ref in asset_refs:
            asset_path = MODULE_PATH / asset_ref
            if not asset_path.exists():
                missing_assets.append(asset_ref)
    
    if missing_assets:
        print(f"❌ Missing asset files: {missing_assets}")
        return False
    else:
        print("✅ Asset References: All asset files exist")
        return True

def main():
    print("=" * 60)
    print("ACCOUNT PAYMENT FINAL - DEPLOYMENT VALIDATION")
    print("=" * 60)
    
    validations = [
        validate_manifest(),
        validate_xml_files(),
        validate_python_files(),
        validate_file_references(),
        validate_asset_files()
    ]
    
    if all(validations):
        print("\n🎉 ALL VALIDATIONS PASSED")
        print("🚀 MODULE IS READY FOR PRODUCTION DEPLOYMENT")
        
        # Final stats
        total_files = len(list(MODULE_PATH.rglob("*"))) - len(list(MODULE_PATH.rglob("*/")))
        print(f"\n📊 Final Module Statistics:")
        print(f"   Total Files: {total_files}")
        print(f"   Python Files: {len(list(MODULE_PATH.rglob('*.py')))}")
        print(f"   XML Files: {len(list(MODULE_PATH.rglob('*.xml')))}")
        print(f"   JavaScript Files: {len(list(MODULE_PATH.rglob('*.js')))}")
        print(f"   SCSS Files: {len(list(MODULE_PATH.rglob('*.scss')))}")
        
    else:
        print("\n❌ VALIDATION FAILED")
        print("🔧 Please fix the issues above before deployment")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
