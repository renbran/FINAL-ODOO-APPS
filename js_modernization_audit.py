#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo 17 JavaScript Module Audit & Modernization Tool
===================================================

Comprehensive audit tool for identifying and flagging outdated JavaScript 
patterns in Odoo 17 modules according to modern coding guidelines.

Author: Odoo 17 Development Team  
Date: August 17, 2025
"""

import os
import re
import json
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class Odoo17JSAuditor:
    def __init__(self):
        self.modules_processed = 0
        self.files_processed = 0
        self.issues_found = 0
        self.report = {
            'audit_date': datetime.now().isoformat(),
            'modules': {},
            'summary': {
                'total_modules': 0,
                'total_files': 0,
                'total_issues': 0,
                'critical_issues': 0,
                'modernization_required': []
            }
        }
        
        # Define deprecated patterns
        self.deprecated_patterns = {
            'odoo_define': {
                'pattern': r'odoo\.define\s*\(',
                'severity': 'CRITICAL',
                'description': 'Legacy odoo.define() module definition',
                'replacement': '/** @odoo-module **/ with ES6 imports'
            },
            'jquery_usage': {
                'pattern': r'\$\s*\(|jQuery',
                'severity': 'HIGH', 
                'description': 'jQuery usage (should be minimized)',
                'replacement': 'Native DOM APIs or OWL framework methods'
            },
            'old_require': {
                'pattern': r'var\s+\w+\s*=\s*require\s*\(',
                'severity': 'CRITICAL',
                'description': 'Legacy require() syntax',
                'replacement': 'ES6 import statements'
            },
            'include_syntax': {
                'pattern': r'include\s*:\s*\[',
                'severity': 'CRITICAL', 
                'description': 'Legacy include: dependency declaration',
                'replacement': 'ES6 import statements'
            },
            'web_legacy_imports': {
                'pattern': r'web\.(core|Widget|Model|View)\.',
                'severity': 'HIGH',
                'description': 'Legacy web.* import paths',
                'replacement': 'Modern @web/* import paths'
            },
            'old_extend_pattern': {
                'pattern': r'\.extend\s*\(\s*\{',
                'severity': 'MEDIUM',
                'description': 'Legacy .extend() class definition',
                'replacement': 'ES6 class syntax or OWL Component'
            },
            'document_ready': {
                'pattern': r'\$\(document\)\.ready|\$\(function',
                'severity': 'MEDIUM',
                'description': 'jQuery document ready pattern',
                'replacement': 'OWL component lifecycle methods'
            },
            'underscore_js': {
                'pattern': r'_\.(map|each|filter|find|extend)',
                'severity': 'LOW',
                'description': 'Underscore.js usage',
                'replacement': 'Native JavaScript array methods'
            }
        }
        
        # Modern patterns to encourage
        self.modern_patterns = {
            'odoo_module': r'/\*\*\s*@odoo-module\s*\*\*/',
            'owl_imports': r'import\s+.*from\s+["\']@odoo/owl["\']',
            'web_imports': r'import\s+.*from\s+["\']@web/',
            'es6_class': r'class\s+\w+\s+(extends\s+\w+\s+)?\{',
            'arrow_functions': r'=>\s*[\{\(]',
            'const_let': r'(const|let)\s+\w+'
        }

    def scan_module(self, module_path):
        """Scan a single module for JavaScript files"""
        module_name = os.path.basename(module_path)
        
        # Check if it's a valid Odoo module
        if not os.path.exists(os.path.join(module_path, '__manifest__.py')):
            return None
            
        module_info = {
            'name': module_name,
            'path': module_path,
            'last_modified': datetime.fromtimestamp(os.path.getmtime(module_path)).isoformat(),
            'js_files': [],
            'issues': [],
            'modernization_score': 0,
            'total_lines': 0,
            'deprecated_lines': 0
        }
        
        # Find all JavaScript files
        for root, dirs, files in os.walk(module_path):
            for file in files:
                if file.endswith('.js'):
                    js_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(js_file_path, module_path)
                    file_info = self.analyze_js_file(js_file_path, relative_path)
                    if file_info:
                        module_info['js_files'].append(file_info)
                        module_info['issues'].extend(file_info['issues'])
                        module_info['total_lines'] += file_info['total_lines']
                        module_info['deprecated_lines'] += file_info['deprecated_lines']
        
        # Calculate modernization score
        if module_info['total_lines'] > 0:
            module_info['modernization_score'] = max(0, 100 - (
                (module_info['deprecated_lines'] / module_info['total_lines']) * 100
            ))
        
        self.modules_processed += 1
        return module_info

    def analyze_js_file(self, file_path, relative_path):
        """Analyze a single JavaScript file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            file_info = {
                'path': relative_path,
                'total_lines': len(content.splitlines()),
                'deprecated_lines': 0,
                'issues': [],
                'modern_patterns_found': [],
                'requires_update': False
            }
            
            lines = content.splitlines()
            
            # Check for deprecated patterns
            for pattern_name, pattern_info in self.deprecated_patterns.items():
                matches = re.finditer(pattern_info['pattern'], content, re.MULTILINE | re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issue = {
                        'type': pattern_name,
                        'severity': pattern_info['severity'],
                        'line': line_num,
                        'description': pattern_info['description'],
                        'replacement': pattern_info['replacement'],
                        'code_snippet': lines[line_num - 1].strip() if line_num <= len(lines) else ''
                    }
                    file_info['issues'].append(issue)
                    file_info['deprecated_lines'] += 1
                    self.issues_found += 1
            
            # Check for modern patterns
            for pattern_name, pattern in self.modern_patterns.items():
                if re.search(pattern, content, re.MULTILINE):
                    file_info['modern_patterns_found'].append(pattern_name)
            
            # Determine if file requires update
            file_info['requires_update'] = len(file_info['issues']) > 0
            
            self.files_processed += 1
            return file_info
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return None

    def generate_module_report(self, modules):
        """Generate comprehensive report"""
        print("\n" + "="*80)
        print("🔍 ODOO 17 JAVASCRIPT MODERNIZATION AUDIT REPORT")
        print("="*80)
        print(f"📅 Audit Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Modules Scanned: {len(modules)}")
        print(f"📄 JavaScript Files: {self.files_processed}")
        print(f"🐛 Total Issues Found: {self.issues_found}")
        
        # Sort modules by priority (most issues first, then by modification date)
        priority_modules = sorted(modules, 
                                key=lambda x: (len(x['issues']), x['last_modified']), 
                                reverse=True)
        
        print(f"\n📋 TOP PRIORITY MODULES (by issues & recency):")
        print("-" * 60)
        
        critical_modules = []
        for i, module in enumerate(priority_modules[:10]):
            if len(module['issues']) > 0:
                critical_count = sum(1 for issue in module['issues'] if issue['severity'] == 'CRITICAL')
                high_count = sum(1 for issue in module['issues'] if issue['severity'] == 'HIGH')
                
                status = "🚨 CRITICAL" if critical_count > 0 else "⚠️  HIGH" if high_count > 0 else "⚡ MEDIUM"
                score = f"{module['modernization_score']:.1f}%"
                
                print(f"{i+1:2d}. {module['name']:<30} {status} ({len(module['issues'])} issues, {score} modern)")
                
                if len(module['issues']) > 0:
                    critical_modules.append(module)
        
        # Detailed issue breakdown
        print(f"\n🔍 DETAILED ISSUE ANALYSIS:")
        print("-" * 60)
        
        issue_types = {}
        for module in modules:
            for issue in module['issues']:
                issue_type = issue['type']
                if issue_type not in issue_types:
                    issue_types[issue_type] = {'count': 0, 'severity': issue['severity']}
                issue_types[issue_type]['count'] += 1
        
        for issue_type, info in sorted(issue_types.items(), key=lambda x: x[1]['count'], reverse=True):
            pattern_info = self.deprecated_patterns[issue_type]
            print(f"• {pattern_info['description']:<40} {info['count']:3d} occurrences ({info['severity']})")
        
        return critical_modules

    def generate_modernization_plan(self, critical_modules):
        """Generate step-by-step modernization plan"""
        print(f"\n🚀 MODERNIZATION PLAN:")
        print("="*60)
        
        for i, module in enumerate(critical_modules[:5], 1):
            print(f"\n{i}. MODULE: {module['name']}")
            print(f"   📁 Path: {module['path']}")
            print(f"   📊 Modernization Score: {module['modernization_score']:.1f}%")
            print(f"   🐛 Total Issues: {len(module['issues'])}")
            
            # Group issues by severity
            critical_issues = [issue for issue in module['issues'] if issue['severity'] == 'CRITICAL']
            high_issues = [issue for issue in module['issues'] if issue['severity'] == 'HIGH']
            
            if critical_issues:
                print(f"   🚨 CRITICAL ({len(critical_issues)} issues):")
                for issue in critical_issues[:3]:  # Show top 3
                    print(f"      - {issue['description']} (Line {issue['line']})")
                    print(f"        Fix: {issue['replacement']}")
            
            if high_issues:
                print(f"   ⚠️  HIGH ({len(high_issues)} issues):")
                for issue in high_issues[:2]:  # Show top 2
                    print(f"      - {issue['description']} (Line {issue['line']})")
                    print(f"        Fix: {issue['replacement']}")

def main():
    """Main audit function"""
    auditor = Odoo17JSAuditor()
    
    print("🔍 Starting Odoo 17 JavaScript Module Audit...")
    print("Scanning workspace for modules...")
    
    # Get all directories that contain __manifest__.py
    modules = []
    workspace_dir = "."
    
    for item in os.listdir(workspace_dir):
        item_path = os.path.join(workspace_dir, item)
        if os.path.isdir(item_path):
            module_info = auditor.scan_module(item_path)
            if module_info and module_info['js_files']:  # Only include modules with JS files
                modules.append(module_info)
    
    if not modules:
        print("❌ No modules with JavaScript files found!")
        return 1
    
    # Generate report
    critical_modules = auditor.generate_module_report(modules)
    
    # Generate modernization plan
    if critical_modules:
        auditor.generate_modernization_plan(critical_modules)
        
        print(f"\n📋 NEXT STEPS:")
        print("1. 🔄 Start with CRITICAL severity issues")
        print("2. 📝 Update modules in priority order")
        print("3. 🧪 Test each module after modernization")
        print("4. 📊 Re-run audit to track progress")
        print("5. 🚀 Deploy to CloudPepper after validation")
    else:
        print("\n🎉 ALL MODULES ARE ALREADY MODERN!")
        print("✅ No JavaScript modernization required")
    
    # Save detailed report to JSON
    report_file = f"js_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump({
            'modules': modules,
            'summary': {
                'total_modules': len(modules),
                'total_files': auditor.files_processed,
                'total_issues': auditor.issues_found,
                'critical_modules': len(critical_modules)
            }
        }, f, indent=2)
    
    print(f"\n💾 Detailed report saved to: {report_file}")
    return 0

if __name__ == "__main__":
    exit(main())
