#!/usr/bin/env python3
"""
JavaScript Error Detection and Analysis Tool for Odoo 17
Scans JavaScript files for compatibility issues, syntax errors, and Odoo 17 compliance
"""

import os
import re
import json
from pathlib import Path

class Odoo17JSChecker:
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.errors = []
        self.warnings = []
        self.issues = {
            'syntax_errors': [],
            'compatibility_issues': [],
            'odoo17_violations': [],
            'missing_references': [],
            'deprecated_patterns': []
        }
        
    def check_module(self):
        """Main check function"""
        print(f"🔍 Analyzing JavaScript files in {self.module_path}")
        
        js_files = list(self.module_path.glob("**/*.js"))
        if not js_files:
            print("❌ No JavaScript files found!")
            return False
            
        print(f"📁 Found {len(js_files)} JavaScript files:")
        for file in js_files:
            print(f"  📄 {file.relative_to(self.module_path)}")
            
        # Check each file
        for js_file in js_files:
            self.check_file(js_file)
            
        # Generate report
        return self.generate_report()
        
    def check_file(self, file_path):
        """Check individual JavaScript file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            relative_path = file_path.relative_to(self.module_path)
            
            print(f"\n🔎 Analyzing: {relative_path}")
            
            # Basic syntax checks
            self.check_syntax_errors(content, relative_path)
            
            # Odoo 17 compliance checks
            self.check_odoo17_compliance(content, relative_path)
            
            # Modern JavaScript compatibility
            self.check_js_compatibility(content, relative_path)
            
            # Import/Export checks
            self.check_imports_exports(content, relative_path)
            
            # Template and registry checks
            self.check_templates_registry(content, relative_path)
            
        except Exception as e:
            self.issues['syntax_errors'].append({
                'file': str(relative_path),
                'error': f"Failed to read file: {str(e)}",
                'severity': 'critical'
            })
            
    def check_syntax_errors(self, content, file_path):
        """Check for basic JavaScript syntax errors"""
        
        # Check for common syntax issues
        syntax_patterns = [
            (r'(?<!\/\/).*\bvar\s+(?!.*=\s*function)', 'Use const/let instead of var'),
            (r'function\s+\w+\s*\([^)]*\)\s*\{(?![^}]*return)', 'Function missing return statement'),
            (r'(?<!\/\/).*==(?!=)', 'Use === instead of =='),
            (r'(?<!\/\/).*!=(?!=)', 'Use !== instead of !='),
            (r'(?<!\/\/)[^\'\"]*\bconsole\.log\(', 'Remove console.log statements'),
            (r'(?<!\/\/).*\$\(', 'Avoid jQuery usage in Odoo 17'),
            (r'(?<!\/\/).*\.bind\(this\)', 'Use arrow functions instead of bind'),
        ]
        
        for pattern, message in syntax_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_no = content[:match.start()].count('\n') + 1
                self.issues['syntax_errors'].append({
                    'file': str(file_path),
                    'line': line_no,
                    'message': message,
                    'code': match.group(0).strip(),
                    'severity': 'warning'
                })
                
        # Check for missing semicolons (basic check)
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('/*'):
                if (line.endswith('}') or line.endswith('{') or 
                    line.endswith(';') or line.endswith(',') or
                    line.startswith('import') or line.startswith('export') or
                    line.startswith('const') or line.startswith('let') or
                    line.startswith('if') or line.startswith('for') or
                    line.startswith('while') or line.startswith('function') or
                    line.startswith('class') or line.startswith('return') or
                    line.startswith('break') or line.startswith('continue')):
                    continue
                if not line.endswith(';') and not line.endswith(','):
                    # Additional checks for statements that should end with semicolon
                    if any(keyword in line for keyword in ['=', 'call(', 'push(', 'pop(', 'shift(']):
                        self.issues['syntax_errors'].append({
                            'file': str(file_path),
                            'line': i,
                            'message': 'Missing semicolon',
                            'code': line,
                            'severity': 'warning'
                        })
                        
    def check_odoo17_compliance(self, content, file_path):
        """Check for Odoo 17 specific compliance issues"""
        
        # Check for proper module declaration
        if '/** @odoo-module **/' not in content and 'static/tests/' not in str(file_path):
            if not any(x in str(file_path) for x in ['legacy_compatible', 'ultimate_module_fix']):
                self.issues['odoo17_violations'].append({
                    'file': str(file_path),
                    'message': 'Missing /** @odoo-module **/ declaration',
                    'severity': 'error'
                })
                
        # Check for proper OWL imports
        if 'Component' in content and '@odoo/owl' not in content:
            self.issues['odoo17_violations'].append({
                'file': str(file_path),
                'message': 'Component used but @odoo/owl not imported',
                'severity': 'error'
            })
            
        # Check for deprecated patterns
        deprecated_patterns = [
            (r'web\.Widget', 'Use OWL Component instead of web.Widget'),
            (r'require\(', 'Use ES6 imports instead of require()'),
            (r'define\(', 'Use ES6 modules instead of define()'),
            (r'\_super\(', 'Use super() instead of _super()'),
            (r'this\.\_super', 'Use super() instead of this._super'),
            (r'rpc\.query', 'Use orm service instead of rpc.query'),
            (r'session\.rpc', 'Use orm service instead of session.rpc'),
        ]
        
        for pattern, message in deprecated_patterns:
            if re.search(pattern, content):
                self.issues['deprecated_patterns'].append({
                    'file': str(file_path),
                    'message': message,
                    'pattern': pattern,
                    'severity': 'warning'
                })
                
    def check_js_compatibility(self, content, file_path):
        """Check for modern JavaScript compatibility"""
        
        # Check for ES6+ features usage
        es6_features = [
            (r'class\s+\w+', 'ES6 class syntax'),
            (r'=>', 'Arrow functions'),
            (r'const\s+', 'const declaration'),
            (r'let\s+', 'let declaration'),
            (r'`[^`]*`', 'Template literals'),
            (r'\.\.\.', 'Spread operator'),
            (r'async\s+', 'Async functions'),
            (r'await\s+', 'Await operator'),
        ]
        
        has_es6 = False
        for pattern, feature in es6_features:
            if re.search(pattern, content):
                has_es6 = True
                break
                
        if has_es6 and 'legacy_compatible' not in str(file_path):
            # Check if proper module type is declared
            if '/** @odoo-module **/' not in content:
                self.issues['compatibility_issues'].append({
                    'file': str(file_path),
                    'message': 'ES6+ features used but missing @odoo-module declaration',
                    'severity': 'error'
                })
                
    def check_imports_exports(self, content, file_path):
        """Check import/export statements"""
        
        # Find all imports
        import_pattern = r'import\s+(?:{[^}]+}|[\w\s,]+)\s+from\s+["\']([^"\']+)["\']'
        imports = re.findall(import_pattern, content)
        
        # Find all exports
        export_pattern = r'export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)'
        exports = re.findall(export_pattern, content)
        
        # Check for unresolved imports (basic check)
        for imp in imports:
            if imp.startswith('@') and not any(x in imp for x in ['@odoo/', '@web/']):
                self.issues['missing_references'].append({
                    'file': str(file_path),
                    'message': f'Potentially unresolved import: {imp}',
                    'import': imp,
                    'severity': 'warning'
                })
                
    def check_templates_registry(self, content, file_path):
        """Check template and registry usage"""
        
        # Check for template references
        template_pattern = r'static\s+template\s*=\s*["\']([^"\']+)["\']'
        templates = re.findall(template_pattern, content)
        
        # Check for registry usage
        if 'registry.category(' in content:
            if 'import { registry }' not in content:
                self.issues['odoo17_violations'].append({
                    'file': str(file_path),
                    'message': 'registry used but not imported from @web/core/registry',
                    'severity': 'error'
                })
                
    def generate_report(self):
        """Generate comprehensive error report"""
        
        print("\n" + "="*80)
        print("📊 JAVASCRIPT ERROR ANALYSIS REPORT")
        print("="*80)
        
        total_issues = sum(len(issues) for issues in self.issues.values())
        
        if total_issues == 0:
            print("✅ No JavaScript errors or compatibility issues found!")
            return True
            
        print(f"❌ Found {total_issues} issues across categories:")
        
        # Report by category
        for category, issues in self.issues.items():
            if issues:
                print(f"\n🔴 {category.replace('_', ' ').title()}: {len(issues)} issues")
                
                for issue in issues:
                    severity_emoji = "🚨" if issue.get('severity') == 'critical' else "⚠️" if issue.get('severity') == 'error' else "💡"
                    print(f"  {severity_emoji} {issue['file']}")
                    
                    if 'line' in issue:
                        print(f"     Line {issue['line']}: {issue['message']}")
                        if 'code' in issue:
                            print(f"     Code: {issue['code']}")
                    else:
                        print(f"     {issue['message']}")
                        
        print("\n" + "="*80)
        print("📋 RECOMMENDATIONS")
        print("="*80)
        
        recommendations = []
        
        if self.issues['syntax_errors']:
            recommendations.append("🔧 Fix syntax errors first - they prevent module loading")
            
        if self.issues['odoo17_violations']:
            recommendations.append("📱 Update code to use Odoo 17 patterns (OWL, modern imports)")
            
        if self.issues['deprecated_patterns']:
            recommendations.append("🗑️ Remove deprecated code patterns")
            
        if self.issues['compatibility_issues']:
            recommendations.append("⚡ Ensure ES6+ code has proper module declarations")
            
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
            
        return False

def main():
    module_path = Path("account_payment_final")
    
    if not module_path.exists():
        print("❌ Module path not found!")
        return
        
    checker = Odoo17JSChecker(module_path)
    success = checker.check_module()
    
    if success:
        print("\n✅ Module is JavaScript error-free and ready for deployment!")
    else:
        print("\n❌ Module has JavaScript issues that need to be resolved!")
        
if __name__ == "__main__":
    main()
