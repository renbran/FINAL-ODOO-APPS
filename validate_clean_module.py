#!/usr/bin/env python3
"""
Final Production Readiness Check for account_payment_final module
"""

import os
import glob

def validate_clean_module():
    """Validate that the module is clean and production-ready"""
    print("🔍 Production Readiness Validation")
    print("=" * 50)
    
    base_path = "account_payment_final"
    issues = []
    
    # 1. Check for development artifacts
    dev_artifacts = [
        '**/__pycache__',
        '**/*.pyc',
        '**/*.pyo',
        '**/*.backup',
        '**/*.bak',
        '**/*~',
        '**/*.swp',
        '**/*.tmp',
        '**/test_*.py',
        '**/*_test.py',
        '**/debug*.py',
        '**/temp*.py'
    ]
    
    print("🧹 Checking for development artifacts...")
    found_artifacts = False
    for pattern in dev_artifacts:
        matches = glob.glob(os.path.join(base_path, pattern), recursive=True)
        if matches:
            print(f"  ❌ Found {pattern}: {matches}")
            issues.extend(matches)
            found_artifacts = True
    
    if not found_artifacts:
        print("  ✅ No development artifacts found")
    
    # 2. Check for proper file structure
    print("\n📁 Checking module structure...")
    required_files = [
        '__init__.py',
        '__manifest__.py',
        'models/__init__.py',
        'security/ir.model.access.csv',
        'security/payment_security.xml'
    ]
    
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ Missing: {file_path}")
            issues.append(f"Missing required file: {file_path}")
    
    # 3. Check for empty directories
    print("\n📂 Checking for empty directories...")
    empty_dirs = []
    for root, dirs, files in os.walk(base_path):
        if not dirs and not files:
            empty_dirs.append(root)
    
    if empty_dirs:
        for empty_dir in empty_dirs:
            print(f"  ⚠️ Empty directory: {empty_dir}")
    else:
        print("  ✅ No empty directories found")
    
    # 4. Count files by type
    print("\n📊 File inventory:")
    file_types = {}
    total_files = 0
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            total_files += 1
            ext = os.path.splitext(file)[1].lower()
            if not ext:
                ext = 'no_extension'
            file_types[ext] = file_types.get(ext, 0) + 1
    
    for ext, count in sorted(file_types.items()):
        print(f"  {ext}: {count} files")
    
    print(f"  Total files: {total_files}")
    
    # 5. Check manifest dependencies
    print("\n📋 Checking manifest...")
    manifest_path = os.path.join(base_path, '__manifest__.py')
    try:
        with open(manifest_path, 'r') as f:
            manifest_content = f.read()
        
        if "'installable': True" in manifest_content:
            print("  ✅ Module is marked as installable")
        else:
            print("  ❌ Module is not marked as installable")
            issues.append("Module not marked as installable")
        
        if "views/payment_actions_minimal.xml" in manifest_content:
            print("  ✅ Actions file is included")
        else:
            print("  ❌ Actions file not included")
            issues.append("Actions file not included in manifest")
            
    except Exception as e:
        print(f"  ❌ Error reading manifest: {e}")
        issues.append(f"Cannot read manifest: {e}")
    
    # 6. Final assessment
    print("\n" + "=" * 50)
    print("📊 PRODUCTION READINESS ASSESSMENT")
    print("=" * 50)
    
    if not issues:
        print("🎉 MODULE IS PRODUCTION READY!")
        print("✅ Clean structure - no development artifacts")
        print("✅ All required files present")
        print("✅ Proper configuration in manifest")
        print("✅ Ready for deployment")
        
        # Show clean structure summary
        print(f"\n📈 Module Statistics:")
        print(f"  • Total files: {total_files}")
        print(f"  • Python files: {file_types.get('.py', 0)}")
        print(f"  • XML files: {file_types.get('.xml', 0)}")
        print(f"  • CSS/SCSS files: {file_types.get('.css', 0) + file_types.get('.scss', 0)}")
        print(f"  • JS files: {file_types.get('.js', 0)}")
        
    else:
        print(f"❌ {len(issues)} ISSUES FOUND:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print("\n🔧 Please resolve these issues before deployment")
    
    return len(issues) == 0

if __name__ == "__main__":
    validate_clean_module()
