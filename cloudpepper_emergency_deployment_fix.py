#!/usr/bin/env python3
"""
CloudPepper Emergency Deployment Fix
Resolves SyntaxError issues during module installation
"""

import os
import shutil
import tempfile
import sys
from pathlib import Path

def clean_python_cache():
    """Remove all Python cache files."""
    print("🧹 Cleaning Python cache files...")
    
    cache_patterns = ['__pycache__', '*.pyc', '*.pyo']
    cleaned_count = 0
    
    for root, dirs, files in os.walk('.'):
        # Remove __pycache__ directories
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"  Removed: {pycache_path}")
                cleaned_count += 1
            except Exception as e:
                print(f"  Failed to remove {pycache_path}: {e}")
        
        # Remove .pyc and .pyo files
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"  Removed: {file_path}")
                    cleaned_count += 1
                except Exception as e:
                    print(f"  Failed to remove {file_path}: {e}")
    
    print(f"✅ Cleaned {cleaned_count} cache files")
    return cleaned_count

def validate_all_python_files():
    """Validate all Python files in the module."""
    print("\n🔍 Validating all Python files...")
    
    module_path = "order_status_override"
    if not os.path.exists(module_path):
        print(f"❌ Module not found: {module_path}")
        return False
    
    import ast
    all_valid = True
    file_count = 0
    
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                file_count += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    ast.parse(content)
                    print(f"  ✅ {file_path}")
                    
                except SyntaxError as e:
                    print(f"  ❌ {file_path}: SyntaxError at line {e.lineno}: {e.msg}")
                    all_valid = False
                except Exception as e:
                    print(f"  ❌ {file_path}: {e}")
                    all_valid = False
    
    print(f"\n📊 Validated {file_count} Python files")
    return all_valid

def create_clean_deployment_package():
    """Create a clean deployment package."""
    print("\n📦 Creating clean deployment package...")
    
    source_module = "order_status_override"
    temp_dir = tempfile.mkdtemp(prefix="osus_deploy_")
    
    try:
        # Copy module to temp directory
        temp_module = os.path.join(temp_dir, source_module)
        shutil.copytree(source_module, temp_module)
        
        # Clean the copied module
        for root, dirs, files in os.walk(temp_module):
            # Remove cache directories
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            # Remove cache files
            for file in files[:]:
                if file.endswith(('.pyc', '.pyo')):
                    os.remove(os.path.join(root, file))
        
        # Validate the clean module
        print(f"  📁 Clean package created at: {temp_module}")
        
        # Create deployment instructions
        instructions_file = os.path.join(temp_dir, "DEPLOYMENT_INSTRUCTIONS.txt")
        with open(instructions_file, 'w') as f:
            f.write("""
CLOUDPEPPER DEPLOYMENT INSTRUCTIONS
===================================

1. Upload the 'order_status_override' folder to CloudPepper
2. Ensure commission_ax module is installed first
3. Install the module via Apps menu
4. If errors persist, restart Odoo service

Module Details:
- Name: OSUS Enhanced Sales Order Workflow
- Version: 17.0.2.0.0
- Dependencies: sale, mail, commission_ax, account, web

Contact support if issues persist.
""")
        
        print(f"  📄 Instructions created: {instructions_file}")
        print(f"  🎯 Deployment package ready at: {temp_dir}")
        
        return temp_dir
        
    except Exception as e:
        print(f"  ❌ Failed to create package: {e}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return None

def emergency_manifest_fix():
    """Apply emergency fixes to manifest file."""
    print("\n🚑 Applying emergency manifest fixes...")
    
    manifest_path = "order_status_override/__manifest__.py"
    
    try:
        # Read current manifest
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create emergency backup
        backup_path = f"{manifest_path}.emergency_backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  📝 Emergency backup: {backup_path}")
        
        # Apply fixes
        fixed_content = content
        
        # Ensure clean line endings
        fixed_content = fixed_content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove any potential BOM
        if fixed_content.startswith('\ufeff'):
            fixed_content = fixed_content[1:]
        
        # Ensure proper formatting
        fixed_content = fixed_content.strip() + '\n'
        
        # Write fixed version
        with open(manifest_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(fixed_content)
        
        print("  ✅ Emergency fixes applied")
        
        # Validate the fix
        import ast
        ast.literal_eval(fixed_content)
        print("  ✅ Validation successful")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Emergency fix failed: {e}")
        return False

def main():
    """Main emergency deployment function."""
    print("🚨 CLOUDPEPPER EMERGENCY DEPLOYMENT FIX")
    print("=" * 80)
    
    success_count = 0
    total_steps = 4
    
    # Step 1: Clean cache
    if clean_python_cache() >= 0:
        success_count += 1
        print("✅ Step 1/4: Cache cleaning completed")
    else:
        print("❌ Step 1/4: Cache cleaning failed")
    
    # Step 2: Apply emergency manifest fix
    if emergency_manifest_fix():
        success_count += 1
        print("✅ Step 2/4: Emergency manifest fix completed")
    else:
        print("❌ Step 2/4: Emergency manifest fix failed")
    
    # Step 3: Validate Python files
    if validate_all_python_files():
        success_count += 1
        print("✅ Step 3/4: Python validation completed")
    else:
        print("❌ Step 3/4: Python validation failed")
    
    # Step 4: Create deployment package
    package_path = create_clean_deployment_package()
    if package_path:
        success_count += 1
        print("✅ Step 4/4: Deployment package created")
    else:
        print("❌ Step 4/4: Deployment package creation failed")
    
    # Final result
    print("\n" + "="*80)
    print(f"📊 Emergency fix completed: {success_count}/{total_steps} steps successful")
    
    if success_count == total_steps:
        print("🎉 ALL STEPS COMPLETED - Module ready for CloudPepper deployment!")
        if package_path:
            print(f"📦 Use deployment package at: {package_path}")
    else:
        print("⚠️  Some steps failed - manual intervention may be required")
    
    return 0 if success_count == total_steps else 1

if __name__ == "__main__":
    sys.exit(main())
