#!/usr/bin/env python3
"""
Style Compilation Error Diagnostic Tool
Comprehensive diagnosis and fix for Odoo style compilation issues
"""

import os
import json
import subprocess
from pathlib import Path

def diagnose_style_errors():
    """Comprehensive style error diagnosis"""
    print("🔍 Style Compilation Error Diagnosis")
    print("=" * 50)
    
    issues_found = []
    
    # Check 1: Module structure
    print("1️⃣  Checking Module Structure...")
    required_files = [
        "account_payment_final/__manifest__.py",
        "account_payment_final/__init__.py",
        "account_payment_final/static/src/scss/emergency_fix.scss"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            issues_found.append(f"Missing file: {file_path}")
    
    # Check 2: SCSS syntax validation
    print("\n2️⃣  Validating SCSS Syntax...")
    scss_files = list(Path("account_payment_final/static/src/scss").glob("**/*.scss"))
    
    for scss_file in scss_files:
        try:
            with open(scss_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Common SCSS issues
            if '//' in content and ':root' in content:
                print(f"   ⚠️  {scss_file.name}: May have CSS comment issues")
                issues_found.append(f"CSS comment syntax in {scss_file.name}")
            elif content.strip():
                print(f"   ✅ {scss_file.name}: Syntax OK")
            else:
                print(f"   ⚠️  {scss_file.name}: Empty file")
                
        except Exception as e:
            print(f"   ❌ {scss_file.name}: Error reading file - {e}")
            issues_found.append(f"File read error: {scss_file.name}")
    
    # Check 3: Asset configuration
    print("\n3️⃣  Checking Asset Configuration...")
    try:
        with open("account_payment_final/__manifest__.py", 'r') as f:
            manifest_content = f.read()
        
        if "'assets':" in manifest_content:
            print("   ✅ Assets section found")
            if "'web.assets_backend':" in manifest_content:
                print("   ✅ Backend assets configured")
            else:
                print("   ❌ No backend assets configuration")
                issues_found.append("Missing backend assets configuration")
        else:
            print("   ❌ No assets configuration found")
            issues_found.append("Missing assets configuration")
            
    except Exception as e:
        print(f"   ❌ Error reading manifest: {e}")
        issues_found.append("Manifest read error")
    
    # Check 4: Odoo service status
    print("\n4️⃣  Checking Odoo Service...")
    try:
        result = subprocess.run(['docker-compose', 'ps'], 
                              capture_output=True, text=True, timeout=10)
        if 'odoo' in result.stdout:
            print("   ✅ Odoo container found")
        else:
            print("   ⚠️  Odoo container not running")
            issues_found.append("Odoo container not running")
    except Exception as e:
        print(f"   ⚠️  Cannot check Docker status: {e}")
    
    return issues_found

def create_minimal_fix():
    """Create minimal working configuration"""
    print("\n🔧 Creating Minimal Working Configuration")
    print("=" * 40)
    
    # Create ultra-minimal SCSS
    minimal_css = """/* Account Payment Final - Minimal CSS */
.o_payment_approval_widget {
    padding: 16px;
    border: 1px solid #ddd;
    margin: 8px 0;
}

.o_payment_state_draft { color: #6c757d; }
.o_payment_state_posted { color: #28a745; }
.o_payment_state_rejected { color: #dc3545; }
"""
    
    minimal_file = Path("account_payment_final/static/src/scss/minimal_fix.scss")
    minimal_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(minimal_file, 'w') as f:
        f.write(minimal_css)
    
    print(f"✅ Created minimal CSS: {minimal_file}")
    
    # Create backup manifest configuration
    backup_config = """
# Add this to __manifest__.py if needed:
    'assets': {
        'web.assets_backend': [
            'account_payment_final/static/src/scss/minimal_fix.scss',
        ],
    },
"""
    
    with open("BACKUP_MANIFEST_CONFIG.txt", 'w') as f:
        f.write(backup_config)
    
    print("✅ Created backup manifest config")
    
    return str(minimal_file)

def suggest_fixes(issues):
    """Suggest fixes for found issues"""
    print("\n💡 Suggested Fixes")
    print("=" * 20)
    
    if not issues:
        print("🎉 No issues found! Styles should compile correctly.")
        return
    
    fix_commands = []
    
    for issue in issues:
        if "Missing file" in issue:
            print(f"📁 File Issue: {issue}")
            print("   → Ensure all required files exist")
            fix_commands.append("Check file paths and create missing files")
            
        elif "CSS comment" in issue:
            print(f"🎨 CSS Issue: {issue}")
            print("   → Convert // comments to /* */ in CSS custom property blocks")
            fix_commands.append("Fix SCSS comment syntax")
            
        elif "assets" in issue.lower():
            print(f"📦 Asset Issue: {issue}")
            print("   → Check manifest.py assets configuration")
            fix_commands.append("Update manifest assets configuration")
            
        elif "container" in issue.lower():
            print(f"🐳 Docker Issue: {issue}")
            print("   → Start Odoo container: docker-compose up -d")
            fix_commands.append("docker-compose up -d")
    
    print("\n🔧 Quick Fix Commands:")
    for i, cmd in enumerate(set(fix_commands), 1):
        print(f"{i}. {cmd}")

def main():
    """Main diagnostic function"""
    print("🚨 Odoo Style Compilation Error Diagnostic")
    print("=" * 60)
    
    try:
        os.chdir(Path(__file__).parent)
        
        # Run diagnosis
        issues = diagnose_style_errors()
        
        # Create minimal fix
        minimal_file = create_minimal_fix()
        
        # Suggest fixes
        suggest_fixes(issues)
        
        print("\n📋 IMMEDIATE ACTIONS:")
        print("1. 🧹 Clear browser cache (Ctrl+F5)")
        print("2. 🔄 Restart Odoo: docker-compose restart odoo")
        print("3. 📱 Update module: Apps → account_payment_final → Upgrade")
        print("4. 🔍 Check browser console for errors")
        
        if issues:
            print(f"\n⚠️  Found {len(issues)} issues to address")
            return False
        else:
            print("\n✅ No critical issues found")
            return True
            
    except Exception as e:
        print(f"\n❌ Diagnostic failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
