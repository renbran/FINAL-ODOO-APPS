#!/usr/bin/env python3
"""
Enhanced Order Status Override Report - Validation Test
Validate the new enhanced report template and integration
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

class EnhancedReportValidator:
    def __init__(self, module_path="order_status_override"):
        self.module_path = Path(module_path)
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_tests = 0
        
    def log_success(self, message):
        print(f"✅ {message}")
        self.success_count += 1
        
    def log_error(self, message):
        print(f"❌ {message}")
        self.errors.append(message)
        
    def log_warning(self, message):
        print(f"⚠️ {message}")
        self.warnings.append(message)
        
    def run_test(self, test_name, test_func):
        """Run a test and track results"""
        self.total_tests += 1
        print(f"\n{'='*60}")
        print(f"🧪 Testing: {test_name}")
        print(f"{'='*60}")
        try:
            test_func()
        except Exception as e:
            self.log_error(f"Test '{test_name}' failed: {str(e)}")

    def test_enhanced_report_template(self):
        """Test the enhanced report template file"""
        template_path = self.module_path / "reports" / "enhanced_order_status_report_template.xml"
        
        if not template_path.exists():
            self.log_error("Enhanced report template file not found")
            return
            
        try:
            tree = ET.parse(template_path)
            root = tree.getroot()
            
            # Test for template structure
            templates = root.findall(".//template[@id='enhanced_order_status_report_template']")
            if templates:
                self.log_success("Enhanced report template definition found")
            else:
                self.log_error("Enhanced report template definition missing")
                
            # Test for key components
            components = [
                ".//div[@class='info-grid']",  # 2-column layout
                ".//div[@class='commission-table-header']",  # Commission headers
                ".//table[@class='commission-table table table-sm table-striped']",  # Commission tables
                ".//span[@class='status-badge']"  # Status badges
            ]
            
            for component in components:
                elements = root.findall(component)
                if elements:
                    self.log_success(f"Found {len(elements)} instances of component: {component}")
                else:
                    self.log_warning(f"Component not found or different class: {component}")
                    
        except ET.ParseError as e:
            self.log_error(f"XML parsing error in enhanced template: {str(e)}")

    def test_report_actions(self):
        """Test the report actions file"""
        actions_path = self.module_path / "reports" / "enhanced_order_status_report_actions.xml"
        
        if not actions_path.exists():
            self.log_error("Enhanced report actions file not found")
            return
            
        try:
            tree = ET.parse(actions_path)
            root = tree.getroot()
            
            # Test for report actions
            reports = root.findall(".//record[@model='ir.actions.report']")
            if len(reports) >= 2:
                self.log_success(f"Found {len(reports)} report actions (PDF and HTML)")
            else:
                self.log_warning(f"Expected at least 2 report actions, found {len(reports)}")
                
            # Test for button integration
            buttons = root.findall(".//button[@name='%(enhanced_order_status_report)d']")
            if buttons:
                self.log_success("Report button integration found")
            else:
                self.log_warning("Report button integration not found")
                
        except ET.ParseError as e:
            self.log_error(f"XML parsing error in actions file: {str(e)}")

    def test_manifest_integration(self):
        """Test manifest file includes new reports"""
        manifest_path = self.module_path / "__manifest__.py"
        
        if not manifest_path.exists():
            self.log_error("Manifest file not found")
            return
            
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Test for new report files
        required_files = [
            "enhanced_order_status_report_template.xml",
            "enhanced_order_status_report_actions.xml"
        ]
        
        for file_name in required_files:
            if file_name in content:
                self.log_success(f"Manifest includes: {file_name}")
            else:
                self.log_error(f"Manifest missing: {file_name}")

    def test_template_content(self):
        """Test template content for key features"""
        template_path = self.module_path / "reports" / "enhanced_order_status_report_template.xml"
        
        if not template_path.exists():
            self.log_error("Template file not found for content test")
            return
            
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Test for key features
        features = [
            ("2-Column Layout", "info-grid"),
            ("External Commission", "External Commission"),
            ("Internal Commission", "Internal Commission"),
            ("Status Badges", "status-badge"),
            ("OSUS Branding", "#1f4788"),
            ("Bootstrap Classes", "table table-sm table-striped"),
            ("Responsive Design", "@media (max-width: 768px)"),
            ("Print Optimization", "@media print"),
            ("Currency Formatting", "widget': 'monetary'"),
            ("Field Access", "t-field=")
        ]
        
        for feature_name, feature_text in features:
            if feature_text in content:
                self.log_success(f"Feature implemented: {feature_name}")
            else:
                self.log_warning(f"Feature might be missing: {feature_name}")

    def test_commission_structure(self):
        """Test commission structure in template"""
        template_path = self.module_path / "reports" / "enhanced_order_status_report_template.xml"
        
        if not template_path.exists():
            self.log_error("Template file not found for commission test")
            return
            
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Test for commission types
        external_commissions = ["broker_partner_id", "referrer_partner_id", "cashback_partner_id"]
        internal_commissions = ["agent1_partner_id", "agent2_partner_id", "manager_partner_id", "director_partner_id"]
        
        for commission in external_commissions:
            if commission in content:
                self.log_success(f"External commission found: {commission}")
            else:
                self.log_warning(f"External commission missing: {commission}")
                
        for commission in internal_commissions:
            if commission in content:
                self.log_success(f"Internal commission found: {commission}")
            else:
                self.log_warning(f"Internal commission missing: {commission}")

    def generate_report(self):
        """Generate comprehensive test report"""
        print(f"\n{'='*80}")
        print("🏁 ENHANCED ORDER STATUS REPORT - VALIDATION REPORT")
        print(f"{'='*80}")
        
        print(f"\n📊 TEST SUMMARY:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Successful Checks: {self.success_count}")
        print(f"   Errors: {len(self.errors)}")
        print(f"   Warnings: {len(self.warnings)}")
        
        if self.errors:
            print(f"\n❌ ERRORS FOUND ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
                
        if self.warnings:
            print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
                
        # Overall status
        print(f"\n🎯 OVERALL STATUS:")
        if not self.errors:
            print("   ✅ ENHANCED REPORT VALIDATION PASSED - Ready for use!")
            if self.warnings:
                print(f"   ⚠️ Note: {len(self.warnings)} warnings found (review recommended)")
        else:
            print(f"   ❌ ENHANCED REPORT VALIDATION FAILED - {len(self.errors)} errors need fixing")
            
        print(f"\n{'='*80}")

def main():
    """Main validation function"""
    print("🚀 Starting Enhanced Order Status Report Validation...")
    
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    validator = EnhancedReportValidator()
    
    # Run all validation tests
    validator.run_test("Enhanced Report Template", validator.test_enhanced_report_template)
    validator.run_test("Report Actions", validator.test_report_actions)
    validator.run_test("Manifest Integration", validator.test_manifest_integration)
    validator.run_test("Template Content Features", validator.test_template_content)
    validator.run_test("Commission Structure", validator.test_commission_structure)
    
    # Generate final report
    validator.generate_report()
    
    # Return exit code based on validation result
    return 0 if not validator.errors else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
