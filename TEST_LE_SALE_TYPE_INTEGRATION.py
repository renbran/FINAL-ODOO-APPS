#!/usr/bin/env python3
"""
Test le_sale_type Integration
Validates that the sale_order_type_id field integration works correctly.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LeSaleTypeIntegrationTest:
    def __init__(self):
        self.base_path = r"d:\RUNNING APPS\ready production\latest\odoo17_final\oe_sale_dashboard_17"
        self.test_results = []
        self.errors = []
        
    def log_test(self, test_name, status, details=""):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if status == 'PASS':
            logger.info(f"✅ {test_name}: {details}")
        elif status == 'FAIL':
            logger.error(f"❌ {test_name}: {details}")
            self.errors.append(result)
        else:
            logger.warning(f"⚠️  {test_name}: {details}")
    
    def test_manifest_dependencies(self):
        """Test that le_sale_type is added to dependencies"""
        try:
            manifest_path = os.path.join(self.base_path, "__manifest__.py")
            
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "'le_sale_type'" in content:
                self.log_test("Manifest Dependencies", "PASS", "le_sale_type found in dependencies")
            else:
                self.log_test("Manifest Dependencies", "FAIL", "le_sale_type not found in dependencies")
                
        except Exception as e:
            self.log_test("Manifest Dependencies", "FAIL", f"Error reading manifest: {e}")
    
    def test_backend_get_sales_types_method(self):
        """Test that get_sales_types method exists in backend"""
        try:
            backend_path = os.path.join(self.base_path, "models", "sale_dashboard.py")
            
            with open(backend_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "def get_sales_types(self):" in content:
                self.log_test("Backend get_sales_types Method", "PASS", "get_sales_types method found")
            else:
                self.log_test("Backend get_sales_types Method", "FAIL", "get_sales_types method not found")
            
            # Check for le.sale.type model usage
            if "le.sale.type" in content:
                self.log_test("Backend le.sale.type Usage", "PASS", "le.sale.type model reference found")
            else:
                self.log_test("Backend le.sale.type Usage", "FAIL", "le.sale.type model reference not found")
                
        except Exception as e:
            self.log_test("Backend get_sales_types Method", "FAIL", f"Error reading backend: {e}")
    
    def test_field_mapping_improvements(self):
        """Test field mapping improvements for sale_order_type_id"""
        try:
            field_mapping_path = os.path.join(self.base_path, "static", "src", "js", "field_mapping.js")
            
            with open(field_mapping_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for enhanced buildSaleTypeDomain function
            if "buildSaleTypeDomain" in content and "sale_order_type_id" in content:
                self.log_test("Field Mapping buildSaleTypeDomain", "PASS", "buildSaleTypeDomain function found")
            else:
                self.log_test("Field Mapping buildSaleTypeDomain", "FAIL", "buildSaleTypeDomain function not found")
            
            # Check for sale_order_type_id field logging
            if "sale_order_type_id field found from le_sale_type module" in content:
                self.log_test("Field Mapping Logging", "PASS", "le_sale_type module logging found")
            else:
                self.log_test("Field Mapping Logging", "FAIL", "le_sale_type module logging not found")
                
        except Exception as e:
            self.log_test("Field Mapping Improvements", "FAIL", f"Error reading field mapping: {e}")
    
    def test_frontend_integration(self):
        """Test frontend integration improvements"""
        try:
            js_path = os.path.join(self.base_path, "static", "src", "js", "dashboard.js")
            
            with open(js_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for updated _loadSalesTypes method
            if "get_sales_types" in content and "le_sale_type module" in content:
                self.log_test("Frontend Sales Types Integration", "PASS", "Updated _loadSalesTypes method found")
            else:
                self.log_test("Frontend Sales Types Integration", "FAIL", "Updated _loadSalesTypes method not found")
            
            # Check for fallback mechanism
            if "fallback search" in content.lower():
                self.log_test("Frontend Fallback Mechanism", "PASS", "Fallback mechanism found")
            else:
                self.log_test("Frontend Fallback Mechanism", "WARNING", "Fallback mechanism may be missing")
                
        except Exception as e:
            self.log_test("Frontend Integration", "FAIL", f"Error reading frontend: {e}")
    
    def test_file_structure_integrity(self):
        """Test that all required files exist and are accessible"""
        expected_files = [
            "__manifest__.py",
            "models/sale_dashboard.py",
            "static/src/js/field_mapping.js",
            "static/src/js/dashboard.js"
        ]
        
        missing_files = []
        for file_path in expected_files:
            full_path = os.path.join(self.base_path, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        if not missing_files:
            self.log_test("File Structure Integrity", "PASS", "All integration files found")
        else:
            self.log_test("File Structure Integrity", "FAIL", f"Missing files: {missing_files}")
    
    def test_code_quality_checks(self):
        """Test code quality and consistency"""
        try:
            # Check backend for proper logging usage
            backend_path = os.path.join(self.base_path, "models", "sale_dashboard.py")
            with open(backend_path, 'r', encoding='utf-8') as f:
                backend_content = f.read()
            
            if "_logger.warning" in backend_content and "_logger.error" in backend_content:
                self.log_test("Backend Logging Consistency", "PASS", "Proper logging usage found")
            else:
                self.log_test("Backend Logging Consistency", "FAIL", "Inconsistent logging usage")
            
            # Check frontend for proper error handling
            js_path = os.path.join(self.base_path, "static", "src", "js", "dashboard.js")
            with open(js_path, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            if "try {" in js_content and "catch (error)" in js_content:
                self.log_test("Frontend Error Handling", "PASS", "Proper error handling found")
            else:
                self.log_test("Frontend Error Handling", "FAIL", "Missing error handling")
                
        except Exception as e:
            self.log_test("Code Quality Checks", "FAIL", f"Error during quality checks: {e}")
    
    def generate_report(self):
        """Generate integration test report"""
        report = {
            'test_summary': {
                'total_tests': len(self.test_results),
                'passed': len([t for t in self.test_results if t['status'] == 'PASS']),
                'failed': len([t for t in self.test_results if t['status'] == 'FAIL']),
                'warnings': len([t for t in self.test_results if t['status'] == 'WARNING']),
                'timestamp': datetime.now().isoformat()
            },
            'test_results': self.test_results,
            'errors': self.errors
        }
        
        # Save report
        report_path = os.path.join(
            r"d:\RUNNING APPS\ready production\latest\odoo17_final",
            f"le_sale_type_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report, report_path
    
    def run_all_tests(self):
        """Run all integration tests"""
        logger.info("Starting le_sale_type integration validation...")
        
        # Run all tests
        self.test_manifest_dependencies()
        self.test_backend_get_sales_types_method()
        self.test_field_mapping_improvements()
        self.test_frontend_integration()
        self.test_file_structure_integrity()
        self.test_code_quality_checks()
        
        # Generate and display report
        report, report_path = self.generate_report()
        
        logger.info("\n" + "="*60)
        logger.info("LE_SALE_TYPE INTEGRATION RESULTS")
        logger.info("="*60)
        logger.info(f"Total Tests: {report['test_summary']['total_tests']}")
        logger.info(f"✅ Passed: {report['test_summary']['passed']}")
        logger.info(f"❌ Failed: {report['test_summary']['failed']}")
        logger.info(f"⚠️  Warnings: {report['test_summary']['warnings']}")
        logger.info(f"Report saved to: {report_path}")
        logger.info("="*60)
        
        if self.errors:
            logger.error("\nFAILED TESTS:")
            for error in self.errors:
                logger.error(f"- {error['test']}: {error['details']}")
        
        return report

def main():
    """Main test execution"""
    try:
        tester = LeSaleTypeIntegrationTest()
        report = tester.run_all_tests()
        
        # Return exit code based on results
        if report['test_summary']['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Integration test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
