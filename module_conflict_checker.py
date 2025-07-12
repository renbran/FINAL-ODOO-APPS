#!/usr/bin/env python3
"""
Odoo Module Conflict and Compatibility Checker
This script analyzes all Odoo modules for potential conflicts and compatibility issues.
"""

import os
import ast
import sys
from collections import defaultdict
from pathlib import Path
import json

class ModuleAnalyzer:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.modules = {}
        self.conflicts = []
        self.warnings = []
        self.dependencies = defaultdict(set)
        
    def find_modules(self):
        """Find all modules with __manifest__.py files"""
        manifest_files = list(self.base_path.rglob("__manifest__.py"))
        
        for manifest_path in manifest_files:
            module_dir = manifest_path.parent
            module_name = module_dir.name
            
            # Skip if this is a nested module (like odoo_dynamic_dashboard-17.0.2.0.1/odoo_dynamic_dashboard)
            relative_path = module_dir.relative_to(self.base_path)
            if len(relative_path.parts) > 1:
                # Check if parent directory also has a manifest
                parent_manifest = module_dir.parent / "__manifest__.py"
                if parent_manifest.exists():
                    self.warnings.append(f"Nested module detected: {relative_path}")
                    continue
            
            try:
                self.modules[module_name] = self.parse_manifest(manifest_path)
                self.modules[module_name]['path'] = str(module_dir)
            except Exception as e:
                self.warnings.append(f"Failed to parse manifest for {module_name}: {str(e)}")
    
    def parse_manifest(self, manifest_path):
        """Parse __manifest__.py file"""
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the manifest file
        try:
            tree = ast.parse(content)
            manifest_dict = ast.literal_eval(tree.body[0].value)
            return manifest_dict
        except:
            # Fallback: execute the file in a controlled environment
            manifest_globals = {}
            exec(content, manifest_globals)
            # Find the dictionary that was assigned
            for key, value in manifest_globals.items():
                if isinstance(value, dict) and 'name' in value:
                    return value
            return {}
    
    def check_duplicate_modules(self):
        """Check for modules with the same name"""
        name_to_modules = defaultdict(list)
        
        for module_name, manifest in self.modules.items():
            display_name = manifest.get('name', module_name)
            name_to_modules[display_name].append(module_name)
        
        for display_name, module_list in name_to_modules.items():
            if len(module_list) > 1:
                self.conflicts.append({
                    'type': 'duplicate_name',
                    'severity': 'high',
                    'message': f"Multiple modules with same display name '{display_name}': {module_list}"
                })
    
    def check_version_compatibility(self):
        """Check for version compatibility issues"""
        versions = defaultdict(list)
        
        for module_name, manifest in self.modules.items():
            version = manifest.get('version', 'unknown')
            odoo_version = self.extract_odoo_version(version, manifest)
            versions[odoo_version].append(module_name)
        
        if len(versions) > 1:
            self.conflicts.append({
                'type': 'version_mismatch',
                'severity': 'high',
                'message': f"Modules for different Odoo versions detected: {dict(versions)}"
            })
    
    def extract_odoo_version(self, version, manifest):
        """Extract Odoo version from module version or other indicators"""
        # Check if version starts with Odoo version (like 16.0.1.0.0)
        if version and version[0].isdigit():
            parts = version.split('.')
            if len(parts) >= 2:
                major_minor = f"{parts[0]}.{parts[1]}"
                return major_minor
        
        # Check installable flag and other indicators
        if not manifest.get('installable', True):
            return 'disabled'
        
        # Check for version indicators in dependencies
        depends = manifest.get('depends', [])
        if 'account_accountant' in depends:
            return '17.0+'  # Enterprise feature
        
        return 'unknown'
    
    def check_dependencies(self):
        """Check for dependency conflicts and missing dependencies"""
        all_module_names = set(self.modules.keys())
        
        # Build dependency graph
        for module_name, manifest in self.modules.items():
            depends = manifest.get('depends', [])
            self.dependencies[module_name] = set(depends)
            
            # Check for missing dependencies
            missing_deps = set(depends) - all_module_names - self.get_standard_modules()
            if missing_deps:
                self.warnings.append(f"Module '{module_name}' has missing dependencies: {missing_deps}")
        
        # Check for circular dependencies
        self.check_circular_dependencies()
    
    def get_standard_modules(self):
        """Return set of standard Odoo modules"""
        return {
            'base', 'web', 'account', 'sale', 'purchase', 'stock', 'mrp', 'hr', 'crm',
            'project', 'website', 'mail', 'calendar', 'contacts', 'product', 'payment',
            'portal', 'survey', 'mass_mailing', 'maintenance', 'fleet', 'lunch',
            'note', 'document', 'board', 'account_accountant', 'sale_management',
            'purchase_requisition', 'stock_account', 'analytic', 'uom', 'decimal_precision',
            'resource', 'web_tour', 'bus', 'iap', 'sms', 'phone_validation'
        }
    
    def check_circular_dependencies(self):
        """Check for circular dependencies using DFS"""
        def has_cycle(node, visited, rec_stack):
            visited[node] = True
            rec_stack[node] = True
            
            for neighbor in self.dependencies.get(node, []):
                if neighbor in self.modules:  # Only check custom modules
                    if not visited.get(neighbor, False):
                        if has_cycle(neighbor, visited, rec_stack):
                            return True
                    elif rec_stack.get(neighbor, False):
                        return True
            
            rec_stack[node] = False
            return False
        
        visited = {}
        rec_stack = {}
        
        for module in self.modules:
            if not visited.get(module, False):
                if has_cycle(module, visited, rec_stack):
                    self.conflicts.append({
                        'type': 'circular_dependency',
                        'severity': 'high',
                        'message': f"Circular dependency detected involving module: {module}"
                    })
    
    def check_theme_conflicts(self):
        """Check for conflicting themes"""
        themes = []
        
        for module_name, manifest in self.modules.items():
            category = manifest.get('category', '')
            if 'theme' in category.lower() or 'theme' in module_name.lower():
                themes.append(module_name)
            
            # Check for theme-related dependencies
            depends = manifest.get('depends', [])
            if any('theme' in dep for dep in depends):
                themes.append(module_name)
        
        if len(themes) > 1:
            self.warnings.append(f"Multiple themes detected (may cause conflicts): {themes}")
    
    def check_dashboard_conflicts(self):
        """Check for conflicting dashboard modules"""
        dashboards = []
        
        for module_name, manifest in self.modules.items():
            if 'dashboard' in module_name.lower() or 'dashboard' in manifest.get('name', '').lower():
                dashboards.append(module_name)
        
        if len(dashboards) > 3:  # More than 3 dashboard modules might be excessive
            self.warnings.append(f"Many dashboard modules detected (may cause UI conflicts): {dashboards}")
    
    def check_accounting_conflicts(self):
        """Check for conflicting accounting modules"""
        accounting_modules = []
        budget_modules = []
        
        for module_name, manifest in self.modules.items():
            name_lower = module_name.lower()
            display_name_lower = manifest.get('name', '').lower()
            
            if 'account' in name_lower or 'accounting' in name_lower:
                accounting_modules.append(module_name)
            
            if 'budget' in name_lower or 'budget' in display_name_lower:
                budget_modules.append(module_name)
        
        # Check for potential conflicts in accounting modules
        core_accounting = ['base_accounting_kit', 'om_account_accountant']
        installed_core = [m for m in core_accounting if m in accounting_modules]
        
        if len(installed_core) > 1:
            self.conflicts.append({
                'type': 'accounting_conflict',
                'severity': 'medium',
                'message': f"Multiple core accounting modules detected: {installed_core}"
            })
        
        if len(budget_modules) > 1:
            self.warnings.append(f"Multiple budget modules detected: {budget_modules}")
    
    def check_property_management_conflicts(self):
        """Check for conflicting property management modules"""
        property_modules = []
        
        for module_name, manifest in self.modules.items():
            name_lower = module_name.lower()
            display_name_lower = manifest.get('name', '').lower()
            
            if any(keyword in name_lower for keyword in ['property', 'real_estate', 'rental']):
                property_modules.append(module_name)
        
        if len(property_modules) > 2:
            self.warnings.append(f"Multiple property management modules detected (may have overlapping functionality): {property_modules}")
    
    def check_report_conflicts(self):
        """Check for conflicting report modules"""
        report_modules = []
        
        for module_name, manifest in self.modules.items():
            if 'report' in module_name.lower():
                report_modules.append(module_name)
        
        # Check for xlsx report conflicts
        xlsx_modules = [m for m in report_modules if 'xlsx' in m.lower()]
        if len(xlsx_modules) > 1:
            self.conflicts.append({
                'type': 'report_conflict',
                'severity': 'medium',
                'message': f"Multiple XLSX report modules detected: {xlsx_modules}"
            })
    
    def analyze(self):
        """Run all analysis checks"""
        print("🔍 Finding modules...")
        self.find_modules()
        print(f"Found {len(self.modules)} modules")
        
        print("🔍 Checking for conflicts...")
        self.check_duplicate_modules()
        self.check_version_compatibility()
        self.check_dependencies()
        self.check_theme_conflicts()
        self.check_dashboard_conflicts()
        self.check_accounting_conflicts()
        self.check_property_management_conflicts()
        self.check_report_conflicts()
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate a comprehensive report"""
        report = {
            'summary': {
                'total_modules': len(self.modules),
                'conflicts_found': len(self.conflicts),
                'warnings_found': len(self.warnings)
            },
            'modules': list(self.modules.keys()),
            'conflicts': self.conflicts,
            'warnings': self.warnings
        }
        
        return report

def main():
    base_path = r"d:\GitHub\osus_main\odoo\custom"
    
    print("🚀 Starting Odoo Module Conflict Analysis...")
    print(f"📁 Analyzing modules in: {base_path}")
    print("=" * 60)
    
    analyzer = ModuleAnalyzer(base_path)
    report = analyzer.analyze()
    
    print("\n📊 ANALYSIS REPORT")
    print("=" * 60)
    print(f"Total modules found: {report['summary']['total_modules']}")
    print(f"Conflicts found: {report['summary']['conflicts_found']}")
    print(f"Warnings found: {report['summary']['warnings_found']}")
    
    if report['conflicts']:
        print("\n🚨 CONFLICTS (High Priority)")
        print("-" * 40)
        for i, conflict in enumerate(report['conflicts'], 1):
            print(f"{i}. [{conflict['severity'].upper()}] {conflict['type']}")
            print(f"   {conflict['message']}")
            print()
    
    if report['warnings']:
        print("\n⚠️  WARNINGS (Review Recommended)")
        print("-" * 40)
        for i, warning in enumerate(report['warnings'], 1):
            print(f"{i}. {warning}")
        print()
    
    if not report['conflicts'] and not report['warnings']:
        print("\n✅ No major conflicts detected!")
    
    print("\n📋 ALL MODULES")
    print("-" * 40)
    for i, module in enumerate(sorted(report['modules']), 1):
        print(f"{i:2d}. {module}")
    
    # Save detailed report
    with open('module_analysis_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Detailed report saved to: module_analysis_report.json")

if __name__ == "__main__":
    main()
