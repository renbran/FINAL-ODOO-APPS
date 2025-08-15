#!/usr/bin/env python3
"""
COMPREHENSIVE ODOO 17 MODULE AUDIT SCRIPT
Performs deep technical validation of all modules for production readiness
"""

import os
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import ast
import re
from collections import defaultdict

class Odoo17ModuleAuditor:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path)
        self.audit_results = {
            'total_modules': 0,
            'clean_modules': [],
            'problematic_modules': [],
            'modules_with_warnings': [],
            'modules_with_errors': [],
            'cleanup_summary': {
                'files_removed': [],
                'directories_cleaned': [],
                'issues_fixed': []
            }
        }
        
    def find_modules(self):
        """Find all Odoo modules in workspace"""
        modules = []
        for item in self.workspace_path.iterdir():
            if item.is_dir() and (item / '__manifest__.py').exists():
                modules.append(item)
        return sorted(modules)
    
    def validate_manifest(self, module_path):
        """Validate module manifest file"""
        issues = []
        warnings = []
        
        manifest_file = module_path / '__manifest__.py'
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse as AST to check syntax
            ast.parse(content)
            
            # Execute to get manifest data
            manifest = {}
            exec(compile(ast.parse(content), manifest_file, 'exec'), {}, manifest)
            
            # Required fields check
            required_fields = ['name', 'version', 'depends', 'data']
            for field in required_fields:
                if field not in manifest:
                    issues.append(f"Missing required field: {field}")
            
            # Version format check
            if 'version' in manifest:
                version = manifest['version']
                if not re.match(r'17\.0\.\d+\.\d+\.\d+', version) and version != '17.0':
                    warnings.append(f"Version format should be 17.0.x.x.x, got: {version}")
            
            # Dependencies check
            if 'depends' in manifest:
                deps = manifest['depends']
                if not isinstance(deps, list):
                    issues.append("'depends' should be a list")
                elif len(deps) == 0:
                    warnings.append("No dependencies specified - should at least include 'base'")
            
            # Data files existence check
            if 'data' in manifest:
                for data_file in manifest['data']:
                    file_path = module_path / data_file
                    if not file_path.exists():
                        issues.append(f"Referenced data file does not exist: {data_file}")
            
            # Assets check
            if 'assets' in manifest:
                assets = manifest['assets']
                for bundle, files in assets.items():
                    for asset_file in files:
                        # Check if it's a local file (not CDN)
                        if not asset_file.startswith(('http://', 'https://')):
                            # Remove module prefix if present
                            clean_path = asset_file.replace(f'{module_path.name}/', '')
                            asset_path = module_path / clean_path
                            if not asset_path.exists():
                                issues.append(f"Referenced asset file does not exist: {asset_file}")
                                
        except SyntaxError as e:
            issues.append(f"Manifest syntax error: {e}")
        except Exception as e:
            issues.append(f"Manifest validation error: {e}")
            
        return issues, warnings, manifest if 'manifest' in locals() else {}
    
    def validate_python_files(self, module_path):
        """Validate all Python files in module"""
        issues = []
        warnings = []
        
        for py_file in module_path.rglob('*.py'):
            if py_file.name.startswith('.'):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for BOM
                if content.startswith('\ufeff'):
                    issues.append(f"BOM found in {py_file.relative_to(module_path)}")
                
                # Parse AST
                ast.parse(content)
                
                # Check for common issues
                if 'from odoo import' not in content and py_file.name != '__init__.py':
                    if any(keyword in content for keyword in ['models.Model', 'fields.', 'api.']):
                        warnings.append(f"Missing 'from odoo import' in {py_file.relative_to(module_path)}")
                
                # Check for old API usage
                if '@api.one' in content or '@api.multi' in content:
                    issues.append(f"Old API usage found in {py_file.relative_to(module_path)}")
                
            except SyntaxError as e:
                issues.append(f"Syntax error in {py_file.relative_to(module_path)}: {e}")
            except Exception as e:
                warnings.append(f"Could not validate {py_file.relative_to(module_path)}: {e}")
                
        return issues, warnings
    
    def validate_xml_files(self, module_path):
        """Validate all XML files in module"""
        issues = []
        warnings = []
        
        for xml_file in module_path.rglob('*.xml'):
            if xml_file.name.startswith('.'):
                continue
                
            try:
                ET.parse(xml_file)
                
                # Check for common XML issues
                with open(xml_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check encoding
                if 'encoding="utf-8"' not in content:
                    warnings.append(f"Missing UTF-8 encoding declaration in {xml_file.relative_to(module_path)}")
                
                # Check for proper Odoo XML structure
                if xml_file.parent.name == 'views' and '<odoo>' not in content:
                    warnings.append(f"Missing <odoo> root element in {xml_file.relative_to(module_path)}")
                    
            except ET.ParseError as e:
                issues.append(f"XML parse error in {xml_file.relative_to(module_path)}: {e}")
            except Exception as e:
                warnings.append(f"Could not validate {xml_file.relative_to(module_path)}: {e}")
                
        return issues, warnings
    
    def check_module_structure(self, module_path):
        """Check if module follows Odoo structure conventions"""
        issues = []
        warnings = []
        
        # Required files
        required_files = ['__init__.py', '__manifest__.py']
        for req_file in required_files:
            if not (module_path / req_file).exists():
                issues.append(f"Missing required file: {req_file}")
        
        # Common directories
        expected_dirs = ['models', 'views', 'security']
        existing_dirs = [d.name for d in module_path.iterdir() if d.is_dir()]
        
        if 'models' not in existing_dirs:
            warnings.append("No 'models' directory found - unusual for Odoo modules")
        
        if 'security' not in existing_dirs:
            warnings.append("No 'security' directory found - may need access control files")
        
        # Check for unnecessary files
        unwanted_patterns = ['*.pyc', '*.pyo', '__pycache__', '.DS_Store', '*.orig', '*.backup']
        for pattern in unwanted_patterns:
            matches = list(module_path.rglob(pattern))
            if matches:
                issues.append(f"Found unwanted files: {[str(m.relative_to(module_path)) for m in matches]}")
        
        return issues, warnings
    
    def audit_module(self, module_path):
        """Perform comprehensive audit of a single module"""
        module_name = module_path.name
        print(f"\nüîç Auditing module: {module_name}")
        
        module_issues = []
        module_warnings = []
        
        # 1. Manifest validation
        manifest_issues, manifest_warnings, manifest_data = self.validate_manifest(module_path)
        module_issues.extend(manifest_issues)
        module_warnings.extend(manifest_warnings)
        
        # 2. Python files validation
        py_issues, py_warnings = self.validate_python_files(module_path)
        module_issues.extend(py_issues)
        module_warnings.extend(py_warnings)
        
        # 3. XML files validation
        xml_issues, xml_warnings = self.validate_xml_files(module_path)
        module_issues.extend(xml_issues)
        module_warnings.extend(xml_warnings)
        
        # 4. Module structure check
        struct_issues, struct_warnings = self.check_module_structure(module_path)
        module_issues.extend(struct_issues)
        module_warnings.extend(struct_warnings)
        
        # Categorize module
        if module_issues:
            self.audit_results['modules_with_errors'].append({
                'name': module_name,
                'path': str(module_path),
                'issues': module_issues,
                'warnings': module_warnings,
                'manifest': manifest_data
            })
            print(f"‚ùå {module_name}: {len(module_issues)} errors, {len(module_warnings)} warnings")
        elif module_warnings:
            self.audit_results['modules_with_warnings'].append({
                'name': module_name,
                'path': str(module_path),
                'warnings': module_warnings,
                'manifest': manifest_data
            })
            print(f"‚ö†Ô∏è  {module_name}: {len(module_warnings)} warnings")
        else:
            self.audit_results['clean_modules'].append({
                'name': module_name,
                'path': str(module_path),
                'manifest': manifest_data
            })
            print(f"‚úÖ {module_name}: Clean")
    
    def run_comprehensive_audit(self):
        """Run audit on all modules"""
        print("üöÄ Starting Comprehensive Odoo 17 Module Audit")
        print("=" * 60)
        
        modules = self.find_modules()
        self.audit_results['total_modules'] = len(modules)
        
        print(f"Found {len(modules)} modules to audit...")
        
        for module_path in modules:
            self.audit_module(module_path)
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive audit report"""
        results = self.audit_results
        
        print("\n" + "=" * 60)
        print("üìä COMPREHENSIVE AUDIT REPORT")
        print("=" * 60)
        
        print(f"Total Modules Audited: {results['total_modules']}")
        print(f"‚úÖ Clean Modules: {len(results['clean_modules'])}")
        print(f"‚ö†Ô∏è  Modules with Warnings: {len(results['modules_with_warnings'])}")
        print(f"‚ùå Modules with Errors: {len(results['modules_with_errors'])}")
        
        if results['modules_with_errors']:
            print("\nüö® MODULES WITH ERRORS (NEED IMMEDIATE ATTENTION):")
            for module in results['modules_with_errors']:
                print(f"\n‚ùå {module['name']}:")
                for issue in module['issues']:
                    print(f"   ‚Ä¢ {issue}")
        
        if results['modules_with_warnings']:
            print("\n‚ö†Ô∏è  MODULES WITH WARNINGS (SHOULD BE REVIEWED):")
            for module in results['modules_with_warnings']:
                print(f"\n‚ö†Ô∏è  {module['name']}:")
                for warning in module['warnings']:
                    print(f"   ‚Ä¢ {warning}")
        
        if results['clean_modules']:
            print(f"\n‚úÖ CLEAN MODULES ({len(results['clean_modules'])}):")
            for module in results['clean_modules']:
                print(f"   ‚úÖ {module['name']}")
        
        # Success rate
        success_rate = (len(results['clean_modules']) / results['total_modules']) * 100
        print(f"\nüìà Module Quality Score: {success_rate:.1f}%")
        
        return results

if __name__ == "__main__":
    workspace = r"d:\GitHub\osus_main\cleanup osus\odoo17_final"
    auditor = Odoo17ModuleAuditor(workspace)
    results = auditor.run_comprehensive_audit()
    
    # Save results to JSON file
    with open(workspace + r"\AUDIT_RESULTS.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nüíæ Detailed audit results saved to: AUDIT_RESULTS.json")
