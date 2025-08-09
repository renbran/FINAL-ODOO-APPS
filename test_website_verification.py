#!/usr/bin/env python3
"""
Test script for Payment Verification Website functionality
"""

import sys
import os

def test_controller_imports():
    """Test if the controller imports are working"""
    print("Testing controller imports...")
    
    try:
        # Add the account_payment_final path
        sys.path.insert(0, 'account_payment_final')
        
        # Test controller import
        from controllers.main import PaymentVerificationController
        print("✅ Controller import successful")
        
        # Test controller methods exist
        controller = PaymentVerificationController()
        assert hasattr(controller, 'verify_payment'), "verify_payment method missing"
        assert hasattr(controller, 'verify_payment_json'), "verify_payment_json method missing"
        assert hasattr(controller, 'qr_verification_guide'), "qr_verification_guide method missing"
        assert hasattr(controller, 'bulk_verify_payments'), "bulk_verify_payments method missing"
        
        print("✅ All controller methods present")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_templates_exist():
    """Test if the template files exist"""
    print("\nTesting template files...")
    
    template_file = 'account_payment_final/views/payment_verification_templates.xml'
    
    if os.path.exists(template_file):
        print("✅ Template file exists")
        
        # Check if required templates are in the file
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        required_templates = [
            'payment_verification_page',
            'payment_verification_not_found',
            'payment_verification_error',
            'payment_qr_guide',
            'bulk_verification_form',
            'bulk_verification_results'
        ]
        
        missing_templates = []
        for template in required_templates:
            if f'id="{template}"' not in content:
                missing_templates.append(template)
        
        if missing_templates:
            print(f"❌ Missing templates: {missing_templates}")
            return False
        else:
            print("✅ All required templates found")
            return True
    else:
        print(f"❌ Template file not found: {template_file}")
        return False

def test_website_routes():
    """Test the expected website routes"""
    print("\nTesting website route definitions...")
    
    controller_file = 'account_payment_final/controllers/main.py'
    
    if os.path.exists(controller_file):
        with open(controller_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        expected_routes = [
            '/payment/verify/',
            '/payment/verify/json/',
            '/payment/qr-guide',
            '/payment/bulk-verify'
        ]
        
        missing_routes = []
        for route in expected_routes:
            if route not in content:
                missing_routes.append(route)
        
        if missing_routes:
            print(f"❌ Missing routes: {missing_routes}")
            return False
        else:
            print("✅ All required routes found")
            return True
    else:
        print(f"❌ Controller file not found: {controller_file}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Payment Verification Website Setup")
    print("=" * 50)
    
    results = []
    
    # Test 1: Controller imports
    results.append(test_controller_imports())
    
    # Test 2: Templates exist
    results.append(test_templates_exist())
    
    # Test 3: Routes defined
    results.append(test_website_routes())
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All tests passed ({passed}/{total})")
        print("\n🚀 Website verification system is ready for deployment!")
        print("\nWebsite URLs will be available at:")
        print("  • /payment/verify/<payment_id> - Main verification page")
        print("  • /payment/qr-guide - QR code help guide")
        print("  • /payment/bulk-verify - Bulk verification (authenticated users)")
        return True
    else:
        print(f"❌ {total - passed} tests failed ({passed}/{total} passed)")
        print("\n🔧 Please fix the issues above before deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
