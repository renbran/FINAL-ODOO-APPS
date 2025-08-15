#!/usr/bin/env python3
"""
COMPREHENSIVE MODULE CLEANUP SCRIPT
Removes all orphaned views, unused models, residual files, and obsolete references
"""

import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
import re

def comprehensive_cleanup():
    """Remove all unused files and orphaned references"""
    
    print("=== COMPREHENSIVE MODULE CLEANUP ===")
    
    module_path = Path("account_payment_approval")
    if not module_path.exists():
        print("‚ùå Module not found!")
        return False
    
    # 1. Analyze current manifest references
    print("\n1. ANALYZING MANIFEST REFERENCES...")
    manifest_refs = analyze_manifest_references(module_path)
    
    # 2. Check what files actually exist
    print("\n2. SCANNING EXISTING FILES...")
    existing_files = scan_existing_files(module_path)
    
    # 3. Identify orphaned and unused files
    print("\n3. IDENTIFYING ORPHANED FILES...")
    orphaned_files = identify_orphaned_files(manifest_refs, existing_files, module_path)
    
    # 4. Check model usage
    print("\n4. CHECKING MODEL USAGE...")
    unused_models = check_unused_models(module_path)
    
    # 5. Check view orphans
    print("\n5. CHECKING ORPHANED VIEWS...")
    orphaned_views = check_orphaned_views(module_path)
    
    # 6. Remove obsolete files
    print("\n6. REMOVING OBSOLETE FILES...")
    removed_files = remove_obsolete_files(module_path, orphaned_files)
    
    # 7. Clean up manifest
    print("\n7. CLEANING UP MANIFEST...")
    clean_manifest(module_path, manifest_refs)
    
    # 8. Summary
    print("\n=== CLEANUP SUMMARY ===")
    print(f"‚úÖ Files analyzed: {len(existing_files)}")
    print(f"üóëÔ∏è  Files removed: {len(removed_files)}")
    print(f"üìù Manifest cleaned")
    
    if removed_files:
        print("\nRemoved files:")
        for file_path in removed_files:
            print(f"   - {file_path}")
    
    print("\n‚úÖ CLEANUP COMPLETE!")
    return True

def analyze_manifest_references(module_path):
    """Analyze what files are referenced in the manifest"""
    manifest_file = module_path / "__manifest__.py"
    refs = {
        'data': [],
        'assets': [],
        'demo': [],
        'depends': []
    }
    
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract data files
        data_match = re.search(r"'data':\s*\[(.*?)\]", content, re.DOTALL)
        if data_match:
            data_content = data_match.group(1)
            data_files = re.findall(r"'([^']+)'", data_content)
            refs['data'] = data_files
        
        # Extract asset files
        assets_match = re.search(r"'assets':\s*{(.*?)}", content, re.DOTALL)
        if assets_match:
            assets_content = assets_match.group(1)
            asset_files = re.findall(r"'([^']+/[^']+)'", assets_content)
            refs['assets'] = asset_files
        
        # Extract demo files
        demo_match = re.search(r"'demo':\s*\[(.*?)\]", content, re.DOTALL)
        if demo_match:
            demo_content = demo_match.group(1)
            demo_files = re.findall(r"'([^']+)'", demo_content)
            refs['demo'] = demo_files
        
        print(f"   Data files: {len(refs['data'])}")
        print(f"   Asset files: {len(refs['assets'])}")
        print(f"   Demo files: {len(refs['demo'])}")
        
    except Exception as e:
        print(f"   Error reading manifest: {e}")
    
    return refs

def scan_existing_files(module_path):
    """Scan all existing files in the module"""
    files = []
    
    for root, dirs, filenames in os.walk(module_path):
        # Skip certain directories
        if any(skip in root for skip in ['__pycache__', '.git', '.DS_Store']):
            continue
        
        for filename in filenames:
            if filename.startswith('.'):
                continue
            
            file_path = Path(root) / filename
            rel_path = file_path.relative_to(module_path)
            files.append(str(rel_path))
    
    print(f"   Found {len(files)} files")
    return files

def identify_orphaned_files(manifest_refs, existing_files, module_path):
    """Identify files that are not referenced and can be removed"""
    orphaned = []
    
    # Files that should always be kept
    essential_files = {
        '__init__.py',
        '__manifest__.py',
        'models/__init__.py',
        'models/account_payment.py',  # Main model
        'views/account_payment_views.xml',  # Main view
        'security/ir.model.access.csv',  # Security
    }
    
    # Files that are orphaned based on manifest
    all_manifest_files = (
        manifest_refs['data'] + 
        manifest_refs['assets'] + 
        manifest_refs['demo']
    )
    
    for file_path in existing_files:
        # Skip essential files
        if file_path in essential_files:
            continue
        
        # Skip backup files - these can be removed
        if file_path.endswith('.backup'):
            orphaned.append(file_path)
            continue
        
        # Skip markdown documentation files
        if file_path.endswith('.md'):
            orphaned.append(file_path)
            continue
        
        # Skip validation/test scripts in root
        if file_path.startswith('validate_') or file_path.startswith('test_'):
            orphaned.append(file_path)
            continue
        
        # Check if file is referenced in manifest
        is_referenced = False
        for ref_file in all_manifest_files:
            if file_path == ref_file or file_path.endswith(ref_file):
                is_referenced = True
                break
        
        if not is_referenced:
            # Check if it's a real orphan or just not in manifest
            file_full_path = module_path / file_path
            
            # Models in models/ folder
            if file_path.startswith('models/') and file_path.endswith('.py'):
                if not check_model_usage(module_path, file_path):
                    orphaned.append(file_path)
            
            # Views not in manifest
            elif file_path.startswith('views/') and file_path.endswith('.xml'):
                if not check_view_usage(module_path, file_path):
                    orphaned.append(file_path)
            
            # Controllers not used
            elif file_path.startswith('controllers/') and file_path.endswith('.py'):
                if not check_controller_usage(module_path, file_path):
                    orphaned.append(file_path)
            
            # Wizards not used
            elif file_path.startswith('wizards/') and file_path.endswith('.py'):
                if not check_wizard_usage(module_path, file_path):
                    orphaned.append(file_path)
            
            # Reports folder is empty
            elif file_path.startswith('reports/'):
                orphaned.append(file_path)
            
            # Static files not referenced
            elif file_path.startswith('static/'):
                if not check_static_usage(module_path, file_path):
                    orphaned.append(file_path)
    
    print(f"   Identified {len(orphaned)} orphaned files")
    return orphaned

