#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Manual Cleanup - Remove remaining temporary files
"""

import os
from pathlib import Path

def final_manual_cleanup():
    """Remove remaining temporary files manually"""
    workspace = Path.cwd()
    
    # Remaining files to remove
    files_to_remove = [
        # ZIP files
        "commission_ax_cloudpepper_ready.zip",
        "commission_ax_emergency_fix.zip",
        
        # SQL files  
        "cloudpepper_commission_email_emergency_fix.sql",
        "cloudpepper_commission_email_fix.sql",
        
        # JavaScript emergency fixes
        "cloudpepper_global_protection.js",
        "emergency_nuclear_rpc_fix.js", 
        "emergency_rpc_global_fix.js",
        "js_safety_wrapper.js",
        
        # Validation and diagnostic scripts
        "commission_dependency_validator.py",
        "critical_button_fix_validation.py",
        "critical_field_dependency_validation.py", 
        "database_initialization_error_fix_validation.py",
        "enhanced_dashboard_integration_test.py",
        "enhanced_dashboard_validator.py",
        "enhanced_template_validation.py",
        "javascript_component_conflict_validator.py",
        "javascript_error_diagnostic.py",
        "order_status_override_security_validation.py",
        "order_status_override_white_screen_fix.py",
        "unified_statusbar_validation.py",
        
        # Shell scripts
        "emergency_order_commission_install.sh",
        "osus_premium_deployment_fix.sh",
        "odoo_management_oldosus.ps1",
        
        # Config files
        "order_net_commission_deployment_package.json",
        
        # This cleanup script itself
        "commission_ax_deployment_validator.py",
        "commission_ax_emergency_cloudpepper_fix.py"
    ]
    
    print("🧹 Final Manual Cleanup")
    print("=" * 30)
    
    total_size = 0
    removed_count = 0
    
    for filename in files_to_remove:
        file_path = workspace / filename
        if file_path.exists():
            try:
                size_mb = file_path.stat().st_size / (1024 * 1024)
                file_path.unlink()
                total_size += size_mb
                removed_count += 1
                print(f"✅ Removed: {filename} ({size_mb:.2f} MB)")
            except Exception as e:
                print(f"❌ Error removing {filename}: {e}")
        else:
            print(f"⚠️ Not found: {filename}")
    
    print("\n" + "=" * 30)
    print(f"🎉 Final cleanup complete!")
    print(f"📊 Files removed: {removed_count}")
    print(f"💾 Space freed: {total_size:.2f} MB")
    
    # Show remaining non-module files
    print("\n📋 Remaining non-module files:")
    remaining_files = []
    for item in workspace.iterdir():
        if (item.is_file() and 
            not item.name.startswith('.') and
            not item.name.startswith('workspace_cleanup') and
            not item.name.endswith('_REPORT.json')):
            remaining_files.append(item.name)
    
    if remaining_files:
        for filename in sorted(remaining_files):
            print(f"  📄 {filename}")
    else:
        print("  ✅ Only essential configuration files remain")
    
    return removed_count, total_size

if __name__ == "__main__":
    final_manual_cleanup()
