#!/usr/bin/env python3
"""
CloudPepper Deployment Fix Validation
Validates the XPath field name corrections for Odoo 17 compatibility
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_cloudpepper_fixes():
    """Validate CloudPepper deployment fixes"""
    
    print("🔧 CLOUDPEPPER DEPLOYMENT FIX VALIDATION")
    print("=" * 60)
    
    module_path = Path("account_payment_final")
    results = {
        'xml_validation': False,
        'xpath_fixes': 0,
        'field_references': 0,
        'errors': []
    }
    
    # Test 1: XML Syntax Validation
    print("\n1. 🔍 XML Syntax Validation...")
    
    view_file = module_path / "views" / "account_payment_views.xml"
    if view_file.exists():
        try:
            tree = ET.parse(view_file)
            root = tree.getroot()
            print("   ✅ XML syntax is valid")
            results['xml_validation'] = True
        except ET.ParseError as e:
            print(f"   ❌ XML syntax error: {e}")
            results['errors'].append(f"XML parsing error: {e}")
    
    # Test 2: XPath Field Name Fixes
    print("\n2. 🔄 XPath Field Name Fixes...")
    
    if view_file.exists():
        with open(view_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for problematic old field names
        old_fields = ['communication']
        new_fields = ['ref']
        
        for old_field in old_fields:
            if f"[@name='{old_field}']" in content:
                print(f"   ❌ Still using old field: {old_field}")
                results['errors'].append(f"Old field reference found: {old_field}")
            else:
                print(f"   ✅ No references to old field: {old_field}")
                results['xpath_fixes'] += 1
        
        for new_field in new_fields:
            if f"[@name='{new_field}']" in content:
                print(f"   ✅ Using correct field: {new_field}")
                results['field_references'] += 1
            else:
                print(f"   ⚠️ Expected field not found: {new_field}")
    
    # Test 3: Odoo 17 Compatibility Check
    print("\n3. 🚀 Odoo 17 Compatibility Check...")
    
    odoo17_features = [
        'statusbar_colors',
        'widget="statusbar"',
        'readonly="0"',
        'approval_state',
        'invisible="approval_state'
    ]
    
    compatibility_score = 0
    for feature in odoo17_features:
        if feature in content:
            print(f"   ✅ {feature}")
            compatibility_score += 1
        else:
            print(f"   ❌ {feature}")
    
    results['compatibility_score'] = compatibility_score / len(odoo17_features)
    
    # Final Results
    print("\n" + "=" * 60)
    print("📊 CLOUDPEPPER FIX RESULTS")
    print("=" * 60)
    
    print(f"🔍 XML Validation: {'✅' if results['xml_validation'] else '❌'}")
    print(f"🔄 XPath Fixes: {results['xpath_fixes']}/1 ({'✅' if results['xpath_fixes'] >= 1 else '❌'})")
    print(f"📋 Field References: {results['field_references']}/1 ({'✅' if results['field_references'] >= 1 else '❌'})")
    print(f"🚀 Odoo 17 Compatibility: {results['compatibility_score']*100:.1f}% ({'✅' if results['compatibility_score'] >= 0.8 else '❌'})")
    
    # Calculate overall success
    success_criteria = [
        results['xml_validation'],
        results['xpath_fixes'] >= 1,
        results['field_references'] >= 1,
        results['compatibility_score'] >= 0.8,
        len(results['errors']) == 0
    ]
    
    success_rate = sum(success_criteria) / len(success_criteria)
    
    print(f"\n🎯 Overall Fix Success Rate: {success_rate*100:.1f}%")
    
    if success_rate >= 0.9:
        print("🎉 EXCELLENT - Ready for CloudPepper deployment!")
        status = "✅ DEPLOYMENT READY"
    elif success_rate >= 0.7:
        print("✅ GOOD - CloudPepper deployment should succeed")
        status = "✅ DEPLOYMENT READY"
    else:
        print("❌ ISSUES - Additional fixes needed before deployment")
        status = "❌ NEEDS MORE FIXES"
        
    print(f"📋 Status: {status}")
    
    if results['errors']:
        print(f"\n⚠️ Issues Found:")
        for error in results['errors']:
            print(f"   - {error}")
    
    print(f"\n🚀 CloudPepper Deployment Command:")
    print(f"   odoo --install=account_payment_final --log-level=debug")
    
    return success_rate >= 0.8

if __name__ == "__main__":
    success = validate_cloudpepper_fixes()
    sys.exit(0 if success else 1)
