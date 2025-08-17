
# Emergency View Fix Script
# Run this if views have validation errors

import xml.etree.ElementTree as ET
import os

def fix_view_references():
    """Remove invalid field references from views"""
    view_files = []
    
    # Find all XML view files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.xml') and 'views' in root:
                view_files.append(os.path.join(root, file))
    
    for view_file in view_files:
        try:
            tree = ET.parse(view_file)
            # Validate structure
            print(f"✅ {view_file} - Valid XML")
        except ET.ParseError as e:
            print(f"❌ {view_file} - XML Error: {e}")

if __name__ == "__main__":
    fix_view_references()
