#!/usr/bin/env python3
"""
Module Cleanup Script for account_payment_final
Removes test files, pycache, and irrelevant files for production deployment
"""

import os
import shutil
import glob

def cleanup_module():
    """Clean up the account_payment_final module"""
    print("🧹 Cleaning up account_payment_final module...")
    print("=" * 50)
    
    base_path = "account_payment_final"
    files_removed = 0
    dirs_removed = 0
    
    # 1. Remove __pycache__ directories
    pycache_dirs = []
    for root, dirs, files in os.walk(base_path):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            pycache_dirs.append(pycache_path)
    
    for pycache_dir in pycache_dirs:
        try:
            shutil.rmtree(pycache_dir)
            print(f"✅ Removed: {pycache_dir}")
            dirs_removed += 1
        except Exception as e:
            print(f"❌ Error removing {pycache_dir}: {e}")
    
    # 2. Remove .pyc files
    pyc_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.pyc'):
                pyc_files.append(os.path.join(root, file))
    
    for pyc_file in pyc_files:
        try:
            os.remove(pyc_file)
            print(f"✅ Removed: {pyc_file}")
            files_removed += 1
        except Exception as e:
            print(f"❌ Error removing {pyc_file}: {e}")
    
    # 3. Remove backup files
    backup_patterns = ['*.backup', '*.bak', '*~', '*.swp', '*.tmp']
    for pattern in backup_patterns:
        backup_files = []
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith(pattern.replace('*', '')):
                    backup_files.append(os.path.join(root, file))
        
        for backup_file in backup_files:
            try:
                os.remove(backup_file)
                print(f"✅ Removed: {backup_file}")
                files_removed += 1
            except Exception as e:
                print(f"❌ Error removing {backup_file}: {e}")
    
    # 4. Remove alternative manifest files
    alt_manifests = [
        os.path.join(base_path, '__manifest_minimal.py'),
        os.path.join(base_path, '__manifest_backup.py'),
        os.path.join(base_path, '__manifest_old.py'),
    ]
    
    for manifest in alt_manifests:
        if os.path.exists(manifest):
            try:
                os.remove(manifest)
                print(f"✅ Removed: {manifest}")
                files_removed += 1
            except Exception as e:
                print(f"❌ Error removing {manifest}: {e}")
    
    # 5. Remove development/testing artifacts
    dev_files = [
        os.path.join(base_path, 'test.py'),
        os.path.join(base_path, 'debug.py'),
        os.path.join(base_path, 'temp.py'),
    ]
    
    for dev_file in dev_files:
        if os.path.exists(dev_file):
            try:
                os.remove(dev_file)
                print(f"✅ Removed: {dev_file}")
                files_removed += 1
            except Exception as e:
                print(f"❌ Error removing {dev_file}: {e}")
    
    # 6. Clean empty directories (except required structure)
    required_dirs = [
        'models', 'views', 'security', 'data', 'reports', 
        'controllers', 'static', 'static/src', 'demo'
    ]
    
    for root, dirs, files in os.walk(base_path, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            rel_path = os.path.relpath(dir_path, base_path)
            
            # Skip required directories
            if rel_path in required_dirs or any(req in rel_path for req in required_dirs):
                continue
            
            # Remove if empty
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    print(f"✅ Removed empty directory: {dir_path}")
                    dirs_removed += 1
            except Exception as e:
                pass  # Directory not empty or permission issue
    
    print("\n" + "=" * 50)
    print("🎉 Cleanup Complete!")
    print(f"📊 Files removed: {files_removed}")
    print(f"📊 Directories removed: {dirs_removed}")
    
    # 7. Show current module structure
    print("\n📋 Current module structure:")
    show_clean_structure(base_path)
    
    return files_removed + dirs_removed > 0

def show_clean_structure(base_path):
    """Show the clean module structure"""
    for root, dirs, files in os.walk(base_path):
        level = root.replace(base_path, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if not file.startswith('.') and not file.endswith('.pyc'):
                print(f"{subindent}{file}")

if __name__ == "__main__":
    cleanup_module()
