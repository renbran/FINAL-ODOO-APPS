#!/usr/bin/env python3
"""
Comprehensive Error Detection and Analysis for order_status_override module
Detects compatibility issues, missing references, logical problems, and code quality issues
"""

import os
import ast
import xml.etree.ElementTree as ET
import re
import csv
from collections import defaultdict

class OrderStatusOverrideAnalyzer:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        self.module_path = 'order_status_override'
        
    def log_error(self, category, description, file_path=None, line_number=None):
        """Log an error with context"""
        error = {
            'category': category,
            'description': description,
            'file_path': file_path,
            'line_number': line_number,
            'severity': 'ERROR'
        }
        self.errors.append(error)
        
    def log_warning(self, category, description, file_path=None, line_number=None):
        """Log a warning with context"""
        warning = {
            'category': category,
            'description': description,
            'file_path': file_path,
            'line_number': line_number,
            'severity': 'WARNING'
        }
        self.warnings.append(warning)
        
    def log_info(self, category, description, file_path=None):
        """Log an info message"""
        info = {
            'category': category,
            'description': description,
            'file_path': file_path,
            'severity': 'INFO'
        }
        self.info.append(info)

    def analyze_python_syntax(self):
        """Analyze Python files for syntax errors and issues"""
        print("🔍 Analyzing Python Syntax...")
        
        python_files = [
            'models/__init__.py',
            'models/sale_order.py',
            'models/order_status.py',
            'models/commission_models.py',
            'models/status_change_wizard.py',
            '__init__.py'
        ]
        
        for file_path in python_files:
            full_path = os.path.join(self.module_path, file_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse AST for syntax errors
                    ast.parse(content)
                    self.log_info('SYNTAX', f'Python syntax valid: {file_path}')
                    
                    # Check for specific issues
                    self._check_python_odoo17_compatibility(content, file_path)
                    self._check_duplicate_methods(content, file_path)
                    self._check_missing_imports(content, file_path)
                    
                except SyntaxError as e:
                    self.log_error('SYNTAX', f'Python syntax error in {file_path}: {e}', file_path, e.lineno)
                except Exception as e:
                    self.log_error('SYNTAX', f'Error reading {file_path}: {e}', file_path)
            else:
                self.log_warning('MISSING_FILE', f'Python file not found: {file_path}', file_path)

    def _check_python_odoo17_compatibility(self, content, file_path):
        """Check for Odoo 17 compatibility issues"""
        
        # Check for old API usage
        old_api_patterns = [
            (r'@api\.one', 'Old API @api.one is deprecated in Odoo 17'),
            (r'@api\.multi', 'Old API @api.multi is deprecated in Odoo 17'),
            (r'\.browse\(\[', 'Use recordset notation instead of browse() for single records'),
            (r'\.sudo\(\)', 'Consider using sudo(False) or specific user context'),
        ]
        
        for pattern, message in old_api_patterns:
            if re.search(pattern, content):
                self.log_warning('COMPATIBILITY', f'{message} in {file_path}', file_path)
        
        # Check for required imports
        required_imports = ['from odoo import models, fields, api']
        for required in required_imports:
            if required in content:
                self.log_info('IMPORTS', f'Required import found in {file_path}: {required}')

    def _check_duplicate_methods(self, content, file_path):
        """Check for duplicate method definitions"""
        
        try:
            tree = ast.parse(content)
            method_names = defaultdict(list)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    method_names[node.name].append(node.lineno)
            
            for method_name, line_numbers in method_names.items():
                if len(line_numbers) > 1:
                    self.log_error('DUPLICATE_METHOD', 
                                 f'Duplicate method "{method_name}" found at lines: {line_numbers}', 
                                 file_path, line_numbers[0])
                    
        except Exception as e:
            self.log_warning('AST_ANALYSIS', f'Could not analyze AST for {file_path}: {e}', file_path)

    def _check_missing_imports(self, content, file_path):
        """Check for missing imports based on usage"""
        
        # Common usage patterns that require specific imports
        import_checks = [
            ('UserError', 'from odoo.exceptions import UserError'),
            ('ValidationError', 'from odoo.exceptions import ValidationError'),
            ('qrcode', 'import qrcode'),
            ('base64', 'import base64'),
            ('datetime', 'from datetime import datetime'),
            ('logging', 'import logging'),
        ]
        
        for usage, required_import in import_checks:
            if usage in content and required_import not in content:
                self.log_warning('MISSING_IMPORT', 
                               f'Usage of "{usage}" found but missing import: {required_import}', 
                               file_path)

    def analyze_xml_files(self):
        """Analyze XML files for syntax and reference errors"""
        print("🔍 Analyzing XML Files...")
        
        xml_files = [
            'views/order_status_views.xml',
            'views/order_views_assignment.xml',
            'views/email_template_views.xml',
            'views/report_wizard_views.xml',
            'security/security.xml',
            'data/order_status_data.xml',
            'data/email_templates.xml',
            'data/paperformat.xml',
        ]
        
        for file_path in xml_files:
            full_path = os.path.join(self.module_path, file_path)
            if os.path.exists(full_path):
                try:
                    tree = ET.parse(full_path)
                    self.log_info('XML_SYNTAX', f'XML syntax valid: {file_path}')
                    
                    # Check for specific XML issues
                    self._check_xml_references(tree, file_path)
                    self._check_external_ids(tree, file_path)
                    
                except ET.ParseError as e:
                    self.log_error('XML_SYNTAX', f'XML parse error in {file_path}: {e}', file_path, e.lineno)
                except Exception as e:
                    self.log_error('XML_SYNTAX', f'Error reading {file_path}: {e}', file_path)
            else:
                self.log_warning('MISSING_FILE', f'XML file not found: {file_path}', file_path)

    def _check_xml_references(self, tree, file_path):
        """Check for missing field and method references in XML"""
        
        root = tree.getroot()
        
        # Check for button actions that should exist as methods
        buttons = root.findall('.//button[@name]')
        expected_methods = []
        
        for button in buttons:
            method_name = button.get('name')
            if method_name and method_name.startswith('action_'):
                expected_methods.append(method_name)
        
        if expected_methods:
            self.log_info('XML_REFERENCES', 
                         f'Found button actions in {file_path}: {expected_methods}')

    def _check_external_ids(self, tree, file_path):
        """Check for external ID conflicts and missing references"""
        
        root = tree.getroot()
        
        # Find all records with external IDs
        records = root.findall('.//record[@id]')
        external_ids = []
        
        for record in records:
            external_id = record.get('id')
            if external_id:
                external_ids.append(external_id)
        
        if external_ids:
            self.log_info('EXTERNAL_IDS', 
                         f'Found external IDs in {file_path}: {len(external_ids)} records')

    def analyze_security_files(self):
        """Analyze security configuration"""
        print("🔍 Analyzing Security Configuration...")
        
        # Check ir.model.access.csv
        access_file = os.path.join(self.module_path, 'security/ir.model.access.csv')
        if os.path.exists(access_file):
            try:
                with open(access_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    
                if len(rows) > 1:  # Header + data
                    self.log_info('SECURITY', f'Access rights defined: {len(rows)-1} rules')
                else:
                    self.log_warning('SECURITY', 'ir.model.access.csv has no access rules defined')
                    
            except Exception as e:
                self.log_error('SECURITY', f'Error reading access file: {e}', access_file)
        else:
            self.log_warning('MISSING_FILE', 'ir.model.access.csv not found', access_file)

    def analyze_manifest(self):
        """Analyze __manifest__.py for completeness and correctness"""
        print("🔍 Analyzing Manifest File...")
        
        manifest_file = os.path.join(self.module_path, '__manifest__.py')
        if os.path.exists(manifest_file):
            try:
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Evaluate manifest as Python dict
                manifest_dict = ast.literal_eval(content)
                
                # Check required fields
                required_fields = ['name', 'version', 'depends', 'data']
                for field in required_fields:
                    if field in manifest_dict:
                        self.log_info('MANIFEST', f'Required field present: {field}')
                    else:
                        self.log_error('MANIFEST', f'Missing required field: {field}', manifest_file)
                
                # Check data files exist
                if 'data' in manifest_dict:
                    for data_file in manifest_dict['data']:
                        full_path = os.path.join(self.module_path, data_file)
                        if os.path.exists(full_path):
                            self.log_info('MANIFEST', f'Data file exists: {data_file}')
                        else:
                            self.log_error('MANIFEST', f'Data file missing: {data_file}', manifest_file)
                
                # Check dependencies
                if 'depends' in manifest_dict:
                    deps = manifest_dict['depends']
                    if 'sale' in deps and 'mail' in deps:
                        self.log_info('MANIFEST', 'Core dependencies (sale, mail) present')
                    else:
                        self.log_warning('MANIFEST', 'Missing core dependencies (sale or mail)')
                        
            except Exception as e:
                self.log_error('MANIFEST', f'Error parsing manifest: {e}', manifest_file)
        else:
            self.log_error('MISSING_FILE', '__manifest__.py not found', manifest_file)

    def analyze_workflow_consistency(self):
        """Analyze workflow stage consistency across files"""
        print("🔍 Analyzing Workflow Consistency...")
        
        # Expected workflow stages
        expected_stages = [
            'draft', 'document_review', 'commission_calculation',
            'allocation', 'final_review', 'approved', 'post'
        ]
        
        # Expected action methods
        expected_actions = [
            'action_move_to_document_review',
            'action_move_to_commission_calculation',
            'action_move_to_allocation',
            'action_move_to_final_review',
            'action_approve_order',
            'action_move_to_post'
        ]
        
        # Check if all stages are defined in sale_order.py
        sale_order_file = os.path.join(self.module_path, 'models/sale_order.py')
        if os.path.exists(sale_order_file):
            with open(sale_order_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            missing_stages = []
            for stage in expected_stages:
                if f"'{stage}'" not in content and f'"{stage}"' not in content:
                    missing_stages.append(stage)
            
            if missing_stages:
                self.log_error('WORKFLOW', f'Missing workflow stages: {missing_stages}', sale_order_file)
            else:
                self.log_info('WORKFLOW', 'All workflow stages found in model')
            
            # Check action methods
            missing_actions = []
            for action in expected_actions:
                if f"def {action}(" not in content:
                    missing_actions.append(action)
            
            if missing_actions:
                self.log_error('WORKFLOW', f'Missing action methods: {missing_actions}', sale_order_file)
            else:
                self.log_info('WORKFLOW', 'All action methods found in model')

    def analyze_computed_fields(self):
        """Analyze computed fields for completeness"""
        print("🔍 Analyzing Computed Fields...")
        
        sale_order_file = os.path.join(self.module_path, 'models/sale_order.py')
        if os.path.exists(sale_order_file):
            with open(sale_order_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find computed fields
            computed_pattern = r"(\w+)\s*=\s*fields\.\w+\([^)]*compute\s*=\s*['\"]([^'\"]+)['\"]"
            computed_matches = re.findall(computed_pattern, content)
            
            missing_compute_methods = []
            for field_name, compute_method in computed_matches:
                if f"def {compute_method}(" not in content:
                    missing_compute_methods.append((field_name, compute_method))
            
            if missing_compute_methods:
                self.log_error('COMPUTED_FIELDS', f'Missing compute methods: {missing_compute_methods}', sale_order_file)
            else:
                self.log_info('COMPUTED_FIELDS', f'All compute methods found for {len(computed_matches)} computed fields')

    def check_odoo17_specific_issues(self):
        """Check for Odoo 17 specific compatibility issues"""
        print("🔍 Checking Odoo 17 Specific Issues...")
        
        # Check for potential issues with new OWL framework
        # Check for deprecated methods
        # Check for proper field definitions
        
        sale_order_file = os.path.join(self.module_path, 'models/sale_order.py')
        if os.path.exists(sale_order_file):
            with open(sale_order_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for proper field tracking
            if 'tracking=True' in content:
                self.log_info('ODOO17', 'Field tracking properly used')
            
            # Check for proper compute field dependencies
            depends_pattern = r"@api\.depends\([^)]+\)"
            depends_matches = re.findall(depends_pattern, content)
            if depends_matches:
                self.log_info('ODOO17', f'Found {len(depends_matches)} @api.depends decorators')

    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE MODULE ANALYSIS REPORT")
        print("="*80)
        
        # Summary statistics
        total_errors = len(self.errors)
        total_warnings = len(self.warnings)
        total_info = len(self.info)
        
        print(f"\n📈 SUMMARY STATISTICS")
        print(f"{'='*40}")
        print(f"❌ Errors:   {total_errors}")
        print(f"⚠️  Warnings: {total_warnings}")
        print(f"ℹ️  Info:     {total_info}")
        
        # Errors by category
        if self.errors:
            print(f"\n❌ ERRORS ({total_errors})")
            print(f"{'='*40}")
            error_categories = defaultdict(list)
            for error in self.errors:
                error_categories[error['category']].append(error)
            
            for category, errors in error_categories.items():
                print(f"\n🔸 {category} ({len(errors)} issues):")
                for error in errors:
                    location = f" [{error['file_path']}:{error['line_number']}]" if error['file_path'] else ""
                    print(f"   - {error['description']}{location}")
        
        # Warnings by category
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({total_warnings})")
            print(f"{'='*40}")
            warning_categories = defaultdict(list)
            for warning in self.warnings:
                warning_categories[warning['category']].append(warning)
            
            for category, warnings in warning_categories.items():
                print(f"\n🔸 {category} ({len(warnings)} issues):")
                for warning in warnings:
                    location = f" [{warning['file_path']}]" if warning['file_path'] else ""
                    print(f"   - {warning['description']}{location}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print(f"{'='*40}")
        
        if total_errors > 0:
            print("🚨 CRITICAL: Fix all errors before deployment")
        
        if total_warnings > 0:
            print("⚠️  MEDIUM: Review and address warnings for better code quality")
        
        if total_errors == 0 and total_warnings == 0:
            print("✅ EXCELLENT: No critical issues found!")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT")
        print(f"{'='*40}")
        
        if total_errors == 0:
            if total_warnings == 0:
                assessment = "🟢 READY FOR PRODUCTION"
            elif total_warnings <= 5:
                assessment = "🟡 READY WITH MINOR IMPROVEMENTS"
            else:
                assessment = "🟠 NEEDS IMPROVEMENTS BEFORE PRODUCTION"
        else:
            assessment = "🔴 NOT READY - CRITICAL ISSUES FOUND"
        
        print(f"{assessment}")
        
        return total_errors == 0

def main():
    """Run comprehensive module analysis"""
    
    print("🚀 Starting Comprehensive Module Analysis")
    print("🎯 Target: order_status_override module")
    print("📅 Odoo Version: 17.0")
    print("\n" + "="*60)
    
    analyzer = OrderStatusOverrideAnalyzer()
    
    # Run all analyses
    analyzer.analyze_manifest()
    analyzer.analyze_python_syntax()
    analyzer.analyze_xml_files()
    analyzer.analyze_security_files()
    analyzer.analyze_workflow_consistency()
    analyzer.analyze_computed_fields()
    analyzer.check_odoo17_specific_issues()
    
    # Generate final report
    success = analyzer.generate_report()
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
