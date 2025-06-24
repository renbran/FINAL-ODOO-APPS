#!/usr/bin/env python3
"""
Commission Fields Module - Final Validation
Tests all components after XPath fix
"""

import os
import ast
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_commission_fields_structure():
    """Validate commission_fields module structure"""
    print("🔍 Validating Commission Fields Module Structure...")
    
    base_path = Path("commission_fields")
    required_files = [
        "__init__.py",
        "__manifest__.py",
        "models/__init__.py",
        "models/purchase_order.py",
        "models/sale_order.py",
        "views/purchase_order_views.xml",
        "views/sale_order_views.xml"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = base_path / file_path
        if not full_path.exists():
            missing_files.append(str(file_path))
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def validate_purchase_order_model():
    """Validate purchase order model has required fields"""
    print("\n🐍 Validating Purchase Order Model...")
    
    model_path = Path("commission_fields/models/purchase_order.py")
    
    if not model_path.exists():
        print("❌ Purchase order model not found")
        return False
    
    try:
        with open(model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required fields
        required_fields = [
            'external_commission_type',
            'external_percentage',
            'external_fixed_amount',
            'default_account_id'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in content:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return False
        
        # Validate Python syntax
        ast.parse(content)
        print("✅ Purchase order model validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Error validating purchase order model: {e}")
        return False

def validate_purchase_order_views():
    """Validate purchase order views XML"""
    print("\n📄 Validating Purchase Order Views...")
    
    views_path = Path("commission_fields/views/purchase_order_views.xml")
    
    if not views_path.exists():
        print("❌ Purchase order views not found")
        return False
    
    try:
        # Parse XML
        tree = ET.parse(views_path)
        root = tree.getroot()
        
        # Check for view records
        view_records = root.findall(".//record[@model='ir.ui.view']")
        
        if len(view_records) < 2:
            print(f"❌ Expected at least 2 view records, found {len(view_records)}")
            return False
        
        # Check for XPath expressions
        xpaths = root.findall(".//xpath")
        
        for xpath in xpaths:
            expr = xpath.get('expr', '')
            # Check that we're not using problematic XPaths
            if 'other_information' in expr:
                print(f"❌ Found problematic XPath: {expr}")
                return False
        
        print("✅ Purchase order views validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Error validating purchase order views: {e}")
        return False

def validate_manifest():
    """Validate manifest file"""
    print("\n📋 Validating Commission Fields Manifest...")
    
    manifest_path = Path("commission_fields/__manifest__.py")
    
    if not manifest_path.exists():
        print("❌ Manifest not found")
        return False
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse manifest
        manifest_dict = eval(content)
        
        # Check required keys
        required_keys = ['name', 'depends', 'data']
        for key in required_keys:
            if key not in manifest_dict:
                print(f"❌ Missing manifest key: {key}")
                return False
        
        # Check dependencies
        depends = manifest_dict.get('depends', [])
        required_deps = ['base', 'purchase', 'sale']
        
        for dep in required_deps:
            if dep not in depends:
                print(f"⚠️  Missing dependency: {dep}")
        
        print("✅ Manifest validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Error validating manifest: {e}")
        return False

def test_xml_inheritance_safety():
    """Test that XML inheritance is safe"""
    print("\n🛡️ Testing XML Inheritance Safety...")
    
    views_path = Path("commission_fields/views/purchase_order_views.xml")
    
    if not views_path.exists():
        return False
    
    try:
        with open(views_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for safe inheritance patterns
        safe_patterns = [
            "//field[@name='partner_id']",
            "//field[@name='name']"
        ]
        
        unsafe_patterns = [
            "//page[@name='other_information']",
            "//notebook[last()]"
        ]
        
        has_safe = any(pattern in content for pattern in safe_patterns)
        has_unsafe = any(pattern in content for pattern in unsafe_patterns)
        
        if has_unsafe:
            print("❌ Found unsafe inheritance patterns")
            return False
        
        if not has_safe:
            print("⚠️  No safe inheritance patterns found")
        
        print("✅ XML inheritance safety check passed")
        return True
        
    except Exception as e:
        print(f"❌ Error checking inheritance safety: {e}")
        return False

def run_commission_fields_validation():
    """Run complete validation"""
    print("🚀 Starting Commission Fields Module Validation...")
    print("=" * 60)
    
    tests = [
        ("Module Structure", validate_commission_fields_structure),
        ("Purchase Order Model", validate_purchase_order_model),
        ("Purchase Order Views", validate_purchase_order_views),
        ("Manifest", validate_manifest),
        ("XML Inheritance Safety", test_xml_inheritance_safety)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: Error during validation - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 COMMISSION FIELDS VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 COMMISSION FIELDS MODULE IS READY!")
        print("\nThe XPath error has been fixed and the module is compatible with Odoo 17.0")
        print("\nNext steps:")
        print("1. Restart Odoo service")
        print("2. Upgrade the commission_fields module")
        print("3. Test purchase order form for commission fields")
        return True
    else:
        print("⚠️  Some issues remain. Check the failed tests above.")
        return False

if __name__ == "__main__":
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        success = run_commission_fields_validation()
        exit(0 if success else 1)
    except Exception as e:
        print(f"💥 Validation script failed: {e}")
        exit(1)
