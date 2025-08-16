#!/usr/bin/env python3
"""
Menu Order Validation Script for order_status_override
Ensures that parent menu items are defined before child menu items
"""

import xml.etree.ElementTree as ET
import os

def validate_menu_order():
    """Validate that menu items are defined in correct order"""
    print("🔍 Validating menu order in order_status_override...")
    
    file_path = "order_status_override/reports/sale_commission_report.xml"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        # Parse XML
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Track menu definitions and references
        defined_menus = set()
        menu_order = []
        
        # Process all menuitem elements
        for element in root.iter():
            if element.tag == 'menuitem':
                menu_id = element.get('id')
                parent_id = element.get('parent')
                
                menu_order.append({
                    'id': menu_id,
                    'parent': parent_id,
                    'name': element.get('name')
                })
                
                # Check if parent is defined before this menu (if parent is in same module)
                if parent_id and parent_id.startswith('menu_') and parent_id not in defined_menus:
                    # Check if parent is defined later in the same file
                    parent_found_later = False
                    current_pos = list(root.iter()).index(element)
                    
                    for later_element in list(root.iter())[current_pos + 1:]:
                        if later_element.tag == 'menuitem' and later_element.get('id') == parent_id:
                            parent_found_later = True
                            break
                    
                    if parent_found_later:
                        print(f"❌ Menu order error: '{menu_id}' references parent '{parent_id}' that is defined later")
                        return False
                
                defined_menus.add(menu_id)
        
        print("✅ Menu order validation passed!")
        print("\n📋 Menu structure:")
        for menu in menu_order:
            parent_info = f" (parent: {menu['parent']})" if menu['parent'] else " (root)"
            print(f"  - {menu['id']}: {menu['name']}{parent_info}")
        
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML Parse Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Validation Error: {e}")
        return False

if __name__ == "__main__":
    success = validate_menu_order()
    if success:
        print("\n🎉 Menu order validation completed successfully!")
    else:
        print("\n💥 Menu order validation failed!")
        exit(1)
