#!/usr/bin/env python3
"""
CloudPepper Field Validation Test
Simulates the field validation that CloudPepper performs when loading views
"""

import xml.etree.ElementTree as ET
import re

def extract_field_references(xml_content):
    """Extract all field references from XML conditions"""
    field_refs = set()
    
    # Pattern to find field references in invisible/readonly conditions
    patterns = [
        r'invisible="[^"]*\b(\w+)\s*(?:!=|==|in|not in)',  # invisible="field != 'value'"
        r'readonly="[^"]*\b(\w+)\s*(?:!=|==|in|not in)',   # readonly="field != 'value'"
        r'invisible="[^"]*\bnot\s+(\w+)\b',                # invisible="not field"
        r'readonly="[^"]*\bnot\s+(\w+)\b',                 # readonly="not field"
        r'invisible="[^"]*\b(\w+)\s+(?:and|or)',           # invisible="field and other"
        r'readonly="[^"]*\b(\w+)\s+(?:and|or)',            # readonly="field and other"
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, xml_content)
        for match in matches:
            field_name = match.group(1)
            if field_name not in ['and', 'or', 'not', 'in']:  # Exclude keywords
                field_refs.add(field_name)
    
    return field_refs

def extract_defined_fields(xml_content):
    """Extract all fields defined in the view"""
    defined_fields = set()
    
    # Pattern to find <field name="..."> tags
    pattern = r'<field\s+name="([^"]+)"'
    matches = re.finditer(pattern, xml_content)
    for match in matches:
        defined_fields.add(match.group(1))
    
    return defined_fields

def validate_field_availability():
    """Validate that all referenced fields are available in the view"""
    xml_file = "account_payment_final/views/account_payment_views.xml"
    
    try:
        # Parse XML to check syntax
        tree = ET.parse(xml_file)
        print(f"✅ {xml_file} - XML syntax is valid")
        
        # Read file content
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract field references and definitions
        referenced_fields = extract_field_references(content)
        defined_fields = extract_defined_fields(content)
        
        print(f"\n📊 Field Analysis:")
        print(f"   🔍 Fields referenced in conditions: {len(referenced_fields)}")
        for field in sorted(referenced_fields):
            print(f"      - {field}")
        
        print(f"   📝 Fields defined in view: {len(defined_fields)}")
        for field in sorted(defined_fields):
            print(f"      - {field}")
        
        # Check for missing fields
        missing_fields = referenced_fields - defined_fields
        
        if missing_fields:
            print(f"\n❌ Missing fields referenced in conditions but not defined in view:")
            for field in sorted(missing_fields):
                print(f"   - {field}")
            return False
        else:
            print(f"\n✅ All referenced fields are properly defined in the view")
        
        # Standard fields that should be inherited from base view
        expected_inherited_fields = {
            'partner_id', 'amount', 'payment_type', 'voucher_number', 
            'reviewer_id', 'approver_id', 'authorizer_id'
        }
        
        available_fields = defined_fields | expected_inherited_fields
        still_missing = referenced_fields - available_fields
        
        if still_missing:
            print(f"\n⚠️ Fields that might not be inherited from base view:")
            for field in sorted(still_missing):
                print(f"   - {field}")
            print(f"   💡 These fields should be available from the inherited account.payment view")
        
        print(f"\n🎉 Field validation completed!")
        return len(missing_fields) == 0
        
    except ET.ParseError as e:
        print(f"❌ XML syntax error in {xml_file}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error processing {xml_file}: {e}")
        return False

if __name__ == "__main__":
    validate_field_availability()
