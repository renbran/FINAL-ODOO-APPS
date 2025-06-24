#!/usr/bin/env python3
"""
XML Duplicate Checker for Odoo Modules
This script checks for duplicate record IDs across XML files in a module.
"""

import os
import xml.etree.ElementTree as ET
from collections import defaultdict

def check_xml_duplicates(module_path):
    """Check for duplicate record IDs in XML files"""
    
    record_ids = defaultdict(list)
    issues_found = []
    
    # Find all XML files in views directory
    views_path = os.path.join(module_path, 'views')
    
    if not os.path.exists(views_path):
        return ["Views directory not found"]
    
    xml_files = [f for f in os.listdir(views_path) if f.endswith('.xml')]
    
    print(f"📁 Checking XML files in: {views_path}")
    print(f"📄 Found {len(xml_files)} XML files: {xml_files}")
    
    for xml_file in xml_files:
        file_path = os.path.join(views_path, xml_file)
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Find all record elements
            for record in root.findall('.//record'):
                record_id = record.get('id')
                if record_id:
                    record_ids[record_id].append({
                        'file': xml_file,
                        'model': record.get('model', 'unknown'),
                        'line': getattr(record, 'sourceline', 'unknown')
                    })
            
            # Find all menuitem elements  
            for menuitem in root.findall('.//menuitem'):
                menu_id = menuitem.get('id')
                if menu_id:
                    record_ids[menu_id].append({
                        'file': xml_file,
                        'model': 'ir.ui.menu',
                        'line': getattr(menuitem, 'sourceline', 'unknown')
                    })
                    
        except ET.ParseError as e:
            issues_found.append(f"❌ XML Parse Error in {xml_file}: {e}")
            continue
        except Exception as e:
            issues_found.append(f"❌ Error reading {xml_file}: {e}")
            continue
    
    # Check for duplicates
    duplicates_found = False
    for record_id, occurrences in record_ids.items():
        if len(occurrences) > 1:
            duplicates_found = True
            issues_found.append(f"🔥 DUPLICATE ID '{record_id}' found in:")
            for occ in occurrences:
                issues_found.append(f"   - {occ['file']} (model: {occ['model']}, line: {occ['line']})")
    
    if not duplicates_found:
        issues_found.append("✅ No duplicate IDs found in XML files!")
    
    return issues_found

def main():
    """Main function"""
    
    print("🔍 XML DUPLICATE CHECKER FOR ODOO MODULES")
    print("=" * 50)
    
    # Check account_statement module
    module_path = os.path.join(os.path.dirname(__file__), 'account_statement')
    
    if not os.path.exists(module_path):
        print(f"❌ Module path not found: {module_path}")
        return
    
    print(f"🎯 Checking module: account_statement")
    print(f"📂 Module path: {module_path}")
    print()
    
    issues = check_xml_duplicates(module_path)
    
    print("📋 RESULTS:")
    print("-" * 30)
    for issue in issues:
        print(issue)
    
    print()
    print("🛠️ RECOMMENDATIONS:")
    print("-" * 30)
    print("1. Remove duplicate record IDs from XML files")
    print("2. Keep primary definitions in appropriate files:")
    print("   - Actions & main menus → wizard_views.xml")
    print("   - Views & specific menus → respective view files")
    print("3. Restart Odoo after fixing duplicates")
    print("4. Update Apps List and reinstall module")

if __name__ == "__main__":
    main()