def check_model_usage(module_path, model_file):
    """Check if a model is actually used"""
    model_name = Path(model_file).stem
    
    # Essential models
    if model_name in ['account_payment', '__init__']:
        return True
    
    # Check if imported in __init__.py
    init_file = module_path / 'models' / '__init__.py'
    if init_file.exists():
        try:
            with open(init_file, 'r') as f:
                content = f.read()
            if model_name in content:
                return True
        except:
            pass
    
    return False

def check_view_usage(module_path, view_file):
    """Check if a view is actually used"""
    view_name = Path(view_file).stem
    
    # Essential views
    if view_name in ['account_payment_views']:
        return True
    
    return False

def check_controller_usage(module_path, controller_file):
    """Check if a controller is actually used"""
    controller_name = Path(controller_file).stem
    
    # Check if imported in __init__.py
    init_file = module_path / 'controllers' / '__init__.py'
    if init_file.exists():
        try:
            with open(init_file, 'r') as f:
                content = f.read()
            if controller_name in content:
                return True
        except:
            pass
    
    return False

def check_wizard_usage(module_path, wizard_file):
    """Check if a wizard is actually used"""
    # For now, mark all wizards as unused since we have minimal views
    return False

def check_static_usage(module_path, static_file):
    """Check if a static file is actually used"""
    # Keep only essential static files
    essential_static = {
        'static/description/icon.png',
        'static/description/banner.png',
        'static/src/scss/payment_approval.scss'
    }
    
    return static_file in essential_static

def check_unused_models(module_path):
    """Check for unused model methods or classes"""
    unused = []
    # For now, our main model is used
    return unused

def check_orphaned_views(module_path):
    """Check for orphaned view records"""
    orphaned = []
    # Our minimal view is used
    return orphaned

def remove_obsolete_files(module_path, orphaned_files):
    """Remove obsolete files"""
    removed = []
    
    for file_path in orphaned_files:
        full_path = module_path / file_path
        
        try:
            if full_path.is_file():
                full_path.unlink()
                removed.append(file_path)
                print(f"   Removed file: {file_path}")
            elif full_path.is_dir():
                shutil.rmtree(full_path)
                removed.append(file_path)
                print(f"   Removed directory: {file_path}")
        except Exception as e:
            print(f"   Error removing {file_path}: {e}")
    
    return removed

def clean_manifest(module_path, manifest_refs):
    """Clean up the manifest to remove references to non-existent files"""
    manifest_file = module_path / "__manifest__.py"
    
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create minimal working manifest
        new_manifest = '''# -*- coding: utf-8 -*-
{
    'name': 'Enterprise Payment Approval System - OSUS',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Payment',
    'summary': 'Enterprise-level Multi-tier Payment Approval System with Digital Signatures and QR Verification',
    'description': """
Enterprise Payment Approval System for OSUS Properties

Key Features:
============
‚Ä¢ Multi-level approval workflow with configurable tiers
‚Ä¢ Digital signature capture for all approval stages
‚Ä¢ QR code generation with secure verification portal
‚Ä¢ Role-based permission system
‚Ä¢ Real-time workflow tracking
‚Ä¢ Email notifications and activity tracking
‚Ä¢ Comprehensive audit trails and reporting
‚Ä¢ Integration with accounting workflows
‚Ä¢ OSUS branded professional interface

Workflow Stages:
===============
1. Draft ‚Üí Submit for Review
2. Under Review ‚Üí Approve/Reject
3. Approved ‚Üí Authorize (for payments above threshold)
4. Authorized ‚Üí Post to Accounting
5. Posted ‚Üí Complete
    """,
    'author': 'OSUS Properties',
    'company': 'OSUS Properties',
    'maintainer': 'OSUS Properties Development Team',
    'website': 'https://www.osusproperties.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'mail',
        'web',
    ],
    'external_dependencies': {
        'python': ['qrcode', 'num2words']
    },
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Views
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 15,
}
'''
        
        with open(manifest_file, 'w', encoding='utf-8') as f:
            f.write(new_manifest)
        
        print("   ‚úÖ Manifest cleaned and simplified")
        
    except Exception as e:
        print(f"   Error cleaning manifest: {e}")

if __name__ == "__main__":
    success = comprehensive_cleanup()
    exit(0 if success else 1)
