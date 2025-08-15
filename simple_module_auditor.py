#!/usr/bin/env python3
"""
SIMPLE ODOO 17 MODULE AUDITOR
Production-ready module validation with focus on critical issues
"""

import os
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import ast
import re

class SimpleOdoo17Auditor:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path)
        self.results = {
            'total_modules': 0,
            'clean_modules': [],
            'modules_with_issues': [],
            'critical_issues': [],
            'warnings': []
        }
        
    def find_modules(self):
        """Find all Odoo modules"""
        modules = []
        for item in self.workspace_path.iterdir():
            if item.is_dir() and (item / '__manifest__.py').exists():
                modules.append(item)
        return sorted(modules)
    
    def validate_manifest(self, module_path):
        """Quick manifest validation"""
        issues = []
        warnings = []
        
        manifest_file = module_path / '__manifest__.py'
        try:
            with open(manifest_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Basic validation
            if 'name' not in content:
                issues.append("Missing 'name' field")
            if 'version' not in content:
                issues.append("Missing 'version' field")
            if 'depends' not in content:
                issues.append("Missing 'depends' field")
                
            # Try to execute manifest
            try:
                manifest_data = eval(content)
                
                # Check data files exist
                if 'data' in manifest_data:
                    for data_file in manifest_data['data']:
                        file_path = module_path / data_file
                        if not file_path.exists():
                            issues.append(f"Missing data file: {data_file}")
                
                return issues, warnings, manifest_data
            except:
                issues.append("Cannot parse manifest as valid Python dict")
                return issues, warnings, {}
                
        except Exception as e:
            issues.append(f"Cannot read manifest: {e}")
            return issues, warnings, {}
    
    def check_python_syntax(self, module_path):
        """Check Python file syntax"""
        issues = []
        
        for py_file in module_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check syntax
                ast.parse(content)
                
            except SyntaxError as e:
                issues.append(f"Syntax error in {py_file.relative_to(module_path)}: {e}")
            except Exception:
                pass  # Skip other errors
                
        return issues
    
    def check_xml_syntax(self, module_path):
        """Check XML file syntax"""
        issues = []
        
        for xml_file in module_path.rglob('*.xml'):
            try:
                with open(xml_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().strip()
                
                if content:  # Skip empty files
                    ET.parse(xml_file)
                    
            except ET.ParseError as e:
                issues.append(f"XML error in {xml_file.relative_to(module_path)}: {e}")
            except Exception:
                pass  # Skip other errors
                
        return issues
    
    def check_required_files(self, module_path):
        """Check required files exist"""
        issues = []
        
        required_files = ['__init__.py', '__manifest__.py']
        for req_file in required_files:
            if not (module_path / req_file).exists():
                issues.append(f"Missing required file: {req_file}")
                
        return issues
    
    def audit_module(self, module_path):
        """Audit single module"""
        module_name = module_path.name
        all_issues = []
        
        # 1. Required files
        req_issues = self.check_required_files(module_path)
        all_issues.extend(req_issues)
        
        # 2. Manifest validation
        manifest_issues, manifest_warnings, manifest_data = self.validate_manifest(module_path)
        all_issues.extend(manifest_issues)
        
        # 3. Python syntax
        py_issues = self.check_python_syntax(module_path)
        all_issues.extend(py_issues)
        
        # 4. XML syntax
        xml_issues = self.check_xml_syntax(module_path)
        all_issues.extend(xml_issues)
        
        return all_issues, manifest_warnings, manifest_data
    
    def run_audit(self):
        """Run comprehensive audit"""
        print("🚀 Starting Simple Odoo 17 Module Audit")
        print("=" * 50)
        
        modules = self.find_modules()
        self.results['total_modules'] = len(modules)
        
        for module_path in modules:
            module_name = module_path.name
            issues, warnings, manifest = self.audit_module(module_path)
            
            if issues:
                self.results['modules_with_issues'].append({
                    'name': module_name,
                    'issues': issues,
                    'warnings': warnings,
                    'manifest': manifest
                })
                print(f"❌ {module_name}: {len(issues)} issues")
                
                # Check for critical issues
                critical = [issue for issue in issues if any(keyword in issue.lower() 
                          for keyword in ['syntax error', 'missing required', 'cannot parse'])]
                if critical:
                    self.results['critical_issues'].extend([f"{module_name}: {issue}" for issue in critical])
                    
            else:
                self.results['clean_modules'].append({
                    'name': module_name,
                    'manifest': manifest
                })
                print(f"✅ {module_name}: Clean")
        
        self.generate_report()
        return self.results
    
    def generate_report(self):
        """Generate audit report"""
        total = self.results['total_modules']
        clean = len(self.results['clean_modules'])
        issues = len(self.results['modules_with_issues'])
        critical = len(self.results['critical_issues'])
        
        print("\n" + "=" * 50)
        print("📊 AUDIT SUMMARY REPORT")
        print("=" * 50)
        print(f"Total Modules: {total}")
        print(f"✅ Clean: {clean}")
        print(f"❌ With Issues: {issues}")
        print(f"🚨 Critical Issues: {critical}")
        
        success_rate = (clean / total) * 100 if total > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        if self.results['critical_issues']:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in self.results['critical_issues'][:10]:  # Show first 10
                print(f"   • {issue}")
            if len(self.results['critical_issues']) > 10:
                print(f"   ... and {len(self.results['critical_issues']) - 10} more")
        
        if self.results['modules_with_issues']:
            print(f"\n❌ MODULES NEEDING ATTENTION:")
            for module in self.results['modules_with_issues'][:10]:  # Show first 10
                print(f"   • {module['name']}: {len(module['issues'])} issues")
            if len(self.results['modules_with_issues']) > 10:
                print(f"   ... and {len(self.results['modules_with_issues']) - 10} more")
        
        if self.results['clean_modules']:
            print(f"\n✅ CLEAN MODULES ({clean}):")
            clean_names = [m['name'] for m in self.results['clean_modules']]
            for i in range(0, len(clean_names), 5):
                group = clean_names[i:i+5]
                print(f"   {', '.join(group)}")

if __name__ == "__main__":
    workspace = r"d:\GitHub\osus_main\cleanup osus\odoo17_final"
    auditor = SimpleOdoo17Auditor(workspace)
    results = auditor.run_audit()
    
    # Save results
    with open(workspace + r"\SIMPLE_AUDIT_RESULTS.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: SIMPLE_AUDIT_RESULTS.json")
