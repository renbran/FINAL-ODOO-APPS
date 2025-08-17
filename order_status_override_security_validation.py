#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLOUDPEPPER ORDER STATUS OVERRIDE SECURITY FIX VALIDATION
==========================================================

This script validates the security.xml model reference fixes for the 
order_status_override module to prevent the "Invalid domain: 'order.status'" error.

Date: August 17, 2025
Module: order_status_override
Issue: ParseError in security.xml line 98 - Invalid domain: 'order.status'
Fix: Removed manual ir.model definitions, updated model references to use module prefix
"""

import os
import sys
import xml.etree.ElementTree as ET
import csv
from pathlib import Path

def validate_order_status_security():
    """Validate order_status_override security configuration"""
    print("🔍 VALIDATING ORDER STATUS OVERRIDE SECURITY FIXES")
    print("=" * 60)
    
    base_path = Path("order_status_override")
    issues_found = []
    fixes_applied = []
    
    # 1. Validate security.xml model references
    security_xml_path = base_path / "security" / "security.xml"
    if security_xml_path.exists():
        print("📂 Checking security.xml model references...")
        try:
            tree = ET.parse(security_xml_path)
            root = tree.getroot()
            
            # Check for manual ir.model definitions (should not exist)
            model_records = root.findall(".//record[@model='ir.model']")
            if model_records:
                issues_found.append(f"❌ Manual ir.model definitions found: {len(model_records)}")
            else:
                fixes_applied.append("✅ No manual ir.model definitions (CORRECT)")
            
            # Check ir.rule model_id references
            rule_records = root.findall(".//record[@model='ir.rule']")
            correct_refs = 0
            incorrect_refs = 0
            
            for rule in rule_records:
                model_id_field = rule.find(".//field[@name='model_id']")
                if model_id_field is not None:
                    ref_value = model_id_field.get('ref', '')
                    if ref_value.startswith('order_status_override.model_'):
                        correct_refs += 1
                    elif ref_value.startswith('model_') and not '.' in ref_value:
                        incorrect_refs += 1
                        issues_found.append(f"❌ Incorrect model reference: {ref_value}")
            
            if correct_refs > 0:
                fixes_applied.append(f"✅ Correct model references: {correct_refs}")
            if incorrect_refs == 0:
                fixes_applied.append("✅ No incorrect model references")
            
        except ET.ParseError as e:
            issues_found.append(f"❌ XML Parse Error in security.xml: {e}")
        except Exception as e:
            issues_found.append(f"❌ Error reading security.xml: {e}")
    else:
        issues_found.append("❌ security.xml file not found")
    
    # 2. Validate ir.model.access.csv references
    access_csv_path = base_path / "security" / "ir.model.access.csv"
    if access_csv_path.exists():
        print("📂 Checking ir.model.access.csv model references...")
        try:
            with open(access_csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                correct_csv_refs = 0
                incorrect_csv_refs = 0
                
                for row in reader:
                    model_id = row.get('model_id:id', '')
                    if model_id.startswith('order_status_override.model_'):
                        correct_csv_refs += 1
                    elif model_id.startswith('model_') and not '.' in model_id:
                        incorrect_csv_refs += 1
                        issues_found.append(f"❌ Incorrect CSV model reference: {model_id}")
                
                if correct_csv_refs > 0:
                    fixes_applied.append(f"✅ Correct CSV model references: {correct_csv_refs}")
                if incorrect_csv_refs == 0:
                    fixes_applied.append("✅ No incorrect CSV model references")
                    
        except Exception as e:
            issues_found.append(f"❌ Error reading ir.model.access.csv: {e}")
    else:
        issues_found.append("❌ ir.model.access.csv file not found")
    
    # 3. Validate model files exist
    print("📂 Checking model definitions...")
    models_path = base_path / "models"
    expected_models = [
        "order_status.py",
        "commission_models.py", 
        "sale_order.py",
        "__init__.py"
    ]
    
    for model_file in expected_models:
        model_path = models_path / model_file
        if model_path.exists():
            fixes_applied.append(f"✅ Model file exists: {model_file}")
        else:
            issues_found.append(f"❌ Missing model file: {model_file}")
    
    # 4. Check for model class definitions
    if (models_path / "order_status.py").exists():
        try:
            with open(models_path / "order_status.py", 'r', encoding='utf-8') as f:
                content = f.read()
                if "_name = 'order.status'" in content:
                    fixes_applied.append("✅ order.status model properly defined")
                else:
                    issues_found.append("❌ order.status model not found in order_status.py")
        except Exception as e:
            issues_found.append(f"❌ Error reading order_status.py: {e}")
    
    # 5. Validate manifest file
    manifest_path = base_path / "__manifest__.py"
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "'security/security.xml'" in content or "'security/ir.model.access.csv'" in content:
                    fixes_applied.append("✅ Security files included in manifest")
                else:
                    issues_found.append("❌ Security files not referenced in manifest")
        except Exception as e:
            issues_found.append(f"❌ Error reading __manifest__.py: {e}")
    
    print("\n📊 VALIDATION RESULTS:")
    print("=" * 40)
    
    if fixes_applied:
        print("✅ FIXES APPLIED:")
        for fix in fixes_applied:
            print(f"   {fix}")
    
    if issues_found:
        print("\n❌ ISSUES FOUND:")
        for issue in issues_found:
            print(f"   {issue}")
    else:
        print("\n🎉 NO ISSUES FOUND - ALL SECURITY FIXES APPLIED CORRECTLY!")
    
    # Summary
    total_checks = len(fixes_applied) + len(issues_found)
    success_rate = (len(fixes_applied) / total_checks * 100) if total_checks > 0 else 0
    
    print(f"\n📈 SUCCESS RATE: {len(fixes_applied)}/{total_checks} ({success_rate:.1f}%)")
    
    if len(issues_found) == 0:
        print("\n🚀 ORDER STATUS OVERRIDE MODULE IS READY FOR CLOUDPEPPER DEPLOYMENT!")
        print("   The security.xml model reference issue has been resolved.")
        return True
    else:
        print("\n⚠️  ADDITIONAL FIXES NEEDED BEFORE DEPLOYMENT")
        return False

def create_deployment_test_command():
    """Create a test command for CloudPepper deployment"""
    print("\n🧪 CLOUDPEPPER DEPLOYMENT TEST COMMAND:")
    print("=" * 50)
    print("To test the module in CloudPepper, run:")
    print()
    print("1. Upload the order_status_override module")
    print("2. Update the module in CloudPepper Apps")
    print("3. Check the logs for any errors:")
    print("   tail -f /var/log/odoo/odoo.log | grep order_status_override")
    print()
    print("Expected result: No 'Invalid domain' errors")

if __name__ == "__main__":
    print("🔧 CLOUDPEPPER ORDER STATUS OVERRIDE SECURITY VALIDATION")
    print("=========================================================")
    print("Date: August 17, 2025")
    print("Issue: ParseError in security.xml - Invalid domain: 'order.status'")
    print("Fix: Corrected model references to use module prefix format")
    print()
    
    success = validate_order_status_security()
    create_deployment_test_command()
    
    if success:
        print("\n✅ VALIDATION PASSED - READY FOR DEPLOYMENT!")
        sys.exit(0)
    else:
        print("\n❌ VALIDATION FAILED - ADDITIONAL FIXES NEEDED!")
        sys.exit(1)
