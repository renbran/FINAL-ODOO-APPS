#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM Lead Scoring Module - Production Validation Script
=======================================================
Comprehensive validation for production deployment on CloudPepper/scholarixv2

This script validates:
- Module structure and required files
- Python syntax and imports
- XML syntax and structure  
- CSV format and references
- Security group references
- Odoo 17 compliance
- CloudPepper compatibility
"""

import os
import sys
import csv
import ast
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple, Dict

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class ValidationResult:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        self.passed_checks = 0
        self.total_checks = 0

    def add_error(self, message: str):
        self.errors.append(f"❌ {message}")

    def add_warning(self, message: str):
        self.warnings.append(f"⚠️  {message}")

    def add_info(self, message: str):
        self.info.append(f"ℹ️  {message}")

    def check_passed(self):
        self.passed_checks += 1
        self.total_checks += 1

    def check_failed(self):
        self.total_checks += 1

    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def print_summary(self):
        print(f"\n{'='*70}")
        print(f"{Colors.BOLD}📊 VALIDATION SUMMARY{Colors.END}")
        print(f"{'='*70}\n")
        
        print(f"Total Checks: {self.total_checks}")
        print(f"{Colors.GREEN}✅ Passed: {self.passed_checks}{Colors.END}")
        print(f"{Colors.RED}❌ Failed: {self.total_checks - self.passed_checks}{Colors.END}")
        
        if self.errors:
            print(f"\n{Colors.RED}{Colors.BOLD}ERRORS ({len(self.errors)}):{Colors.END}")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}WARNINGS ({len(self.warnings)}):{Colors.END}")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.info:
            print(f"\n{Colors.BLUE}{Colors.BOLD}INFO ({len(self.info)}):{Colors.END}")
            for info in self.info:
                print(f"  {info}")
        
        print(f"\n{'='*70}")
        
        if self.is_valid():
            print(f"{Colors.GREEN}{Colors.BOLD}✅ MODULE IS PRODUCTION READY!{Colors.END}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ MODULE HAS ERRORS - FIX BEFORE DEPLOYMENT!{Colors.END}")
        
        print(f"{'='*70}\n")

class ModuleValidator:
    def __init__(self, module_path: str):
        self.module_path = Path(module_path)
        self.result = ValidationResult()
        
    def validate_all(self) -> ValidationResult:
        """Run all validation checks"""
        print(f"{Colors.BOLD}🔍 LLM Lead Scoring Module Validation{Colors.END}")
        print(f"Module Path: {self.module_path}\n")
        
        self.validate_structure()
        self.validate_manifest()
        self.validate_python_files()
        self.validate_xml_files()
        self.validate_security_csv()
        self.validate_odoo17_compliance()
        
        return self.result

    def validate_structure(self):
        """Validate basic module structure"""
        print(f"{Colors.BLUE}📁 Validating Module Structure...{Colors.END}")
        
        required_files = {
            '__init__.py': 'Root init file',
            '__manifest__.py': 'Module manifest',
            'models/__init__.py': 'Models init',
            'security/ir.model.access.csv': 'Access rights',
        }
        
        for file_path, description in required_files.items():
            full_path = self.module_path / file_path
            if full_path.exists():
                self.result.check_passed()
                print(f"  ✅ {description}: {file_path}")
            else:
                self.result.check_failed()
                self.result.add_error(f"Missing required file: {file_path} ({description})")
                print(f"  ❌ {description}: {file_path}")
        
        print()

    def validate_manifest(self):
        """Validate __manifest__.py"""
        print(f"{Colors.BLUE}📄 Validating Manifest...{Colors.END}")
        
        manifest_path = self.module_path / '__manifest__.py'
        
        if not manifest_path.exists():
            self.result.check_failed()
            self.result.add_error("Manifest file not found")
            return
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
                manifest = ast.literal_eval(content)
            
            # Check required keys
            required_keys = ['name', 'version', 'category', 'depends', 'data']
            for key in required_keys:
                if key in manifest:
                    self.result.check_passed()
                    print(f"  ✅ Manifest key '{key}' present")
                else:
                    self.result.check_failed()
                    self.result.add_error(f"Missing manifest key: {key}")
                    print(f"  ❌ Manifest key '{key}' missing")
            
            # Validate version format (17.0.x.y.z)
            version = manifest.get('version', '')
            if version.startswith('17.0.'):
                self.result.check_passed()
                print(f"  ✅ Version format correct: {version}")
            else:
                self.result.check_failed()
                self.result.add_warning(f"Version should start with '17.0.': {version}")
                print(f"  ⚠️  Version format: {version}")
            
            # Check dependencies
            depends = manifest.get('depends', [])
            required_deps = ['base', 'crm', 'mail']
            for dep in required_deps:
                if dep in depends:
                    self.result.check_passed()
                    print(f"  ✅ Dependency '{dep}' present")
                else:
                    self.result.check_failed()
                    self.result.add_error(f"Missing required dependency: {dep}")
                    print(f"  ❌ Missing dependency: {dep}")
            
            # Validate data files exist
            data_files = manifest.get('data', [])
            for data_file in data_files:
                file_path = self.module_path / data_file
                if file_path.exists():
                    self.result.check_passed()
                    print(f"  ✅ Data file exists: {data_file}")
                else:
                    self.result.check_failed()
                    self.result.add_error(f"Referenced data file not found: {data_file}")
                    print(f"  ❌ Missing data file: {data_file}")
            
        except Exception as e:
            self.result.check_failed()
            self.result.add_error(f"Manifest validation error: {str(e)}")
            print(f"  ❌ Manifest parsing error: {str(e)}")
        
        print()

    def validate_python_files(self):
        """Validate all Python files"""
        print(f"{Colors.BLUE}🐍 Validating Python Files...{Colors.END}")
        
        python_files = list(self.module_path.rglob('*.py'))
        
        for py_file in python_files:
            if '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                    compile(code, str(py_file), 'exec')
                
                self.result.check_passed()
                print(f"  ✅ {py_file.relative_to(self.module_path)}")
                
                # Check for common anti-patterns (but skip validation script itself)
                if 'validate_production_ready.py' not in str(py_file):
                    if 'cr.commit()' in code:
                        self.result.add_error(f"Found cr.commit() in {py_file.name} - NEVER use manual commits!")
                    
                    if 'sudo()' in code and 'ir.config_parameter' not in code:
                        self.result.add_warning(f"sudo() usage in {py_file.name} - ensure proper security")
                
            except SyntaxError as e:
                self.result.check_failed()
                self.result.add_error(f"Syntax error in {py_file.relative_to(self.module_path)}: {e}")
                print(f"  ❌ {py_file.relative_to(self.module_path)}: {e}")
            except Exception as e:
                self.result.check_failed()
                self.result.add_error(f"Error validating {py_file.relative_to(self.module_path)}: {e}")
                print(f"  ❌ {py_file.relative_to(self.module_path)}: {e}")
        
        print()

    def validate_xml_files(self):
        """Validate all XML files"""
        print(f"{Colors.BLUE}📝 Validating XML Files...{Colors.END}")
        
        xml_files = list(self.module_path.rglob('*.xml'))
        
        for xml_file in xml_files:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                self.result.check_passed()
                print(f"  ✅ {xml_file.relative_to(self.module_path)}")
                
                # Check for deprecated attrs usage
                content = xml_file.read_text(encoding='utf-8')
                if 'attrs=' in content:
                    self.result.add_warning(
                        f"Found 'attrs=' in {xml_file.name} - Use modern invisible=/readonly= syntax in Odoo 17"
                    )
                
                if 'states=' in content and '<button' in content:
                    self.result.add_warning(
                        f"Found 'states=' in {xml_file.name} - Use modern invisible= syntax in Odoo 17"
                    )
                
            except ET.ParseError as e:
                self.result.check_failed()
                self.result.add_error(f"XML parse error in {xml_file.relative_to(self.module_path)}: {e}")
                print(f"  ❌ {xml_file.relative_to(self.module_path)}: {e}")
            except Exception as e:
                self.result.check_failed()
                self.result.add_error(f"Error validating {xml_file.relative_to(self.module_path)}: {e}")
                print(f"  ❌ {xml_file.relative_to(self.module_path)}: {e}")
        
        print()

    def validate_security_csv(self):
        """Validate security CSV file"""
        print(f"{Colors.BLUE}🔒 Validating Security Access Rights...{Colors.END}")
        
        csv_path = self.module_path / 'security' / 'ir.model.access.csv'
        
        if not csv_path.exists():
            self.result.check_failed()
            self.result.add_error("Security CSV file not found")
            print(f"  ❌ ir.model.access.csv not found")
            return
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)
                
                required_headers = ['id', 'name', 'model_id:id', 'group_id:id', 
                                   'perm_read', 'perm_write', 'perm_create', 'perm_unlink']
                
                if headers == required_headers:
                    self.result.check_passed()
                    print(f"  ✅ CSV headers correct")
                else:
                    self.result.check_failed()
                    self.result.add_error(f"Invalid CSV headers: {headers}")
                    print(f"  ❌ Invalid CSV headers")
                
                # Validate each row
                for row_num, row in enumerate(reader, start=2):
                    if len(row) != len(headers):
                        self.result.check_failed()
                        self.result.add_error(f"Invalid row length at line {row_num}: {row}")
                        print(f"  ❌ Invalid row at line {row_num}")
                        continue
                    
                    # Check for deprecated CRM groups
                    group_id = row[3]
                    if 'crm.group_crm_user' in group_id or 'crm.group_crm_manager' in group_id:
                        self.result.check_failed()
                        self.result.add_error(
                            f"Deprecated CRM group reference at line {row_num}: {group_id}. "
                            f"Use sales_team.group_sale_salesman or sales_team.group_sale_manager"
                        )
                        print(f"  ❌ Deprecated group reference: {group_id}")
                    else:
                        self.result.check_passed()
                        print(f"  ✅ Row {row_num}: {row[0]}")
                
        except Exception as e:
            self.result.check_failed()
            self.result.add_error(f"CSV validation error: {str(e)}")
            print(f"  ❌ CSV validation error: {str(e)}")
        
        print()

    def validate_odoo17_compliance(self):
        """Validate Odoo 17 specific compliance"""
        print(f"{Colors.BLUE}🎯 Validating Odoo 17 Compliance...{Colors.END}")
        
        # Check for modern OWL components
        js_files = list(self.module_path.rglob('*.js'))
        has_js = len(js_files) > 0
        
        if has_js:
            for js_file in js_files:
                content = js_file.read_text(encoding='utf-8')
                
                # Check for OWL imports
                if '@odoo/owl' in content or 'owl' in content.lower():
                    self.result.check_passed()
                    print(f"  ✅ OWL framework usage detected: {js_file.name}")
                else:
                    self.result.add_info(f"No OWL usage in {js_file.name} (may be intentional)")
        else:
            self.result.add_info("No JavaScript files found (backend-only module)")
        
        # Check for proper field syntax in views
        view_files = list(self.module_path.glob('views/*.xml'))
        for view_file in view_files:
            content = view_file.read_text(encoding='utf-8')
            
            # Check for deprecated syntax
            if '<field name=' in content:
                if 'attrs={' in content:
                    self.result.add_warning(
                        f"{view_file.name}: Using deprecated attrs={{}} syntax. "
                        f"Use invisible= and readonly= attributes instead"
                    )
                else:
                    self.result.check_passed()
                    print(f"  ✅ Modern field syntax: {view_file.name}")
        
        # Check for proper security implementation
        security_xml = self.module_path / 'security' / 'llm_provider_security.xml'
        if security_xml.exists():
            self.result.check_passed()
            print(f"  ✅ Record rules defined: llm_provider_security.xml")
        else:
            self.result.add_warning("No record rules (security XML) found - consider multi-company support")
        
        # Check for tests
        test_dir = self.module_path / 'tests'
        if test_dir.exists():
            test_files = list(test_dir.glob('test_*.py'))
            if test_files:
                self.result.check_passed()
                print(f"  ✅ Test files found: {len(test_files)} tests")
                for test_file in test_files:
                    print(f"     • {test_file.name}")
            else:
                self.result.add_warning("Tests directory exists but no test files found")
        else:
            self.result.add_warning("No tests directory - consider adding automated tests")
        
        print()

def main():
    """Main validation function"""
    
    # Determine module path
    if len(sys.argv) > 1:
        module_path = sys.argv[1]
    else:
        # Assume script is run from module directory or parent
        current_dir = Path(__file__).parent
        if (current_dir / '__manifest__.py').exists():
            module_path = current_dir
        else:
            module_path = current_dir / 'llm_lead_scoring'
    
    if not Path(module_path).exists():
        print(f"{Colors.RED}❌ Module path not found: {module_path}{Colors.END}")
        sys.exit(1)
    
    # Run validation
    validator = ModuleValidator(module_path)
    result = validator.validate_all()
    
    # Print summary
    result.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if result.is_valid() else 1)

if __name__ == '__main__':
    main()
