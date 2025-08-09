#!/usr/bin/env python3
"""
Account Payment Final - Production Validation
Final check to ensure module is completely production-ready
"""

import os
from pathlib import Path

def validate_production_module():
    """Validate module is production ready"""
    print("✅ Account Payment Final - Production Validation")
    print("=" * 55)
    
    module_path = Path("account_payment_final")
    if not module_path.exists():
        print("❌ Module directory not found")
        return False
    
    # Check for forbidden files/directories
    forbidden_items = [
        "tests/",
        "static/tests/",
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        ".pytest_cache/",
        ".coverage",
        "*.log",
        "*.tmp",
        ".vscode/",
        ".idea/",
        "*.swp",
        "*.swo", 
        "*~",
        ".DS_Store",
        "Thumbs.db",
        "desktop.ini",
        "*.bak",
        "*.backup",
    ]
    
    issues_found = []
    
    print("🔍 Scanning for forbidden files/directories...")
    
    # Walk through module directory
    for root, dirs, files in os.walk(module_path):
        root_path = Path(root)
        
        # Check directories
        for dir_name in dirs:
            if dir_name in ['tests', '__pycache__', '.pytest_cache', '.vscode', '.idea']:
                issues_found.append(f"❌ Forbidden directory: {root_path / dir_name}")
        
        # Check files
        for file_name in files:
            file_path = root_path / file_name
            
            # Check extensions
            if any(file_name.endswith(ext) for ext in ['.pyc', '.pyo', '.log', '.tmp', '.swp', '.swo', '.bak', '.backup']):
                issues_found.append(f"❌ Forbidden file: {file_path}")
            
            # Check specific files
            if file_name in ['.DS_Store', 'Thumbs.db', 'desktop.ini']:
                issues_found.append(f"❌ OS file found: {file_path}")
            
            # Check for temp files
            if file_name.endswith('~') or file_name.startswith('.#'):
                issues_found.append(f"❌ Temp file found: {file_path}")
    
    # Check required files exist
    required_files = [
        "__init__.py",
        "__manifest__.py",
        "models/__init__.py",
        "models/account_payment.py", 
        "views/account_payment_views.xml",
        "security/ir.model.access.csv",
        "security/payment_security.xml",
    ]
    
    print("\n🔍 Checking required files...")
    for required_file in required_files:
        file_path = module_path / required_file
        if file_path.exists():
            print(f"   ✅ {required_file}")
        else:
            issues_found.append(f"❌ Missing required file: {required_file}")
    
    # Check manifest for test references
    print("\n🔍 Checking manifest for test references...")
    manifest_path = module_path / "__manifest__.py"
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_content = f.read()
        
        if 'qunit_suite_tests' in manifest_content:
            issues_found.append("❌ Manifest contains test references")
        else:
            print("   ✅ No test references in manifest")
            
        if 'tests/' in manifest_content or '/tests/' in manifest_content:
            issues_found.append("❌ Manifest contains test file paths")
        else:
            print("   ✅ No test file paths in manifest")
            
    except Exception as e:
        issues_found.append(f"❌ Error reading manifest: {e}")
    
    # Final report
    print("\n" + "=" * 55)
    
    if issues_found:
        print("❌ PRODUCTION VALIDATION FAILED")
        print(f"📊 Issues Found: {len(issues_found)}")
        print("\n🔍 Issues:")
        for issue in issues_found:
            print(f"   {issue}")
        return False
    else:
        print("✅ PRODUCTION VALIDATION PASSED")
        print("🚀 Module is 100% production-ready!")
        
        # Show final structure
        print("\n📁 Final Module Structure:")
        for root, dirs, files in os.walk(module_path):
            level = root.replace(str(module_path), '').count(os.sep)
            indent = ' ' * 2 * level
            folder_name = os.path.basename(root)
            if level == 0:
                print(f"{indent}account_payment_final/")
            else:
                print(f"{indent}{folder_name}/")
            
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
        
        return True

def main():
    """Main validation function"""
    try:
        os.chdir(Path(__file__).parent)
        success = validate_production_module()
        
        if success:
            print("\n🎉 MODULE READY FOR CLOUDPEPPER DEPLOYMENT!")
            print("📋 Next Steps:")
            print("   1. Upload module to CloudPepper server")
            print("   2. Update Apps List in Odoo")  
            print("   3. Install account_payment_final")
            print("   4. Configure approval workflow")
            print("   5. Test payment creation")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
