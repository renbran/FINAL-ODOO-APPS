#!/usr/bin/env python3
"""
JavaScript Component Conflict Validator
Identifies duplicate Component declarations that cause "Identifier 'Component' has already been declared" errors
"""

import os
import re
import glob

def check_component_conflicts():
    """Check for JavaScript Component identifier conflicts"""
    
    print("🔍 JAVASCRIPT COMPONENT CONFLICT VALIDATION")
    print("=" * 60)
    
    # Find all JavaScript files
    js_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.js') and 'static' in root:
                js_files.append(os.path.join(root, file))
    
    print(f"🔍 Found {len(js_files)} JavaScript files in static directories")
    
    # Check for Component import patterns
    modern_imports = []  # import { Component } from "@odoo/owl"
    legacy_imports = []  # const { Component } = owl
    global_declarations = []  # Component = something
    
    duplicate_classes = {}  # Track duplicate class names
    
    for js_file in js_files:
        try:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for modern Component imports
            if re.search(r'import\s*{[^}]*Component[^}]*}\s*from\s*["\']@odoo/owl["\']', content):
                modern_imports.append(js_file)
            
            # Check for legacy Component imports
            if re.search(r'const\s*{[^}]*Component[^}]*}\s*=\s*owl', content):
                legacy_imports.append(js_file)
            
            # Check for global Component declarations
            if re.search(r'^\s*(var|let|const)\s+Component\s*=', content, re.MULTILINE):
                global_declarations.append(js_file)
            
            # Check for duplicate class names
            class_matches = re.findall(r'export\s+class\s+(\w+)', content)
            for class_name in class_matches:
                if class_name not in duplicate_classes:
                    duplicate_classes[class_name] = []
                duplicate_classes[class_name].append(js_file)
        
        except Exception as e:
            print(f"⚠️ Error reading {js_file}: {e}")
    
    # Report findings
    print(f"\n📊 COMPONENT IMPORT ANALYSIS:")
    print(f"   • Modern imports (import {{ Component }}): {len(modern_imports)}")
    print(f"   • Legacy imports (const {{ Component }} = owl): {len(legacy_imports)}")
    print(f"   • Global declarations: {len(global_declarations)}")
    
    if modern_imports:
        print(f"\n✅ Modern Component imports found in:")
        for file in modern_imports[:5]:  # Show first 5
            print(f"   • {file}")
        if len(modern_imports) > 5:
            print(f"   • ... and {len(modern_imports) - 5} more files")
    
    if legacy_imports:
        print(f"\n⚠️ Legacy Component imports found in:")
        for file in legacy_imports:
            print(f"   • {file}")
    
    if global_declarations:
        print(f"\n❌ Global Component declarations found in:")
        for file in global_declarations:
            print(f"   • {file}")
    
    # Check for duplicate class names
    print(f"\n🔍 DUPLICATE CLASS NAME ANALYSIS:")
    conflicts_found = False
    
    for class_name, files in duplicate_classes.items():
        if len(files) > 1:
            print(f"\n❌ CONFLICT: Class '{class_name}' found in multiple files:")
            for file in files:
                print(f"   • {file}")
            conflicts_found = True
    
    if not conflicts_found:
        print("✅ No duplicate class names found")
    
    # Final assessment
    print(f"\n" + "=" * 60)
    print("📊 CONFLICT ASSESSMENT:")
    
    has_conflicts = len(legacy_imports) > 0 or len(global_declarations) > 0 or conflicts_found
    
    if has_conflicts:
        print("❌ COMPONENT CONFLICTS DETECTED!")
        print("   Issues that can cause 'Identifier Component has already been declared':")
        if legacy_imports:
            print(f"   • {len(legacy_imports)} files using legacy OWL syntax")
        if global_declarations:
            print(f"   • {len(global_declarations)} files with global Component declarations")
        if conflicts_found:
            print("   • Duplicate class names causing namespace collisions")
        print("\n🔧 RECOMMENDED ACTIONS:")
        print("   1. Convert legacy OWL syntax to modern ES6 imports")
        print("   2. Remove global Component declarations")
        print("   3. Rename or remove duplicate classes")
        print("   4. Use specific file imports instead of wildcard includes")
        return False
    else:
        print("🎉 NO COMPONENT CONFLICTS DETECTED!")
        print("✅ All Component imports are properly structured")
        print("✅ No duplicate class names found")
        print("✅ JavaScript should load without identifier conflicts")
        return True

if __name__ == "__main__":
    success = check_component_conflicts()
    exit(0 if success else 1)
