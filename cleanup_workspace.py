#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Workspace Cleanup Script
Removes empty, deprecated, temporary, and garbage files
"""

import os
import glob
import shutil
from pathlib import Path

def cleanup_workspace():
    """Clean up the entire workspace"""
    
    print("üßπ Starting Comprehensive Workspace Cleanup...")
    
    root_dir = Path(".")
    removed_count = 0
    
    # Categories of files to remove
    cleanup_patterns = {
        "Empty Files": [],
        "Temporary Scripts": [
            "*_fix*.py",
            "*_test*.py", 
            "*validation*.py",
            "*_nuclear*.py",
            "*_emergency*.py",
            "*cleanup*.py",
            "extract_*",
            "quick_*",
            "simple_*",
            "final_*",
            "create_missing_*",
            "restore_*",
            "run_*"
        ],
        "Status/Documentation MD Files": [
            "*_FIX*.md",
            "*_COMPLETE*.md",
            "*_SUMMARY*.md", 
            "*_CRITICAL*.md",
            "*_RESOLVED*.md",
            "*_DEPLOYMENT*.md",
            "*CLOUDPEPPER*.md",
            "*NUCLEAR*.md",
            "*COMPREHENSIVE*.md",
            "*CHECKLIST*.md",
            "CRITICAL_*.md",
            "FIELD_*.md",
            "EMAIL_*.md",
            "HR_*.md",
            "PAYMENT_*.md",
            "SCSS_*.md",
            "SEARCHABLE_*.md"
        ],
        "Shell/Batch Scripts": [
            "*fix*.sh",
            "*emergency*.sh", 
            "*nuclear*.sh",
            "*cloudpepper*.sh",
            "*validation*.sh",
            "*test*.sh",
            "extract_*.bat",
            "*validation*.ps1",
            "*test*.ps1",
            "simple_*.ps1"
        ],
        "SQL Scripts": [
            "*cleanup*.sql",
            "*fix*.sql",
            "*nuclear*.sql"
        ],
        "Text Files": [
            "*.txt"
        ]
    }
    
    # Files to keep (important ones)
    keep_files = {
        "setup.bat",
        "setup.sh", 
        "Dockerfile",
        "docker-compose.yml",
        "validate_module_structure.py",
        "validate_payment_approval.py",
        "ACCOUNT_PAYMENT_APPROVAL_REBUILD_COMPLETE.md",
        "ODOO17_SYNTAX_GUIDELINES.md"
    }
    
    # Step 1: Remove empty files
    print("\nüóëÔ∏è  Removing empty files...")
    for file_path in root_dir.rglob("*"):
        if file_path.is_file() and file_path.stat().st_size == 0:
            if file_path.name not in keep_files:
                print(f"   Removing empty: {file_path}")
                file_path.unlink()
                removed_count += 1
    
    # Step 2: Remove files by patterns
    for category, patterns in cleanup_patterns.items():
        if patterns:
            print(f"\nüóëÔ∏è  Removing {category}...")
            for pattern in patterns:
                for file_path in root_dir.glob(pattern):
                    if file_path.is_file() and file_path.name not in keep_files:
                        print(f"   Removing: {file_path}")
                        file_path.unlink()
                        removed_count += 1
    
    # Step 3: Clean up account_payment_approval module empty files
    payment_module = root_dir / "account_payment_approval"
    if payment_module.exists():
        print(f"\nüßπ Cleaning account_payment_approval module...")
        
        # Remove empty files in module
        for file_path in payment_module.rglob("*"):
            if file_path.is_file() and file_path.stat().st_size == 0:
                # Keep essential empty __init__.py files
                if not (file_path.name == "__init__.py" and "models" in str(file_path.parent)):
                    print(f"   Removing empty module file: {file_path}")
                    file_path.unlink()
                    removed_count += 1
        
        # Remove specific garbage files
        garbage_files = [
            "FRONTEND_REORGANIZATION_COMPLETE.md",
            "JOURNAL_ENTRY_ENHANCEMENT_SUMMARY.md", 
            "MODERN_ASSET_MANAGEMENT.md",
            "validate_assets.py"
        ]
        
        for garbage_file in garbage_files:
            garbage_path = payment_module / garbage_file
            if garbage_path.exists():
                print(f"   Removing garbage: {garbage_path}")
                garbage_path.unlink()
                removed_count += 1
        
        # Remove empty directories
        for dir_path in payment_module.rglob("*"):
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                print(f"   Removing empty directory: {dir_path}")
                dir_path.rmdir()
    
    # Step 4: Remove __pycache__ directories
    print(f"\nüóëÔ∏è  Removing __pycache__ directories...")
    for pycache_dir in root_dir.rglob("__pycache__"):
        if pycache_dir.is_dir():
            print(f"   Removing: {pycache_dir}")
            shutil.rmtree(pycache_dir)
            removed_count += 1
    
    # Step 5: Remove .pyc files
    print(f"\nüóëÔ∏è  Removing .pyc files...")
    for pyc_file in root_dir.rglob("*.pyc"):
        print(f"   Removing: {pyc_file}")
        pyc_file.unlink()
        removed_count += 1
    
    print(f"\n‚úÖ Cleanup Complete!")
    print(f"üìä Total files/directories removed: {removed_count}")
    
    # Show what's left
    print(f"\nüìÇ Remaining files in root:")
    remaining_files = sorted([f.name for f in root_dir.iterdir() if f.is_file()])
    for remaining_file in remaining_files:
        print(f"   ‚úÖ {remaining_file}")
    
    print(f"\nüöÄ Workspace is now clean and production-ready!")

if __name__ == "__main__":
    cleanup_workspace()
