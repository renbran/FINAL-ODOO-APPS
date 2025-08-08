#!/usr/bin/env python3
"""
Alert and XPath Fix Validation Test
Tests the specific issues reported in the latest CloudPepper deployment
"""

import xml.etree.ElementTree as ET
import re

def test_alert_and_xpath_fixes():
    """Test that alert accessibility and XPath issues are resolved"""
    xml_file = "account_payment_final/views/account_payment_views.xml"
    
    print("🎯 ALERT AND XPATH FIX VALIDATION TEST")
    print("=" * 55)
    
    try:
        # Parse XML
        tree = ET.parse(xml_file)
        
        # Read content
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔍 Testing specific reported issues:")
        
        # Test 1: Alert accessibility - all alerts should have ARIA roles
        alert_divs = re.findall(r'<div[^>]*class="alert alert-[^"]*"[^>]*>', content)
        alerts_with_roles = re.findall(r'<div[^>]*class="alert alert-[^"]*"[^>]*role="[^"]*"[^>]*>', content)
        
        test1_passed = len(alert_divs) == len(alerts_with_roles) and len(alert_divs) > 0
        print(f"   {'✅' if test1_passed else '❌'} Test 1: Alert accessibility (found {len(alert_divs)} alerts, {len(alerts_with_roles)} with roles)")
        
        # Test 2: No invalid XPath references to missing fields
        invalid_xpath_patterns = [
            r'xpath.*expr="[^"]*//field\[@name=\'ref\'\]',  # ref field in tree view
            r'xpath.*expr="[^"]*//field\[@name="ref"\]',    # ref field in tree view
        ]
        
        invalid_xpath_found = False
        for pattern in invalid_xpath_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                invalid_xpath_found = True
                break
        
        test2_passed = not invalid_xpath_found
        print(f"   {'✅' if test2_passed else '❌'} Test 2: No invalid XPath references to missing fields")
        
        # Test 3: Valid XML structure
        test3_passed = True  # If we got here, XML parsed successfully
        print(f"   {'✅' if test3_passed else '❌'} Test 3: Valid XML structure")
        
        # Test 4: All XPath expressions use valid field references
        xpath_expressions = re.findall(r'xpath.*expr="([^"]*)"', content)
        valid_xpath_patterns = [
            '//header', '//form', '//field[@name=\'name\']', '//field[@name=\'partner_id\']',
            '//field[@name=\'amount\']', '//field[@name=\'journal_id\']', '//field[@name=\'date\']',
            '//field[@name=\'amount_company_currency_signed\']', '//search'
        ]
        
        invalid_xpaths = []
        for xpath in xpath_expressions:
            if not any(pattern in xpath for pattern in valid_xpath_patterns):
                invalid_xpaths.append(xpath)
        
        test4_passed = len(invalid_xpaths) == 0
        print(f"   {'✅' if test4_passed else '❌'} Test 4: All XPath expressions reference valid fields")
        if invalid_xpaths:
            print(f"      Invalid XPaths found: {invalid_xpaths}")
        
        # Test 5: Tree view inheritance works properly
        tree_view_content = re.search(r'view_account_payment_tree_enhanced.*?</record>', content, re.DOTALL)
        if tree_view_content:
            tree_content = tree_view_content.group(0)
            # Should not have references to non-existent fields like 'ref'
            invalid_tree_refs = re.findall(r'field\[@name=\'ref\'\]', tree_content)
            test5_passed = len(invalid_tree_refs) == 0
        else:
            test5_passed = False
        
        print(f"   {'✅' if test5_passed else '❌'} Test 5: Tree view inheritance is valid")
        
        # Test 6: All alert divs have proper structure
        alert_structure_valid = True
        for alert in alert_divs:
            if 'role=' not in alert:
                alert_structure_valid = False
                break
        
        test6_passed = alert_structure_valid
        print(f"   {'✅' if test6_passed else '❌'} Test 6: All alert divs have proper ARIA roles")
        
        # Calculate overall results
        tests = [test1_passed, test2_passed, test3_passed, test4_passed, test5_passed, test6_passed]
        passed_tests = sum(tests)
        total_tests = len(tests)
        
        print(f"\n" + "=" * 55)
        print(f"📊 ALERT AND XPATH FIX RESULTS")
        print(f"=" * 55)
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print(f"\n🎉 ALL ALERT AND XPATH ISSUES RESOLVED!")
            print(f"")
            print(f"✅ Alert accessibility warnings FIXED")
            print(f"✅ XPath reference errors FIXED") 
            print(f"✅ Tree view inheritance FIXED")
            print(f"✅ All XML structure is valid")
            print(f"")
            print(f"🚀 READY FOR CLOUDPEPPER DEPLOYMENT!")
            return True
        else:
            print(f"\n❌ {total_tests - passed_tests} issues remain unresolved")
            return False
            
    except ET.ParseError as e:
        print(f"❌ CRITICAL: XML syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ CRITICAL: Test error: {e}")
        return False

if __name__ == "__main__":
    test_alert_and_xpath_fixes()
