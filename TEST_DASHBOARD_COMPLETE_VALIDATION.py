#!/usr/bin/env python3
"""
Complete Dashboard Validation Test
Tests all recent improvements and ensures everything works together.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DashboardValidationTest:
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
    
    def test_manifest_configuration(self):
        """Test __manifest__.py configuration"""
        try:
            manifest_path = os.path.join(self.base_path, "__manifest__.py")
            
            if not os.path.exists(manifest_path):
                self.log_test("Manifest File Exists", "FAIL", "Manifest file not found")
                return
            
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check version update
            if "17.0.2.0.0" in content:
                self.log_test("Version Updated", "PASS", "Version 17.0.2.0.0 found")
            else:
                self.log_test("Version Updated", "FAIL", "Version 17.0.2.0.0 not found")
            
            # Check Chart.js CDN
            if "chart.js" in content.lower() and ("https://cdn" in content or "https://cdnjs" in content):
                self.log_test("Chart.js CDN Integration", "PASS", "Chart.js CDN found in manifest")
            else:
                self.log_test("Chart.js CDN Integration", "FAIL", "Chart.js CDN not found")
            
            # Check enhanced description
            if "Production-ready" in content:
                self.log_test("Enhanced Description", "PASS", "Production-ready description found")
            else:
                self.log_test("Enhanced Description", "WARNING", "Enhanced description may be missing")
                
        except Exception as e:
            self.log_test("Manifest Configuration", "FAIL", f"Error reading manifest: {e}")
    
    def test_backend_improvements(self):
        """Test backend file improvements"""
        try:
            backend_path = os.path.join(self.base_path, "models", "sale_dashboard.py")
            
            if not os.path.exists(backend_path):
                self.log_test("Backend File Exists", "FAIL", "Backend file not found")
                return
            
            with open(backend_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check sample data method
            if "_get_sample_dashboard_data" in content:
                self.log_test("Sample Data Method", "PASS", "Sample data method found")
            else:
                self.log_test("Sample Data Method", "FAIL", "Sample data method not found")
            
            # Check AED currency formatting
            if "AED" in content and ("format_dashboard_value" in content or "currency_format" in content):
                self.log_test("AED Currency Integration", "PASS", "AED currency formatting found")
            else:
                self.log_test("AED Currency Integration", "FAIL", "AED currency formatting not found")
            
            # Check enhanced error handling
            if "logger.info" in content and "logger.error" in content:
                self.log_test("Enhanced Logging", "PASS", "Enhanced logging found")
            else:
                self.log_test("Enhanced Logging", "WARNING", "Enhanced logging may be missing")
                
        except Exception as e:
            self.log_test("Backend Improvements", "FAIL", f"Error reading backend: {e}")
    
    def test_frontend_improvements(self):
        """Test frontend JavaScript improvements"""
        try:
            js_path = os.path.join(self.base_path, "static", "src", "js", "dashboard.js")
            
            if not os.path.exists(js_path):
                self.log_test("JavaScript File Exists", "FAIL", "JavaScript file not found")
                return
            
            with open(js_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check 90-day date range
            if "90" in content and "days" in content:
                self.log_test("Extended Date Range", "PASS", "90-day date range found")
            else:
                self.log_test("Extended Date Range", "WARNING", "90-day date range may be missing")
            
            # Check sample data state management
            if "showSampleDataWarning" in content:
                self.log_test("Sample Data State Management", "PASS", "Sample data state management found")
            else:
                self.log_test("Sample Data State Management", "FAIL", "Sample data state management not found")
            
            # Check close banner method
            if "closeSampleDataBanner" in content:
                self.log_test("Close Banner Method", "PASS", "Close banner method found")
            else:
                self.log_test("Close Banner Method", "FAIL", "Close banner method not found")
            
            # Check AED currency formatting
            if "_formatCurrency" in content and "AED" in content:
                self.log_test("Frontend Currency Formatting", "PASS", "Frontend currency formatting found")
            else:
                self.log_test("Frontend Currency Formatting", "WARNING", "Frontend currency formatting may be missing")
                
        except Exception as e:
            self.log_test("Frontend Improvements", "FAIL", f"Error reading JavaScript: {e}")
    
    def test_template_improvements(self):
        """Test template improvements"""
        try:
            template_path = os.path.join(self.base_path, "static", "src", "xml", "dashboard_template.xml")
            
            if not os.path.exists(template_path):
                self.log_test("Template File Exists", "FAIL", "Template file not found")
                return
            
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check sample data banner
            if "sample-data-banner" in content and "t-if" in content and "showSampleDataWarning" in content:
                self.log_test("Sample Data Banner", "PASS", "Sample data banner template found")
            else:
                self.log_test("Sample Data Banner", "FAIL", "Sample data banner template not found")
            
            # Check close button
            if "closeSampleDataBanner" in content and "t-on-click" in content:
                self.log_test("Banner Close Button", "PASS", "Banner close button found")
            else:
                self.log_test("Banner Close Button", "FAIL", "Banner close button not found")
            
            # Check warning content
            if "demonstration" in content.lower() and "sample" in content.lower():
                self.log_test("Warning Content", "PASS", "Warning content found")
            else:
                self.log_test("Warning Content", "WARNING", "Warning content may be missing")
                
        except Exception as e:
            self.log_test("Template Improvements", "FAIL", f"Error reading template: {e}")
    
    def test_styling_improvements(self):
        """Test CSS styling improvements"""
        try:
            css_path = os.path.join(self.base_path, "static", "src", "scss", "dashboard.scss")
            
            if not os.path.exists(css_path):
                self.log_test("CSS File Exists", "FAIL", "CSS file not found")
                return
            
            with open(css_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check sample data banner styling
            if ".sample-data-banner" in content:
                self.log_test("Sample Data Banner Styling", "PASS", "Sample data banner styling found")
            else:
                self.log_test("Sample Data Banner Styling", "FAIL", "Sample data banner styling not found")
            
            # Check container width fixes
            if "max-width" in content and "width: 100%" in content:
                self.log_test("Container Width Fixes", "PASS", "Container width fixes found")
            else:
                self.log_test("Container Width Fixes", "WARNING", "Container width fixes may be missing")
            
            # Check gradient styling
            if "linear-gradient" in content:
                self.log_test("Modern Gradient Styling", "PASS", "Modern gradient styling found")
            else:
                self.log_test("Modern Gradient Styling", "WARNING", "Modern gradient styling may be missing")
                
        except Exception as e:
            self.log_test("Styling Improvements", "FAIL", f"Error reading CSS: {e}")
    
    def test_file_structure(self):
        """Test overall file structure integrity"""
        expected_files = [
            "__manifest__.py",
            "models/sale_dashboard.py",
            "static/src/js/dashboard.js",
            "static/src/xml/dashboard_template.xml",
            "static/src/scss/dashboard.scss",
            "views/dashboard_views.xml"  # Corrected filename
        ]
        
        missing_files = []
        for file_path in expected_files:
            full_path = os.path.join(self.base_path, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        if not missing_files:
            self.log_test("File Structure Integrity", "PASS", "All expected files found")
        else:
            self.log_test("File Structure Integrity", "FAIL", f"Missing files: {missing_files}")
    
    def test_cloudpeer_deployment_package(self):
        """Test CloudPeer deployment package"""
        deployment_files = [
            "setup.bat",
            "setup.sh"
        ]
        
        base_dir = r"d:\RUNNING APPS\ready production\latest\odoo17_final"
        missing_deployment_files = []
        
        for file_name in deployment_files:
            file_path = os.path.join(base_dir, file_name)
            if not os.path.exists(file_path):
                missing_deployment_files.append(file_name)
        
        if not missing_deployment_files:
            self.log_test("CloudPeer Deployment Package", "PASS", "All deployment files found")
        else:
            self.log_test("CloudPeer Deployment Package", "FAIL", f"Missing deployment files: {missing_deployment_files}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
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
            f"dashboard_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report, report_path
    
    def run_all_tests(self):
        """Run all validation tests"""
        logger.info("Starting comprehensive dashboard validation...")
        
        # Run all tests
        self.test_manifest_configuration()
        self.test_backend_improvements()
        self.test_frontend_improvements()
        self.test_template_improvements()
        self.test_styling_improvements()
        self.test_file_structure()
        self.test_cloudpeer_deployment_package()
        
        # Generate and display report
        report, report_path = self.generate_report()
        
        logger.info("\n" + "="*60)
        logger.info("DASHBOARD VALIDATION RESULTS")
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
        validator = DashboardValidationTest()
        report = validator.run_all_tests()
        
        # Return exit code based on results
        if report['test_summary']['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
