#!/usr/bin/env python3
"""
OSUS Properties Web Theme Validation Script
Validates that all muk_web modules have been properly customized with OSUS branding
"""

import os
import re
from pathlib import Path

# OSUS Brand Colors
OSUS_COLORS = {
    'maroon': '#800020',
    'gold': '#FFD700',
    'light_maroon': '#A62939',
    'dark_maroon': '#600018',
}

# Base path
BASE_PATH = Path(__file__).parent

# Modules to validate
MODULES = [
    'muk_web_colors',
    'muk_web_theme',
    'muk_web_chatter',
    'muk_web_dialog',
]

def check_manifest_branding(module_path):
    """Check if manifest has OSUS branding"""
    manifest_path = module_path / '__manifest__.py'
    if not manifest_path.exists():
        return False, "Manifest file not found"
    
    content = manifest_path.read_text()
    
    checks = {
        'OSUS in name': 'OSUS Properties' in content,
        'Author updated': "'author': 'OSUS Properties'" in content,
        'Website updated': "'website': 'https://osusproperties.com'" in content,
    }
    
    failed = [k for k, v in checks.items() if not v]
    if failed:
        return False, f"Missing: {', '.join(failed)}"
    
    return True, "All branding present"

def check_color_usage(module_path):
    """Check if OSUS colors are used in SCSS files"""
    scss_files = list(module_path.rglob('*.scss'))
    
    if not scss_files:
        return None, "No SCSS files found"
    
    found_colors = []
    for scss_file in scss_files:
        content = scss_file.read_text().lower()
        for color_name, color_code in OSUS_COLORS.items():
            if color_code.lower() in content:
                found_colors.append(color_name)
    
    if found_colors:
        return True, f"OSUS colors found: {', '.join(set(found_colors))}"
    
    return False, "No OSUS colors detected"

def validate_module(module_name):
    """Validate a single module"""
    module_path = BASE_PATH / module_name
    
    print(f"\n{'='*60}")
    print(f"Validating: {module_name}")
    print(f"{'='*60}")
    
    if not module_path.exists():
        print(f"❌ Module directory not found: {module_path}")
        return False
    
    # Check manifest branding
    manifest_ok, manifest_msg = check_manifest_branding(module_path)
    print(f"\n📄 Manifest Branding:")
    print(f"  {'✅' if manifest_ok else '❌'} {manifest_msg}")
    
    # Check color usage
    colors_ok, colors_msg = check_color_usage(module_path)
    if colors_ok is not None:
        print(f"\n🎨 Color Usage:")
        print(f"  {'✅' if colors_ok else '❌'} {colors_msg}")
    
    return manifest_ok and (colors_ok or colors_ok is None)

def main():
    """Main validation routine"""
    print("="*60)
    print("OSUS Properties Web Theme Validation")
    print("="*60)
    print(f"\nBase Path: {BASE_PATH}")
    print(f"Modules to validate: {len(MODULES)}")
    print(f"\nOSUS Brand Colors:")
    for name, code in OSUS_COLORS.items():
        print(f"  - {name}: {code}")
    
    results = {}
    for module in MODULES:
        results[module] = validate_module(module)
    
    # Summary
    print(f"\n{'='*60}")
    print("VALIDATION SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for module, result in results.items():
        status = '✅ PASS' if result else '❌ FAIL'
        print(f"{status} - {module}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} modules passed validation")
    print(f"{'='*60}")
    
    if passed == total:
        print("\n🎉 All modules successfully customized with OSUS branding!")
        return 0
    else:
        print("\n⚠️ Some modules need attention. Please review the errors above.")
        return 1

if __name__ == '__main__':
    exit(main())
