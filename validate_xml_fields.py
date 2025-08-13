#!/usr/bin/env python3
"""
XML View Validation Script for Odoo 17
Checks for common field reference issues in view definitions
"""

import xml.etree.ElementTree as ET
import re

def check_invisible_fields(xml_file):
    """Check if fields used in invisible attributes are present in the view"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Find all fields that are made invisible
        invisible_fields = set()
        view_fields = set()
        
        # Extract fields used in invisible attributes
        for elem in root.iter():
            if 'invisible' in elem.attrib:
                invisible_expr = elem.attrib['invisible']
                # Extract field names from expressions like "not move_id" or "state != 'draft'"
                field_matches = re.findall(r'\b([a-z_]+[a-z0-9_]*)\b', invisible_expr)
                for field in field_matches:
                    if field not in ['not', 'and', 'or', 'in', 'True', 'False']:
                        invisible_fields.add(field)
        
        # Extract all field elements in the view
        for field_elem in root.iter('field'):
            if 'name' in field_elem.attrib:
                view_fields.add(field_elem.attrib['name'])
        
        # Check for missing fields
        missing_fields = invisible_fields - view_fields
        
        if missing_fields:
            print(f"⚠️  {xml_file}: Missing fields in invisible expressions: {missing_fields}")
            print("   Add these fields as invisible: <field name='field_name' invisible='1'/>")
            return False
        else:
            print(f"✅ {xml_file}: All invisible field references are valid")
            return True
            
    except Exception as e:
        print(f"❌ {xml_file}: Error checking invisible fields - {e}")
        return False

def main():
    xml_file = "payment_approval_workflow/views/account_payment_views.xml"
    print("🔍 Checking XML view field references...")
    print("=" * 50)
    
    result = check_invisible_fields(xml_file)
    
    print("=" * 50)
    if result:
        print("🎉 XML validation PASSED!")
    else:
        print("💥 XML validation FAILED!")

if __name__ == "__main__":
    main()
