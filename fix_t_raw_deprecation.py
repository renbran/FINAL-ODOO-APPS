#!/usr/bin/env python3
"""
Fix t-raw deprecation warnings across all modules
Replace t-raw with t-out for Odoo 17 compliance
"""

import os
import re
from pathlib import Path

def fix_t_raw_in_file(file_path):
    """Replace t-raw with t-out in XML files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace t-raw with t-out
        # Pattern 1: <t t-raw="..."/>
        content = re.sub(r'<t\s+t-raw="([^"]+)"\s*/>', r'<t t-out="\1"/>', content)
        
        # Pattern 2: <t t-raw="...">
        content = re.sub(r'<t\s+t-raw="([^"]+)">', r'<t t-out="\1">', content)
        
        # Pattern 3: <span t-raw="..."/>
        content = re.sub(r'<span\s+t-raw="([^"]+)"\s*/>', r'<span t-out="\1"/>', content)
        
        # Pattern 4: <span t-raw="...">
        content = re.sub(r'<span\s+t-raw="([^"]+)">', r'<span t-out="\1">', content)
        
        # Pattern 5: <p t-raw="..."/>
        content = re.sub(r'<p\s+t-raw="([^"]+)"\s*/>', r'<p t-out="\1"/>', content)
        
        # Pattern 6: <p t-raw="...">
        content = re.sub(r'<p\s+t-raw="([^"]+)">', r'<p t-out="\1">', content)
        
        # Pattern 7: With attributes - <t t-att-style="..." t-raw="..."/>
        content = re.sub(r't-raw="([^"]+)"', r't-out="\1"', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, file_path
        
        return False, None
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, None

def main():
    """Main execution"""
    base_path = Path(__file__).parent.parent
    
    # Modules to fix
    modules = [
        'ks_dynamic_financial_report',
        'rental_management',
        'om_account_followup',
    ]
    
    fixed_files = []
    
    print("=" * 70)
    print("🔧 FIXING t-raw DEPRECATION WARNINGS")
    print("=" * 70)
    print()
    
    for module in modules:
        module_path = base_path / module
        if not module_path.exists():
            print(f"⚠️  Module not found: {module}")
            continue
        
        print(f"📦 Processing module: {module}")
        
        # Find all XML files
        xml_files = list(module_path.rglob('*.xml'))
        
        for xml_file in xml_files:
            modified, path = fix_t_raw_in_file(xml_file)
            if modified:
                fixed_files.append(str(path))
                print(f"  ✅ Fixed: {xml_file.relative_to(base_path)}")
    
    print()
    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"Files fixed: {len(fixed_files)}")
    print()
    
    if fixed_files:
        print("Fixed files:")
        for file in fixed_files:
            print(f"  - {file}")
        print()
        print("⚠️  IMPORTANT: Update these modules on the server:")
        for module in modules:
            print(f"  sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 -u {module} --stop-after-init")
        print()
    else:
        print("✅ No files needed fixing")
    
    print("=" * 70)

if __name__ == '__main__':
    main()
