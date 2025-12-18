#!/usr/bin/env python3
"""
Genspark AI Module Analyzer
AI-powered analysis of Odoo 17 modules for CloudPepper deployment
"""

import os
import sys
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET


class AIModuleAnalyzer:
    """AI-enhanced module analyzer for Odoo 17 CloudPepper compatibility"""
    
    def __init__(self):
        self.analysis_results = {
            'critical_issues': [],
            'warnings': [],
            'suggestions': [],
            'cloudpepper_compatibility': True,
            'modules_analyzed': []
        }
        
    def analyze_manifest(self, manifest_path):
        """Analyze __manifest__.py for AI insights"""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # AI pattern recognition for common issues
            if "'prepend'" not in content and 'static/src/js' in content:
                self.analysis_results['warnings'].append({
                    'file': str(manifest_path),
                    'message': 'Consider using prepend loading for emergency fixes',
                    'suggestion': 'Add ("prepend", "path/to/emergency_fix.js") for CloudPepper compatibility'
                })
                
            # Check for CloudPepper required dependencies
            odoo17_patterns = ['mail', 'base', 'web']
            missing_deps = []
            for pattern in odoo17_patterns:
                if f"'{pattern}'" not in content and f'"{pattern}"' not in content:
                    missing_deps.append(pattern)
                    
            if missing_deps:
                self.analysis_results['suggestions'].append({
                    'file': str(manifest_path),
                    'message': f'Consider adding common dependencies: {", ".join(missing_deps)}',
                    'type': 'dependency_optimization'
                })
                
        except Exception as e:
            self.analysis_results['critical_issues'].append({
                'file': str(manifest_path),
                'message': f'Failed to analyze manifest: {str(e)}'
            })
    
    def analyze_python_models(self, model_path):
        """AI analysis of Python model files"""
        try:
            with open(model_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # AI pattern detection for common CloudPepper issues
            if '@api.depends' in content and 'store=True' not in content:
                if 'commission' in content.lower() or 'payment' in content.lower():
                    self.analysis_results['warnings'].append({
                        'file': str(model_path),
                        'message': 'Computed fields in commission/payment modules should consider store=True',
                        'suggestion': 'Add store=True for fields used in email templates or external references'
                    })
                    
            # Check for proper error handling
            if 'def ' in content and 'try:' not in content:
                method_count = len(re.findall(r'def \w+', content))
                if method_count > 5:
                    self.analysis_results['suggestions'].append({
                        'file': str(model_path),
                        'message': 'Consider adding try-catch blocks for better error handling',
                        'type': 'error_handling'
                    })
                    
        except Exception as e:
            self.analysis_results['critical_issues'].append({
                'file': str(model_path),
                'message': f'Failed to analyze Python model: {str(e)}'
            })
    
    def analyze_javascript_files(self, js_path):
        """AI analysis of JavaScript files for OWL compatibility"""
        try:
            with open(js_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # AI detection of CloudPepper JavaScript issues
            if 'owl' in content.lower() or 'component' in content.lower():
                if 'addEventListener(\'error\'' not in content:
                    self.analysis_results['warnings'].append({
                        'file': str(js_path),
                        'message': 'OWL components should include error handlers for CloudPepper',
                        'suggestion': 'Add global error and unhandledrejection listeners'
                    })
                    
            # Check for jQuery usage (should be avoided in Odoo 17)
            if '$(' in content or 'jQuery' in content:
                self.analysis_results['warnings'].append({
                    'file': str(js_path),
                    'message': 'Avoid jQuery in Odoo 17 - use native JS or OWL patterns',
                    'type': 'modernization'
                })
                
        except Exception as e:
            self.analysis_results['critical_issues'].append({
                'file': str(js_path),
                'message': f'Failed to analyze JavaScript: {str(e)}'
            })
    
    def analyze_xml_views(self, xml_path):
        """AI analysis of XML view files"""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # AI detection of field reference issues
            for field_elem in root.iter('field'):
                field_name = field_elem.get('name', '')
                if field_name == 'x_lead_id':
                    self.analysis_results['critical_issues'].append({
                        'file': str(xml_path),
                        'message': 'Remove x_lead_id field reference - known CloudPepper incompatibility',
                        'suggestion': 'Replace with proper lead_id or remove entirely'
                    })
                    
            # Check for missing invisible fields in modifiers
            for elem in root.iter():
                if elem.get('readonly') and 'locked' in str(elem.get('readonly', '')):
                    # Check if locked field is defined in view
                    locked_fields = [f.get('name') for f in root.iter('field') if f.get('name') == 'locked']
                    if not locked_fields:
                        self.analysis_results['critical_issues'].append({
                            'file': str(xml_path),
                            'message': 'locked field used in readonly modifier but not defined in view',
                            'suggestion': 'Add <field name="locked" invisible="1"/> to view'
                        })
                        
        except ET.ParseError as e:
            self.analysis_results['critical_issues'].append({
                'file': str(xml_path),
                'message': f'XML parsing error: {str(e)}'
            })
        except Exception as e:
            self.analysis_results['critical_issues'].append({
                'file': str(xml_path),
                'message': f'Failed to analyze XML view: {str(e)}'
            })
    
    def generate_ai_recommendations(self):
        """Generate AI-powered recommendations based on analysis"""
        recommendations = []
        
        # CloudPepper specific recommendations
        if self.analysis_results['critical_issues']:
            recommendations.append({
                'priority': 'HIGH',
                'title': 'Critical Issues Detected',
                'description': 'These issues will prevent CloudPepper deployment',
                'action': 'Fix immediately before deployment'
            })
            
        # OSUS branding recommendations
        css_files = list(Path('.').glob('**/static/src/scss/*.scss')) + list(Path('.').glob('**/static/src/css/*.css'))
        if css_files:
            recommendations.append({
                'priority': 'MEDIUM',
                'title': 'OSUS Branding Consistency',
                'description': 'Ensure color scheme consistency: #800020 (maroon), #FFD700 (gold)',
                'action': 'Review CSS files for brand color usage'
            })
            
        # Emergency script recommendations
        recommendations.append({
            'priority': 'INFO',
            'title': 'Emergency Scripts Available',
            'description': 'Use emergency scripts for quick fixes',
            'scripts': [
                'cloudpepper_deployment_final_validation.py',
                'create_emergency_cloudpepper_fix.py',
                'create_commission_ax_emergency_deployment.py'
            ]
        })
        
        return recommendations
    
    def run_analysis(self):
        """Run comprehensive AI analysis"""
        print("🤖 Starting AI-powered module analysis...")
        
        # Find all Odoo modules
        for module_dir in Path('.').iterdir():
            if module_dir.is_dir() and (module_dir / '__manifest__.py').exists():
                print(f"   Analyzing module: {module_dir.name}")
                self.analysis_results['modules_analyzed'].append(module_dir.name)
                
                # Analyze manifest
                self.analyze_manifest(module_dir / '__manifest__.py')
                
                # Analyze Python models
                models_dir = module_dir / 'models'
                if models_dir.exists():
                    for py_file in models_dir.glob('*.py'):
                        self.analyze_python_models(py_file)
                
                # Analyze JavaScript files
                static_js_dir = module_dir / 'static' / 'src' / 'js'
                if static_js_dir.exists():
                    for js_file in static_js_dir.glob('*.js'):
                        self.analyze_javascript_files(js_file)
                
                # Analyze XML views
                views_dir = module_dir / 'views'
                if views_dir.exists():
                    for xml_file in views_dir.glob('*.xml'):
                        self.analyze_xml_views(xml_file)
        
        # Generate AI recommendations
        recommendations = self.generate_ai_recommendations()
        
        # Create analysis report
        self.create_analysis_report(recommendations)
        
        print(f"✅ Analysis complete. Found {len(self.analysis_results['critical_issues'])} critical issues")
        print(f"   Warnings: {len(self.analysis_results['warnings'])}")
        print(f"   Suggestions: {len(self.analysis_results['suggestions'])}")
    
    def create_analysis_report(self, recommendations):
        """Create markdown report for GitHub"""
        report = "## 🤖 AI Module Analysis Results\n\n"
        
        if self.analysis_results['critical_issues']:
            report += "### 🚨 Critical Issues\n"
            for issue in self.analysis_results['critical_issues']:
                report += f"- **{issue['file']}**: {issue['message']}\n"
                if 'suggestion' in issue:
                    report += f"  - 💡 Suggestion: {issue['suggestion']}\n"
            report += "\n"
        
        if self.analysis_results['warnings']:
            report += "### ⚠️ Warnings\n"
            for warning in self.analysis_results['warnings']:
                report += f"- **{warning['file']}**: {warning['message']}\n"
                if 'suggestion' in warning:
                    report += f"  - 💡 Suggestion: {warning['suggestion']}\n"
            report += "\n"
        
        if recommendations:
            report += "### 🎯 AI Recommendations\n"
            for rec in recommendations:
                priority_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'INFO': '🔵'}.get(rec['priority'], '⚪')
                report += f"{priority_emoji} **{rec['title']}**\n"
                report += f"   {rec['description']}\n"
                if 'action' in rec:
                    report += f"   *Action*: {rec['action']}\n"
                if 'scripts' in rec:
                    report += "   *Available Scripts*:\n"
                    for script in rec['scripts']:
                        report += f"   - `{script}`\n"
                report += "\n"
        
        report += f"### 📊 Analysis Summary\n"
        report += f"- Modules Analyzed: {len(self.analysis_results['modules_analyzed'])}\n"
        report += f"- Critical Issues: {len(self.analysis_results['critical_issues'])}\n"
        report += f"- Warnings: {len(self.analysis_results['warnings'])}\n"
        report += f"- CloudPepper Compatible: {'✅' if self.analysis_results['cloudpepper_compatibility'] and not self.analysis_results['critical_issues'] else '❌'}\n"
        
        # Save report
        with open('ai_analysis_results.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save JSON for other tools
        with open('ai_analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'analysis_results': self.analysis_results,
                'recommendations': recommendations
            }, f, indent=2)


def main():
    """Main execution"""
    analyzer = AIModuleAnalyzer()
    analyzer.run_analysis()


if __name__ == "__main__":
    main()