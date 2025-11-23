#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM Executive Dashboard - Module Validator
Comprehensive validation script for production readiness

Usage:
    python3 module_validator.py [--verbose]
"""

import os
import sys
import ast
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ModuleValidator:
    """Comprehensive module validator for Odoo modules"""

    def __init__(self, module_path: str, verbose: bool = False):
        self.module_path = Path(module_path)
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        self.info = []
        self.score = 100

    def log(self, message: str, level: str = "INFO"):
        """Log messages with color coding"""
        if level == "ERROR":
            print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")
            self.errors.append(message)
            self.score -= 5
        elif level == "WARNING":
            print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")
            self.warnings.append(message)
            self.score -= 2
        elif level == "INFO":
            if self.verbose:
                print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")
            self.info.append(message)
        elif level == "SUCCESS":
            print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{text:^70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}\n")

    def validate_manifest(self) -> bool:
        """Validate __manifest__.py file"""
        self.print_header("Validating Manifest")

        manifest_path = self.module_path / '__manifest__.py'
        if not manifest_path.exists():
            self.log(f"Manifest file not found: {manifest_path}", "ERROR")
            return False

        try:
            with open(manifest_path, 'r') as f:
                manifest_content = f.read()
                manifest = ast.literal_eval(manifest_content)

            # Required fields
            required_fields = ['name', 'version', 'depends', 'data']
            for field in required_fields:
                if field not in manifest:
                    self.log(f"Missing required field in manifest: {field}", "ERROR")
                else:
                    self.log(f"Required field '{field}' present", "SUCCESS")

            # Check version format
            if 'version' in manifest:
                version = manifest['version']
                if not re.match(r'^\d+\.\d+\.\d+\.\d+\.\d+$', version):
                    self.log(f"Invalid version format: {version}. Expected: X.Y.Z.A.B", "WARNING")
                else:
                    self.log(f"Version format valid: {version}", "SUCCESS")

            # Check dependencies
            if 'depends' in manifest:
                deps = manifest['depends']
                required_deps = ['base', 'crm', 'sales_team']
                for dep in required_deps:
                    if dep not in deps:
                        self.log(f"Missing recommended dependency: {dep}", "WARNING")
                    else:
                        self.log(f"Dependency '{dep}' found", "INFO")

            # Check metadata
            metadata_fields = ['author', 'website', 'category', 'license']
            for field in metadata_fields:
                if field not in manifest:
                    self.log(f"Missing metadata field: {field}", "WARNING")
                else:
                    self.log(f"Metadata field '{field}' present", "INFO")

            # Check installable flag
            if manifest.get('installable', True) == False:
                self.log("Module marked as not installable", "WARNING")
            else:
                self.log("Module marked as installable", "SUCCESS")

            return True

        except Exception as e:
            self.log(f"Error parsing manifest: {str(e)}", "ERROR")
            return False

    def validate_structure(self) -> bool:
        """Validate module directory structure"""
        self.print_header("Validating Module Structure")

        # Required directories
        required_dirs = ['models', 'views', 'security']
        for dir_name in required_dirs:
            dir_path = self.module_path / dir_name
            if not dir_path.exists():
                self.log(f"Missing required directory: {dir_name}/", "ERROR")
            else:
                self.log(f"Directory '{dir_name}/' exists", "SUCCESS")

        # Recommended directories
        recommended_dirs = ['controllers', 'static', 'data', 'tests']
        for dir_name in recommended_dirs:
            dir_path = self.module_path / dir_name
            if not dir_path.exists():
                self.log(f"Missing recommended directory: {dir_name}/", "WARNING")
            else:
                self.log(f"Directory '{dir_name}/' exists", "INFO")

        # Required files
        required_files = ['__init__.py', '__manifest__.py']
        for file_name in required_files:
            file_path = self.module_path / file_name
            if not file_path.exists():
                self.log(f"Missing required file: {file_name}", "ERROR")
            else:
                self.log(f"File '{file_name}' exists", "SUCCESS")

        return len(self.errors) == 0

    def validate_python_files(self) -> bool:
        """Validate Python files syntax and style"""
        self.print_header("Validating Python Files")

        python_files = list(self.module_path.rglob('*.py'))
        self.log(f"Found {len(python_files)} Python files", "INFO")

        for py_file in python_files:
            try:
                with open(py_file, 'r') as f:
                    content = f.read()

                # Check syntax
                try:
                    ast.parse(content)
                    self.log(f"Syntax valid: {py_file.name}", "INFO")
                except SyntaxError as e:
                    self.log(f"Syntax error in {py_file.name}: {str(e)}", "ERROR")

                # Check for common issues
                if 'import *' in content:
                    self.log(f"Wildcard import found in {py_file.name}", "WARNING")

                # Check encoding declaration
                if not content.startswith('# -*- coding: utf-8 -*-'):
                    self.log(f"Missing encoding declaration in {py_file.name}", "WARNING")

            except Exception as e:
                self.log(f"Error reading {py_file.name}: {str(e)}", "ERROR")

        self.log("Python syntax validation complete", "SUCCESS")
        return True

    def validate_security(self) -> bool:
        """Validate security configuration"""
        self.print_header("Validating Security Configuration")

        # Check ir.model.access.csv
        access_csv = self.module_path / 'security' / 'ir.model.access.csv'
        if not access_csv.exists():
            self.log("Missing ir.model.access.csv", "ERROR")
        else:
            self.log("Access rights file exists", "SUCCESS")
            try:
                with open(access_csv, 'r') as f:
                    lines = f.readlines()
                    self.log(f"Found {len(lines)-1} access rights records", "INFO")

                    # Check header
                    expected_header = "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink"
                    if lines[0].strip() != expected_header:
                        self.log("Invalid access rights CSV header", "ERROR")

            except Exception as e:
                self.log(f"Error reading access rights: {str(e)}", "ERROR")

        # Check for security groups XML
        security_xml = self.module_path / 'security' / 'security_groups.xml'
        if not security_xml.exists():
            self.log("Security groups XML not found", "WARNING")
        else:
            self.log("Security groups XML exists", "SUCCESS")

        return True

    def validate_views(self) -> bool:
        """Validate XML view files"""
        self.print_header("Validating Views")

        view_files = list((self.module_path / 'views').rglob('*.xml'))
        self.log(f"Found {len(view_files)} view files", "INFO")

        for view_file in view_files:
            try:
                with open(view_file, 'r') as f:
                    content = f.read()

                # Basic XML validation
                if not content.strip().startswith('<?xml'):
                    self.log(f"Missing XML declaration in {view_file.name}", "WARNING")

                if '<odoo>' not in content and '<openerp>' not in content:
                    self.log(f"Missing Odoo root tag in {view_file.name}", "WARNING")

                # Check for common issues
                if 'eval=' in content and ('__import__' in content or 'exec(' in content):
                    self.log(f"Potentially dangerous eval in {view_file.name}", "ERROR")

                self.log(f"View file OK: {view_file.name}", "INFO")

            except Exception as e:
                self.log(f"Error reading {view_file.name}: {str(e)}", "ERROR")

        return True

    def validate_javascript(self) -> bool:
        """Validate JavaScript files"""
        self.print_header("Validating JavaScript Files")

        js_files = list(self.module_path.rglob('*.js'))
        self.log(f"Found {len(js_files)} JavaScript files", "INFO")

        for js_file in js_files:
            try:
                with open(js_file, 'r') as f:
                    content = f.read()

                # Check for Odoo module declaration
                if '/** @odoo-module */' not in content:
                    self.log(f"Missing @odoo-module declaration in {js_file.name}", "WARNING")

                # Check for OWL imports
                if 'import' in content and '@odoo/owl' in content:
                    self.log(f"OWL components found in {js_file.name}", "INFO")

                # Check for deprecated patterns
                deprecated = ['odoo.define', 'require(', 'openerp']
                for pattern in deprecated:
                    if pattern in content:
                        self.log(f"Deprecated pattern '{pattern}' in {js_file.name}", "WARNING")

                self.log(f"JavaScript file OK: {js_file.name}", "INFO")

            except Exception as e:
                self.log(f"Error reading {js_file.name}: {str(e)}", "ERROR")

        return True

    def validate_tests(self) -> bool:
        """Validate test files"""
        self.print_header("Validating Tests")

        test_dir = self.module_path / 'tests'
        if not test_dir.exists():
            self.log("No tests directory found", "WARNING")
            return True

        test_files = list(test_dir.glob('test_*.py'))
        self.log(f"Found {len(test_files)} test files", "INFO")

        if len(test_files) == 0:
            self.log("No test files found", "WARNING")
        else:
            for test_file in test_files:
                self.log(f"Test file found: {test_file.name}", "INFO")

                try:
                    with open(test_file, 'r') as f:
                        content = f.read()

                    # Check for test class
                    if 'TransactionCase' not in content and 'SingleTransactionCase' not in content:
                        self.log(f"No test case class in {test_file.name}", "WARNING")
                    else:
                        self.log(f"Test case class found in {test_file.name}", "SUCCESS")

                except Exception as e:
                    self.log(f"Error reading {test_file.name}: {str(e)}", "ERROR")

        return True

    def generate_report(self):
        """Generate final validation report"""
        self.print_header("Validation Report")

        print(f"\n{Colors.BOLD}Summary:{Colors.ENDC}")
        print(f"  {Colors.FAIL}Errors:   {len(self.errors)}{Colors.ENDC}")
        print(f"  {Colors.WARNING}Warnings: {len(self.warnings)}{Colors.ENDC}")
        print(f"  {Colors.OKCYAN}Info:     {len(self.info)}{Colors.ENDC}")

        # Calculate final score
        self.score = max(0, min(100, self.score))

        if self.score >= 90:
            color = Colors.OKGREEN
            status = "EXCELLENT"
        elif self.score >= 80:
            color = Colors.OKGREEN
            status = "GOOD"
        elif self.score >= 70:
            color = Colors.WARNING
            status = "ACCEPTABLE"
        else:
            color = Colors.FAIL
            status = "NEEDS IMPROVEMENT"

        print(f"\n{Colors.BOLD}Overall Score: {color}{self.score}/100 - {status}{Colors.ENDC}\n")

        if self.errors:
            print(f"\n{Colors.FAIL}{Colors.BOLD}Errors Found:{Colors.ENDC}")
            for error in self.errors:
                print(f"  {Colors.FAIL}✗ {error}{Colors.ENDC}")

        if self.warnings:
            print(f"\n{Colors.WARNING}{Colors.BOLD}Warnings:{Colors.ENDC}")
            for warning in self.warnings:
                print(f"  {Colors.WARNING}⚠ {warning}{Colors.ENDC}")

        # Final verdict
        print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
        if self.score >= 80 and len(self.errors) == 0:
            print(f"{Colors.OKGREEN}{Colors.BOLD}✓ MODULE IS PRODUCTION READY{Colors.ENDC}")
        elif len(self.errors) == 0:
            print(f"{Colors.WARNING}{Colors.BOLD}⚠ MODULE IS ACCEPTABLE BUT HAS WARNINGS{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}{Colors.BOLD}✗ MODULE HAS ERRORS - NOT PRODUCTION READY{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

        return len(self.errors) == 0

    def run_all_validations(self) -> bool:
        """Run all validation checks"""
        print(f"\n{Colors.BOLD}{Colors.HEADER}")
        print("╔════════════════════════════════════════════════════════════════════╗")
        print("║       CRM EXECUTIVE DASHBOARD - MODULE VALIDATOR v1.0              ║")
        print("║                  Production Readiness Checker                      ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}\n")

        validations = [
            self.validate_manifest,
            self.validate_structure,
            self.validate_python_files,
            self.validate_security,
            self.validate_views,
            self.validate_javascript,
            self.validate_tests,
        ]

        for validation in validations:
            try:
                validation()
            except Exception as e:
                self.log(f"Validation error: {str(e)}", "ERROR")

        return self.generate_report()

def main():
    """Main entry point"""
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    # Get module path (current directory or provided path)
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        module_path = sys.argv[1]
    else:
        module_path = os.path.dirname(os.path.abspath(__file__))

    validator = ModuleValidator(module_path, verbose=verbose)
    success = validator.run_all_validations()

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
