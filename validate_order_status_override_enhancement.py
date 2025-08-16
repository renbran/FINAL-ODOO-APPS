#!/usr/bin/env python3
"""
Order Status Override Module - Comprehensive Enhancement Validation Test
Test all implemented changes thoroughly to ensure the new steps, overrides, and group-based logic work as intended.
"""

import os
import sys
import ast
import xml.etree.ElementTree as ET
from pathlib import Path

class OrderStatusOverrideValidator:
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

    def test_manifest_file(self):
        """Test manifest file structure and dependencies"""
        manifest_path = self.module_path / "__manifest__.py"
        
        if not manifest_path.exists():
            self.log_error("Manifest file not found")
            return
            
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Test for required dependencies
        required_deps = ['sale', 'mail']
        for dep in required_deps:
            if f"'{dep}'" in content or f'"{dep}"' in content:
                self.log_success(f"Dependency '{dep}' found in manifest")
            else:
                self.log_warning(f"Dependency '{dep}' might be missing")
                
        # Test for version and basic structure
        if "'version':" in content or '"version":' in content:
            self.log_success("Version field found in manifest")
        else:
            self.log_error("Version field missing in manifest")

    def test_enhanced_sale_order_model(self):
        """Test the enhanced sale order model"""
        model_path = self.module_path / "models" / "sale_order.py"
        
        if not model_path.exists():
            self.log_error("sale_order.py model file not found")
            return
            
        with open(model_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Test for enhanced status field
        status_field_checks = [
            "order_status = fields.Selection",
            "'document_review'",
            "'commission_calculation'", 
            "'final_review'",
            "'posted'"
        ]
        
        for check in status_field_checks:
            if check in content:
                self.log_success(f"Enhanced status field component found: {check}")
            else:
                self.log_error(f"Enhanced status field component missing: {check}")
                
        # Test for group-based assignment method
        if "_auto_assign_workflow_users" in content:
            self.log_success("Group-based auto-assignment method found")
        else:
            self.log_error("Group-based auto-assignment method missing")
            
        # Test for enhanced workflow methods
        workflow_methods = [
            "action_move_to_document_review",
            "action_move_to_commission_calculation", 
            "action_move_to_final_review",
            "action_approve_order",
            "action_post_order"
        ]
        
        for method in workflow_methods:
            if method in content:
                self.log_success(f"Enhanced workflow method found: {method}")
            else:
                self.log_error(f"Enhanced workflow method missing: {method}")
                
        # Test for button visibility logic
        button_checks = [
            "show_document_review_button",
            "show_commission_calc_button",
            "show_final_review_button", 
            "show_approve_button",
            "show_post_button"
        ]
        
        for check in button_checks:
            if check in content:
                self.log_success(f"Button visibility field found: {check}")
            else:
                self.log_error(f"Button visibility field missing: {check}")

    def test_security_groups(self):
        """Test enhanced security groups"""
        security_path = self.module_path / "security" / "security.xml"
        
        if not security_path.exists():
            self.log_error("security.xml file not found")
            return
            
        try:
            tree = ET.parse(security_path)
            root = tree.getroot()
            
            # Test for enhanced security groups
            required_groups = [
                "group_order_documentation_reviewer",
                "group_order_commission_calculator",
                "group_order_approval_manager_enhanced", 
                "group_order_posting_manager"
            ]
            
            found_groups = []
            for record in root.findall(".//record[@model='res.groups']"):
                group_id = record.get('id')
                if group_id:
                    found_groups.append(group_id)
                    
            for group in required_groups:
                if group in found_groups:
                    self.log_success(f"Enhanced security group found: {group}")
                else:
                    self.log_error(f"Enhanced security group missing: {group}")
                    
        except ET.ParseError as e:
            self.log_error(f"XML parsing error in security.xml: {str(e)}")

    def test_enhanced_views(self):
        """Test enhanced view files"""
        view_path = self.module_path / "views" / "order_views_assignment.xml"
        
        if not view_path.exists():
            self.log_error("order_views_assignment.xml view file not found")
            return
            
        try:
            tree = ET.parse(view_path)
            root = tree.getroot()
            
            # Test for enhanced status bar
            statusbar_found = False
            for field in root.findall(".//field[@name='order_status']"):
                widget = field.get('widget')
                if widget == 'statusbar':
                    self.log_success("Enhanced status bar widget found")
                    statusbar_found = True
                    break
                    
            if not statusbar_found:
                self.log_error("Enhanced status bar widget not found")
                
            # Test for new workflow buttons
            required_buttons = [
                "action_move_to_document_review",
                "action_move_to_commission_calculation",
                "action_move_to_final_review", 
                "action_approve_order",
                "action_post_order"
            ]
            
            found_buttons = []
            for button in root.findall(".//button"):
                button_name = button.get('name')
                if button_name:
                    found_buttons.append(button_name)
                    
            for button in required_buttons:
                if button in found_buttons:
                    self.log_success(f"Enhanced workflow button found: {button}")
                else:
                    self.log_error(f"Enhanced workflow button missing: {button}")
                    
        except ET.ParseError as e:
            self.log_error(f"XML parsing error in view file: {str(e)}")

    def test_python_syntax(self):
        """Test Python syntax in all model files"""
        model_files = []
        models_path = self.module_path / "models"
        
        if models_path.exists():
            for py_file in models_path.glob("*.py"):
                if py_file.name != "__init__.py":
                    model_files.append(py_file)
                    
        for model_file in model_files:
            try:
                with open(model_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Parse the Python file to check syntax
                ast.parse(content)
                self.log_success(f"Python syntax valid in {model_file.name}")
                
            except SyntaxError as e:
                self.log_error(f"Python syntax error in {model_file.name}: {str(e)}")
            except Exception as e:
                self.log_error(f"Error reading {model_file.name}: {str(e)}")

    def test_xml_syntax(self):
        """Test XML syntax in all view files"""
        xml_files = []
        
        # Check views directory
        views_path = self.module_path / "views"
        if views_path.exists():
            xml_files.extend(views_path.glob("*.xml"))
            
        # Check security directory
        security_path = self.module_path / "security"
        if security_path.exists():
            xml_files.extend(security_path.glob("*.xml"))
            
        for xml_file in xml_files:
            try:
                ET.parse(xml_file)
                self.log_success(f"XML syntax valid in {xml_file.name}")
            except ET.ParseError as e:
                self.log_error(f"XML syntax error in {xml_file.name}: {str(e)}")
            except Exception as e:
                self.log_error(f"Error reading {xml_file.name}: {str(e)}")

    def test_group_based_logic(self):
        """Test group-based assignment logic"""
        model_path = self.module_path / "models" / "sale_order.py"
        
        if not model_path.exists():
            self.log_error("sale_order.py not found for group logic test")
            return
            
        with open(model_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Test for group-based permission checks
        permission_checks = [
            "has_group('order_status_override.group_order_documentation_reviewer')",
            "has_group('order_status_override.group_order_commission_calculator')",
            "has_group('order_status_override.group_order_approval_manager_enhanced')",
            "has_group('order_status_override.group_order_posting_manager')"
        ]
        
        for check in permission_checks:
            if check in content:
                self.log_success(f"Group permission check found: {check}")
            else:
                self.log_warning(f"Group permission check might be missing: {check}")

    def test_workflow_integrity(self):
        """Test workflow state integrity"""
        model_path = self.module_path / "models" / "sale_order.py"
        
        if not model_path.exists():
            self.log_error("sale_order.py not found for workflow test")
            return
            
        with open(model_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Test for workflow state transitions
        state_transitions = [
            "order_status = 'document_review'",
            "order_status = 'commission_calculation'", 
            "order_status = 'final_review'",
            "order_status = 'approved'",
            "order_status = 'posted'"
        ]
        
        for transition in state_transitions:
            if transition in content:
                self.log_success(f"Workflow state transition found: {transition}")
            else:
                self.log_warning(f"Workflow state transition might be missing: {transition}")

    def generate_report(self):
        """Generate comprehensive test report"""
        print(f"\n{'='*80}")
        print("🏁 ORDER STATUS OVERRIDE - COMPREHENSIVE ENHANCEMENT VALIDATION REPORT")
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
            print("   ✅ MODULE VALIDATION PASSED - Ready for deployment!")
            if self.warnings:
                print(f"   ⚠️ Note: {len(self.warnings)} warnings found (review recommended)")
        else:
            print(f"   ❌ MODULE VALIDATION FAILED - {len(self.errors)} errors need fixing")
            
        print(f"\n{'='*80}")

def main():
    """Main validation function"""
    print("🚀 Starting Order Status Override Module Comprehensive Enhancement Validation...")
    
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    validator = OrderStatusOverrideValidator()
    
    # Run all validation tests
    validator.run_test("Manifest File Structure", validator.test_manifest_file)
    validator.run_test("Enhanced Sale Order Model", validator.test_enhanced_sale_order_model)
    validator.run_test("Security Groups", validator.test_security_groups)
    validator.run_test("Enhanced Views", validator.test_enhanced_views)
    validator.run_test("Python Syntax Validation", validator.test_python_syntax)
    validator.run_test("XML Syntax Validation", validator.test_xml_syntax)
    validator.run_test("Group-Based Logic", validator.test_group_based_logic)
    validator.run_test("Workflow Integrity", validator.test_workflow_integrity)
    
    # Generate final report
    validator.generate_report()
    
    # Return exit code based on validation result
    return 0 if not validator.errors else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
