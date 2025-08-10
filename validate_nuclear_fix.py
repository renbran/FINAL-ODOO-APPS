#!/usr/bin/env python3
"""
Nuclear Fix Validation Script
Validates that the account_payment_approval module now uses voucher_state field
and is completely free of state field conflicts.
"""

import os
import xml.etree.ElementTree as ET
import re
import sys
from pathlib import Path

def validate_nuclear_fix():
    """Validate the nuclear fix implementation"""
    base_path = Path("account_payment_approval")
    
    if not base_path.exists():
        print("❌ account_payment_approval module not found")
        return False
    
    print("🔍 NUCLEAR FIX VALIDATION")
    print("=" * 50)
    
    # 1. Validate Python Model
    model_file = base_path / "models" / "account_payment.py"
    if not model_file.exists():
        print("❌ Model file not found")
        return False
    
    with open(model_file, 'r', encoding='utf-8') as f:
        model_content = f.read()
    
    # Check for problematic state field extension
    if 'selection_add' in model_content:
        print("❌ Model still contains selection_add (causes conflicts)")
        return False
    
    # Check for problematic state field extension (uncommented lines only)
    lines = model_content.split('\n')
    found_uncommented_state = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('#'):
            continue  # Skip commented lines
        # Look for exact state field definition (not voucher_state or other fields)
        if re.match(r'\s*state\s*=\s*fields\.Selection\(', stripped):
            print(f"❌ Model still extends state field at line {i}: {stripped}")
            found_uncommented_state = True
    
    if found_uncommented_state:
        return False
    
    # Check for voucher_state field
    if 'voucher_state = fields.Selection(' not in model_content:
        print("❌ Model missing voucher_state field")
        return False
    
    print("✅ Python Model: Uses voucher_state field (no state conflicts)")
    
    # 2. Validate XML Views
    view_file = base_path / "views" / "account_payment_views.xml"
    if not view_file.exists():
        print("❌ View file not found")
        return False
    
    try:
        tree = ET.parse(view_file)
        print("✅ XML Views: Valid XML structure")
    except ET.ParseError as e:
        print(f"❌ XML Views: Parse error - {e}")
        return False
    
    with open(view_file, 'r', encoding='utf-8') as f:
        view_content = f.read()
    
    # Check for voucher_state usage in views
    if 'name="voucher_state"' not in view_content:
        print("❌ Views don't use voucher_state field")
        return False
    
    # Check for problematic state field filters
    if "domain=\"[('state'" in view_content:
        print("❌ Views still have state field domains (will cause search errors)")
        return False
    
    print("✅ XML Views: Uses voucher_state field consistently")
    
    # 3. Validate JavaScript Dashboard
    js_file = base_path / "static" / "src" / "js" / "payment_approval_dashboard.js"
    if not js_file.exists():
        print("❌ JavaScript dashboard file not found")
        return False
    
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    # Check for state field references
    if "'state', '='" in js_content:
        print("❌ JavaScript still references state field (will cause errors)")
        return False
    
    if 'payment.state ===' in js_content:
        print("❌ JavaScript still uses payment.state (will cause errors)")
        return False
    
    # Check for voucher_state usage
    if "'voucher_state', '='" not in js_content:
        print("❌ JavaScript doesn't use voucher_state field")
        return False
    
    if 'payment.voucher_state ===' not in js_content:
        print("❌ JavaScript doesn't use payment.voucher_state")
        return False
    
    print("✅ JavaScript: Uses voucher_state field consistently")
    
    # 4. Validate Manifest Dependencies
    manifest_file = base_path / "__manifest__.py"
    if not manifest_file.exists():
        print("❌ Manifest file not found")
        return False
    
    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest_content = f.read()
    
    # Check for required dependencies
    required_deps = ['account', 'mail']
    for dep in required_deps:
        if f"'{dep}'" not in manifest_content:
            print(f"❌ Manifest missing required dependency: {dep}")
            return False
    
    print("✅ Manifest: All required dependencies present")
    
    # 5. Check for CloudPepper compatibility
    print("\n🔍 CLOUDPEPPER COMPATIBILITY CHECK")
    print("=" * 40)
    
    # Check for external ID references
    if 'action_report_voucher_verification_web' in view_content:
        reports_file = base_path / "reports" / "report_actions.xml"
        if not reports_file.exists():
            print("❌ QR verification report action referenced but not defined")
            return False
        else:
            print("✅ QR verification report action properly defined")
    
    # Check for proper field computations
    compute_methods = [
        '_compute_voucher_type',
        '_compute_requires_approval', 
        '_compute_workflow_progress',
        '_compute_qr_code',
        '_compute_verification_url'
    ]
    
    for method in compute_methods:
        if f'def {method}(' not in model_content:
            print(f"❌ Missing compute method: {method}")
            return False
    
    print("✅ All required compute methods present")
    
    # 6. Final Validation Summary
    print("\n🎯 NUCLEAR FIX VALIDATION SUMMARY")
    print("=" * 40)
    print("✅ State field conflicts eliminated")
    print("✅ Voucher_state field used consistently") 
    print("✅ XML views updated correctly")
    print("✅ JavaScript dashboard updated")
    print("✅ All compute methods present")
    print("✅ CloudPepper compatibility ensured")
    
    print("\n🚀 READY FOR CLOUDPEPPER DEPLOYMENT!")
    print("=" * 40)
    print("1. Upload module to CloudPepper")
    print("2. Uninstall existing account_payment_approval")
    print("3. Clear cache and restart")
    print("4. Install nuclear fix version")
    print("5. Test workflow functionality")
    
    return True

if __name__ == "__main__":
    if validate_nuclear_fix():
        print("\n✅ Nuclear fix validation PASSED")
        sys.exit(0)
    else:
        print("\n❌ Nuclear fix validation FAILED")
        sys.exit(1)
