#!/usr/bin/env python3
"""
Module Structure Validation Script
Validates that all module directories have proper structure and required files
"""

import os
from pathlib import Path

def validate_module_structure(module_path):
    """Validate a single module's structure"""
    issues = []
    
    # Check for required files
    required_files = ['__init__.py', '__manifest__.py']
    
    for req_file in required_files:
        file_path = module_path / req_file
        if not file_path.exists():
            issues.append(f"Missing required file: {req_file}")
        elif file_path.stat().st_size == 0:
            issues.append(f"Empty required file: {req_file}")
    
    # Check manifest syntax if it exists
    manifest_path = module_path / '__manifest__.py'
    if manifest_path.exists() and manifest_path.stat().st_size > 0:
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
                compile(content, str(manifest_path), 'exec')
        except SyntaxError as e:
            issues.append(f"Syntax error in __manifest__.py: {e}")
        except Exception as e:
            issues.append(f"Error reading __manifest__.py: {e}")
    
    return issues

def find_potential_modules():
    """Find all potential module directories"""
    current_dir = Path('.')
    potential_modules = []
    
    for item in current_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            # Skip known non-module directories
            skip_dirs = {
                'deployment_package', 'database_cleanup', 
                'REMOVED_MODULES_BACKUP_20250812_074936'
            }
            if item.name not in skip_dirs:
                # Check if it looks like a module (has Python files or views)
                has_python = any(item.rglob('*.py'))
                has_views = any(item.rglob('views/*.xml'))
                has_manifest = (item / '__manifest__.py').exists()
                
                if has_python or has_views or has_manifest:
                    potential_modules.append(item)
    
    return potential_modules

def main():
    """Main validation function"""
    print("=== Module Structure Validation ===\n")
    
    # Change to the correct directory
    os.chdir('d:\\RUNNING APPS\\ready production\\latest\\odoo17_final')
    
    potential_modules = find_potential_modules()
    
    print(f"Found {len(potential_modules)} potential modules to validate:\n")
    
    total_issues = 0
    problematic_modules = []
    
    for module_path in potential_modules:
        print(f"Validating {module_path.name}...")
        issues = validate_module_structure(module_path)
        
        if issues:
            print(f"  ❌ Issues found:")
            for issue in issues:
                print(f"    - {issue}")
            total_issues += len(issues)
            problematic_modules.append(module_path.name)
        else:
            print(f"  ✅ Module structure is valid")
        print()
    
    # Summary
    print("=== VALIDATION SUMMARY ===")
    print(f"Modules checked: {len(potential_modules)}")
    print(f"Total issues found: {total_issues}")
    
    if problematic_modules:
        print(f"Problematic modules: {', '.join(problematic_modules)}")
        print("\n⚠️  These modules may cause registry loading errors!")
        print("💡 Consider fixing missing files or removing incomplete modules.")
    else:
        print("🎉 All modules have valid structure!")
        print("✅ Ready for Odoo deployment")
    
    return total_issues == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
