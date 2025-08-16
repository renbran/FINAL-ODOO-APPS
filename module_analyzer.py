#!/usr/bin/env python3
"""
Comprehensive Module Analysis Tool for account_payment_final
Analyzes module structure, functionality, complexity, and areas for improvement
"""

import os
import re
import ast
import json
from pathlib import Path
from collections import defaultdict

class ModuleAnalyzer:
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.analysis_report = {
            'module_info': {},
            'file_structure': {},
            'functionality_analysis': {},
            'complexity_metrics': {},
            'enhancement_opportunities': [],
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }
        
    def analyze_module(self):
        """Main analysis function"""
        print("🔍 COMPREHENSIVE MODULE ANALYSIS")
        print("=" * 60)
        print(f"Module: {self.module_path.name}")
        print()
        
        # Basic module info
        self.analyze_manifest()
        
        # File structure analysis
        self.analyze_file_structure()
        
        # Code complexity analysis
        self.analyze_code_complexity()
        
        # Functionality analysis
        self.analyze_functionality()
        
        # Performance analysis
        self.analyze_performance_patterns()
        
        # Security analysis
        self.analyze_security_patterns()
        
        # Generate comprehensive report
        self.generate_comprehensive_report()
        
    def analyze_manifest(self):
        """Analyze the module manifest"""
        manifest_path = self.module_path / "__manifest__.py"
        
        if not manifest_path.exists():
            return
            
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract manifest data
            manifest_dict = ast.literal_eval(content.split('=', 1)[1].strip())
            
            self.analysis_report['module_info'] = {
                'name': manifest_dict.get('name', 'Unknown'),
                'version': manifest_dict.get('version', 'Unknown'),
                'category': manifest_dict.get('category', 'Unknown'),
                'depends': manifest_dict.get('depends', []),
                'data_files': len(manifest_dict.get('data', [])),
                'assets': manifest_dict.get('assets', {}),
                'external_dependencies': manifest_dict.get('external_dependencies', {}),
                'installable': manifest_dict.get('installable', False),
                'auto_install': manifest_dict.get('auto_install', False),
                'application': manifest_dict.get('application', False)
            }
            
        except Exception as e:
            print(f"❌ Error analyzing manifest: {e}")
            
    def analyze_file_structure(self):
        """Analyze the module file structure"""
        structure = {
            'models': [],
            'views': [],
            'controllers': [],
            'reports': [],
            'static_js': [],
            'static_css': [],
            'static_xml': [],
            'security': [],
            'data': [],
            'tests': [],
            'other': []
        }
        
        for file_path in self.module_path.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.module_path)
                
                # Categorize files
                if 'models' in str(relative_path):
                    structure['models'].append(str(relative_path))
                elif 'views' in str(relative_path):
                    structure['views'].append(str(relative_path))
                elif 'controllers' in str(relative_path):
                    structure['controllers'].append(str(relative_path))
                elif 'reports' in str(relative_path):
                    structure['reports'].append(str(relative_path))
                elif file_path.suffix == '.js':
                    structure['static_js'].append(str(relative_path))
                elif file_path.suffix == '.css' or file_path.suffix == '.scss':
                    structure['static_css'].append(str(relative_path))
                elif file_path.suffix == '.xml' and 'static' in str(relative_path):
                    structure['static_xml'].append(str(relative_path))
                elif 'security' in str(relative_path):
                    structure['security'].append(str(relative_path))
                elif 'data' in str(relative_path):
                    structure['data'].append(str(relative_path))
                elif 'tests' in str(relative_path):
                    structure['tests'].append(str(relative_path))
                else:
                    structure['other'].append(str(relative_path))
        
        self.analysis_report['file_structure'] = structure
        
    def analyze_code_complexity(self):
        """Analyze code complexity metrics"""
        complexity_metrics = {
            'total_lines': 0,
            'python_files': 0,
            'classes': 0,
            'methods': 0,
            'functions': 0,
            'complexity_score': 0,
            'largest_files': [],
            'most_complex_methods': []
        }
        
        for py_file in self.module_path.rglob('*.py'):
            if py_file.name == '__init__.py':
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = len(content.splitlines())
                    
                complexity_metrics['total_lines'] += lines
                complexity_metrics['python_files'] += 1
                
                # Track largest files
                complexity_metrics['largest_files'].append((str(py_file.relative_to(self.module_path)), lines))
                
                # Parse AST for complexity
                try:
                    tree = ast.parse(content)
                    
                    class ComplexityVisitor(ast.NodeVisitor):
                        def __init__(self):
                            self.classes = 0
                            self.methods = 0
                            self.functions = 0
                            
                        def visit_ClassDef(self, node):
                            self.classes += 1
                            self.generic_visit(node)
                            
                        def visit_FunctionDef(self, node):
                            if hasattr(node, 'decorator_list') and any(
                                isinstance(d, ast.Name) and d.id == 'api' 
                                for d in node.decorator_list
                            ):
                                self.methods += 1
                            else:
                                self.functions += 1
                            self.generic_visit(node)
                    
                    visitor = ComplexityVisitor()
                    visitor.visit(tree)
                    
                    complexity_metrics['classes'] += visitor.classes
                    complexity_metrics['methods'] += visitor.methods
                    complexity_metrics['functions'] += visitor.functions
                    
                except SyntaxError:
                    pass
                    
            except Exception:
                continue
        
        # Sort largest files
        complexity_metrics['largest_files'].sort(key=lambda x: x[1], reverse=True)
        complexity_metrics['largest_files'] = complexity_metrics['largest_files'][:5]
        
        self.analysis_report['complexity_metrics'] = complexity_metrics
        
    def analyze_functionality(self):
        """Analyze module functionality and features"""
        functionality = {
            'main_models': [],
            'workflow_features': [],
            'reporting_features': [],
            'security_features': [],
            'integration_features': [],
            'ui_features': []
        }
        
        # Analyze main models
        models_dir = self.module_path / 'models'
        if models_dir.exists():
            for py_file in models_dir.glob('*.py'):
                if py_file.name == '__init__.py':
                    continue
                    
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find model classes
                    model_pattern = r'class\s+(\w+)\s*\(\s*models\.(\w+)\s*\)'
                    matches = re.findall(model_pattern, content)
                    
                    for class_name, model_type in matches:
                        functionality['main_models'].append({
                            'file': py_file.name,
                            'class': class_name,
                            'type': model_type
                        })
                    
                    # Check for workflow features
                    if 'state' in content and 'selection' in content:
                        functionality['workflow_features'].append(f"State workflow in {py_file.name}")
                    
                    if '@api.constrains' in content:
                        functionality['workflow_features'].append(f"Data constraints in {py_file.name}")
                    
                    if 'mail.thread' in content:
                        functionality['workflow_features'].append(f"Mail tracking in {py_file.name}")
                        
                except Exception:
                    continue
        
        # Analyze reports
        reports_dir = self.module_path / 'reports'
        if reports_dir.exists():
            for xml_file in reports_dir.glob('*.xml'):
                functionality['reporting_features'].append(f"Report template: {xml_file.name}")
        
        # Analyze security
        security_dir = self.module_path / 'security'
        if security_dir.exists():
            for file in security_dir.iterdir():
                if file.suffix == '.xml':
                    functionality['security_features'].append(f"Security groups: {file.name}")
                elif file.suffix == '.csv':
                    functionality['security_features'].append(f"Access rights: {file.name}")
        
        # Analyze UI features
        static_dir = self.module_path / 'static'
        if static_dir.exists():
            js_files = list(static_dir.rglob('*.js'))
            css_files = list(static_dir.rglob('*.css')) + list(static_dir.rglob('*.scss'))
            
            functionality['ui_features'].append(f"JavaScript files: {len(js_files)}")
            functionality['ui_features'].append(f"Stylesheet files: {len(css_files)}")
        
        self.analysis_report['functionality_analysis'] = functionality
        
    def analyze_performance_patterns(self):
        """Analyze performance-related patterns"""
        performance_issues = []
        performance_strengths = []
        
        # Check for common performance anti-patterns
        for py_file in self.module_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for performance issues
                if 'search(' in content and 'limit=' not in content:
                    performance_issues.append(f"Unlimited search in {py_file.name}")
                
                if 'for record in self:' in content:
                    performance_strengths.append(f"Proper record iteration in {py_file.name}")
                
                if '@api.depends' in content:
                    performance_strengths.append(f"Computed fields with dependencies in {py_file.name}")
                
                if 'self.env.cr.execute' in content:
                    performance_issues.append(f"Raw SQL usage in {py_file.name}")
                    
            except Exception:
                continue
        
        self.analysis_report['performance_patterns'] = {
            'issues': performance_issues,
            'strengths': performance_strengths
        }
        
    def analyze_security_patterns(self):
        """Analyze security patterns"""
        security_issues = []
        security_strengths = []
        
        for py_file in self.module_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Security checks
                if 'sudo()' in content:
                    security_issues.append(f"sudo() usage in {py_file.name}")
                
                if '@api.model' in content:
                    security_strengths.append(f"Proper API decorators in {py_file.name}")
                
                if 'check_access_rights' in content:
                    security_strengths.append(f"Access rights checking in {py_file.name}")
                    
            except Exception:
                continue
        
        self.analysis_report['security_patterns'] = {
            'issues': security_issues,
            'strengths': security_strengths
        }
        
    def generate_comprehensive_report(self):
        """Generate the final comprehensive report"""
        print("📊 MODULE ANALYSIS REPORT")
        print("=" * 60)
        
        # Module Information
        info = self.analysis_report['module_info']
        print(f"\n🏷️  MODULE INFORMATION")
        print(f"   Name: {info.get('name', 'Unknown')}")
        print(f"   Version: {info.get('version', 'Unknown')}")
        print(f"   Category: {info.get('category', 'Unknown')}")
        print(f"   Dependencies: {', '.join(info.get('depends', []))}")
        print(f"   Data Files: {info.get('data_files', 0)}")
        print(f"   Installable: {info.get('installable', False)}")
        
        # File Structure
        structure = self.analysis_report['file_structure']
        print(f"\n📁 FILE STRUCTURE ANALYSIS")
        print(f"   Models: {len(structure['models'])} files")
        print(f"   Views: {len(structure['views'])} files")
        print(f"   Controllers: {len(structure['controllers'])} files")
        print(f"   Reports: {len(structure['reports'])} files")
        print(f"   JavaScript: {len(structure['static_js'])} files")
        print(f"   Stylesheets: {len(structure['static_css'])} files")
        print(f"   Security: {len(structure['security'])} files")
        print(f"   Tests: {len(structure['tests'])} files")
        
        # Complexity Metrics
        complexity = self.analysis_report['complexity_metrics']
        print(f"\n📈 COMPLEXITY METRICS")
        print(f"   Total Lines of Code: {complexity['total_lines']:,}")
        print(f"   Python Files: {complexity['python_files']}")
        print(f"   Classes: {complexity['classes']}")
        print(f"   Methods: {complexity['methods']}")
        print(f"   Functions: {complexity['functions']}")
        
        if complexity['largest_files']:
            print(f"\n   📊 Largest Files:")
            for file, lines in complexity['largest_files']:
                print(f"      {file}: {lines:,} lines")
        
        # Functionality Analysis
        functionality = self.analysis_report['functionality_analysis']
        print(f"\n🔧 FUNCTIONALITY ANALYSIS")
        
        print(f"   Main Models ({len(functionality['main_models'])}):")
        for model in functionality['main_models']:
            print(f"      {model['class']} ({model['type']}) in {model['file']}")
        
        if functionality['workflow_features']:
            print(f"   Workflow Features:")
            for feature in functionality['workflow_features']:
                print(f"      ✅ {feature}")
        
        if functionality['reporting_features']:
            print(f"   Reporting Features:")
            for feature in functionality['reporting_features']:
                print(f"      📄 {feature}")
        
        if functionality['security_features']:
            print(f"   Security Features:")
            for feature in functionality['security_features']:
                print(f"      🔒 {feature}")
        
        # Performance Analysis
        performance = self.analysis_report.get('performance_patterns', {})
        if performance.get('issues') or performance.get('strengths'):
            print(f"\n⚡ PERFORMANCE ANALYSIS")
            
            if performance.get('strengths'):
                print(f"   Strengths:")
                for strength in performance['strengths']:
                    print(f"      ✅ {strength}")
            
            if performance.get('issues'):
                print(f"   Issues:")
                for issue in performance['issues']:
                    print(f"      ⚠️ {issue}")
        
        # Security Analysis
        security = self.analysis_report.get('security_patterns', {})
        if security.get('issues') or security.get('strengths'):
            print(f"\n🔒 SECURITY ANALYSIS")
            
            if security.get('strengths'):
                print(f"   Strengths:")
                for strength in security['strengths']:
                    print(f"      ✅ {strength}")
            
            if security.get('issues'):
                print(f"   Issues:")
                for issue in security['issues']:
                    print(f"      ⚠️ {issue}")
        
        # Generate recommendations
        self.generate_recommendations()
        
    def generate_recommendations(self):
        """Generate improvement recommendations"""
        recommendations = []
        
        complexity = self.analysis_report['complexity_metrics']
        structure = self.analysis_report['file_structure']
        
        # Size and complexity recommendations
        if complexity['total_lines'] > 5000:
            recommendations.append("🔄 Consider breaking down large files for better maintainability")
        
        if len(structure['static_js']) > 10:
            recommendations.append("📦 Consider bundling JavaScript files for better performance")
        
        if not structure['tests']:
            recommendations.append("🧪 Add comprehensive test coverage")
        
        # Performance recommendations
        performance = self.analysis_report.get('performance_patterns', {})
        if performance.get('issues'):
            recommendations.append("⚡ Address performance anti-patterns identified")
        
        # Security recommendations
        security = self.analysis_report.get('security_patterns', {})
        if security.get('issues'):
            recommendations.append("🔒 Review and improve security patterns")
        
        # Architecture recommendations
        if len(structure['models']) > 5:
            recommendations.append("🏗️ Consider modular architecture for better separation of concerns")
        
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        self.analysis_report['recommendations'] = recommendations

def main():
    module_path = Path("account_payment_final")
    
    if not module_path.exists():
        print("❌ Module not found!")
        return
    
    analyzer = ModuleAnalyzer(module_path)
    analyzer.analyze_module()

if __name__ == "__main__":
    main()
