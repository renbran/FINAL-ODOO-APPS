#!/usr/bin/env python3
"""
Commission AX CloudPepper Emergency Deployment Package Creator
Creates a clean deployment package for CloudPepper hosting
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_cloudpepper_deployment_package():
    """Create a clean deployment package for CloudPepper"""
    print("📦 Creating Commission AX CloudPepper Deployment Package...")
    
    # Source and destination paths
    source_dir = Path("commission_ax")
    package_dir = Path("commission_ax_cloudpepper_deploy")
    zip_file = Path("commission_ax_cloudpepper_ready.zip")
    
    # Clean up any existing package
    if package_dir.exists():
        shutil.rmtree(package_dir)
    if zip_file.exists():
        os.remove(zip_file)
    
    # Create clean package directory
    package_dir.mkdir()
    
    # Essential files to include
    essential_files = [
        "__manifest__.py",
        "__init__.py",
        "models/__init__.py",
        "models/commission_ax.py",
        "models/sale_order.py", 
        "models/purchase_order.py",
        "models/account_move.py",
        "models/account_payment.py",
        "models/cloudpepper_compatibility.py",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/commission_ax_views.xml",
        "views/sale_order.xml",
        "views/purchase_order_views.xml",
        "data/commission_data.xml",
        "data/commission_demo_data.xml",
        "data/commission_email_templates.xml",
        "static/src/js/cloudpepper_compatibility_patch.js"
    ]
    
    # Copy essential files
    copied_files = []
    missing_files = []
    
    for file_path in essential_files:
        source_file = source_dir / file_path
        dest_file = package_dir / file_path
        
        if source_file.exists():
            # Create directory if needed
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_file, dest_file)
            copied_files.append(file_path)
            print(f"✅ Copied: {file_path}")
        else:
            missing_files.append(file_path)
            print(f"⚠️ Missing: {file_path}")
    
    # Create ZIP package
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(package_dir)
                zf.write(file_path, f"commission_ax/{arcname}")
    
    print(f"\n📦 Package created: {zip_file}")
    print(f"✅ Files included: {len(copied_files)}")
    if missing_files:
        print(f"⚠️ Files missing: {len(missing_files)}")
        for missing in missing_files:
            print(f"   - {missing}")
    
    # Create deployment instructions
    instructions_file = package_dir.parent / "COMMISSION_AX_CLOUDPEPPER_DEPLOYMENT_INSTRUCTIONS.txt"
    with open(instructions_file, 'w') as f:
        f.write("""COMMISSION AX CLOUDPEPPER DEPLOYMENT INSTRUCTIONS
=================================================

EMERGENCY DEPLOYMENT PACKAGE FOR CLOUDPEPPER
Module: commission_ax v17.0.2.0.0
Date: 2024-01-XX

DEPLOYMENT STEPS:
1. Stop Odoo service on CloudPepper
2. Remove existing commission_ax module folder (if any)
3. Upload commission_ax_cloudpepper_ready.zip to CloudPepper
4. Extract in addons directory
5. Restart Odoo service
6. Update module list in Odoo
7. Install/Update commission_ax module

CRITICAL FILES INCLUDED:
✅ __manifest__.py (with all dependencies)
✅ security/ir.model.access.csv (fixed CSV format)
✅ security/security.xml (group definitions)
✅ All model files with CloudPepper compatibility
✅ All view files with optimized field access
✅ Data files with sequences and templates
✅ JavaScript compatibility patch

TROUBLESHOOTING:
- If file not found errors: Check file permissions in CloudPepper
- If CSV format errors: All security files use UTF-8 encoding
- If JavaScript errors: CloudPepper compatibility patch handles them
- If field errors: cloudpepper_compatibility.py provides missing fields

POST-DEPLOYMENT VERIFICATION:
1. Check Odoo logs for errors
2. Access Commission menu in Sales/CRM
3. Create test commission record
4. Verify state transitions work
5. Test smart button navigation

SUPPORT:
For deployment issues, check the cloudpepper_compatibility_patch.js
console output for detailed error information.
""")
    
    print(f"✅ Instructions created: {instructions_file}")
    
    return zip_file, len(copied_files), len(missing_files)

def main():
    """Main deployment package creation"""
    print("🚀 Commission AX CloudPepper Emergency Deployment")
    print("=" * 50)
    
    if not Path("commission_ax").exists():
        print("❌ commission_ax directory not found!")
        return False
    
    try:
        zip_file, copied, missing = create_cloudpepper_deployment_package()
        
        print("\n" + "=" * 50)
        print("🎉 DEPLOYMENT PACKAGE READY!")
        print(f"📦 Package: {zip_file}")
        print(f"✅ Files: {copied} included")
        if missing > 0:
            print(f"⚠️ Missing: {missing} files")
        
        print("\n🚀 NEXT STEPS:")
        print("1. Upload commission_ax_cloudpepper_ready.zip to CloudPepper")
        print("2. Extract in addons directory")
        print("3. Restart Odoo and update module")
        print("4. This should resolve the FileNotFoundError")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating package: {e}")
        return False

if __name__ == "__main__":
    main()
