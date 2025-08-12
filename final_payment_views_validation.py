#!/usr/bin/env python3
"""
Final validation for account_payment_views.xml fix
"""

import xml.etree.ElementTree as ET

def validate_payment_views():
    try:
        file_path = 'account_payment_approval/views/account_payment_views.xml'
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        print("🔍 Validating account_payment_views.xml...")
        print("✅ XML is syntactically valid")
        
        # Check for problematic XPath patterns
        problematic_patterns = []
        for record in root.findall('.//record[@model="ir.ui.view"]'):
            view_id = record.get('id')
            arch = record.find('.//field[@name="arch"]')
            if arch is not None:
                xpaths = arch.findall('.//xpath')
                for xpath in xpaths:
                    expr = xpath.get('expr')
                    if expr:
                        # Check for problematic patterns
                        if expr == '//group' or expr == '//group[@name="amount_group"]':
                            problematic_patterns.append(f"{view_id}: {expr}")
                        elif 'group[@expand=' in expr and 'requires_approval' not in expr:
                            print(f"⚠️  {view_id}: {expr} (might be problematic)")
                        else:
                            print(f"✅ {view_id}: {expr} (looks good)")
        
        if problematic_patterns:
            print("❌ Found problematic patterns:")
            for pattern in problematic_patterns:
                print(f"   {pattern}")
            return False
        else:
            print("✅ No problematic XPath patterns found")
            return True
            
    except ET.ParseError as e:
        print(f"❌ XML Parse Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = validate_payment_views()
    if result:
        print("\n🎉 VALIDATION PASSED - Module should install without RPC_ERROR")
    else:
        print("\n💥 VALIDATION FAILED - Issues need to be resolved")
