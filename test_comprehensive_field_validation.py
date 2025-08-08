#!/usr/bin/env python3
"""
Comprehensive CloudPepper Field Validation Test
Ensures all common account.payment fields are available for inherited conditions
"""

import xml.etree.ElementTree as ET

def test_comprehensive_field_availability():
    """Test that all commonly referenced account.payment fields are available"""
    xml_file = "account_payment_final/views/account_payment_views.xml"
    
    print("🔍 COMPREHENSIVE CLOUDPEPPER FIELD VALIDATION")
    print("=" * 60)
    
    try:
        # Parse XML to check syntax
        tree = ET.parse(xml_file)
        print(f"✅ XML syntax validation - PASSED")
        
        # Read file content
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract all fields defined in our view
        import re
        defined_fields = set(re.findall(r'<field\s+name="([^"]+)"', content))
        
        # Common account.payment fields that might be referenced in inherited views
        critical_payment_fields = {
            'state',                    # Payment state (draft, posted, etc.)
            'partner_id',              # Partner field
            'amount',                  # Payment amount
            'payment_type',            # Inbound/outbound
            'is_internal_transfer',    # Internal transfer flag
            'journal_id',              # Payment journal
            'currency_id',             # Payment currency
            'partner_type',            # Customer/vendor
            'destination_account_id',  # Destination account for transfers
        }
        
        # Our custom fields that should also be available
        custom_fields = {
            'approval_state',
            'voucher_number',
            'qr_code',
            'qr_in_report',
            'reviewer_id',
            'approver_id',
            'authorizer_id',
        }
        
        all_required_fields = critical_payment_fields | custom_fields
        
        print(f"\n📊 Field Availability Check:")
        print(f"   🎯 Critical payment fields needed: {len(critical_payment_fields)}")
        print(f"   🔧 Custom workflow fields needed: {len(custom_fields)}")
        print(f"   📝 Total fields defined in view: {len(defined_fields)}")
        
        # Check for missing critical fields
        missing_critical = critical_payment_fields - defined_fields
        missing_custom = custom_fields - defined_fields
        
        if missing_critical:
            print(f"\n❌ Missing critical payment fields:")
            for field in sorted(missing_critical):
                print(f"   - {field}")
        else:
            print(f"\n✅ All critical payment fields available")
        
        if missing_custom:
            print(f"\n❌ Missing custom workflow fields:")
            for field in sorted(missing_custom):
                print(f"   - {field}")
        else:
            print(f"\n✅ All custom workflow fields available")
        
        # Additional CloudPepper compatibility checks
        print(f"\n🏗️ CloudPepper Compatibility Checks:")
        
        # Check 1: No direct state field conditions in our code
        state_conditions = re.findall(r'\bstate\s*(!=|==|in|not in)', content)
        if not state_conditions:
            print(f"   ✅ No problematic state field conditions")
        else:
            print(f"   ❌ Found {len(state_conditions)} problematic state conditions")
        
        # Check 2: All approval_state references are properly used
        approval_state_count = content.count('approval_state')
        if approval_state_count >= 50:
            print(f"   ✅ Extensive approval_state usage ({approval_state_count} references)")
        else:
            print(f"   ⚠️ Limited approval_state usage ({approval_state_count} references)")
        
        # Check 3: Required field availability for inherited conditions
        all_available = len(missing_critical) == 0 and len(missing_custom) == 0
        if all_available:
            print(f"   ✅ All fields available for inherited view conditions")
        else:
            print(f"   ❌ Some fields missing for inherited conditions")
        
        print(f"\n" + "=" * 60)
        print(f"📋 COMPREHENSIVE VALIDATION RESULTS")
        print(f"=" * 60)
        
        tests_passed = 0
        total_tests = 4
        
        if len(missing_critical) == 0:
            tests_passed += 1
        if len(missing_custom) == 0:
            tests_passed += 1
        if len(state_conditions) == 0:
            tests_passed += 1
        if approval_state_count >= 50:
            tests_passed += 1
        
        print(f"Tests Passed: {tests_passed}/{total_tests}")
        print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
        
        if tests_passed == total_tests:
            print(f"🎉 COMPREHENSIVE VALIDATION PASSED!")
            print(f"💡 All potential CloudPepper field issues resolved")
            print(f"🚀 Ready for deployment")
            return True
        else:
            print(f"❌ {total_tests - tests_passed} validation checks failed")
            return False
        
    except ET.ParseError as e:
        print(f"❌ CRITICAL: XML syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ CRITICAL: Validation error: {e}")
        return False

if __name__ == "__main__":
    test_comprehensive_field_availability()
