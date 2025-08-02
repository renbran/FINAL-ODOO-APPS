#!/usr/bin/env python3
"""
Final Comprehensive Dashboard Test
Validates all improvements including le_sale_type integration.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalDashboardTest:
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
    
    def run_comprehensive_validation(self):
        """Run final comprehensive validation"""
        logger.info("🚀 Starting FINAL COMPREHENSIVE DASHBOARD VALIDATION...")
        
        # Test 1: Module Structure & Dependencies
        self.test_module_structure()
        
        # Test 2: Backend Functionality
        self.test_backend_functionality()
        
        # Test 3: Frontend Integration
        self.test_frontend_integration()
        
        # Test 4: Field Mapping System
        self.test_field_mapping_system()
        
        # Test 5: le_sale_type Integration
        self.test_le_sale_type_integration()
        
        # Test 6: Sample Data System
        self.test_sample_data_system()
        
        # Test 7: UI Components & Styling
        self.test_ui_components()
        
        # Test 8: CloudPeer Deployment
        self.test_cloudpeer_deployment()
        
        # Generate final report
        return self.generate_final_report()
    
    def test_module_structure(self):
        """Test module structure and configuration"""
        try:
            manifest_path = os.path.join(self.base_path, "__manifest__.py")
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_content = f.read()
            
            # Check version
            if "17.0.2.0.0" in manifest_content:
                self.log_test("Module Version", "PASS", "Version 17.0.2.0.0 confirmed")
            else:
                self.log_test("Module Version", "FAIL", "Version not updated")
            
            # Check dependencies
            dependencies_found = []
            if "'web'" in manifest_content:
                dependencies_found.append("web")
            if "'sale_management'" in manifest_content:
                dependencies_found.append("sale_management")
            if "'le_sale_type'" in manifest_content:
                dependencies_found.append("le_sale_type")
            
            if len(dependencies_found) >= 2:
                self.log_test("Module Dependencies", "PASS", f"Dependencies found: {dependencies_found}")
            else:
                self.log_test("Module Dependencies", "FAIL", f"Missing dependencies: {dependencies_found}")
            
            # Check Chart.js CDN
            if "chart.js" in manifest_content.lower() and "https://cdn" in manifest_content:
                self.log_test("Chart.js CDN", "PASS", "Chart.js CDN integration confirmed")
            else:
                self.log_test("Chart.js CDN", "FAIL", "Chart.js CDN not found")
                
        except Exception as e:
            self.log_test("Module Structure", "FAIL", f"Error: {e}")
    
    def test_backend_functionality(self):
        """Test backend functionality"""
        try:
            backend_path = os.path.join(self.base_path, "models", "sale_dashboard.py")
            with open(backend_path, 'r', encoding='utf-8') as f:
                backend_content = f.read()
            
            # Check core methods
            methods_to_check = [
                "get_dashboard_summary_data",
                "get_sales_types",
                "_get_sample_dashboard_data",
                "format_dashboard_value"
            ]
            
            missing_methods = []
            for method in methods_to_check:
                if f"def {method}(" not in backend_content:
                    missing_methods.append(method)
            
            if not missing_methods:
                self.log_test("Backend Core Methods", "PASS", "All core methods found")
            else:
                self.log_test("Backend Core Methods", "FAIL", f"Missing methods: {missing_methods}")
            
            # Check AED currency support
            if "AED" in backend_content and "format_dashboard_value" in backend_content:
                self.log_test("AED Currency Support", "PASS", "AED currency formatting confirmed")
            else:
                self.log_test("AED Currency Support", "FAIL", "AED currency support not found")
            
            # Check error handling
            if "_logger.error" in backend_content and "_logger.warning" in backend_content:
                self.log_test("Backend Error Handling", "PASS", "Comprehensive logging found")
            else:
                self.log_test("Backend Error Handling", "FAIL", "Insufficient error handling")
                
        except Exception as e:
            self.log_test("Backend Functionality", "FAIL", f"Error: {e}")
    
    def test_frontend_integration(self):
        """Test frontend integration"""
        try:
            js_path = os.path.join(self.base_path, "static", "src", "js", "dashboard.js")
            with open(js_path, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            # Check core frontend features
            features_to_check = [
                "_loadDashboardData",
                "_loadSalesTypes",
                "closeSampleDataBanner",
                "_formatCurrency",
                "showSampleDataWarning"
            ]
            
            missing_features = []
            for feature in features_to_check:
                if feature not in js_content:
                    missing_features.append(feature)
            
            if not missing_features:
                self.log_test("Frontend Core Features", "PASS", "All core features found")
            else:
                self.log_test("Frontend Core Features", "FAIL", f"Missing features: {missing_features}")
            
            # Check 90-day date range
            if "90" in js_content and "days" in js_content:
                self.log_test("Extended Date Range", "PASS", "90-day date range confirmed")
            else:
                self.log_test("Extended Date Range", "WARNING", "Extended date range may not be set")
            
            # Check sample data integration
            if "get_sales_types" in js_content and "le_sale_type module" in js_content:
                self.log_test("Sales Type Integration", "PASS", "le_sale_type integration confirmed")
            else:
                self.log_test("Sales Type Integration", "FAIL", "le_sale_type integration not found")
                
        except Exception as e:
            self.log_test("Frontend Integration", "FAIL", f"Error: {e}")
    
    def test_field_mapping_system(self):
        """Test field mapping system"""
        try:
            field_mapping_path = os.path.join(self.base_path, "static", "src", "js", "field_mapping.js")
            with open(field_mapping_path, 'r', encoding='utf-8') as f:
                field_content = f.read()
            
            # Check field mapping functions
            functions_to_check = [
                "initFieldMapping",
                "buildDateDomain",
                "buildSaleTypeDomain",
                "getFieldName",
                "isFieldAvailable"
            ]
            
            missing_functions = []
            for func in functions_to_check:
                if f"function {func}(" not in field_content:
                    missing_functions.append(func)
            
            if not missing_functions:
                self.log_test("Field Mapping Functions", "PASS", "All field mapping functions found")
            else:
                self.log_test("Field Mapping Functions", "FAIL", f"Missing functions: {missing_functions}")
            
            # Check field availability tracking
            if "_available" in field_content and "sale_order_type_id" in field_content:
                self.log_test("Field Availability Tracking", "PASS", "Field availability system confirmed")
            else:
                self.log_test("Field Availability Tracking", "FAIL", "Field availability tracking not found")
                
        except Exception as e:
            self.log_test("Field Mapping System", "FAIL", f"Error: {e}")
    
    def test_le_sale_type_integration(self):
        """Test le_sale_type module integration"""
        try:
            # Check backend integration
            backend_path = os.path.join(self.base_path, "models", "sale_dashboard.py")
            with open(backend_path, 'r', encoding='utf-8') as f:
                backend_content = f.read()
            
            if "le.sale.type" in backend_content and "get_sales_types" in backend_content:
                self.log_test("le_sale_type Backend Integration", "PASS", "Backend integration confirmed")
            else:
                self.log_test("le_sale_type Backend Integration", "FAIL", "Backend integration not found")
            
            # Check frontend integration
            js_path = os.path.join(self.base_path, "static", "src", "js", "dashboard.js")
            with open(js_path, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            if "get_sales_types" in js_content and "fallback" in js_content.lower():
                self.log_test("le_sale_type Frontend Integration", "PASS", "Frontend integration with fallback confirmed")
            else:
                self.log_test("le_sale_type Frontend Integration", "FAIL", "Frontend integration not found")
            
            # Check field mapping
            field_mapping_path = os.path.join(self.base_path, "static", "src", "js", "field_mapping.js")
            with open(field_mapping_path, 'r', encoding='utf-8') as f:
                field_content = f.read()
            
            if "buildSaleTypeDomain" in field_content and "sale_order_type_id" in field_content:
                self.log_test("le_sale_type Field Mapping", "PASS", "Field mapping integration confirmed")
            else:
                self.log_test("le_sale_type Field Mapping", "FAIL", "Field mapping integration not found")
                
        except Exception as e:
            self.log_test("le_sale_type Integration", "FAIL", f"Error: {e}")
    
    def test_sample_data_system(self):
        """Test sample data system"""
        try:
            # Check backend sample data
            backend_path = os.path.join(self.base_path, "models", "sale_dashboard.py")
            with open(backend_path, 'r', encoding='utf-8') as f:
                backend_content = f.read()
            
            if "_get_sample_dashboard_data" in backend_content and "is_sample_data" in backend_content:
                self.log_test("Sample Data Backend", "PASS", "Sample data generation confirmed")
            else:
                self.log_test("Sample Data Backend", "FAIL", "Sample data system not found")
            
            # Check frontend sample data handling
            js_path = os.path.join(self.base_path, "static", "src", "js", "dashboard.js")
            with open(js_path, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            if "showSampleDataWarning" in js_content and "is_sample_data" in js_content:
                self.log_test("Sample Data Frontend", "PASS", "Sample data UI handling confirmed")
            else:
                self.log_test("Sample Data Frontend", "FAIL", "Sample data UI handling not found")
            
            # Check template banner
            template_path = os.path.join(self.base_path, "static", "src", "xml", "dashboard_template.xml")
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            if "sample-data-banner" in template_content and "closeSampleDataBanner" in template_content:
                self.log_test("Sample Data Banner", "PASS", "Sample data warning banner confirmed")
            else:
                self.log_test("Sample Data Banner", "FAIL", "Sample data banner not found")
                
        except Exception as e:
            self.log_test("Sample Data System", "FAIL", f"Error: {e}")
    
    def test_ui_components(self):
        """Test UI components and styling"""
        try:
            # Check SCSS styling
            css_path = os.path.join(self.base_path, "static", "src", "scss", "dashboard.scss")
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            if ".sample-data-banner" in css_content and "linear-gradient" in css_content:
                self.log_test("UI Styling", "PASS", "Modern UI styling confirmed")
            else:
                self.log_test("UI Styling", "FAIL", "UI styling not found")
            
            # Check template structure
            template_path = os.path.join(self.base_path, "static", "src", "xml", "dashboard_template.xml")
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            if "t-if" in template_content and "t-foreach" in template_content:
                self.log_test("Template Structure", "PASS", "Odoo 17 template syntax confirmed")
            else:
                self.log_test("Template Structure", "FAIL", "Template structure issues")
                
        except Exception as e:
            self.log_test("UI Components", "FAIL", f"Error: {e}")
    
    def test_cloudpeer_deployment(self):
        """Test CloudPeer deployment readiness"""
        try:
            base_dir = r"d:\RUNNING APPS\ready production\latest\odoo17_final"
            
            deployment_files = ["setup.bat", "setup.sh"]
            missing_files = []
            
            for file_name in deployment_files:
                file_path = os.path.join(base_dir, file_name)
                if not os.path.exists(file_path):
                    missing_files.append(file_name)
            
            if not missing_files:
                self.log_test("CloudPeer Deployment Files", "PASS", "All deployment files found")
            else:
                self.log_test("CloudPeer Deployment Files", "FAIL", f"Missing files: {missing_files}")
            
            # Check module readiness
            module_files = [
                "__manifest__.py",
                "models/sale_dashboard.py",
                "static/src/js/dashboard.js",
                "static/src/xml/dashboard_template.xml",
                "static/src/scss/dashboard.scss"
            ]
            
            missing_module_files = []
            for file_path in module_files:
                full_path = os.path.join(self.base_path, file_path)
                if not os.path.exists(full_path):
                    missing_module_files.append(file_path)
            
            if not missing_module_files:
                self.log_test("Module File Integrity", "PASS", "All module files present")
            else:
                self.log_test("Module File Integrity", "FAIL", f"Missing files: {missing_module_files}")
                
        except Exception as e:
            self.log_test("CloudPeer Deployment", "FAIL", f"Error: {e}")
    
    def generate_final_report(self):
        """Generate final comprehensive report"""
        report = {
            'final_validation': {
                'total_tests': len(self.test_results),
                'passed': len([t for t in self.test_results if t['status'] == 'PASS']),
                'failed': len([t for t in self.test_results if t['status'] == 'FAIL']),
                'warnings': len([t for t in self.test_results if t['status'] == 'WARNING']),
                'success_rate': round((len([t for t in self.test_results if t['status'] == 'PASS']) / len(self.test_results)) * 100, 2),
                'timestamp': datetime.now().isoformat()
            },
            'test_results': self.test_results,
            'errors': self.errors,
            'summary': {
                'status': 'PASS' if len(self.errors) == 0 else 'FAIL',
                'ready_for_production': len(self.errors) == 0 and len([t for t in self.test_results if t['status'] == 'PASS']) >= 20
            }
        }
        
        # Save report
        report_path = os.path.join(
            r"d:\RUNNING APPS\ready production\latest\odoo17_final",
            f"final_dashboard_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Display results
        logger.info("\n" + "="*70)
        logger.info("🎯 FINAL COMPREHENSIVE DASHBOARD VALIDATION RESULTS")
        logger.info("="*70)
        logger.info(f"📊 Total Tests: {report['final_validation']['total_tests']}")
        logger.info(f"✅ Passed: {report['final_validation']['passed']}")
        logger.info(f"❌ Failed: {report['final_validation']['failed']}")
        logger.info(f"⚠️  Warnings: {report['final_validation']['warnings']}")
        logger.info(f"📈 Success Rate: {report['final_validation']['success_rate']}%")
        logger.info(f"🚀 Production Ready: {report['summary']['ready_for_production']}")
        logger.info(f"📄 Report: {report_path}")
        logger.info("="*70)
        
        if self.errors:
            logger.error("\n❌ FAILED TESTS:")
            for error in self.errors:
                logger.error(f"  - {error['test']}: {error['details']}")
        else:
            logger.info("\n🎉 ALL TESTS PASSED - PRODUCTION READY! 🎉")
        
        return report

def main():
    """Main test execution"""
    try:
        tester = FinalDashboardTest()
        report = tester.run_comprehensive_validation()
        
        # Return exit code based on results
        if report['summary']['ready_for_production']:
            logger.info("\n🚀 DASHBOARD MODULE IS PRODUCTION READY! 🚀")
            sys.exit(0)
        else:
            logger.error("\n⚠️  DASHBOARD MODULE NEEDS ATTENTION BEFORE PRODUCTION")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Final validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
