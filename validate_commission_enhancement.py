#!/usr/bin/env python3
"""
Commission AX Enhancement Validation Script
============================================

This script validates the comprehensive enhancement of the commission_ax module
including the new CommissionAX model, views, security, automation, and integration.
"""

import os
import sys
import json
from datetime import datetime
import xml.etree.ElementTree as ET

class CommissionAXValidator:
    def __init__(self, module_path):
        self.module_path = module_path
        self.errors = []
        self.warnings = []
        self.success = []
        
    def log_error(self, message):
        self.errors.append(f"❌ ERROR: {message}")
        
    def log_warning(self, message):
        self.warnings.append(f"⚠️  WARNING: {message}")
        
    def log_success(self, message):
        self.success.append(f"✅ SUCCESS: {message}")
    
    def validate_file_exists(self, filepath, required=True):
        """Validate that a file exists"""
        full_path = os.path.join(self.module_path, filepath)
        if os.path.exists(full_path):
            self.log_success(f"File exists: {filepath}")
            return True
        else:
            if required:
                self.log_error(f"Required file missing: {filepath}")
            else:
                self.log_warning(f"Optional file missing: {filepath}")
            return False
    
    def validate_python_syntax(self, filepath):
        """Validate Python file syntax"""
        full_path = os.path.join(self.module_path, filepath)
        if not os.path.exists(full_path):
            return False
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, full_path, 'exec')
            self.log_success(f"Python syntax valid: {filepath}")
            return True
        except SyntaxError as e:
            self.log_error(f"Python syntax error in {filepath}: {e}")
            return False
        except Exception as e:
            self.log_error(f"Error reading {filepath}: {e}")
            return False
    
    def validate_xml_syntax(self, filepath):
        """Validate XML file syntax"""
        full_path = os.path.join(self.module_path, filepath)
        if not os.path.exists(full_path):
            return False
            
        try:
            ET.parse(full_path)
            self.log_success(f"XML syntax valid: {filepath}")
            return True
        except ET.ParseError as e:
            self.log_error(f"XML syntax error in {filepath}: {e}")
            return False
        except Exception as e:
            self.log_error(f"Error reading {filepath}: {e}")
            return False
    
    def validate_commission_model(self):
        """Validate the CommissionAX model implementation"""
        model_file = "models/commission_ax.py"
        if not self.validate_file_exists(model_file):
            return False
        
        if not self.validate_python_syntax(model_file):
            return False
        
        full_path = os.path.join(self.module_path, model_file)
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required elements
        required_elements = [
            'class CommissionAX',
            '_name = \'commission.ax\'',
            'state = fields.Selection',
            'action_calculate_commission',
            'action_confirm_commission',
            'action_create_vendor_bill',
            '_cron_process_commissions',
            '_check_order_invoice_requirements',
        ]
        
        for element in required_elements:
            if element in content:
                self.log_success(f"CommissionAX model contains: {element}")
            else:
                self.log_error(f"CommissionAX model missing: {element}")
        
        # Check state workflow
        states = ['draft', 'calculated', 'confirmed', 'paid', 'cancelled']
        for state in states:
            if f"'{state}'" in content:
                self.log_success(f"State workflow contains: {state}")
            else:
                self.log_error(f"State workflow missing: {state}")
    
    def validate_views(self):
        """Validate the commission views"""
        views_file = "views/commission_ax_views.xml"
        if not self.validate_file_exists(views_file):
            return False
        
        if not self.validate_xml_syntax(views_file):
            return False
        
        full_path = os.path.join(self.module_path, views_file)
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required views
        required_views = [
            'view_commission_ax_form',
            'view_commission_ax_tree',
            'view_commission_ax_search',
            'view_commission_ax_kanban',
            'action_commission_ax',
            'menu_commission_ax_root',
        ]
        
        for view in required_views:
            if view in content:
                self.log_success(f"Views contain: {view}")
            else:
                self.log_error(f"Views missing: {view}")
        
        # Check for Odoo 17 compatibility
        if 'attrs=' in content:
            self.log_warning("Views contain deprecated 'attrs' syntax")
        
        if 'invisible=' in content and 'readonly=' in content:
            self.log_success("Views use modern Odoo 17 syntax")
    
    def validate_security(self):
        """Validate security configuration"""
        security_files = [
            "security/security.xml",
            "security/ir.model.access.csv"
        ]
        
        for file in security_files:
            if not self.validate_file_exists(file):
                continue
            
            if file.endswith('.xml'):
                self.validate_xml_syntax(file)
            
            full_path = os.path.join(self.module_path, file)
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'commission_ax' in content:
                self.log_success(f"Security file contains commission_ax references: {file}")
            else:
                self.log_error(f"Security file missing commission_ax references: {file}")
    
    def validate_data_files(self):
        """Validate data configuration"""
        data_file = "data/commission_data.xml"
        if not self.validate_file_exists(data_file):
            return False
        
        if not self.validate_xml_syntax(data_file):
            return False
        
        full_path = os.path.join(self.module_path, data_file)
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required data elements
        required_data = [
            'seq_commission_ax',
            'cron_process_commissions',
            'email_template_commission_created',
            'commission_ax.auto_process_enabled',
        ]
        
        for data in required_data:
            if data in content:
                self.log_success(f"Data file contains: {data}")
            else:
                self.log_error(f"Data file missing: {data}")
    
    def validate_manifest(self):
        """Validate manifest file"""
        manifest_file = "__manifest__.py"
        if not self.validate_file_exists(manifest_file):
            return False
        
        if not self.validate_python_syntax(manifest_file):
            return False
        
        full_path = os.path.join(self.module_path, manifest_file)
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check dependencies
        required_deps = ['sale', 'purchase', 'account', 'mail']
        for dep in required_deps:
            if f"'{dep}'" in content:
                self.log_success(f"Manifest contains dependency: {dep}")
            else:
                self.log_error(f"Manifest missing dependency: {dep}")
        
        # Check data files
        required_data_files = [
            'security/security.xml',
            'security/ir.model.access.csv',
            'data/commission_data.xml',
            'views/commission_ax_views.xml',
        ]
        
        for data_file in required_data_files:
            if data_file in content:
                self.log_success(f"Manifest includes data file: {data_file}")
            else:
                self.log_error(f"Manifest missing data file: {data_file}")
    
    def validate_models_init(self):
        """Validate models __init__.py includes commission_ax"""
        init_file = "models/__init__.py"
        if not self.validate_file_exists(init_file):
            return False
        
        if not self.validate_python_syntax(init_file):
            return False
        
        full_path = os.path.join(self.module_path, init_file)
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'commission_ax' in content:
            self.log_success("Models __init__.py includes commission_ax import")
        else:
            self.log_error("Models __init__.py missing commission_ax import")
    
    def validate_cloudpepper_compatibility(self):
        """Validate CloudPepper deployment compatibility"""
        # Check for stored fields in commission models
        models_to_check = [
            "models/sale_order.py",
            "models/purchase_order.py",
            "models/commission_ax.py"
        ]
        
        for model_file in models_to_check:
            if not os.path.exists(os.path.join(self.module_path, model_file)):
                continue
            
            full_path = os.path.join(self.module_path, model_file)
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for stored=True on computed fields used in email templates
            if 'store=True' in content:
                self.log_success(f"CloudPepper compatibility: {model_file} has stored fields")
            
            # Check for modern Odoo 17 syntax
            if '@api.depends' in content and 'def _compute_' in content:
                self.log_success(f"Modern compute methods in: {model_file}")
    
    def validate_automation_features(self):
        """Validate automation and cron features"""
        commission_model = "models/commission_ax.py"
        if not os.path.exists(os.path.join(self.module_path, commission_model)):
            return False
        
        full_path = os.path.join(self.module_path, commission_model)
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check automation features
        automation_features = [
            '_cron_process_commissions',
            'auto_process_eligible',
            'action_create_vendor_bill',
            'commission_type',
        ]
        
        for feature in automation_features:
            if feature in content:
                self.log_success(f"Automation feature present: {feature}")
            else:
                self.log_error(f"Automation feature missing: {feature}")
    
    def run_validation(self):
        """Run complete validation"""
        print(f"\n🔍 Commission AX Enhancement Validation")
        print(f"{'='*60}")
        print(f"Module Path: {self.module_path}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all validations
        validation_methods = [
            self.validate_manifest,
            self.validate_commission_model,
            self.validate_models_init,
            self.validate_views,
            self.validate_security,
            self.validate_data_files,
            self.validate_cloudpepper_compatibility,
            self.validate_automation_features,
        ]
        
        for method in validation_methods:
            try:
                method()
            except Exception as e:
                self.log_error(f"Validation method {method.__name__} failed: {e}")
        
        # Print results
        print(f"\n📊 Validation Results")
        print(f"{'='*60}")
        
        if self.success:
            print(f"\n✅ Successes ({len(self.success)}):")
            for msg in self.success:
                print(f"  {msg}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for msg in self.warnings:
                print(f"  {msg}")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for msg in self.errors:
                print(f"  {msg}")
        
        # Summary
        print(f"\n📋 Summary")
        print(f"{'='*60}")
        print(f"✅ Successes: {len(self.success)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")
        
        if self.errors:
            print(f"\n🚨 VALIDATION FAILED - Please fix errors before deployment")
            return False
        elif self.warnings:
            print(f"\n⚠️  VALIDATION PASSED WITH WARNINGS - Review warnings before deployment")
            return True
        else:
            print(f"\n🎉 VALIDATION PASSED - Module ready for deployment!")
            return True

def main():
    if len(sys.argv) > 1:
        module_path = sys.argv[1]
    else:
        module_path = os.path.dirname(os.path.abspath(__file__))
        # Assume we're running from module root, look for commission_ax
        if not os.path.exists(os.path.join(module_path, '__manifest__.py')):
            module_path = os.path.join(module_path, 'commission_ax')
    
    if not os.path.exists(module_path):
        print(f"❌ ERROR: Module path does not exist: {module_path}")
        sys.exit(1)
    
    if not os.path.exists(os.path.join(module_path, '__manifest__.py')):
        print(f"❌ ERROR: Not a valid Odoo module (missing __manifest__.py): {module_path}")
        sys.exit(1)
    
    validator = CommissionAXValidator(module_path)
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
