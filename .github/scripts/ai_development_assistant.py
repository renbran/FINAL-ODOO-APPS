#!/usr/bin/env python3
"""
Genspark AI Development Assistant
AI-powered development suggestions and automation for Odoo 17
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime


class AIDevelopmentAssistant:
    """AI-powered development assistant for Odoo 17 CloudPepper projects"""
    
    def __init__(self):
        self.suggestions = {
            'code_improvements': [],
            'performance_optimizations': [],
            'security_enhancements': [],
            'cloudpepper_fixes': [],
            'automation_opportunities': []
        }
    
    def analyze_git_changes(self):
        """Analyze git changes and provide AI suggestions"""
        try:
            # Get modified files from git
            import subprocess
            result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                changed_files = result.stdout.strip().split('\n')
                return [f for f in changed_files if f]
            return []
        except:
            return []
    
    def suggest_emergency_scripts(self):
        """AI suggestions for emergency script usage"""
        suggestions = []
        
        # Check if there are commission-related files
        commission_modules = list(Path('.').glob('**/commission*'))
        if commission_modules:
            suggestions.append({
                'category': 'Emergency Scripts',
                'title': 'Commission System Emergency Fixes Available',
                'description': 'Detected commission modules - emergency scripts can help with quick fixes',
                'scripts': [
                    'create_commission_email_emergency_fix.py',
                    'create_commission_ax_emergency_deployment.py',
                    'validate_commission_enhancement.py'
                ],
                'priority': 'medium'
            })
        
        # Check for payment modules
        payment_modules = list(Path('.').glob('**/payment*')) + list(Path('.').glob('**/account_payment*'))
        if payment_modules:
            suggestions.append({
                'category': 'Emergency Scripts',
                'title': 'Payment System Emergency Tools',
                'description': 'Payment modules found - use emergency scripts for CloudPepper deployment',
                'scripts': [
                    'cloudpepper_deployment_final_validation.py',
                    'create_emergency_cloudpepper_fix.py'
                ],
                'priority': 'high'
            })
        
        return suggestions
    
    def analyze_performance_opportunities(self):
        """AI analysis for performance improvements"""
        suggestions = []
        
        # Check for inefficient database queries
        python_files = list(Path('.').glob('**/*.py'))
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Detect potential N+1 query issues
                if 'for record in self:' in content and '.search(' in content:
                    suggestions.append({
                        'category': 'Performance',
                        'title': f'Potential N+1 Query in {py_file.name}',
                        'description': 'Loop with search operations may cause performance issues',
                        'suggestion': 'Consider using read_group() or bulk operations',
                        'file': str(py_file),
                        'priority': 'medium'
                    })
                
                # Check for missing indexes on frequently searched fields
                if '@api.depends' in content and 'store=False' in content:
                    suggestions.append({
                        'category': 'Performance',
                        'title': f'Computed Field Optimization in {py_file.name}',
                        'description': 'Computed fields without store may impact performance',
                        'suggestion': 'Consider adding store=True for frequently accessed fields',
                        'file': str(py_file),
                        'priority': 'low'
                    })
                    
            except Exception:
                continue
        
        return suggestions
    
    def analyze_security_patterns(self):
        """AI analysis for security improvements"""
        suggestions = []
        
        # Check security files
        security_dirs = list(Path('.').glob('**/security'))
        for security_dir in security_dirs:
            csv_files = list(security_dir.glob('*.csv'))
            xml_files = list(security_dir.glob('*.xml'))
            
            if not csv_files:
                suggestions.append({
                    'category': 'Security',
                    'title': f'Missing Access Control in {security_dir.parent.name}',
                    'description': 'Module has security directory but no ir.model.access.csv',
                    'suggestion': 'Create ir.model.access.csv file with proper access rights',
                    'priority': 'high'
                })
            
            if not xml_files:
                suggestions.append({
                    'category': 'Security',
                    'title': f'Missing Security Groups in {security_dir.parent.name}',
                    'description': 'Consider adding security groups for better access control',
                    'suggestion': 'Create security.xml with user groups and record rules',
                    'priority': 'medium'
                })
        
        return suggestions
    
    def generate_cloudpepper_fixes(self):
        """AI-generated CloudPepper specific fixes"""
        fixes = []
        
        # Check for common CloudPepper issues
        js_files = list(Path('.').glob('**/static/src/js/*.js'))
        for js_file in js_files:
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for OWL error handling
                if ('Component' in content or 'owl' in content.lower()) and 'addEventListener' not in content:
                    fixes.append({
                        'category': 'CloudPepper Compatibility',
                        'title': f'Add Error Handling to {js_file.name}',
                        'description': 'OWL components need error handlers for CloudPepper stability',
                        'fix_code': '''
// Add to component setup
window.addEventListener('error', (event) => {
    console.error('Global error caught:', event.error);
});
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});''',
                        'priority': 'high'
                    })
                    
            except Exception:
                continue
        
        # Check manifest files for CloudPepper compatibility
        manifest_files = list(Path('.').glob('**/__manifest__.py'))
        for manifest_file in manifest_files:
            try:
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'assets' in content and 'prepend' not in content:
                    fixes.append({
                        'category': 'CloudPepper Compatibility',
                        'title': f'Optimize Asset Loading in {manifest_file.parent.name}',
                        'description': 'Emergency fixes should load with prepend for CloudPepper',
                        'suggestion': 'Use ("prepend", "path/to/emergency_fix.js") pattern',
                        'priority': 'medium'
                    })
                    
            except Exception:
                continue
        
        return fixes
    
    def suggest_automation_opportunities(self):
        """AI suggestions for automation improvements"""
        automations = []
        
        # Check for manual processes that could be automated
        py_files = list(Path('.').glob('**/*.py'))
        for py_file in py_files:
            if 'cron' in py_file.name.lower() or 'scheduler' in py_file.name.lower():
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for patterns that could benefit from automation
                if 'state' in content and 'workflow' in content.lower():
                    automations.append({
                        'category': 'Automation',
                        'title': f'Workflow Automation Opportunity in {py_file.name}',
                        'description': 'State-based workflows can benefit from automated transitions',
                        'suggestion': 'Consider adding cron jobs for automatic state transitions',
                        'priority': 'low'
                    })
                
                if 'email' in content.lower() and 'send' in content.lower():
                    automations.append({
                        'category': 'Automation',
                        'title': f'Email Automation in {py_file.name}',
                        'description': 'Manual email sending could be automated',
                        'suggestion': 'Use mail.template and automated triggers',
                        'priority': 'medium'
                    })
                    
            except Exception:
                continue
        
        return automations
    
    def create_development_report(self):
        """Create comprehensive development assistant report"""
        print("🤖 Analyzing development opportunities...")
        
        # Gather all suggestions
        emergency_suggestions = self.suggest_emergency_scripts()
        performance_suggestions = self.analyze_performance_opportunities()
        security_suggestions = self.analyze_security_patterns()
        cloudpepper_fixes = self.generate_cloudpepper_fixes()
        automation_suggestions = self.suggest_automation_opportunities()
        
        # Compile all suggestions
        all_suggestions = (
            emergency_suggestions + 
            performance_suggestions + 
            security_suggestions + 
            cloudpepper_fixes + 
            automation_suggestions
        )
        
        # Create markdown report
        report = "## 🚀 AI Development Assistant Report\n\n"
        report += f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        
        # Group by category
        categories = {}
        for suggestion in all_suggestions:
            category = suggestion.get('category', 'General')
            if category not in categories:
                categories[category] = []
            categories[category].append(suggestion)
        
        for category, suggestions in categories.items():
            if not suggestions:
                continue
                
            category_emoji = {
                'Emergency Scripts': '🚨',
                'Performance': '⚡',
                'Security': '🔒',
                'CloudPepper Compatibility': '☁️',
                'Automation': '🤖'
            }.get(category, '📋')
            
            report += f"### {category_emoji} {category}\n\n"
            
            for suggestion in suggestions:
                priority_emoji = {
                    'high': '🔴',
                    'medium': '🟡', 
                    'low': '🟢'
                }.get(suggestion.get('priority', 'medium'), '⚪')
                
                report += f"{priority_emoji} **{suggestion['title']}**\n"
                report += f"   {suggestion['description']}\n"
                
                if 'suggestion' in suggestion:
                    report += f"   💡 *Suggestion*: {suggestion['suggestion']}\n"
                
                if 'scripts' in suggestion:
                    report += f"   🔧 *Available Scripts*:\n"
                    for script in suggestion['scripts']:
                        report += f"   - `{script}`\n"
                
                if 'fix_code' in suggestion:
                    report += f"   💻 *Example Fix*:\n```javascript\n{suggestion['fix_code']}\n```\n"
                
                report += "\n"
        
        # Add summary
        report += "## 📊 Summary\n\n"
        report += f"- Total Suggestions: {len(all_suggestions)}\n"
        report += f"- High Priority: {len([s for s in all_suggestions if s.get('priority') == 'high'])}\n"
        report += f"- Medium Priority: {len([s for s in all_suggestions if s.get('priority') == 'medium'])}\n"
        report += f"- Low Priority: {len([s for s in all_suggestions if s.get('priority') == 'low'])}\n"
        
        # Save report
        with open('ai_development_suggestions.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save JSON data
        with open('ai_development_data.json', 'w', encoding='utf-8') as f:
            json.dump({
                'suggestions': all_suggestions,
                'summary': {
                    'total': len(all_suggestions),
                    'high_priority': len([s for s in all_suggestions if s.get('priority') == 'high']),
                    'medium_priority': len([s for s in all_suggestions if s.get('priority') == 'medium']),
                    'low_priority': len([s for s in all_suggestions if s.get('priority') == 'low'])
                },
                'generated_at': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"✅ Development analysis complete. {len(all_suggestions)} suggestions generated.")
        return report


def main():
    """Main execution"""
    assistant = AIDevelopmentAssistant()
    assistant.create_development_report()


if __name__ == "__main__":
    main()