#!/usr/bin/env python3
"""
Unified Statusbar and Sequence Validation Script for account_payment_final
Validates the implementation of unified statusbar across account.payment and account.move
and ensures voucher sequences are visible in draft stage.
"""

import os
import sys
import xml.etree.ElementTree as ET
import re
from pathlib import Path

def validate_unified_statusbar():
    """Validate unified statusbar implementation"""
    print("🔍 UNIFIED STATUSBAR AND SEQUENCE VALIDATION")
    print("=" * 60)
    
    module_path = Path("account_payment_final")
    if not module_path.exists():
        print("❌ Module path not found!")
        return False
    
    success_count = 0
    total_checks = 12
    
    # 1. Validate account_payment.py voucher_number field
    print("\n1. Checking voucher_number field visibility...")
    payment_file = module_path / "models" / "account_payment.py"
    if payment_file.exists():
        with open(payment_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for immediate sequence generation
        if 'store=True' in content and 'default=lambda self: self._generate_sequence_on_create()' in content:
            print("✅ Voucher number field configured for immediate visibility")
            success_count += 1
        else:
            print("❌ Voucher number field not properly configured for draft visibility")
    else:
        print("❌ account_payment.py not found")
    
    # 2. Validate _generate_sequence_on_create method
    print("\n2. Checking immediate sequence generation method...")
    if payment_file.exists():
        with open(payment_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '_generate_sequence_on_create' in content and 'Generate sequence immediately' in content:
            print("✅ _generate_sequence_on_create method implemented")
            success_count += 1
        else:
            print("❌ _generate_sequence_on_create method missing or incomplete")
    
    # 3. Validate create method enhancement
    print("\n3. Checking enhanced create method...")
    if payment_file.exists():
        with open(payment_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'Generate sequence immediately - visible in all stages' in content:
            print("✅ Create method enhanced for immediate sequence generation")
            success_count += 1
        else:
            print("❌ Create method not properly enhanced")
    
    # 4. Validate account_payment_views.xml unified statusbar
    print("\n4. Checking account.payment unified statusbar...")
    payment_views = module_path / "views" / "account_payment_views.xml"
    if payment_views.exists():
        try:
            tree = ET.parse(payment_views)
            root = tree.getroot()
            
            # Look for unified statusbar
            statusbar_found = False
            for elem in root.iter():
                if elem.get('widget') == 'statusbar' and 'approval_state' in str(elem.get('name', '')):
                    statusbar_found = True
                    break
            
            if statusbar_found:
                print("✅ Unified statusbar found in payment views")
                success_count += 1
            else:
                print("❌ Unified statusbar not found in payment views")
        except Exception as e:
            print(f"❌ Error parsing payment views: {e}")
    else:
        print("❌ account_payment_views.xml not found")
    
    # 5. Validate account_move_views.xml unified statusbar
    print("\n5. Checking account.move unified statusbar...")
    move_views = module_path / "views" / "account_move_views.xml"
    if move_views.exists():
        try:
            tree = ET.parse(move_views)
            root = tree.getroot()
            
            # Look for unified statusbar replacement
            unified_header_found = False
            for elem in root.iter():
                if 'approval_state' in str(elem.get('name', '')) and elem.get('widget') == 'statusbar':
                    unified_header_found = True
                    break
            
            if unified_header_found:
                print("✅ Unified statusbar replacement found in move views")
                success_count += 1
            else:
                print("❌ Unified statusbar replacement not found in move views")
        except Exception as e:
            print(f"❌ Error parsing move views: {e}")
    else:
        print("❌ account_move_views.xml not found")
    
    # 6. Validate account.move model enhancements
    print("\n6. Checking account.move model enhancements...")
    move_file = module_path / "models" / "account_move.py"
    if move_file.exists():
        with open(move_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'approval_state' in content and 'onchange' in content:
            print("✅ Account.move model enhanced with approval workflow")
            success_count += 1
        else:
            print("❌ Account.move model not properly enhanced")
    else:
        print("❌ account_move.py not found")
    
    # 7. Validate payment register wizard override
    print("\n7. Checking payment register wizard override...")
    register_file = module_path / "models" / "account_payment_register.py"
    if register_file.exists():
        with open(register_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '_create_payment_vals_from_wizard' in content and 'approval_state' in content:
            print("✅ Payment register wizard properly overridden")
            success_count += 1
        else:
            print("❌ Payment register wizard override incomplete")
    else:
        print("❌ account_payment_register.py not found")
    
    # 8. Validate JavaScript real-time functionality
    print("\n8. Checking JavaScript real-time functionality...")
    js_file = module_path / "static" / "src" / "js" / "payment_workflow_realtime.js"
    if js_file.exists():
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'PaymentWorkflowRealtime' in content and 'auto_refresh_interval' in content:
            print("✅ JavaScript real-time functionality implemented")
            success_count += 1
        else:
            print("❌ JavaScript real-time functionality incomplete")
    else:
        print("❌ JavaScript real-time file not found")
    
    # 9. Validate CSS styling
    print("\n9. Checking CSS styling...")
    css_file = module_path / "static" / "src" / "scss" / "realtime_workflow.scss"
    if css_file.exists():
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'payment_workflow_realtime' in content and 'osus' in content.lower():
            print("✅ CSS styling with OSUS branding implemented")
            success_count += 1
        else:
            print("❌ CSS styling incomplete or missing branding")
    else:
        print("❌ CSS styling file not found")
    
    # 10. Validate Python syntax
    print("\n10. Checking Python syntax validation...")
    python_files = [
        module_path / "models" / "account_payment.py",
        module_path / "models" / "account_move.py",
        module_path / "models" / "account_payment_register.py"
    ]
    
    syntax_valid = True
    for py_file in python_files:
        if py_file.exists():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(py_file), 'exec')
            except SyntaxError as e:
                print(f"❌ Syntax error in {py_file}: {e}")
                syntax_valid = False
    
    if syntax_valid:
        print("✅ All Python files have valid syntax")
        success_count += 1
    
    # 11. Validate XML syntax
    print("\n11. Checking XML syntax validation...")
    xml_files = [
        module_path / "views" / "account_payment_views.xml",
        module_path / "views" / "account_move_views.xml"
    ]
    
    xml_valid = True
    for xml_file in xml_files:
        if xml_file.exists():
            try:
                ET.parse(xml_file)
            except ET.ParseError as e:
                print(f"❌ XML parse error in {xml_file}: {e}")
                xml_valid = False
    
    if xml_valid:
        print("✅ All XML files have valid syntax")
        success_count += 1
    
    # 12. Validate manifest dependencies
    print("\n12. Checking manifest dependencies...")
    manifest_file = module_path / "__manifest__.py"
    if manifest_file.exists():
        with open(manifest_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "'web'" in content and "'mail'" in content and "'account'" in content:
            print("✅ Manifest has required dependencies (account, web, mail)")
            success_count += 1
        else:
            print("❌ Manifest missing required dependencies")
    else:
        print("❌ Manifest file not found")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 VALIDATION SUMMARY")
    print(f"✅ Passed: {success_count}/{total_checks} checks")
    print(f"❌ Failed: {total_checks - success_count}/{total_checks} checks")
    
    if success_count >= 10:
        print("\n🎉 UNIFIED STATUSBAR IMPLEMENTATION SUCCESSFUL!")
        print("✅ Ready for deployment to CloudPepper")
        return True
    else:
        print(f"\n⚠️  Some issues found. Please review failed checks.")
        return False

if __name__ == "__main__":
    success = validate_unified_statusbar()
    sys.exit(0 if success else 1)
