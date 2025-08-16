#!/usr/bin/env python3
"""
Comprehensive XML External ID Validation Script
Validates all XML files in order_status_override module for external ID references
"""

import xml.etree.ElementTree as ET
import os
import sys

def extract_external_ids_from_file(file_path):
    """Extract all external ID definitions and references from an XML file"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        definitions = set()
        references = set()
        
        # Extract definitions (id attributes)
        for element in root.iter():
            if 'id' in element.attrib:
                definitions.add(element.attrib['id'])
        
        # Extract references (ref attributes, parent attributes, etc.)
        for element in root.iter():
            for attr_name, attr_value in element.attrib.items():
                if attr_name in ['ref', 'parent', 'inherit_id'] and attr_value:
                    # Skip standard Odoo module references
                    if not attr_value.startswith(('base.', 'sale.', 'mail.', 'web.', 'account.')):
                        references.add(attr_value)
        
        return definitions, references
        
    except Exception as e:
        print(f"❌ Error parsing {file_path}: {e}")
        return set(), set()

def validate_order_status_override():
    """Validate all XML files in order_status_override module"""
    print("🔍 Validating external ID references in order_status_override...")
    
    module_path = "order_status_override"
    if not os.path.exists(module_path):
        print(f"❌ Module path not found: {module_path}")
        return False
    
    # Find all XML files
    xml_files = []
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    
    print(f"📁 Found {len(xml_files)} XML files")
    
    # Collect all definitions and references
    all_definitions = set()
    all_references = set()
    file_definitions = {}
    file_references = {}
    
    for xml_file in xml_files:
        definitions, references = extract_external_ids_from_file(xml_file)
        all_definitions.update(definitions)
        all_references.update(references)
        file_definitions[xml_file] = definitions
        file_references[xml_file] = references
        print(f"  📄 {xml_file}: {len(definitions)} definitions, {len(references)} references")
    
    # Check for missing references
    missing_refs = all_references - all_definitions
    
    if missing_refs:
        print(f"\n❌ Found {len(missing_refs)} missing external ID references:")
        for ref in sorted(missing_refs):
            print(f"  - {ref}")
            # Show which files reference this missing ID
            for file_path, refs in file_references.items():
                if ref in refs:
                    print(f"    Referenced in: {file_path}")
        return False
    else:
        print("\n✅ All external ID references are valid!")
    
    # Check for duplicates
    duplicate_definitions = []
    for definition in all_definitions:
        files_with_def = [f for f, defs in file_definitions.items() if definition in defs]
        if len(files_with_def) > 1:
            duplicate_definitions.append((definition, files_with_def))
    
    if duplicate_definitions:
        print(f"\n⚠️ Found {len(duplicate_definitions)} duplicate definitions:")
        for def_id, files in duplicate_definitions:
            print(f"  - {def_id} defined in:")
            for file in files:
                print(f"    * {file}")
    else:
        print("✅ No duplicate definitions found!")
    
    print(f"\n📊 Summary:")
    print(f"  - Total XML files: {len(xml_files)}")
    print(f"  - Total definitions: {len(all_definitions)}")
    print(f"  - Total references: {len(all_references)}")
    print(f"  - Missing references: {len(missing_refs)}")
    print(f"  - Duplicate definitions: {len(duplicate_definitions)}")
    
    return len(missing_refs) == 0

if __name__ == "__main__":
    success = validate_order_status_override()
    if success:
        print("\n🎉 External ID validation completed successfully!")
    else:
        print("\n💥 External ID validation failed!")
        sys.exit(1)
