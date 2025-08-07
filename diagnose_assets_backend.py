#!/usr/bin/env python3
"""
Diagnostic script to check why web.assets_backend is not found
"""

import os
import sys

def diagnose_assets_backend_issue():
    """Diagnose the web.assets_backend not found issue"""
    
    print("🔍 Diagnosing web.assets_backend issue...")
    
    project_dir = r"d:\RUNNING APPS\ready production\latest\odoo17_final"
    os.chdir(project_dir)
    
    print("\n📋 Step 1: Checking module manifest dependencies...")
    try:
        with open('payment_account_enhanced/__manifest__.py', 'r') as f:
            manifest = f.read()
        
        if "'web'" in manifest:
            print("   ✓ 'web' dependency is declared in manifest")
        else:
            print("   ❌ 'web' dependency is MISSING in manifest")
            
        if "'website'" in manifest:
            print("   ✓ 'website' dependency is declared in manifest") 
        else:
            print("   ⚠️  'website' dependency not found")
            
        print(f"\n   Dependencies found in manifest:")
        import re
        deps_match = re.search(r"'depends':\s*\[(.*?)\]", manifest, re.DOTALL)
        if deps_match:
            deps = deps_match.group(1)
            for dep in deps.split(','):
                dep = dep.strip().strip("'\"")
                if dep:
                    print(f"      - {dep}")
    except Exception as e:
        print(f"   ❌ Error reading manifest: {e}")
    
    print("\n📋 Step 2: Checking for conflicting asset definitions...")
    
    # Check all XML files for asset inheritance
    xml_files = []
    for root, dirs, files in os.walk('payment_account_enhanced'):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    
    print(f"   Found {len(xml_files)} XML files to check:")
    
    for xml_file in xml_files:
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'web.assets_backend' in content:
                print(f"      ⚠️  {xml_file} contains 'web.assets_backend'")
                if 'inherit_id="web.assets_backend"' in content:
                    print(f"         ❌ FOUND PROBLEMATIC INHERITANCE!")
                    # Show the problematic lines
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'inherit_id="web.assets_backend"' in line:
                            print(f"            Line {i+1}: {line.strip()}")
                            
            if 'template' in content and 'inherit_id' in content:
                print(f"      📝 {xml_file} has template inheritance")
                
        except Exception as e:
            print(f"      ❌ Error reading {xml_file}: {e}")
    
    print("\n📋 Step 3: Checking manifest assets configuration...")
    try:
        with open('payment_account_enhanced/__manifest__.py', 'r') as f:
            manifest = f.read()
        
        if "'assets'" in manifest:
            print("   ✓ Assets section found in manifest")
            assets_match = re.search(r"'assets':\s*{(.*?)}", manifest, re.DOTALL)
            if assets_match:
                assets_content = assets_match.group(1)
                if 'web.assets_backend' in assets_content:
                    print("   ✓ web.assets_backend properly configured in manifest")
                else:
                    print("   ❌ web.assets_backend NOT found in manifest assets")
        else:
            print("   ❌ No assets section in manifest")
    except Exception as e:
        print(f"   ❌ Error checking assets: {e}")
    
    print("\n💡 DIAGNOSIS COMPLETE")
    print("\n🔧 RECOMMENDED SOLUTIONS:")
    print("   1. IMMEDIATE: Run fix_assets_backend_error.bat")
    print("   2. If problem persists: Uninstall → Reinstall module")
    print("   3. Nuclear option: Delete module from database manually")
    print("\n🚨 The error is likely caused by:")
    print("   - Cached XML data in database")
    print("   - Incomplete module upgrade process")
    print("   - Conflicting asset definitions")

if __name__ == "__main__":
    diagnose_assets_backend_issue()
