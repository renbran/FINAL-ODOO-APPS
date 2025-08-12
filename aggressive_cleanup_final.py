#!/usr/bin/env python3
"""
AGGRESSIVE MODULE CLEANUP - Remove ALL unused and orphaned files
Keep only the absolute minimum needed for the payment approval functionality
"""

import os
import shutil
from pathlib import Path

def aggressive_cleanup():
    """Remove all unnecessary files, keep only essential ones"""
    
    print("=== AGGRESSIVE MODULE CLEANUP ===")
    
    module_path = Path("account_payment_approval")
    if not module_path.exists():
        print("❌ Module not found!")
        return False
    
    # Define what to keep (essential files only)
    essential_files = {
        '__init__.py',
        '__manifest__.py',
        'models/__init__.py',
        'models/account_payment.py',
        'views/account_payment_views.xml',
        'security/ir.model.access.csv',
        'static/description/icon.png',  # If it exists
    }
    
    # Directories to completely remove
    dirs_to_remove = [
        'controllers',
        'data', 
        'reports',
        'static',
        'tests',
        'wizards',
        'demo'
    ]
    
    removed_files = []
    removed_dirs = []
    
    # 1. Remove entire directories
    print("\n1. REMOVING UNUSED DIRECTORIES...")
    for dir_name in dirs_to_remove:
        dir_path = module_path / dir_name
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                removed_dirs.append(dir_name)
                print(f"   ✅ Removed directory: {dir_name}")
            except Exception as e:
                print(f"   ❌ Error removing {dir_name}: {e}")
    
    # 2. Remove unused models
    print("\n2. REMOVING UNUSED MODELS...")
    models_dir = module_path / 'models'
    if models_dir.exists():
        for model_file in models_dir.glob('*.py'):
            rel_path = f"models/{model_file.name}"
            if rel_path not in essential_files:
                try:
                    model_file.unlink()
                    removed_files.append(rel_path)
                    print(f"   ✅ Removed model: {model_file.name}")
                except Exception as e:
                    print(f"   ❌ Error removing {model_file.name}: {e}")
    
    # 3. Remove unused security files
    print("\n3. CLEANING SECURITY DIRECTORY...")
    security_dir = module_path / 'security'
    if security_dir.exists():
        for security_file in security_dir.glob('*'):
            if security_file.name != 'ir.model.access.csv':
                try:
                    if security_file.is_file():
                        security_file.unlink()
                        removed_files.append(f"security/{security_file.name}")
                        print(f"   ✅ Removed security file: {security_file.name}")
                except Exception as e:
                    print(f"   ❌ Error removing {security_file.name}: {e}")
    
    # 4. Remove unused view files
    print("\n4. CLEANING VIEWS DIRECTORY...")
    views_dir = module_path / 'views'
    if views_dir.exists():
        for view_file in views_dir.glob('*'):
            if view_file.name != 'account_payment_views.xml':
                try:
                    view_file.unlink()
                    removed_files.append(f"views/{view_file.name}")
                    print(f"   ✅ Removed view file: {view_file.name}")
                except Exception as e:
                    print(f"   ❌ Error removing {view_file.name}: {e}")
    
    # 5. Update models/__init__.py to only import account_payment
    print("\n5. UPDATING MODELS __INIT__.PY...")
    models_init = module_path / 'models' / '__init__.py'
    if models_init.exists():
        try:
            with open(models_init, 'w', encoding='utf-8') as f:
                f.write('# -*- coding: utf-8 -*-\\nfrom . import account_payment\\n')
            print("   ✅ Updated models/__init__.py")
        except Exception as e:
            print(f"   ❌ Error updating models/__init__.py: {e}")
    
    # 6. Create minimal manifest
    print("\n6. CREATING MINIMAL MANIFEST...")
    create_minimal_manifest(module_path)
    
    # 7. Create minimal icon if it doesn't exist
    print("\n7. ENSURING DESCRIPTION ICON...")
    ensure_description_icon(module_path)
    
    # Summary
    print("\n=== AGGRESSIVE CLEANUP SUMMARY ===")
    print(f"🗑️  Directories removed: {len(removed_dirs)}")
    print(f"🗑️  Files removed: {len(removed_files)}")
    
    if removed_dirs:
        print("\\nRemoved directories:")
        for dir_name in removed_dirs:
            print(f"   - {dir_name}/")
    
    if removed_files:
        print("\\nRemoved files:")
        for file_name in removed_files:
            print(f"   - {file_name}")
    
    print("\\n✅ AGGRESSIVE CLEANUP COMPLETE!")
    print("\\nModule now contains only:")
    print("   - models/account_payment.py (main model)")
    print("   - views/account_payment_views.xml (main view)")
    print("   - security/ir.model.access.csv (access rights)")
    print("   - __manifest__.py (module definition)")
    print("   - __init__.py files")
    
    return True

def create_minimal_manifest(module_path):
    """Create the most minimal manifest possible"""
    manifest_content = '''# -*- coding: utf-8 -*-
{
    'name': 'Payment Approval System',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Payment Approval Workflow System',
    'description': """
Payment Approval System

Features:
• Multi-level payment approval workflow
• Digital signatures and QR verification
• Status tracking and audit trails
• OSUS Properties branding
    """,
    'author': 'OSUS Properties',
    'website': 'https://www.osusproperties.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
'''
    
    manifest_file = module_path / '__manifest__.py'
    try:
        with open(manifest_file, 'w', encoding='utf-8') as f:
            f.write(manifest_content)
        print("   ✅ Created minimal manifest")
    except Exception as e:
        print(f"   ❌ Error creating manifest: {e}")

def ensure_description_icon(module_path):
    """Ensure description directory and icon exist"""
    desc_dir = module_path / 'static' / 'description'
    desc_dir.mkdir(parents=True, exist_ok=True)
    
    icon_file = desc_dir / 'icon.png'
    if not icon_file.exists():
        # Create a simple placeholder icon (1x1 transparent PNG)
        png_data = b'\\x89PNG\\r\\n\\x1a\\n\\x00\\x00\\x00\\rIHDR\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x01\\x08\\x06\\x00\\x00\\x00\\x1f\\x15\\xc4\\x89\\x00\\x00\\x00\\nIDATx\\x9cc\\xf8\\x00\\x00\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00IEND\\xaeB`\\x82'
        try:
            with open(icon_file, 'wb') as f:
                f.write(png_data)
            print("   ✅ Created placeholder icon")
        except Exception as e:
            print(f"   ❌ Error creating icon: {e}")

if __name__ == "__main__":
    success = aggressive_cleanup()
    exit(0 if success else 1)
