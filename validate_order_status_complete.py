#!/usr/bin/env python3
"""
Complete Order Status Override Module Validation
Comprehensive validation for CloudPepper deployment
"""

import xml.etree.ElementTree as ET
import os
import sys

def validate_xml_files():
    """Validate all XML files for syntax errors"""
    print("🔍 Validating XML syntax...")
    
    xml_files = []
    for root, dirs, files in os.walk("order_status_override"):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    
    errors = []
    for xml_file in xml_files:
        try:
            ET.parse(xml_file)
            print(f"  ✅ {xml_file}")
        except ET.ParseError as e:
            errors.append(f"  ❌ {xml_file}: {e}")
            print(f"  ❌ {xml_file}: {e}")
    
    return len(errors) == 0

def validate_manifest():
    """Validate manifest file"""
    print("\n🔍 Validating manifest file...")
    
    manifest_path = "order_status_override/__manifest__.py"
    if not os.path.exists(manifest_path):
        print("❌ Manifest file not found")
        return False
    
    try:
        with open(manifest_path, 'r') as f:
            content = f.read()
        
        # Try to compile the manifest
        compile(content, manifest_path, 'exec')
        print("  ✅ Manifest syntax is valid")
        
        # Check if all referenced files exist
        exec_globals = {}
        exec(content, exec_globals)
        manifest = exec_globals
        
        if 'data' in manifest:
            missing_files = []
            for data_file in manifest['data']:
                file_path = os.path.join("order_status_override", data_file)
                if not os.path.exists(file_path):
                    missing_files.append(data_file)
            
            if missing_files:
                print(f"  ❌ Missing data files: {missing_files}")
                return False
            else:
                print(f"  ✅ All {len(manifest['data'])} data files exist")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Manifest validation error: {e}")
        return False

def validate_menu_order():
    """Validate menu order in commission report"""
    print("\n🔍 Validating menu order...")
    
    try:
        tree = ET.parse("order_status_override/reports/sale_commission_report.xml")
        root = tree.getroot()
        
        defined_menus = set()
        for element in root.iter():
            if element.tag == 'menuitem':
                menu_id = element.get('id')
                parent_id = element.get('parent')
                
                if parent_id and parent_id.startswith('menu_') and parent_id not in defined_menus:
                    # Check if parent is defined later
                    remaining_elements = list(root.iter())[list(root.iter()).index(element) + 1:]
                    parent_found_later = any(
                        e.tag == 'menuitem' and e.get('id') == parent_id 
                        for e in remaining_elements
                    )
                    
                    if parent_found_later:
                        print(f"  ❌ Menu order error: {menu_id} references {parent_id} defined later")
                        return False
                
                defined_menus.add(menu_id)
        
        print("  ✅ Menu order is correct")
        return True
        
    except Exception as e:
        print(f"  ❌ Menu validation error: {e}")
        return False

def validate_external_ids():
    """Quick external ID validation"""
    print("\n🔍 Validating external IDs...")
    
    try:
        # Run the comprehensive external ID validator
        import subprocess
        result = subprocess.run([sys.executable, 'validate_external_ids.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ All external IDs are valid")
            return True
        else:
            print("  ❌ External ID validation failed")
            print(result.stdout)
            return False
            
    except Exception as e:
        print(f"  ❌ External ID validation error: {e}")
        return False

def validate_python_syntax():
    """Validate Python file syntax"""
    print("\n🔍 Validating Python syntax...")
    
    py_files = []
    for root, dirs, files in os.walk("order_status_override"):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    
    errors = []
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, py_file, 'exec')
            print(f"  ✅ {py_file}")
        except SyntaxError as e:
            errors.append(f"  ❌ {py_file}: {e}")
            print(f"  ❌ {py_file}: {e}")
        except Exception as e:
            errors.append(f"  ❌ {py_file}: {e}")
            print(f"  ❌ {py_file}: {e}")
    
    return len(errors) == 0

def main():
    """Run all validations"""
    print("🚀 Starting comprehensive order_status_override module validation...")
    print("=" * 70)
    
    validations = [
        ("XML Syntax", validate_xml_files),
        ("Manifest File", validate_manifest), 
        ("Menu Order", validate_menu_order),
        ("External IDs", validate_external_ids),
        ("Python Syntax", validate_python_syntax),
    ]
    
    results = []
    for name, validator in validations:
        try:
            result = validator()
            results.append((name, result))
        except Exception as e:
            print(f"💥 {name} validation crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 70)
    print("📊 VALIDATION SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:20} : {status}")
        if not result:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED! Module is ready for CloudPepper deployment.")
        print("\n📋 Deployment Instructions:")
        print("1. Upload the entire order_status_override folder to CloudPepper")
        print("2. Go to Apps menu and search for 'Custom Sales Order Status Workflow'")
        print("3. Click Install or Upgrade")
        print("4. Clear browser cache and refresh")
        print("5. Test menu navigation: Sales → Commission Reports → Generate Reports")
        return True
    else:
        print("💥 VALIDATION FAILED! Fix the issues above before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
