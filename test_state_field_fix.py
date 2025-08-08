#!/usr/bin/env python3
"""
Quick test to verify that state field references are fixed in account_payment_views.xml
"""

import xml.etree.ElementTree as ET
import re

def test_state_field_references():
    """Test that no problematic state field references exist"""
    xml_file = "account_payment_final/views/account_payment_views.xml"
    
    try:
        # Parse XML to check syntax
        tree = ET.parse(xml_file)
        print(f"✅ {xml_file} - XML syntax is valid")
        
        # Read file content to check for problematic patterns
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for problematic state field references (excluding approval_state)
        problematic_patterns = [
            r'\bstate\s*(!=|==|in|not in)\s*[\'"][^\'\"]*[\'"]',  # state != 'draft', state in ['posted'], etc.
            r'[\'"][^\'\"]*[\'\"]\s*(!=|==|or|and)\s*\bstate\b',     # 'draft' != state, etc.
        ]
        
        issues_found = []
        for pattern in problematic_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues_found.append(f"Line {line_num}: {match.group()}")
        
        if issues_found:
            print(f"❌ Found {len(issues_found)} problematic state field references:")
            for issue in issues_found:
                print(f"   {issue}")
            return False
        else:
            print("✅ No problematic state field references found")
        
        # Check that approval_state is used instead
        approval_state_count = content.count('approval_state')
        print(f"✅ Found {approval_state_count} approval_state references (using our custom field)")
        
        print("\n🎉 State field fix validation passed!")
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML syntax error in {xml_file}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error processing {xml_file}: {e}")
        return False

if __name__ == "__main__":
    test_state_field_references()
