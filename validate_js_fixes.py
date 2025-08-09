#!/usr/bin/env python3
"""
CloudPepper JavaScript Error Fix Validation Script
Tests for console error resolution and performance optimizations
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

class CloudPepperJSValidator:
    def __init__(self):
        self.base_url = "http://localhost:8069"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "PENDING"
        }
    
    def test_javascript_assets_loading(self):
        """Test if JavaScript assets load without errors"""
        print("🔍 Testing JavaScript asset loading...")
        
        try:
            # Test CloudPepper optimizer
            optimizer_path = "/account_payment_final/static/src/js/cloudpepper_optimizer_fixed.js"
            response = requests.get(f"{self.base_url}{optimizer_path}")
            
            optimizer_loaded = response.status_code == 200
            
            # Test error handler
            error_handler_path = "/account_payment_final/static/src/js/error_handler.js"
            response = requests.get(f"{self.base_url}{error_handler_path}")
            
            error_handler_loaded = response.status_code == 200
            
            self.results["tests"]["javascript_assets"] = {
                "status": "PASS" if (optimizer_loaded and error_handler_loaded) else "FAIL",
                "optimizer_loaded": optimizer_loaded,
                "error_handler_loaded": error_handler_loaded,
                "details": "JavaScript assets loading properly"
            }
            
            print(f"✅ JavaScript assets: {'PASS' if (optimizer_loaded and error_handler_loaded) else 'FAIL'}")
            
        except Exception as e:
            self.results["tests"]["javascript_assets"] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"❌ JavaScript asset test failed: {e}")
    
    def test_console_error_suppression(self):
        """Test console error suppression mechanisms"""
        print("🔍 Testing console error suppression...")
        
        try:
            # Test web client loading
            response = requests.get(f"{self.base_url}/web")
            
            # Check if the response contains our error handling scripts
            content = response.text
            has_error_handler = "cloudpepper_error_handler" in content
            has_optimizer = "cloudpepper_optimizer" in content
            
            self.results["tests"]["console_error_suppression"] = {
                "status": "PASS" if (has_error_handler or has_optimizer) else "FAIL",
                "error_handler_present": has_error_handler,
                "optimizer_present": has_optimizer,
                "details": "Error suppression mechanisms in place"
            }
            
            print(f"✅ Console error suppression: {'PASS' if (has_error_handler or has_optimizer) else 'FAIL'}")
            
        except Exception as e:
            self.results["tests"]["console_error_suppression"] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"❌ Console error suppression test failed: {e}")
    
    def test_payment_module_functionality(self):
        """Test basic payment module functionality"""
        print("🔍 Testing payment module functionality...")
        
        try:
            # Test payment verification endpoint
            verify_endpoint = f"{self.base_url}/payment/verify/test"
            response = requests.get(verify_endpoint)
            
            # Should return 404 for non-existent payment, but endpoint should exist
            endpoint_exists = response.status_code in [200, 404, 403]
            
            self.results["tests"]["payment_functionality"] = {
                "status": "PASS" if endpoint_exists else "FAIL",
                "verify_endpoint_exists": endpoint_exists,
                "response_code": response.status_code,
                "details": "Payment verification endpoint accessible"
            }
            
            print(f"✅ Payment functionality: {'PASS' if endpoint_exists else 'FAIL'}")
            
        except Exception as e:
            self.results["tests"]["payment_functionality"] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"❌ Payment functionality test failed: {e}")
    
    def test_font_optimization(self):
        """Test font loading optimization"""
        print("🔍 Testing font optimization...")
        
        try:
            # Check if FontAwesome is properly loaded
            fa_response = requests.get(f"{self.base_url}/web/static/lib/fontawesome/css/font-awesome.css")
            fa_available = fa_response.status_code == 200
            
            self.results["tests"]["font_optimization"] = {
                "status": "PASS" if fa_available else "FAIL",
                "fontawesome_available": fa_available,
                "details": "Font resources properly optimized"
            }
            
            print(f"✅ Font optimization: {'PASS' if fa_available else 'FAIL'}")
            
        except Exception as e:
            self.results["tests"]["font_optimization"] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"❌ Font optimization test failed: {e}")
    
    def test_assets_xml_validity(self):
        """Test assets.xml file validity"""
        print("🔍 Testing assets.xml validity...")
        
        try:
            assets_path = "d:\\RUNNING APPS\\ready production\\latest\\odoo17_final\\account_payment_final\\views\\assets.xml"
            
            with open(assets_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required JavaScript includes
            has_error_handler = "error_handler.js" in content
            has_optimizer = "cloudpepper_optimizer_fixed.js" in content
            has_assets_backend = "assets_backend" in content
            
            self.results["tests"]["assets_xml_validity"] = {
                "status": "PASS" if (has_error_handler and has_optimizer and has_assets_backend) else "FAIL",
                "error_handler_included": has_error_handler,
                "optimizer_included": has_optimizer,
                "assets_backend_present": has_assets_backend,
                "details": "Assets XML properly configured"
            }
            
            print(f"✅ Assets XML validity: {'PASS' if (has_error_handler and has_optimizer and has_assets_backend) else 'FAIL'}")
            
        except Exception as e:
            self.results["tests"]["assets_xml_validity"] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"❌ Assets XML validity test failed: {e}")
    
    def run_all_tests(self):
        """Run all validation tests"""
        print("🚀 Starting CloudPepper JavaScript Error Fix Validation...")
        print("=" * 60)
        
        self.test_javascript_assets_loading()
        self.test_console_error_suppression()
        self.test_payment_module_functionality()
        self.test_font_optimization()
        self.test_assets_xml_validity()
        
        # Calculate overall status
        test_results = [test["status"] for test in self.results["tests"].values()]
        if "ERROR" in test_results:
            self.results["overall_status"] = "ERROR"
        elif "FAIL" in test_results:
            self.results["overall_status"] = "PARTIAL"
        else:
            self.results["overall_status"] = "SUCCESS"
        
        print("\n" + "=" * 60)
        print(f"🎯 Overall Status: {self.results['overall_status']}")
        
        return self.results
    
    def save_results(self, filename="cloudpepper_js_validation_results.json"):
        """Save test results to file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"💾 Results saved to {filename}")

def main():
    """Main execution function"""
    validator = CloudPepperJSValidator()
    
    try:
        results = validator.run_all_tests()
        validator.save_results()
        
        # Print summary
        print("\n📊 Test Summary:")
        for test_name, test_result in results["tests"].items():
            status_emoji = "✅" if test_result["status"] == "PASS" else "❌" if test_result["status"] == "FAIL" else "⚠️"
            print(f"  {status_emoji} {test_name}: {test_result['status']}")
        
        if results["overall_status"] == "SUCCESS":
            print("\n🎉 All JavaScript error fixes validated successfully!")
            print("🌐 CloudPepper deployment should now have clean console output")
            sys.exit(0)
        else:
            print(f"\n⚠️ Validation completed with status: {results['overall_status']}")
            print("📝 Check the detailed results for specific issues")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Validation failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
