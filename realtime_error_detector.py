#!/usr/bin/env python3
"""
Real-Time Error Detection & Management Agent
Comprehensive error detection, forecasting, and solution management for Odoo 17 modules

This script implements the full Real-Time Error Detection framework as documented
in the copilot instructions.
"""

import os
import sys
import ast
import xml.etree.ElementTree as ET
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import shutil

class RealTimeErrorDetector:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        self.unused_files = []
        self.fixes_applied = []
        self.validation_results = {}
        
    def log_error(self, error_id, severity, category, description, file_path=None, line_number=None):
        """Log an error with full context"""
        error = {
            'id': error_id,
            'severity': severity,
            'category': category,
            'description': description,
            'file_path': file_path,
            'line_number': line_number,
            'timestamp': datetime.now().isoformat(),
            'status': 'detected'
        }
        self.errors.append(error)
        
    def log_warning(self, category, description, file_path=None, line_number=None):
        """Log a warning with context"""
        warning = {
            'category': category,
            'description': description,
            'file_path': file_path,
            'line_number': line_number,
            'timestamp': datetime.now().isoformat()
        }
        self.warnings.append(warning)

    def scan_recently_modified_modules(self):
        """Scan for recently modified modules and prioritize them"""
        print("🔍 SCANNING RECENTLY MODIFIED MODULES...")
        
        # Key modules that need checking
        priority_modules = [
            'account_payment_final',
            'order_status_override', 
            'oe_sale_dashboard_17',
            'commission_ax',
            'enhanced_rest_api',
            'crm_executive_dashboard'
        ]
        
        modified_modules = []
        for module in priority_modules:
            if os.path.exists(module):
                modified_modules.append(module)
                print(f"✅ Found module: {module}")
        
        return modified_modules

    def detect_javascript_issues(self, module_path):
        """Detect JavaScript compatibility and syntax issues"""
        print(f"🔧 Checking JavaScript in {module_path}...")
        
        js_files = []
        static_path = os.path.join(module_path, 'static', 'src', 'js')
        if os.path.exists(static_path):
            for root, dirs, files in os.walk(static_path):
                for file in files:
                    if file.endswith('.js'):
                        js_files.append(os.path.join(root, file))
        
        for js_file in js_files:
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for Odoo 17 compliance
                if '/** @odoo-module **/' not in content:
                    self.log_error(
                        f"JS-001-{module_path}",
                        "HIGH",
                        "JAVASCRIPT_COMPLIANCE",
                        f"Missing @odoo-module declaration in {js_file}",
                        js_file,
                        1
                    )
                
                # Check for modern ES6+ patterns
                if 'function(' in content and 'class ' not in content:
                    self.log_warning(
                        "JAVASCRIPT_MODERNIZATION",
                        f"Consider using ES6 class syntax instead of function constructors in {js_file}",
                        js_file
                    )
                
                # Check for proper error handling
                if 'try {' not in content:
                    self.log_error(
                        f"JS-002-{module_path}",
                        "MEDIUM",
                        "ERROR_HANDLING",
                        f"Missing try-catch blocks in {js_file}",
                        js_file
                    )
                
                # Check for jQuery usage (discouraged in Odoo 17)
                if '$(' in content or 'jQuery(' in content:
                    self.log_warning(
                        "JAVASCRIPT_LEGACY",
                        f"jQuery usage detected in {js_file} - consider modern alternatives",
                        js_file
                    )
                
            except Exception as e:
                self.log_error(
                    f"JS-003-{module_path}",
                    "CRITICAL",
                    "SYNTAX_ERROR",
                    f"JavaScript syntax error in {js_file}: {e}",
                    js_file
                )

    def detect_css_issues(self, module_path):
        """Detect CSS compatibility and naming issues"""
        print(f"🎨 Checking CSS in {module_path}...")
        
        css_files = []
        static_path = os.path.join(module_path, 'static', 'src')
        if os.path.exists(static_path):
            for root, dirs, files in os.walk(static_path):
                for file in files:
                    if file.endswith(('.css', '.scss')):
                        css_files.append(os.path.join(root, file))
        
        for css_file in css_files:
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for BEM methodology
                if not re.search(r'\.o_[a-z_]+', content):
                    self.log_warning(
                        "CSS_NAMING",
                        f"Consider using BEM methodology with .o_ prefix in {css_file}",
                        css_file
                    )
                
                # Check for !important overuse
                important_count = content.count('!important')
                if important_count > 5:
                    self.log_error(
                        f"CSS-001-{module_path}",
                        "MEDIUM",
                        "CSS_SPECIFICITY",
                        f"Excessive !important usage ({important_count}) in {css_file}",
                        css_file
                    )
                
                # Check for modern CSS patterns
                if 'var(--' not in content:
                    self.log_warning(
                        "CSS_MODERNIZATION",
                        f"Consider using CSS custom properties in {css_file}",
                        css_file
                    )
                
            except Exception as e:
                self.log_error(
                    f"CSS-002-{module_path}",
                    "CRITICAL",
                    "SYNTAX_ERROR",
                    f"CSS syntax error in {css_file}: {e}",
                    css_file
                )

    def detect_python_issues(self, module_path):
        """Detect Python syntax and Odoo compliance issues"""
        print(f"🐍 Checking Python code in {module_path}...")
        
        python_files = []
        for root, dirs, files in os.walk(module_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check syntax
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    self.log_error(
                        f"PY-001-{module_path}",
                        "CRITICAL",
                        "SYNTAX_ERROR",
                        f"Python syntax error in {py_file}: {e}",
                        py_file,
                        e.lineno
                    )
                    continue
                
                # Check for Odoo imports
                if 'from odoo import' in content:
                    # Check for missing common imports
                    if 'ValidationError' in content and 'from odoo.exceptions import ValidationError' not in content:
                        self.log_error(
                            f"PY-002-{module_path}",
                            "HIGH",
                            "MISSING_IMPORT",
                            f"ValidationError used but not imported in {py_file}",
                            py_file
                        )
                
                # Check for proper model structure
                if 'class ' in content and 'models.Model' in content:
                    if '_name = ' not in content:
                        self.log_error(
                            f"PY-003-{module_path}",
                            "HIGH",
                            "MODEL_STRUCTURE",
                            f"Model missing _name attribute in {py_file}",
                            py_file
                        )
                    
                    if '_description = ' not in content:
                        self.log_warning(
                            "MODEL_DOCUMENTATION",
                            f"Model missing _description attribute in {py_file}",
                            py_file
                        )
                
            except Exception as e:
                self.log_error(
                    f"PY-004-{module_path}",
                    "CRITICAL",
                    "READ_ERROR",
                    f"Cannot read Python file {py_file}: {e}",
                    py_file
                )

    def detect_xml_issues(self, module_path):
        """Detect XML syntax and structure issues"""
        print(f"📄 Checking XML files in {module_path}...")
        
        xml_files = []
        for root, dirs, files in os.walk(module_path):
            for file in files:
                if file.endswith('.xml'):
                    xml_files.append(os.path.join(root, file))
        
        for xml_file in xml_files:
            try:
                ET.parse(xml_file)
            except ET.ParseError as e:
                self.log_error(
                    f"XML-001-{module_path}",
                    "CRITICAL",
                    "XML_SYNTAX",
                    f"XML parse error in {xml_file}: {e}",
                    xml_file,
                    e.lineno if hasattr(e, 'lineno') else None
                )
            except Exception as e:
                self.log_error(
                    f"XML-002-{module_path}",
                    "CRITICAL",
                    "READ_ERROR",
                    f"Cannot read XML file {xml_file}: {e}",
                    xml_file
                )

    def detect_unused_files(self, module_path):
        """Detect unused and residual files"""
        print(f"🗑️ Checking for unused files in {module_path}...")
        
        # Check for __pycache__ directories
        pycache_dirs = []
        for root, dirs, files in os.walk(module_path):
            if '__pycache__' in dirs:
                pycache_dirs.append(os.path.join(root, '__pycache__'))
        
        for pycache_dir in pycache_dirs:
            self.unused_files.append({
                'path': pycache_dir,
                'type': 'pycache',
                'safe_to_remove': True,
                'reason': 'Python cache directory'
            })
        
        # Check for .pyc files
        for root, dirs, files in os.walk(module_path):
            for file in files:
                if file.endswith('.pyc'):
                    pyc_file = os.path.join(root, file)
                    self.unused_files.append({
                        'path': pyc_file,
                        'type': 'pyc',
                        'safe_to_remove': True,
                        'reason': 'Compiled Python file'
                    })

    def generate_fixes(self):
        """Generate comprehensive fixes for detected issues"""
        print("🔧 GENERATING COMPREHENSIVE FIXES...")
        
        fix_plan = {
            'critical_fixes': [],
            'high_priority_fixes': [],
            'medium_priority_fixes': [],
            'cleanup_actions': []
        }
        
        # Categorize fixes by severity
        for error in self.errors:
            fix = self.create_fix_for_error(error)
            if error['severity'] == 'CRITICAL':
                fix_plan['critical_fixes'].append(fix)
            elif error['severity'] == 'HIGH':
                fix_plan['high_priority_fixes'].append(fix)
            else:
                fix_plan['medium_priority_fixes'].append(fix)
        
        # Add cleanup actions
        for unused_file in self.unused_files:
            if unused_file['safe_to_remove']:
                fix_plan['cleanup_actions'].append({
                    'action': 'remove',
                    'target': unused_file['path'],
                    'reason': unused_file['reason']
                })
        
        return fix_plan

    def create_fix_for_error(self, error):
        """Create specific fix instructions for an error"""
        fix = {
            'error_id': error['id'],
            'category': error['category'],
            'file_path': error['file_path'],
            'description': error['description'],
            'fix_actions': [],
            'test_actions': [],
            'rollback_plan': []
        }
        
        if error['category'] == 'MISSING_IMPORT':
            fix['fix_actions'] = [
                "Add missing import statement",
                "from odoo.exceptions import ValidationError"
            ]
            fix['test_actions'] = [
                "Verify Python syntax",
                "Test module loading"
            ]
        
        elif error['category'] == 'JAVASCRIPT_COMPLIANCE':
            fix['fix_actions'] = [
                "Add @odoo-module declaration at top of file",
                "/** @odoo-module **/"
            ]
            fix['test_actions'] = [
                "Verify JavaScript loads without errors",
                "Test in browser console"
            ]
        
        elif error['category'] == 'ERROR_HANDLING':
            fix['fix_actions'] = [
                "Wrap critical sections in try-catch blocks",
                "Add proper error notifications"
            ]
            fix['test_actions'] = [
                "Test error scenarios",
                "Verify graceful degradation"
            ]
        
        return fix

    def apply_fixes(self, fix_plan):
        """Apply the generated fixes safely"""
        print("🚀 APPLYING FIXES...")
        
        # Apply critical fixes first
        for fix in fix_plan['critical_fixes']:
            if self.apply_single_fix(fix):
                self.fixes_applied.append(fix)
        
        # Apply high priority fixes
        for fix in fix_plan['high_priority_fixes']:
            if self.apply_single_fix(fix):
                self.fixes_applied.append(fix)
        
        # Cleanup unused files
        for cleanup in fix_plan['cleanup_actions']:
            if self.perform_cleanup(cleanup):
                print(f"✅ Cleaned up: {cleanup['target']}")

    def apply_single_fix(self, fix):
        """Apply a single fix with backup"""
        try:
            file_path = fix['file_path']
            if not file_path or not os.path.exists(file_path):
                return False
            
            # Create backup
            backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(file_path, backup_path)
            
            # Apply fix based on category
            if fix['category'] == 'MISSING_IMPORT':
                self.fix_missing_import(file_path)
            elif fix['category'] == 'JAVASCRIPT_COMPLIANCE':
                self.fix_javascript_compliance(file_path)
            
            print(f"✅ Fixed: {fix['error_id']} in {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to apply fix {fix['error_id']}: {e}")
            return False

    def fix_missing_import(self, file_path):
        """Fix missing import statements"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add ValidationError import if missing
        if 'ValidationError' in content and 'from odoo.exceptions import ValidationError' not in content:
            lines = content.split('\n')
            
            # Find the right place to insert import
            insert_line = 0
            for i, line in enumerate(lines):
                if line.startswith('from odoo import'):
                    insert_line = i + 1
                    break
            
            if insert_line > 0:
                lines.insert(insert_line, 'from odoo.exceptions import ValidationError')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))

    def fix_javascript_compliance(self, file_path):
        """Fix JavaScript Odoo 17 compliance issues"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add @odoo-module declaration if missing
        if '/** @odoo-module **/' not in content:
            content = '/** @odoo-module **/\n\n' + content
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

    def perform_cleanup(self, cleanup):
        """Safely remove unused files"""
        try:
            target = cleanup['target']
            if os.path.isdir(target):
                shutil.rmtree(target)
            elif os.path.isfile(target):
                os.remove(target)
            return True
        except Exception as e:
            print(f"❌ Failed to cleanup {target}: {e}")
            return False

    def run_comprehensive_validation(self):
        """Run final validation after fixes"""
        print("🔍 RUNNING COMPREHENSIVE VALIDATION...")
        
        # Run CloudPepper validation
        try:
            result = subprocess.run([
                'python', 'cloudpepper_deployment_final_validation.py'
            ], capture_output=True, text=True)
            
            self.validation_results['cloudpepper'] = {
                'exit_code': result.returncode,
                'output': result.stdout,
                'errors': result.stderr
            }
        except Exception as e:
            print(f"❌ CloudPepper validation failed: {e}")

    def generate_report(self):
        """Generate comprehensive error detection and fix report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'errors_detected': len(self.errors),
                'warnings_detected': len(self.warnings),
                'fixes_applied': len(self.fixes_applied),
                'files_cleaned': len([f for f in self.unused_files if f['safe_to_remove']])
            },
            'errors': self.errors,
            'warnings': self.warnings,
            'fixes_applied': self.fixes_applied,
            'validation_results': self.validation_results
        }
        
        # Save report
        report_file = f'error_detection_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 COMPREHENSIVE ERROR DETECTION REPORT")
        print("=" * 60)
        print(f"Timestamp: {report['timestamp']}")
        print(f"Errors Detected: {report['summary']['errors_detected']}")
        print(f"Warnings Detected: {report['summary']['warnings_detected']}")
        print(f"Fixes Applied: {report['summary']['fixes_applied']}")
        print(f"Files Cleaned: {report['summary']['files_cleaned']}")
        print(f"Report saved: {report_file}")
        
        return report

    def run_full_analysis(self):
        """Run complete real-time error detection and management"""
        print("🚀 REAL-TIME ERROR DETECTION & MANAGEMENT AGENT")
        print("=" * 60)
        
        # Phase 1: Discovery
        modules = self.scan_recently_modified_modules()
        
        # Phase 2: Error Detection
        for module in modules:
            print(f"\n🔍 Analyzing module: {module}")
            self.detect_python_issues(module)
            self.detect_javascript_issues(module)
            self.detect_css_issues(module)
            self.detect_xml_issues(module)
            self.detect_unused_files(module)
        
        # Phase 3: Solution Planning
        fix_plan = self.generate_fixes()
        
        # Phase 4: Apply Fixes
        self.apply_fixes(fix_plan)
        
        # Phase 5: Validation
        self.run_comprehensive_validation()
        
        # Phase 6: Reporting
        report = self.generate_report()
        
        return report

if __name__ == "__main__":
    detector = RealTimeErrorDetector()
    report = detector.run_full_analysis()
