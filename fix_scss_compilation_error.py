#!/usr/bin/env python3
"""
SCSS Style Compilation Error Fix
Identifies and fixes SCSS syntax issues in account_payment_final
"""

import os
import re
from pathlib import Path

def fix_scss_syntax():
    """Fix common SCSS syntax issues"""
    print("🔧 Fixing SCSS Syntax Issues")
    print("=" * 40)
    
    scss_files = [
        "account_payment_final/static/src/scss/variables.scss",
        "account_payment_final/static/src/scss/components/payment_widget_enhanced.scss",
        "account_payment_final/static/src/scss/cloudpepper_optimizations.scss",
        "account_payment_final/static/src/scss/professional_payment_ui.scss",
        "account_payment_final/static/src/scss/osus_branding.scss"
    ]
    
    fixes_applied = 0
    
    for scss_file in scss_files:
        file_path = Path(scss_file)
        if not file_path.exists():
            print(f"⚠️  File not found: {scss_file}")
            continue
            
        print(f"🔍 Checking: {scss_file}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix 1: Convert // comments to /* */ inside :root blocks
            in_root_block = False
            lines = content.split('\n')
            fixed_lines = []
            
            for line in lines:
                stripped = line.strip()
                if ':root {' in line:
                    in_root_block = True
                elif stripped == '}' and in_root_block:
                    in_root_block = False
                elif in_root_block and '//' in line and not line.strip().startswith('/*'):
                    # Convert // comments to /* */ comments in CSS custom property blocks
                    comment_pos = line.find('//')
                    if comment_pos > 0:
                        line = line[:comment_pos] + '/* ' + line[comment_pos+2:].strip() + ' */'
                
                fixed_lines.append(line)
            
            content = '\n'.join(fixed_lines)
            
            # Fix 2: Ensure proper SCSS imports
            if '@import' in content and not content.startswith('@import'):
                content = re.sub(r'@import\s+[\'"]([^\'"]+)[\'"];?', r"@import '\1';", content)
            
            # Fix 3: Remove any remaining double slashes in CSS context
            content = re.sub(r'(\s+)//([^/\n]*)\n', r'\1/* \2 */\n', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed: {scss_file}")
                fixes_applied += 1
            else:
                print(f"✅ No issues: {scss_file}")
                
        except Exception as e:
            print(f"❌ Error processing {scss_file}: {e}")
    
    return fixes_applied

def check_asset_loading():
    """Check asset loading configuration"""
    print("\n🔍 Checking Asset Loading Configuration")
    print("=" * 40)
    
    manifest_path = Path("account_payment_final/__manifest__.py")
    
    if not manifest_path.exists():
        print("❌ Manifest file not found")
        return False
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_content = f.read()
        
        # Check for asset configuration
        if "'assets':" in manifest_content and "'web.assets_backend':" in manifest_content:
            print("✅ Asset configuration found")
            
            # Check for SCSS files in assets
            scss_count = manifest_content.count('.scss')
            js_count = manifest_content.count('.js')
            
            print(f"📊 Asset files found:")
            print(f"   - SCSS files: {scss_count}")
            print(f"   - JS files: {js_count}")
            
            if scss_count > 0 and js_count > 0:
                print("✅ Assets properly configured")
                return True
            else:
                print("⚠️  Missing asset files in configuration")
                return False
        else:
            print("❌ No asset configuration found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking manifest: {e}")
        return False

def create_emergency_scss_fix():
    """Create a minimal, error-free SCSS structure"""
    print("\n🆘 Creating Emergency SCSS Fix")
    print("=" * 30)
    
    emergency_scss = """/* Account Payment Final - Emergency SCSS Fix */
/* Minimal, error-free styles for production */

/* Basic Payment Widget Styles */
.o_payment_approval_widget {
    padding: 16px;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    background: #ffffff;
    margin: 8px 0;
    transition: all 0.3s ease;
}

.o_payment_approval_widget:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border-color: #0d6efd;
}

/* State-based styling */
.o_payment_state_draft { color: #6c757d; }
.o_payment_state_review { color: #fd7e14; }
.o_payment_state_approval { color: #ffc107; }
.o_payment_state_authorization { color: #0d6efd; }
.o_payment_state_posted { color: #198754; }
.o_payment_state_rejected { color: #dc3545; }

/* QR Code styling */
.o_qr_code_widget {
    text-align: center;
    padding: 16px;
}

.o_qr_code_image {
    max-width: 150px;
    height: auto;
    border: 2px solid #dee2e6;
    border-radius: 4px;
}

/* Responsive design */
@media (max-width: 768px) {
    .o_payment_approval_widget {
        padding: 12px;
        margin: 4px 0;
    }
}

/* Print styles */
@media print {
    .o_payment_approval_widget {
        border: 1px solid #000;
        box-shadow: none;
    }
}
"""
    
    emergency_file = Path("account_payment_final/static/src/scss/emergency_fix.scss")
    emergency_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(emergency_file, 'w', encoding='utf-8') as f:
        f.write(emergency_scss)
    
    print(f"✅ Created emergency SCSS file: {emergency_file}")
    return str(emergency_file)

def main():
    """Main fix function"""
    print("🚨 SCSS Style Compilation Error Fix")
    print("=" * 50)
    
    try:
        # Change to project directory
        os.chdir(Path(__file__).parent)
        
        # Step 1: Fix SCSS syntax issues
        fixes = fix_scss_syntax()
        
        # Step 2: Check asset loading
        assets_ok = check_asset_loading()
        
        # Step 3: Create emergency fix if needed
        if fixes == 0 and assets_ok:
            print("\n✅ No SCSS issues found - styles should compile correctly")
        else:
            emergency_file = create_emergency_scss_fix()
            print(f"\n⚠️  Emergency fix created: {emergency_file}")
            print("💡 You may need to update the manifest to use the emergency CSS file")
        
        print("\n📋 NEXT STEPS:")
        print("1. Clear browser cache (Ctrl+F5)")
        print("2. Restart Odoo service if needed")
        print("3. Check browser console for remaining errors")
        print("4. Update module: Apps > account_payment_final > Upgrade")
        
        return True
        
    except Exception as e:
        print(f"❌ Fix script failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
