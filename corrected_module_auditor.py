#!/usr/bin/env python3
"""
CORRECTED ODOO 17 MODULE AUDIT SCRIPT
Fixed manifest parsing and comprehensive module validation
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
        manifest_data = {}
        
        manifest_file = module_path / '__manifest__.py'
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse as AST to check syntax
            tree = ast.parse(content)
            
            # Execute to get manifest data - FIXED METHOD
            global_dict = {}
            local_dict = {}
            exec(compile(tree, str(manifest_file), 'exec'), global_dict, local_dict)
            
            # The manifest should be the only variable in local_dict or a dict at module level
            if local_dict:
                manifest_data = local_dict.get('manifest', local_dict)
                # If local_dict has multiple items, find the dictionary
                for key, value in local_dict.items():
                    if isinstance(value, dict) and 'name' in value:
                        manifest_data = value
                        break
            else:
                # Try to evaluate the file as a single expression (dictionary)
                try:
                    manifest_data = eval(content)
                except:
                    issues.append("Could not parse manifest as dictionary")
                    return issues, warnings, {}
            
            # Required fields check
            required_fields = ['name', 'version', 'depends']
            for field in required_fields:
                if field not in manifest_data:
                    issues.append(f"Missing required field: {field}")
            
            # Version format check
            if 'version' in manifest_data:
                version = manifest_data['version']
                if not re.match(r'17\.0(\.\d+\.\d+\.\d+)?', version):
                    warnings.append(f"Version format should start with 17.0, got: {version}")
            
            # Dependencies check
            if 'depends' in manifest_data:
                deps = manifest_data['depends']
                if not isinstance(deps, list):
                    issues.append("'depends' should be a list")
                elif len(deps) == 0:
                    warnings.append("No dependencies specified - should at least include 'base'")
                elif 'base' not in deps:
                    warnings.append("'base' dependency missing - usually required")
            
            # Data files existence check
            if 'data' in manifest_data:
                for data_file in manifest_data['data']:
                    file_path = module_path / data_file
                    if not file_path.exists():
                        issues.append(f"Referenced data file does not exist: {data_file}")
            
            # Assets check
            if 'assets' in manifest_data:
                assets = manifest_data['assets']
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
            
        return issues, warnings, manifest_data
    
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
                if 'from odoo import' not in content and py_file.name not in ['__init__.py', '__manifest__.py']:
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
                with open(xml_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                # Skip empty files
                if not content:
                    warnings.append(f"Empty XML file: {xml_file.relative_to(module_path)}")
                    continue
                
                ET.parse(xml_file)
                
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
        existing_dirs = [d.name for d in module_path.iterdir() if d.is_dir()]
        
        # Check for models directory if module extends functionality
        if 'models' not in existing_dirs:
            # Check if __init__.py imports models
            init_file = module_path / '__init__.py'
            if init_file.exists():
                try:
                    with open(init_file, 'r', encoding='utf-8') as f:
                        init_content = f.read()
                        if 'models' in init_content:
                            warnings.append("__init__.py references models but no models directory found")
                except UnicodeDecodeError:
                    warnings.append("__init__.py file has encoding issues")
                except Exception:
                    pass  # Skip if can't read init file
        
        if 'security' not in existing_dirs:
            # Check if manifest references security files
            manifest_file = module_path / '__manifest__.py'
            if manifest_file.exists():
                try:
                    with open(manifest_file, 'r', encoding='utf-8') as f:
                        manifest_content = f.read()
                        if 'ir.model.access.csv' in manifest_content or 'security.xml' in manifest_content:
                            warnings.append("Manifest references security files but no security directory found")
                except UnicodeDecodeError:
                    warnings.append("Manifest file has encoding issues")
                except Exception:
                    pass  # Skip if can't read manifest
        
        return issues, warnings
    
    def check_for_residual_files(self, module_path):
        """Check for temporary/residual files that should be cleaned"""
        issues = []
        
        # Patterns for unwanted files
        unwanted_patterns = ['__pycache__', '*.pyc', '*.pyo', '.DS_Store', '*.orig', '*.backup', '*.bak', '*.tmp']
        
        for pattern in unwanted_patterns:
            if pattern == '__pycache__':
                matches = list(module_path.rglob(pattern))
            else:
                matches = list(module_path.rglob(pattern))
            
            if matches:
                relative_paths = [str(m.relative_to(module_path)) for m in matches]
                issues.append(f"Found residual files ({pattern}): {relative_paths}")
        
        return issues
    
    def audit_module(self, module_path):
        """Perform comprehensive audit of a single module"""
        module_name = module_path.name
        print(f"\n🔍 Auditing module: {module_name}")
        
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
        
        # 5. Residual files check
        residual_issues = self.check_for_residual_files(module_path)
        module_issues.extend(residual_issues)
        
        # Categorize module
        if module_issues:
            self.audit_results['modules_with_errors'].append({
                'name': module_name,
                'path': str(module_path),
                'issues': module_issues,
                'warnings': module_warnings,
                'manifest': manifest_data
            })
            print(f"❌ {module_name}: {len(module_issues)} errors, {len(module_warnings)} warnings")
        elif module_warnings:
            self.audit_results['modules_with_warnings'].append({
                'name': module_name,
                'path': str(module_path),
                'warnings': module_warnings,
                'manifest': manifest_data
            })
            print(f"⚠️  {module_name}: {len(module_warnings)} warnings")
        else:
            self.audit_results['clean_modules'].append({
                'name': module_name,
                'path': str(module_path),
                'manifest': manifest_data
            })
            print(f"✅ {module_name}: Clean")
    
    def run_comprehensive_audit(self):
        """Run audit on all modules"""
        print("🚀 Starting CORRECTED Comprehensive Odoo 17 Module Audit")
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
        print("📊 CORRECTED COMPREHENSIVE AUDIT REPORT")
        print("=" * 60)
        
        print(f"Total Modules Audited: {results['total_modules']}")
        print(f"✅ Clean Modules: {len(results['clean_modules'])}")
        print(f"⚠️  Modules with Warnings: {len(results['modules_with_warnings'])}")
        print(f"❌ Modules with Errors: {len(results['modules_with_errors'])}")
        
        # Calculate success rate
        clean_count = len(results['clean_modules'])
        warning_count = len(results['modules_with_warnings'])
        error_count = len(results['modules_with_errors'])
        
        success_rate = ((clean_count + warning_count) / results['total_modules']) * 100
        production_ready_rate = (clean_count / results['total_modules']) * 100
        
        print(f"\n📈 Overall Health Score: {success_rate:.1f}%")
        print(f"📈 Production Ready Score: {production_ready_rate:.1f}%")
        
        if results['modules_with_errors']:
            print(f"\n🚨 MODULES WITH ERRORS ({len(results['modules_with_errors'])} modules):")
            for module in results['modules_with_errors']:
                print(f"\n❌ {module['name']}:")
                for issue in module['issues'][:5]:  # Show first 5 issues
                    print(f"   • {issue}")
                if len(module['issues']) > 5:
                    print(f"   ... and {len(module['issues']) - 5} more issues")
        
        if results['modules_with_warnings']:
            print(f"\n⚠️  MODULES WITH WARNINGS ({len(results['modules_with_warnings'])} modules):")
            for module in results['modules_with_warnings']:
                print(f"\n⚠️  {module['name']}:")
                for warning in module['warnings'][:3]:  # Show first 3 warnings
                    print(f"   • {warning}")
                if len(module['warnings']) > 3:
                    print(f"   ... and {len(module['warnings']) - 3} more warnings")
        
        if results['clean_modules']:
            print(f"\n✅ CLEAN MODULES ({len(results['clean_modules'])} modules):")
            clean_names = [module['name'] for module in results['clean_modules']]
            # Print in groups of 5
            for i in range(0, len(clean_names), 5):
                group = clean_names[i:i+5]
                print(f"   {', '.join(group)}")
        
        return results

if __name__ == "__main__":
    workspace = r"d:\GitHub\osus_main\cleanup osus\odoo17_final"
    auditor = Odoo17ModuleAuditor(workspace)
    results = auditor.run_comprehensive_audit()
    
    # Save results to JSON file
    with open(workspace + r"\CORRECTED_AUDIT_RESULTS.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed audit results saved to: CORRECTED_AUDIT_RESULTS.json")
