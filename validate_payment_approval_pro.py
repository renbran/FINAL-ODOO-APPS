#!/usr/bin/env python3
"""
Payment Approval Pro Module Validator
=====================================

Validates the payment_approval_pro module for Odoo 17 compliance
and production readiness.
"""

import os
import sys
import json
import ast
import xml.etree.ElementTree as ET
from pathlib import Path

class PaymentApprovalProValidator:
    def __init__(self):
        self.module_path = Path("payment_approval_pro")
        self.errors = []
        self.warnings = []
        self.success_count = 0
        
    def log_error(self, message):
        self.errors.append(f"❌ ERROR: {message}")
        
    def log_warning(self, message):
        self.warnings.append(f"⚠️  WARNING: {message}")
        
    def log_success(self, message):
        self.success_count += 1
        print(f"✅ {message}")
        
    def validate_module_structure(self):
        """Validate module directory structure"""
        print("\n🔍 Validating Module Structure...")
        
        required_files = [
            "__init__.py",
            "__manifest__.py",
            "models/__init__.py",
            "models/payment_voucher.py",
            "models/payment_workflow.py",
            "security/payment_security.xml",
            "security/ir.model.access.csv",
            "data/sequence_data.xml",
            "data/email_templates.xml",
            "views/payment_voucher_views.xml",
            "views/payment_menus.xml",
        ]
        
        required_dirs = [
            "models",
            "security", 
            "data",
            "views",
            "static/src/js",
            "static/src/scss",
            "static/src/xml",
            "static/tests",
            "static/description"
        ]
        
        # Check required files
        for file_path in required_files:
            full_path = self.module_path / file_path
            if full_path.exists():
                self.log_success(f"Required file exists: {file_path}")
            else:
                self.log_error(f"Missing required file: {file_path}")
                
        # Check required directories
        for dir_path in required_dirs:
            full_path = self.module_path / dir_path
            if full_path.exists() and full_path.is_dir():
                self.log_success(f"Required directory exists: {dir_path}")
            else:
                self.log_error(f"Missing required directory: {dir_path}")
                
    def validate_manifest(self):
        """Validate __manifest__.py file"""
        print("\n🔍 Validating Manifest File...")
        
        manifest_path = self.module_path / "__manifest__.py"
        if not manifest_path.exists():
            self.log_error("__manifest__.py file not found")
            return
            
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse as Python AST
            tree = ast.parse(content)
            
            # Find the manifest dictionary
            manifest_dict = None
            for node in ast.walk(tree):
                if isinstance(node, ast.Dict):
                    manifest_dict = ast.literal_eval(node)
                    break
                    
            if not manifest_dict:
                self.log_error("Could not parse manifest dictionary")
                return
                
            # Check required fields
            required_fields = [
                'name', 'version', 'category', 'summary', 'description',
                'author', 'depends', 'data', 'assets', 'installable', 'license'
            ]
            
            for field in required_fields:
                if field in manifest_dict:
                    self.log_success(f"Manifest has required field: {field}")
                else:
                    self.log_error(f"Manifest missing required field: {field}")
                    
            # Validate version format
            version = manifest_dict.get('version', '')
            if version.startswith('17.0.'):
                self.log_success("Version format is correct for Odoo 17")
            else:
                self.log_error(f"Invalid version format: {version} (should start with '17.0.')")
                
            # Check dependencies
            depends = manifest_dict.get('depends', [])
            required_deps = ['base', 'mail', 'account', 'web']
            for dep in required_deps:
                if dep in depends:
                    self.log_success(f"Required dependency found: {dep}")
                else:
                    self.log_warning(f"Missing recommended dependency: {dep}")
                    
            # Validate assets structure
            assets = manifest_dict.get('assets', {})
            if 'web.assets_backend' in assets:
                self.log_success("Backend assets properly defined")
                backend_assets = assets['web.assets_backend']
                
                # Check for required asset types
                has_js = any('.js' in asset for asset in backend_assets)
                has_scss = any('.scss' in asset for asset in backend_assets)
                has_xml = any('.xml' in asset for asset in backend_assets)
                
                if has_js:
                    self.log_success("JavaScript assets included")
                else:
                    self.log_warning("No JavaScript assets found")
                    
                if has_scss:
                    self.log_success("SCSS assets included")
                else:
                    self.log_warning("No SCSS assets found")
                    
                if has_xml:
                    self.log_success("XML template assets included")
                else:
                    self.log_warning("No XML template assets found")
            else:
                self.log_error("Backend assets not properly defined")
                
        except Exception as e:
            self.log_error(f"Error parsing manifest: {str(e)}")
            
    def validate_python_files(self):
        """Validate Python files syntax and imports"""
        print("\n🔍 Validating Python Files...")
        
        python_files = [
            "__init__.py",
            "models/__init__.py", 
            "models/payment_voucher.py",
            "models/payment_workflow.py"
        ]
        
        for file_path in python_files:
            full_path = self.module_path / file_path
            if not full_path.exists():
                continue
                
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check syntax
                ast.parse(content)
                self.log_success(f"Python syntax valid: {file_path}")
                
                # Check for proper Odoo imports
                if 'models/' in file_path:
                    if 'from odoo import models, fields, api' in content:
                        self.log_success(f"Proper Odoo imports: {file_path}")
                    else:
                        self.log_warning(f"Missing standard Odoo imports: {file_path}")
                        
                    # Check for logging
                    if 'import logging' in content:
                        self.log_success(f"Logging properly imported: {file_path}")
                    else:
                        self.log_warning(f"Consider adding logging: {file_path}")
                        
            except SyntaxError as e:
                self.log_error(f"Python syntax error in {file_path}: {str(e)}")
            except Exception as e:
                self.log_error(f"Error reading {file_path}: {str(e)}")
                
    def validate_xml_files(self):
        """Validate XML files syntax"""
        print("\n🔍 Validating XML Files...")
        
        xml_files = [
            "security/payment_security.xml",
            "data/sequence_data.xml", 
            "data/email_templates.xml",
            "views/payment_voucher_views.xml",
            "views/payment_menus.xml",
            "static/src/xml/qr_templates.xml",
            "static/src/xml/payment_templates.xml"
        ]
        
        for file_path in xml_files:
            full_path = self.module_path / file_path
            if not full_path.exists():
                self.log_warning(f"XML file not found: {file_path}")
                continue
                
            try:
                ET.parse(full_path)
                self.log_success(f"XML syntax valid: {file_path}")
                
                # Additional validation for specific file types
                if 'security' in file_path:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if '<record model="res.groups"' in content:
                            self.log_success(f"Security groups defined: {file_path}")
                        if '<record model="ir.model.access"' in content:
                            self.log_success(f"Model access rules defined: {file_path}")
                            
            except ET.ParseError as e:
                self.log_error(f"XML syntax error in {file_path}: {str(e)}")
            except Exception as e:
                self.log_error(f"Error reading {file_path}: {str(e)}")
                
    def validate_javascript_files(self):
        """Validate JavaScript files"""
        print("\n🔍 Validating JavaScript Files...")
        
        js_files = [
            "static/src/js/payment_widget.js",
            "static/src/js/qr_verification.js",
            "static/src/js/dashboard.js",
            "static/tests/payment_tests.js"
        ]
        
        for file_path in js_files:
            full_path = self.module_path / file_path
            if not full_path.exists():
                self.log_warning(f"JavaScript file not found: {file_path}")
                continue
                
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for Odoo 17 module declaration
                if '/** @odoo-module **/' in content:
                    self.log_success(f"Proper Odoo module declaration: {file_path}")
                else:
                    self.log_error(f"Missing @odoo-module declaration: {file_path}")
                    
                # Check for modern imports
                if 'import {' in content and 'from "@' in content:
                    self.log_success(f"Modern ES6 imports: {file_path}")
                else:
                    self.log_warning(f"Consider using ES6 imports: {file_path}")
                    
                # Check for OWL components
                if 'Component' in content and 'useState' in content:
                    self.log_success(f"OWL component patterns: {file_path}")
                    
                # Check for registry usage
                if 'registry.category(' in content:
                    self.log_success(f"Proper registry usage: {file_path}")
                    
            except Exception as e:
                self.log_error(f"Error reading {file_path}: {str(e)}")
                
    def validate_static_assets(self):
        """Validate static assets structure"""
        print("\n🔍 Validating Static Assets...")
        
        # Check SCSS files
        scss_files = [
            "static/src/scss/payment_styles.scss",
            "static/src/scss/frontend.scss"
        ]
        
        for file_path in scss_files:
            full_path = self.module_path / file_path
            if full_path.exists():
                self.log_success(f"SCSS file exists: {file_path}")
                
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for OSUS branding
                if '--osus-primary' in content or '#1f4788' in content:
                    self.log_success(f"OSUS branding colors found: {file_path}")
                    
                # Check for responsive design
                if '@media' in content:
                    self.log_success(f"Responsive design patterns: {file_path}")
            else:
                self.log_warning(f"SCSS file not found: {file_path}")
                
        # Check for description files
        desc_files = [
            "static/description/icon.png",
            "static/description/index.html"
        ]
        
        for file_path in desc_files:
            full_path = self.module_path / file_path
            if full_path.exists():
                self.log_success(f"Description file exists: {file_path}")
            else:
                self.log_warning(f"Description file missing: {file_path}")
                
    def generate_report(self):
        """Generate validation report"""
        print("\n" + "="*60)
        print("📋 PAYMENT APPROVAL PRO VALIDATION REPORT")
        print("="*60)
        
        print(f"\n✅ Successful validations: {self.success_count}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   {warning}")
                
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"   {error}")
        else:
            print("\n🎉 No errors found!")
            
        # Overall assessment
        if len(self.errors) == 0:
            if len(self.warnings) <= 3:
                print("\n🚀 MODULE STATUS: PRODUCTION READY")
            else:
                print("\n⚠️  MODULE STATUS: READY WITH WARNINGS")
        else:
            print("\n❌ MODULE STATUS: NEEDS FIXES")
            
        print("\n📊 VALIDATION SUMMARY:")
        print(f"   • Total Checks: {self.success_count + len(self.warnings) + len(self.errors)}")
        print(f"   • Success Rate: {(self.success_count / (self.success_count + len(self.warnings) + len(self.errors))) * 100:.1f}%")
        
    def run_validation(self):
        """Run complete validation"""
        print("🔍 PAYMENT APPROVAL PRO MODULE VALIDATOR")
        print("="*50)
        
        self.validate_module_structure()
        self.validate_manifest()
        self.validate_python_files()
        self.validate_xml_files()
        self.validate_javascript_files()
        self.validate_static_assets()
        self.generate_report()
        
        return len(self.errors) == 0

if __name__ == "__main__":
    validator = PaymentApprovalProValidator()
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)
