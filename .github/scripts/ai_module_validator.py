#!/usr/bin/env python3
"""
Genspark AI Module Validator
AI-enhanced validation for Odoo 17 modules
"""

import os
import sys
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from datetime import datetime


class AIModuleValidator:
    """AI-enhanced module validation for Odoo 17 CloudPepper compatibility"""
    
    def __init__(self):
        self.validation_results = {
            'modules_validated': [],
            'critical_issues': [],
            'warnings': [],
            'recommendations': [],
            'cloudpepper_ready': True,
            'ai_insights': []
        }
    
    def validate_manifest_ai(self, manifest_path):
        """AI-enhanced manifest validation"""
        module_name = manifest_path.parent.name
        issues = []
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # AI pattern recognition for manifest issues
            exec(compile(content, str(manifest_path), 'exec'), {}, {'manifest_data': None})
            
            # Check for CloudPepper critical patterns
            if 'depends' not in content:
                issues.append({
                    'type': 'critical',
                    'message': f'{module_name}: Missing dependencies declaration',
                    'ai_suggestion': 'Add depends list with required Odoo core modules'
                })
            
            # Check for proper asset loading
            if 'assets' in content:
                if 'prepend' not in content and 'emergency' in content.lower():
                    issues.append({
                        'type': 'warning',
                        'message': f'{module_name}: Emergency scripts should use prepend loading',
                        'ai_suggestion': 'Use ("prepend", "path/to/emergency_fix.js") for critical fixes'
                    })
            
            # AI recommendation for version consistency
            if 'version' in content:
                version_match = re.search(r"'version':\s*'([^']+)'", content)
                if version_match:
                    version = version_match.group(1)
                    if not version.startswith('17.0'):
                        issues.append({
                            'type': 'critical',
                            'message': f'{module_name}: Version {version} not compatible with Odoo 17',
                            'ai_suggestion': 'Update version to 17.0.x.x.x format'
                        })
            
        except Exception as e:
            issues.append({
                'type': 'critical',
                'message': f'{module_name}: Manifest parsing error - {str(e)}',
                'ai_suggestion': 'Fix Python syntax errors in __manifest__.py'
            })
        
        return issues
    
    def validate_python_models_ai(self, models_dir):
        """AI-enhanced Python model validation"""
        module_name = models_dir.parent.name
        issues = []
        
        for py_file in models_dir.glob('*.py'):
            if py_file.name == '__init__.py':
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # AI detection of CloudPepper-specific issues
                
                # Check for proper imports
                required_imports = ['from odoo import models', 'from odoo import fields']
                for req_import in required_imports:
                    if req_import not in content and 'class' in content and 'models.Model' in content:
                        issues.append({
                            'type': 'critical',
                            'message': f'{module_name}/{py_file.name}: Missing required import',
                            'ai_suggestion': f'Add: {req_import}'
                        })
                
                # Check for computed fields without store in commission modules
                if 'commission' in module_name.lower() or 'payment' in module_name.lower():
                    computed_fields = re.findall(r'@api\.depends.*?\n.*?fields\.\w+.*?compute=', content, re.DOTALL)
                    for field_match in computed_fields:
                        if 'store=True' not in field_match:
                            issues.append({
                                'type': 'warning',
                                'message': f'{module_name}/{py_file.name}: Computed field without store in commission module',
                                'ai_suggestion': 'Add store=True for fields used in templates or external references'
                            })
                
                # Check for proper error handling
                method_matches = re.findall(r'def \w+\(self[^)]*\):', content)
                if len(method_matches) > 3 and 'try:' not in content:
                    issues.append({
                        'type': 'recommendation',
                        'message': f'{module_name}/{py_file.name}: Consider adding error handling',
                        'ai_suggestion': 'Add try-except blocks for robust error handling'
                    })
                
                # AI insight for state workflows
                if 'state = fields.Selection' in content:
                    state_methods = re.findall(r'def action_\w+\(', content)
                    if len(state_methods) < 2:
                        issues.append({
                            'type': 'recommendation',
                            'message': f'{module_name}/{py_file.name}: State model with few transition methods',
                            'ai_suggestion': 'Consider adding more state transition methods for complete workflow'
                        })
                
            except Exception as e:
                issues.append({
                    'type': 'critical',
                    'message': f'{module_name}/{py_file.name}: Python file validation error - {str(e)}'
                })
        
        return issues
    
    def validate_xml_views_ai(self, views_dir):
        """AI-enhanced XML view validation"""
        module_name = views_dir.parent.name
        issues = []
        
        for xml_file in views_dir.glob('*.xml'):
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # AI detection of CloudPepper view issues
                
                # Check for problematic field references
                for field_elem in root.iter('field'):
                    field_name = field_elem.get('name', '')
                    
                    # Known CloudPepper incompatible fields
                    if field_name == 'x_lead_id':
                        issues.append({
                            'type': 'critical',
                            'message': f'{module_name}/{xml_file.name}: x_lead_id field causes CloudPepper errors',
                            'ai_suggestion': 'Remove x_lead_id or replace with proper lead_id field'
                        })
                    
                    # Check for fields used in modifiers but not defined
                    parent = field_elem.getparent()
                    if parent is not None:
                        for attr_name in ['readonly', 'invisible', 'required']:
                            attr_value = field_elem.get(attr_name, '')
                            if 'locked' in attr_value:
                                # Check if locked field exists in view
                                locked_fields = [f.get('name') for f in root.iter('field') if f.get('name') == 'locked']
                                if not locked_fields:
                                    issues.append({
                                        'type': 'critical',
                                        'message': f'{module_name}/{xml_file.name}: locked field used in {attr_name} but not defined',
                                        'ai_suggestion': 'Add <field name="locked" invisible="1"/> to view'
                                    })
                
                # Check for button actions without corresponding methods
                for button_elem in root.iter('button'):
                    action_name = button_elem.get('name', '')
                    if action_name.startswith('action_') or action_name.startswith('button_'):
                        # This would need to be cross-referenced with model files
                        issues.append({
                            'type': 'warning',
                            'message': f'{module_name}/{xml_file.name}: Verify {action_name} method exists in model',
                            'ai_suggestion': 'Ensure corresponding method exists in Python model'
                        })
                
                # AI insight for view inheritance
                inherit_views = root.findall('.//field[@name="inherit_id"]')
                if inherit_views and not root.findall('.//field[@name="arch"]'):
                    issues.append({
                        'type': 'warning',
                        'message': f'{module_name}/{xml_file.name}: Inherit view without arch modifications',
                        'ai_suggestion': 'Verify view inheritance is necessary'
                    })
                
            except ET.ParseError as e:
                issues.append({
                    'type': 'critical',
                    'message': f'{module_name}/{xml_file.name}: XML parsing error - {str(e)}',
                    'ai_suggestion': 'Fix XML syntax errors'
                })
            except Exception as e:
                issues.append({
                    'type': 'critical',
                    'message': f'{module_name}/{xml_file.name}: View validation error - {str(e)}'
                })
        
        return issues
    
    def validate_javascript_ai(self, static_dir):
        """AI-enhanced JavaScript validation"""
        module_name = static_dir.parent.name
        issues = []
        
        js_dir = static_dir / 'src' / 'js'
        if not js_dir.exists():
            return issues
        
        for js_file in js_dir.rglob('*.js'):
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # AI detection of JavaScript issues
                
                # Check for CloudPepper error handling
                if ('Component' in content or 'owl' in content.lower()) and 'addEventListener' not in content:
                    issues.append({
                        'type': 'critical',
                        'message': f'{module_name}/{js_file.name}: OWL component missing error handlers',
                        'ai_suggestion': 'Add global error and unhandledrejection listeners'
                    })
                
                # Check for jQuery usage (deprecated in Odoo 17)
                if '$(' in content or 'jQuery' in content:
                    issues.append({
                        'type': 'warning',
                        'message': f'{module_name}/{js_file.name}: jQuery usage detected',
                        'ai_suggestion': 'Use native JavaScript or OWL framework instead'
                    })
                
                # Check for proper module declaration
                if '/** @odoo-module **/' not in content and 'odoo.define' not in content:
                    issues.append({
                        'type': 'warning',
                        'message': f'{module_name}/{js_file.name}: Missing proper module declaration',
                        'ai_suggestion': 'Add /** @odoo-module **/ at the top of the file'
                    })
                
                # AI insight for async/await usage
                if 'rpc' in content.lower() and 'await' not in content:
                    issues.append({
                        'type': 'recommendation',
                        'message': f'{module_name}/{js_file.name}: Consider using async/await for RPC calls',
                        'ai_suggestion': 'Use modern async/await instead of promise chains'
                    })
                
            except Exception as e:
                issues.append({
                    'type': 'critical',
                    'message': f'{module_name}/{js_file.name}: JavaScript validation error - {str(e)}'
                })
        
        return issues
    
    def validate_security_ai(self, security_dir):
        """AI-enhanced security validation"""
        module_name = security_dir.parent.name
        issues = []
        
        # Check for access control file
        access_file = security_dir / 'ir.model.access.csv'
        if not access_file.exists():
            issues.append({
                'type': 'critical',
                'message': f'{module_name}: Missing ir.model.access.csv',
                'ai_suggestion': 'Create access control file with proper permissions'
            })
        else:
            try:
                with open(access_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # AI validation of CSV format
                lines = content.strip().split('\n')
                if len(lines) < 2:
                    issues.append({
                        'type': 'warning',
                        'message': f'{module_name}: Empty or minimal access control file',
                        'ai_suggestion': 'Add proper access rights for all models'
                    })
                
                # Check CSV header
                if lines and not lines[0].startswith('id,name,model_id'):
                    issues.append({
                        'type': 'critical',
                        'message': f'{module_name}: Invalid CSV header in access file',
                        'ai_suggestion': 'Use proper CSV header: id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink'
                    })
                    
            except Exception as e:
                issues.append({
                    'type': 'critical',
                    'message': f'{module_name}: Access file validation error - {str(e)}'
                })
        
        # Check for security groups
        security_file = security_dir / 'security.xml'
        if not security_file.exists():
            issues.append({
                'type': 'warning',
                'message': f'{module_name}: No security.xml found',
                'ai_suggestion': 'Consider adding security groups for better access control'
            })
        
        return issues
    
    def generate_ai_insights(self):
        """Generate AI insights based on validation results"""
        insights = []
        
        total_issues = len(self.validation_results['critical_issues']) + len(self.validation_results['warnings'])
        
        if total_issues == 0:
            insights.append({
                'type': 'positive',
                'message': 'Excellent! No major issues detected. Modules appear CloudPepper ready.',
                'confidence': 'high'
            })
        elif total_issues < 5:
            insights.append({
                'type': 'caution',
                'message': f'Minor issues detected ({total_issues}). Address these before CloudPepper deployment.',
                'confidence': 'medium'
            })
        else:
            insights.append({
                'type': 'warning',
                'message': f'Multiple issues detected ({total_issues}). Thorough testing recommended.',
                'confidence': 'low'
            })
        
        # Module-specific insights
        commission_modules = [m for m in self.validation_results['modules_validated'] if 'commission' in m.lower()]
        if commission_modules:
            insights.append({
                'type': 'info',
                'message': f'Commission modules detected: {", ".join(commission_modules)}',
                'recommendation': 'Ensure store=True for computed fields used in email templates'
            })
        
        payment_modules = [m for m in self.validation_results['modules_validated'] if 'payment' in m.lower()]
        if payment_modules:
            insights.append({
                'type': 'info',
                'message': f'Payment modules detected: {", ".join(payment_modules)}',
                'recommendation': 'Validate signature fields and QR code generation'
            })
        
        return insights
    
    def run_validation(self):
        """Run comprehensive AI-enhanced validation"""
        print("🤖 Starting AI-enhanced module validation...")
        
        # Find all Odoo modules
        for module_dir in Path('.').iterdir():
            if module_dir.is_dir() and (module_dir / '__manifest__.py').exists():
                module_name = module_dir.name
                print(f"   Validating: {module_name}")
                
                self.validation_results['modules_validated'].append(module_name)
                
                # Validate manifest
                manifest_issues = self.validate_manifest_ai(module_dir / '__manifest__.py')
                for issue in manifest_issues:
                    if issue['type'] == 'critical':
                        self.validation_results['critical_issues'].append(issue)
                        self.validation_results['cloudpepper_ready'] = False
                    elif issue['type'] == 'warning':
                        self.validation_results['warnings'].append(issue)
                    else:
                        self.validation_results['recommendations'].append(issue)
                
                # Validate Python models
                models_dir = module_dir / 'models'
                if models_dir.exists():
                    model_issues = self.validate_python_models_ai(models_dir)
                    for issue in model_issues:
                        if issue['type'] == 'critical':
                            self.validation_results['critical_issues'].append(issue)
                            self.validation_results['cloudpepper_ready'] = False
                        elif issue['type'] == 'warning':
                            self.validation_results['warnings'].append(issue)
                        else:
                            self.validation_results['recommendations'].append(issue)
                
                # Validate XML views
                views_dir = module_dir / 'views'
                if views_dir.exists():
                    view_issues = self.validate_xml_views_ai(views_dir)
                    for issue in view_issues:
                        if issue['type'] == 'critical':
                            self.validation_results['critical_issues'].append(issue)
                            self.validation_results['cloudpepper_ready'] = False
                        elif issue['type'] == 'warning':
                            self.validation_results['warnings'].append(issue)
                        else:
                            self.validation_results['recommendations'].append(issue)
                
                # Validate JavaScript
                static_dir = module_dir / 'static'
                if static_dir.exists():
                    js_issues = self.validate_javascript_ai(static_dir)
                    for issue in js_issues:
                        if issue['type'] == 'critical':
                            self.validation_results['critical_issues'].append(issue)
                            self.validation_results['cloudpepper_ready'] = False
                        elif issue['type'] == 'warning':
                            self.validation_results['warnings'].append(issue)
                        else:
                            self.validation_results['recommendations'].append(issue)
                
                # Validate security
                security_dir = module_dir / 'security'
                if security_dir.exists():
                    security_issues = self.validate_security_ai(security_dir)
                    for issue in security_issues:
                        if issue['type'] == 'critical':
                            self.validation_results['critical_issues'].append(issue)
                            self.validation_results['cloudpepper_ready'] = False
                        elif issue['type'] == 'warning':
                            self.validation_results['warnings'].append(issue)
                        else:
                            self.validation_results['recommendations'].append(issue)
        
        # Generate AI insights
        self.validation_results['ai_insights'] = self.generate_ai_insights()
        
        # Create validation report
        self.create_validation_report()
        
        print(f"✅ AI validation complete!")
        print(f"   Modules: {len(self.validation_results['modules_validated'])}")
        print(f"   Critical: {len(self.validation_results['critical_issues'])}")
        print(f"   Warnings: {len(self.validation_results['warnings'])}")
        print(f"   CloudPepper Ready: {'✅' if self.validation_results['cloudpepper_ready'] else '❌'}")
    
    def create_validation_report(self):
        """Create comprehensive validation report"""
        report = "## 🤖 AI Module Validation Report\n\n"
        report += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        
        # Summary
        report += "### 📊 Validation Summary\n\n"
        report += f"- **Modules Validated**: {len(self.validation_results['modules_validated'])}\n"
        report += f"- **Critical Issues**: {len(self.validation_results['critical_issues'])}\n"
        report += f"- **Warnings**: {len(self.validation_results['warnings'])}\n"
        report += f"- **Recommendations**: {len(self.validation_results['recommendations'])}\n"
        report += f"- **CloudPepper Ready**: {'✅ Yes' if self.validation_results['cloudpepper_ready'] else '❌ No'}\n\n"
        
        # AI Insights
        if self.validation_results['ai_insights']:
            report += "### 🧠 AI Insights\n\n"
            for insight in self.validation_results['ai_insights']:
                insight_emoji = {
                    'positive': '✅',
                    'caution': '⚠️',
                    'warning': '❌',
                    'info': 'ℹ️'
                }.get(insight['type'], 'ℹ️')
                
                report += f"{insight_emoji} {insight['message']}\n"
                if 'recommendation' in insight:
                    report += f"   💡 *Recommendation*: {insight['recommendation']}\n"
                report += "\n"
        
        # Critical Issues
        if self.validation_results['critical_issues']:
            report += "### 🚨 Critical Issues (Must Fix)\n\n"
            for issue in self.validation_results['critical_issues']:
                report += f"- **{issue['message']}**\n"
                if 'ai_suggestion' in issue:
                    report += f"  💡 *AI Suggestion*: {issue['ai_suggestion']}\n"
                report += "\n"
        
        # Warnings
        if self.validation_results['warnings']:
            report += "### ⚠️ Warnings (Should Fix)\n\n"
            for warning in self.validation_results['warnings']:
                report += f"- **{warning['message']}**\n"
                if 'ai_suggestion' in warning:
                    report += f"  💡 *AI Suggestion*: {warning['ai_suggestion']}\n"
                report += "\n"
        
        # Recommendations
        if self.validation_results['recommendations']:
            report += "### 💡 AI Recommendations (Nice to Have)\n\n"
            for rec in self.validation_results['recommendations']:
                report += f"- **{rec['message']}**\n"
                if 'ai_suggestion' in rec:
                    report += f"  🤖 *Suggestion*: {rec['ai_suggestion']}\n"
                report += "\n"
        
        # Save reports
        with open('ai_module_analysis.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        with open('ai_validation_report.json', 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2)


def main():
    """Main execution"""
    validator = AIModuleValidator()
    validator.run_validation()


if __name__ == "__main__":
    main()