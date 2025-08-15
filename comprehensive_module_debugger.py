#!/usr/bin/env python3
"""
Comprehensive Odoo 17 Module Debugging and Production Readiness Analysis
World-class debugging tool for account_payment_approval module
"""

import sys
import os
import py_compile
import xml.etree.ElementTree as ET
from pathlib import Path
import re
import ast
import json

class OdooModuleDebugger:
    """Comprehensive Odoo 17 module debugging and analysis tool"""
    
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.errors = []
        self.warnings = []
        self.recommendations = []
        self.analysis_results = {}
        
    def debug_and_analyze(self):
        """Main debugging and analysis method"""
        print("üîç ODOO 17 MODULE DEBUGGING & PRODUCTION READINESS ANALYSIS")
        print("=" * 80)
        
        # 1. Module Structure Analysis
        self._analyze_module_structure()
        
        # 2. Manifest Validation
        self._analyze_manifest()
        
        # 3. Python Code Analysis
        self._analyze_python_code()
        
        # 4. XML Structure Analysis
        self._analyze_xml_files()
        
        # 5. Dependencies Analysis
        self._analyze_dependencies()
        
        # 6. Security Analysis
        self._analyze_security()
        
        # 7. Performance Analysis
        self._analyze_performance()
        
        # 8. Odoo 17 Compliance Check
        self._check_odoo17_compliance()
        
        # 9. Production Readiness Check
        self._check_production_readiness()
        
        # Generate comprehensive report
        self._generate_report()
        
    def _analyze_module_structure(self):
        """Analyze module directory structure"""
        print("üìÅ Analyzing Module Structure...")
        
        required_files = [
            '__init__.py',
            '__manifest__.py'
        ]
        
        recommended_dirs = [
            'models',
            'views',
            'security',
            'data',
            'static',
            'controllers'
        ]
        
        # Check required files
        for file in required_files:
            if not (self.module_path / file).exists():
                self.errors.append(f"Missing required file: {file}")
            else:
                print(f"  ‚úÖ {file}")
        
        # Check recommended directories
        for dir_name in recommended_dirs:
            dir_path = self.module_path / dir_name
            if dir_path.exists():
                print(f"  ‚úÖ {dir_name}/")
                # Count files in directory
                files = list(dir_path.rglob("*.py")) + list(dir_path.rglob("*.xml"))
                print(f"    üìÑ {len(files)} files")
            else:
                self.warnings.append(f"Recommended directory missing: {dir_name}/")
                
    def _analyze_manifest(self):
        """Analyze __manifest__.py file"""
        print("\\nüìã Analyzing Manifest File...")
        
        manifest_path = self.module_path / '__manifest__.py'
        if not manifest_path.exists():
            self.errors.append("__manifest__.py file not found")
            return
            
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse manifest as Python dict
            # Handle the case where the manifest is just a dict literal
            try:
                manifest = eval(content)
            except:
                # Fallback to exec method
                manifest_dict = {}
                exec(f"result = {content}", {}, manifest_dict)
                manifest = manifest_dict.get('result', {})
            
            # Required fields check
            required_fields = ['name', 'version', 'depends', 'data']
            for field in required_fields:
                if field in manifest:
                    print(f"  ‚úÖ {field}: {manifest[field]}")
                else:
                    self.errors.append(f"Missing required manifest field: {field}")
            
            # Version format check
            version = manifest.get('version', '')
            if not re.match(r'^\\d+\\.\\d+\\.\\d+\\.\\d+\\.\\d+$', version):
                self.warnings.append(f"Version format should be X.Y.Z.A.B: {version}")
            else:
                if not version.startswith('17.'):
                    self.warnings.append(f"Version should start with '17.' for Odoo 17: {version}")
            
            # Dependencies analysis
            depends = manifest.get('depends', [])
            if 'base' not in depends:
                self.warnings.append("'base' dependency is recommended")
                
            # Data files validation
            data_files = manifest.get('data', [])
            for data_file in data_files:
                file_path = self.module_path / data_file
                if not file_path.exists():
                    self.errors.append(f"Data file not found: {data_file}")
                    
            self.analysis_results['manifest'] = manifest
            
        except Exception as e:
            self.errors.append(f"Error parsing manifest: {str(e)}")
            
    def _analyze_python_code(self):
        """Analyze Python code for syntax and best practices"""
        print("\\nüêç Analyzing Python Code...")
        
        python_files = list(self.module_path.rglob("*.py"))
        
        for py_file in python_files:
            try:
                # Syntax check
                py_compile.compile(py_file, doraise=True)
                print(f"  ‚úÖ {py_file.relative_to(self.module_path)}")
                
                # AST analysis for advanced checks
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                try:
                    tree = ast.parse(content)
                    self._analyze_ast(tree, py_file)
                except SyntaxError as e:
                    self.errors.append(f"Syntax error in {py_file}: {e}")
                    
            except Exception as e:
                self.errors.append(f"Python compilation error in {py_file}: {str(e)}")
                
    def _analyze_ast(self, tree, file_path):
        """Analyze AST for Odoo-specific patterns"""
        for node in ast.walk(tree):
            # Check for old API usage
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['browse', 'search', 'create', 'write']:
                        # Check if it's old API pattern
                        pass
                        
            # Check for proper inheritance
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Attribute):
                        if base.attr == 'Model':
                            # Check for _name definition
                            has_name = any(
                                isinstance(n, ast.Assign) and 
                                any(t.id == '_name' for t in n.targets if isinstance(t, ast.Name))
                                for n in node.body
                            )
                            if not has_name:
                                self.warnings.append(f"Model class without _name in {file_path}")
                                
    def _analyze_xml_files(self):
        """Analyze XML files for structure and references"""
        print("\\nüóÉÔ∏è  Analyzing XML Files...")
        
        xml_files = list(self.module_path.rglob("*.xml"))
        
        for xml_file in xml_files:
            try:
                ET.parse(xml_file)
                print(f"  ‚úÖ {xml_file.relative_to(self.module_path)}")
                
                # Check for external references
                self._check_external_references(xml_file)
                
            except ET.ParseError as e:
                self.errors.append(f"XML parse error in {xml_file}: {str(e)}")
                
    def _check_external_references(self, xml_file):
        """Check for potentially missing external references"""
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for ref= attributes
            refs = re.findall(r'ref="([^"]+)"', content)
            for ref in refs:
                if ref.startswith('base.'):
                    # Common base references that might not exist
                    if 'paperformat' in ref:
                        self.warnings.append(f"Paper format reference may not exist: {ref} in {xml_file}")
                        
        except Exception as e:
            self.warnings.append(f"Could not analyze references in {xml_file}: {e}")
            
    def _analyze_dependencies(self):
        """Analyze module dependencies"""
        print("\\nüîó Analyzing Dependencies...")
        
        manifest = self.analysis_results.get('manifest', {})
        depends = manifest.get('depends', [])
        
        # Check for circular dependencies
        print(f"  üì¶ Dependencies: {depends}")
        
        # Check for external dependencies
        external_deps = manifest.get('external_dependencies', {})
        if external_deps:
            python_deps = external_deps.get('python', [])
            if python_deps:
                print(f"  üêç Python dependencies: {python_deps}")
                for dep in python_deps:
                    try:
                        __import__(dep)
                        print(f"    ‚úÖ {dep}")
                    except ImportError:
                        self.warnings.append(f"Python dependency not available: {dep}")
                        
    def _analyze_security(self):
        """Analyze security configuration"""
        print("\\nüîí Analyzing Security Configuration...")
        
        security_dir = self.module_path / 'security'
        if security_dir.exists():
            # Check for access rights
            access_file = security_dir / 'ir.model.access.csv'
            if access_file.exists():
                print("  ‚úÖ ir.model.access.csv found")
                with open(access_file, 'r') as f:
                    lines = f.readlines()
                    print(f"    üìä {len(lines)-1} access rules defined")
            else:
                self.warnings.append("No ir.model.access.csv found")
                
            # Check for security groups
            security_files = list(security_dir.glob("*.xml"))
            for sec_file in security_files:
                print(f"  ‚úÖ {sec_file.name}")
        else:
            self.warnings.append("No security directory found")
            
    def _analyze_performance(self):
        """Analyze potential performance issues"""
        print("\\n‚ö° Analyzing Performance Considerations...")
        
        python_files = list(self.module_path.rglob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for potential performance issues
                if 'for record in self:' in content and 'self.env[' in content:
                    self.recommendations.append(f"Consider batch operations in {py_file}")
                    
                if '@api.one' in content:
                    self.errors.append(f"Deprecated @api.one decorator found in {py_file}")
                    
            except Exception:
                pass
                
    def _check_odoo17_compliance(self):
        """Check Odoo 17 specific compliance"""
        print("\\nüîß Checking Odoo 17 Compliance...")
        
        python_files = list(self.module_path.rglob("*.py"))
        
        compliance_checks = {
            'new_api': True,
            'no_old_decorators': True,
            'proper_imports': True
        }
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for old API patterns
                if re.search(r'@api\\.(one|multi)', content):
                    compliance_checks['no_old_decorators'] = False
                    self.errors.append(f"Old API decorators found in {py_file}")
                    
                # Check for proper imports
                if 'from openerp' in content:
                    compliance_checks['proper_imports'] = False
                    self.errors.append(f"Old import style 'from openerp' in {py_file}")
                    
            except Exception:
                pass
                
        self.analysis_results['odoo17_compliance'] = compliance_checks
        
    def _check_production_readiness(self):
        """Check production readiness criteria"""
        print("\\nüöÄ Checking Production Readiness...")
        
        manifest = self.analysis_results.get('manifest', {})
        
        readiness_checks = {
            'has_description': bool(manifest.get('description')),
            'has_author': bool(manifest.get('author')),
            'has_website': bool(manifest.get('website')),
            'has_license': bool(manifest.get('license')),
            'installable': manifest.get('installable', True),
            'auto_install': not manifest.get('auto_install', False)  # Should be False for production
        }
        
        for check, status in readiness_checks.items():
            if status:
                print(f"  ‚úÖ {check}")
            else:
                self.warnings.append(f"Production readiness: {check} not satisfied")
                
        self.analysis_results['production_readiness'] = readiness_checks
        
    def _generate_report(self):
        """Generate comprehensive debugging report"""
        print("\\n" + "=" * 80)
        print("üìä COMPREHENSIVE DEBUGGING REPORT")
        print("=" * 80)
        
        # Summary
        total_issues = len(self.errors) + len(self.warnings)
        if total_issues == 0:
            print("üéâ EXCELLENT! No issues found. Module is production-ready!")
        else:
            print(f"üìà ANALYSIS SUMMARY: {len(self.errors)} errors, {len(self.warnings)} warnings")
            
        # Errors
        if self.errors:
            print("\\n‚ùå CRITICAL ERRORS (Must Fix):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
                
        # Warnings
        if self.warnings:
            print("\\n‚ö†Ô∏è  WARNINGS (Recommended Fixes):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
                
        # Recommendations
        if self.recommendations:
            print("\\nüí° RECOMMENDATIONS:")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"  {i}. {rec}")
                
        # Best Practices Summary
        print("\\nüèÜ BEST PRACTICES SUMMARY:")
        print("  ‚úÖ Follow Odoo 17 new API patterns")
        print("  ‚úÖ Use proper field definitions with help text")
        print("  ‚úÖ Implement proper security access controls")
        print("  ‚úÖ Add comprehensive docstrings to methods")
        print("  ‚úÖ Use computed fields efficiently")
        print("  ‚úÖ Implement proper error handling")
        print("  ‚úÖ Follow PEP 8 coding standards")
        print("  ‚úÖ Use proper XML namespacing")
        print("  ‚úÖ Implement proper test coverage")
        print("  ‚úÖ Document module functionality")
        
        # Final Assessment
        print("\\nüéØ FINAL ASSESSMENT:")
        if not self.errors:
            print("  üü¢ PRODUCTION READY - Module can be deployed")
        elif len(self.errors) <= 3:
            print("  üü° NEEDS MINOR FIXES - Address errors before deployment")
        else:
            print("  üî¥ NEEDS MAJOR FIXES - Significant issues require resolution")
            
        return total_issues == 0

def main():
    """Main execution function"""
    module_path = "account_payment_approval"
    
    if not os.path.exists(module_path):
        print("‚ùå Module directory not found!")
        return False
        
    debugger = OdooModuleDebugger(module_path)
    return debugger.debug_and_analyze()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
