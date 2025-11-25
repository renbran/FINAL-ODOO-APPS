#!/usr/bin/env python3
"""
OSUS Premium Settings Fix Validator
Validates that all required files exist and are properly configured
"""

import os
import sys
from pathlib import Path

def validate_files():
    """Check if all required files exist"""
    base_path = Path(__file__).parent / 'osus_premium'
    
    required_files = {
        'static/src/scss/osus_settings.scss': 'Settings page SCSS',
        'static/src/js/settings_fixes.js': 'Settings page JavaScript fixes',
        '__manifest__.py': 'Module manifest',
    }
    
    print("🔍 Validating OSUS Premium Settings Fix Files")
    print("=" * 50)
    print()
    
    all_good = True
    for file_path, description in required_files.items():
        full_path = base_path / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {description}")
            print(f"   📁 {file_path}")
            print(f"   📊 Size: {size:,} bytes")
        else:
            print(f"❌ MISSING: {description}")
            print(f"   📁 {file_path}")
            all_good = False
        print()
    
    # Check manifest content
    manifest_path = base_path / '__manifest__.py'
    if manifest_path.exists():
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print("🔍 Checking Manifest Configuration")
        print("-" * 50)
        
        checks = {
            'osus_settings.scss': 'Settings SCSS in assets',
            'settings_fixes.js': 'Settings JS in assets',
            '17.0.1.0.1': 'Version updated',
        }
        
        for check, desc in checks.items():
            if check in content:
                print(f"✅ {desc}")
            else:
                print(f"❌ MISSING: {desc}")
                all_good = False
        print()
    
    return all_good

def main():
    print()
    result = validate_files()
    
    if result:
        print("=" * 50)
        print("✅ All validations passed!")
        print()
        print("🚀 Ready to deploy! Run:")
        print("   • Windows: .\\deploy_settings_fix.ps1")
        print("   • Linux:   ./deploy_settings_fix.sh")
        print()
        print("📋 What the fix does:")
        print("   • Hides 'Toggle Dropdown' button via CSS & JS")
        print("   • Applies OSUS burgundy & gold styling")
        print("   • Improves settings page layout")
        print()
        return 0
    else:
        print("=" * 50)
        print("❌ Validation failed!")
        print("   Some files are missing or misconfigured.")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
