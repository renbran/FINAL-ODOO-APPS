#!/usr/bin/env python3
"""
Deploy JavaScript Infinite Recursion Fix
Quick deployment helper for CloudPepper
"""

import os
import shutil
from datetime import datetime

def deploy_js_fix():
    """Deploy the JavaScript fix to CloudPepper."""
    print("🚀 JAVASCRIPT INFINITE RECURSION FIX DEPLOYMENT")
    print("=" * 60)
    
    # Source file
    source_file = "report_font_enhancement/static/src/js/report_font_enhancement.js"
    
    if not os.path.exists(source_file):
        print("❌ Source file not found!")
        return False
    
    # Create backup
    backup_dir = "deployment_package/js_fixes"
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backup_dir}/report_font_enhancement_fix_{timestamp}.js"
    
    try:
        shutil.copy2(source_file, backup_file)
        print(f"✅ Backup created: {backup_file}")
    except Exception as e:
        print(f"⚠️  Backup failed: {e}")
    
    # Validate file content
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key fixes
    required_fixes = [
        'this.isProcessing = false',
        'if (this.isProcessing)',
        'observer.disconnect()',
        'try {',
        'catch (error)',
        'finally {',
        'setTimeout('
    ]
    
    missing_fixes = []
    for fix in required_fixes:
        if fix not in content:
            missing_fixes.append(fix)
    
    if missing_fixes:
        print("❌ Missing required fixes:")
        for fix in missing_fixes:
            print(f"   - {fix}")
        return False
    
    print("✅ All required fixes present in source file")
    
    # File size check
    file_size = os.path.getsize(source_file)
    print(f"📊 File size: {file_size:,} bytes")
    
    if file_size < 1000:
        print("⚠️  File seems too small - possible corruption")
        return False
    
    # Generate deployment instructions
    print("\n📋 DEPLOYMENT INSTRUCTIONS FOR CLOUDPEPPER:")
    print("=" * 50)
    print("1. Upload the fixed file to CloudPepper:")
    print(f"   Source: {source_file}")
    print("   Target: /report_font_enhancement/static/src/js/")
    print()
    print("2. Clear CloudPepper cache:")
    print("   - Go to Settings > Technical > Database Structure > Cache")
    print("   - Clear all caches")
    print()
    print("3. Restart Odoo services:")
    print("   - Restart Odoo server processes")
    print("   - Clear browser cache")
    print()
    print("4. Test the fix:")
    print("   - Load a report page")
    print("   - Check browser console for errors")
    print("   - Verify no 'Maximum call stack' errors")
    print()
    print("🎯 Expected Result: No more infinite recursion errors!")
    
    return True

if __name__ == "__main__":
    success = deploy_js_fix()
    if success:
        print("\n✅ Ready for deployment!")
    else:
        print("\n❌ Deployment validation failed!")
