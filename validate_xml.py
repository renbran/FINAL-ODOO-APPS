#!/usr/bin/env python3
import os
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_xml_files(root_dir):
    """Validate all XML files in the directory and subdirectories."""
    root_path = Path(root_dir)
    xml_files = list(root_path.rglob("*.xml"))
    
    print(f"Found {len(xml_files)} XML files to validate...")
    
    problematic_files = []
    
    for xml_file in xml_files:
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Parse the XML
                ET.fromstring(content)
            print(f"✓ {xml_file}")
        except ET.ParseError as e:
            print(f"✗ {xml_file}: {e}")
            problematic_files.append((xml_file, str(e)))
        except Exception as e:
            print(f"✗ {xml_file}: {e}")
            problematic_files.append((xml_file, str(e)))
    
    if problematic_files:
        print("\n" + "="*50)
        print("PROBLEMATIC FILES:")
        print("="*50)
        for file_path, error in problematic_files:
            print(f"\nFile: {file_path}")
            print(f"Error: {error}")
    else:
        print("\nAll XML files are valid!")
    
    return problematic_files

if __name__ == "__main__":
    root_directory = r"d:\RUNNING APPS\ready production\osus-main\odoo17_final"
    validate_xml_files(root_directory)
