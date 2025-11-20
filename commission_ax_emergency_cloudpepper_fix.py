#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Commission AX CloudPepper Emergency Fix
Addresses the critical FileNotFoundError for ir.model.access.csv
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_emergency_deployment():
    """Create emergency deployment package for CloudPepper"""
    print("COMMISSION AX CLOUDPEPPER EMERGENCY FIX")
    print("=" * 45)
    
    # Create deployment directory
    deploy_dir = Path("commission_ax_emergency_deploy") 
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    # Copy entire commission_ax directory 
    source_dir = Path("commission_ax")
    if not source_dir.exists():
        print("ERROR: commission_ax directory not found!")
        return False
    
    # Copy the module
    shutil.copytree(source_dir, deploy_dir / "commission_ax")
    
    # Create ZIP for easy upload
    zip_path = Path("commission_ax_emergency_fix.zip")
    if zip_path.exists():
        os.remove(zip_path)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(deploy_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(deploy_dir)
                zf.write(file_path, arcname)
    
    # Verify critical files are included
    critical_files = [
        "commission_ax/__manifest__.py",
        "commission_ax/security/ir.model.access.csv", 
        "commission_ax/security/security.xml",
        "commission_ax/models/commission_ax.py"
    ]
    
    print("Verifying critical files in package:")
    all_present = True
    for file_path in critical_files:
        full_path = deploy_dir / file_path
        if full_path.exists():
            print(f"OK: {file_path}")
        else:
            print(f"MISSING: {file_path}")
            all_present = False
    
    # Create deployment instructions
    instructions = deploy_dir / "DEPLOYMENT_INSTRUCTIONS.txt"
    with open(instructions, 'w', encoding='utf-8') as f:
        f.write("""COMMISSION AX EMERGENCY DEPLOYMENT INSTRUCTIONS

ISSUE: FileNotFoundError: File not found: commission_ax/security/ir.model.access.csv

SOLUTION: This package contains a fixed commission_ax module with proper security files.

DEPLOYMENT STEPS:
1. Stop Odoo service on CloudPepper server
2. Navigate to addons directory 
3. Remove existing commission_ax folder (if present)
4. Upload commission_ax_emergency_fix.zip to server
5. Extract: unzip commission_ax_emergency_fix.zip
6. Set proper permissions: chown -R odoo:odoo commission_ax
7. Restart Odoo service
8. Update module list in Odoo interface
9. Install/Update commission_ax module

VERIFICATION:
- Check that commission_ax/security/ir.model.access.csv exists
- Verify file has proper CSV format with header row
- Confirm security/security.xml is present
- Test module installation in Odoo

If the error persists, check file permissions and encoding.
All files in this package use UTF-8 encoding.
""")
    
    print(f"\nDEPLOYMENT PACKAGE CREATED: {zip_path}")
    print(f"SIZE: {zip_path.stat().st_size / 1024:.1f} KB")
    
    if all_present:
        print("STATUS: READY FOR CLOUDPEPPER DEPLOYMENT")
        print("\nUPLOAD commission_ax_emergency_fix.zip TO CLOUDPEPPER")
        print("EXTRACT AND RESTART ODOO TO FIX THE ERROR")
    else:
        print("STATUS: SOME CRITICAL FILES MISSING")
        
    return all_present

if __name__ == "__main__":
    success = create_emergency_deployment()
    if success:
        print("\nEMERGENCY FIX PACKAGE READY!")
    else:
        print("\nERROR CREATING PACKAGE!")
