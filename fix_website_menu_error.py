#!/usr/bin/env python3
"""
Odoo 17 Website Layout Menu Fix
This script helps diagnose and fix the website layout menu rendering error.
"""

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

def find_problematic_templates():
    """Find templates that might be causing the menu rendering issue."""
    problematic_patterns = [
        r"env\['ir\.ui\.menu'\].*load_menus_root",
        r"t-foreach.*env\['ir\.ui\.menu'\]",
        r"force_action.*load_menus_root",
        r"menu\['action'\].*split"
    ]
    
    results = []
    
    # Search in all XML files
    for xml_file in Path('.').rglob('*.xml'):
        if 'backup_removed_modules' in str(xml_file):
            continue
            
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern in problematic_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    results.append({
                        'file': str(xml_file),
                        'pattern': pattern,
                        'content_snippet': content[:500] + '...' if len(content) > 500 else content
                    })
                    break
        except Exception as e:
            print(f"Error reading {xml_file}: {e}")
            
    return results

def check_website_layout_inheritance():
    """Check for templates inheriting from website.layout that might have issues."""
    problematic_files = []
    
    for xml_file in Path('.').rglob('*.xml'):
        if 'backup_removed_modules' in str(xml_file):
            continue
            
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'inherit_id="website.layout"' in content and 'env[' in content:
                problematic_files.append(str(xml_file))
        except Exception as e:
            print(f"Error reading {xml_file}: {e}")
            
    return problematic_files

def generate_fix_template():
    """Generate a proper website menu template to replace problematic ones."""
    return '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="website_menu_fix" inherit_id="website.layout" name="Website Menu Fix">
        <xpath expr="//header//nav" position="inside">
            <!-- Proper website menu implementation -->
            <ul class="navbar-nav">
                <t t-foreach="website.menu_id.child_id" t-as="submenu">
                    <t t-call="website.submenu">
                        <t t-set="item_class" t-valuef="nav-item"/>
                        <t t-set="link_class" t-valuef="nav-link"/>
                    </t>
                </t>
            </ul>
        </xpath>
    </template>
</odoo>
'''

def main():
    print("=== Odoo 17 Website Layout Menu Fix ===\n")
    
    # Find problematic templates
    print("1. Searching for problematic templates...")
    problematic = find_problematic_templates()
    
    if problematic:
        print(f"Found {len(problematic)} potentially problematic templates:")
        for item in problematic:
            print(f"  - {item['file']}")
            print(f"    Pattern: {item['pattern']}")
            print(f"    Snippet: {item['content_snippet'][:100]}...")
            print()
    else:
        print("No problematic templates found in custom modules.")
    
    # Check website.layout inheritance
    print("\n2. Checking website.layout inheritance...")
    layout_files = check_website_layout_inheritance()
    
    if layout_files:
        print(f"Found {len(layout_files)} files inheriting website.layout with env references:")
        for file in layout_files:
            print(f"  - {file}")
    else:
        print("No suspicious website.layout inheritance found.")
    
    print("\n3. Recommendations:")
    print("   - The error suggests a template is mixing backend menu logic with website templates")
    print("   - Check if any custom modules are incorrectly accessing ir.ui.menu in website context")
    print("   - Use website.menu_id.child_id for website menus instead of ir.ui.menu.load_menus_root()")
    print("   - Clear Odoo cache and restart the server")
    
    # Generate fix template
    fix_template = generate_fix_template()
    print(f"\n4. Suggested fix template:\n{fix_template}")

if __name__ == "__main__":
    main()
