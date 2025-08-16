#!/usr/bin/env python3
"""
Installation Test for Payment Approval Pro Module

This script tests the module installation to ensure the company_id domain fix works correctly.
"""

import os
import sys
import tempfile
import xml.etree.ElementTree as ET

def test_xml_parsing():
    """Test that all XML files can be parsed without errors"""
    print("🔍 Testing XML parsing...")
    
    xml_files = [
        'payment_approval_pro/views/payment_voucher_views.xml',
        'payment_approval_pro/views/payment_menus.xml',
        'payment_approval_pro/security/payment_security.xml',
        'payment_approval_pro/data/sequence_data.xml',
        'payment_approval_pro/data/email_templates.xml',
        'payment_approval_pro/static/src/xml/qr_templates.xml',
        'payment_approval_pro/static/src/xml/payment_templates.xml',
    ]
    
    for xml_file in xml_files:
        if os.path.exists(xml_file):
            try:
                ET.parse(xml_file)
                print(f"✅ {xml_file}")
            except ET.ParseError as e:
                print(f"❌ {xml_file}: {e}")
                return False
        else:
            print(f"⚠️  {xml_file}: File not found")
    
    return True

def test_company_id_domain_fix():
    """Test that the company_id domain issue is fixed"""
    print("\n🔍 Testing company_id domain fix...")
    
    views_file = 'payment_approval_pro/views/payment_voucher_views.xml'
    
    if not os.path.exists(views_file):
        print(f"❌ {views_file} not found")
        return False
    
    try:
        # Parse the XML
        tree = ET.parse(views_file)
        root = tree.getroot()
        
        # Find all field elements with name="journal_id"
        journal_fields = root.findall(".//field[@name='journal_id']")
        
        for field in journal_fields:
            domain = field.get('domain', '')
            if 'company_id' in domain:
                print(f"⚠️  Found company_id in journal_id domain: {domain}")
                print("   This may cause ParseError if user doesn't have multi-company group")
                return False
        
        print("✅ No company_id references found in journal_id domains")
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        return False

def test_manifest_structure():
    """Test that the manifest file is properly structured"""
    print("\n🔍 Testing manifest structure...")
    
    manifest_file = 'payment_approval_pro/__manifest__.py'
    
    if not os.path.exists(manifest_file):
        print(f"❌ {manifest_file} not found")
        return False
    
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required fields
        required_fields = [
            'name', 'version', 'category', 'summary', 'description',
            'author', 'depends', 'data', 'assets', 'installable'
        ]
        
        for field in required_fields:
            if f"'{field}'" in content or f'"{field}"' in content:
                print(f"✅ {field}")
            else:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Check dependencies
        if "'base'" in content and "'mail'" in content and "'account'" in content:
            print("✅ Required dependencies present")
        else:
            print("❌ Missing required dependencies")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading manifest: {e}")
        return False

def main():
    """Run all installation tests"""
    print("🚀 PAYMENT APPROVAL PRO INSTALLATION TEST")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: XML Parsing
    if test_xml_parsing():
        tests_passed += 1
    
    # Test 2: Company ID Domain Fix
    if test_company_id_domain_fix():
        tests_passed += 1
    
    # Test 3: Manifest Structure
    if test_manifest_structure():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS: {tests_passed}/{total_tests} PASSED")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED - MODULE READY FOR INSTALLATION")
        return 0
    else:
        print("❌ SOME TESTS FAILED - PLEASE FIX ISSUES BEFORE INSTALLATION")
        return 1

if __name__ == '__main__':
    sys.exit(main())
