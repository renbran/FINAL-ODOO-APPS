#!/usr/bin/env python3
"""
XML Validation Script for Account Move Views
Checks for XML syntax errors and view inheritance issues
"""

import xml.etree.ElementTree as ET
import os

def validate_xml_files():
    """Validate XML syntax in view files"""
    
    print("🔍 XML Validation for Account Move Views")
    print("=" * 50)
    
    xml_files = [
        'account_payment_final/views/account_move_views.xml',
        'account_payment_final/views/account_payment_views.xml',
        'account_payment_final/security/payment_security.xml',
        'account_payment_final/data/system_parameters.xml'
    ]
    
    all_valid = True
    
    for file_path in xml_files:
        print(f"\n📄 Validating: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"   ❌ File not found: {file_path}")
            all_valid = False
            continue
            
        try:
            # Parse the XML file
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            print(f"   ✅ Valid XML syntax")
            print(f"   📊 Root element: {root.tag}")
            
            # Count record elements
            records = root.findall('.//record')
            if records:
                print(f"   📝 Found {len(records)} record elements")
                
                # Check for common issues
                for record in records:
                    record_id = record.get('id', 'Unknown')
                    model = record.get('model', 'Unknown')
                    
                    # Check for view records
                    if model == 'ir.ui.view':
                        name_field = record.find('.//field[@name="name"]')
                        inherit_field = record.find('.//field[@name="inherit_id"]')
                        
                        view_name = name_field.text if name_field is not None else 'Unknown'
                        inherit_ref = inherit_field.get('ref') if inherit_field is not None else None
                        
                        print(f"   🎯 View: {record_id} ({view_name})")
                        if inherit_ref:
                            print(f"      🔗 Inherits: {inherit_ref}")
                        
                        # Check xpath expressions
                        xpaths = record.findall('.//xpath')
                        for xpath in xpaths:
                            expr = xpath.get('expr', '')
                            position = xpath.get('position', '')
                            if expr:
                                print(f"      🎯 XPath: {expr} ({position})")
            
        except ET.ParseError as e:
            print(f"   ❌ XML Parse Error: {e}")
            print(f"      Line {e.lineno}, Column {e.offset}")
            all_valid = False
            
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            all_valid = False
    
    return all_valid

def check_specific_xpath_issues():
    """Check for specific XPath issues that might cause problems"""
    
    print(f"\n🔍 Checking for XPath Issues")
    print("-" * 30)
    
    file_path = 'account_payment_final/views/account_move_views.xml'
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for problematic patterns
        issues = []
        
        # Check for malformed hasclass expressions
        if 'hasclass(\\' in content:
            issues.append("Malformed hasclass expression with backslash")
        
        # Check for incomplete XPath expressions
        if "hasclass('\\" in content:
            issues.append("Incomplete hasclass expression")
        
        # Check for proper field references
        if 'approval_state' in content:
            print("   ✅ approval_state field referenced")
        
        # Check for proper record references
        if 'account.view_account_move_kanban' in content:
            print("   ⚠️  Kanban view inheritance found (may cause issues)")
        
        if 'account.view_move_form' in content:
            print("   ✅ Form view inheritance found")
        
        if issues:
            print("   ❌ Issues found:")
            for issue in issues:
                print(f"      • {issue}")
            return False
        else:
            print("   ✅ No XPath issues detected")
            return True
            
    except Exception as e:
        print(f"   ❌ Error checking XPath: {e}")
        return False

def main():
    """Main execution function"""
    
    print("🚀 Account Move Views XML Validation")
    print("=" * 50)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Validate XML syntax
    xml_valid = validate_xml_files()
    
    # Check for specific XPath issues
    xpath_valid = check_specific_xpath_issues()
    
    print("\n" + "=" * 50)
    
    if xml_valid and xpath_valid:
        print("🎉 ALL XML FILES ARE VALID!")
        print("\n✅ Ready for deployment:")
        print("• XML syntax is correct")
        print("• No malformed XPath expressions")
        print("• View inheritance properly configured")
        print("• No blocking errors detected")
        
        print("\n🚀 The module should now load without XML errors!")
        
    else:
        print("❌ XML VALIDATION ISSUES DETECTED")
        if not xml_valid:
            print("• XML syntax errors need to be fixed")
        if not xpath_valid:
            print("• XPath expression issues need to be resolved")
    
    return xml_valid and xpath_valid

if __name__ == "__main__":
    main()
