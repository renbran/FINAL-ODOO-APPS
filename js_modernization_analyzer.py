#!/usr/bin/env python3
"""
JavaScript Modernization Script for Odoo 17
Identifies and flags legacy JavaScript patterns for modernization

Usage: python js_modernization_analyzer.py
"""

import os
import re
from pathlib import Path
import json

class JSModernizationAnalyzer:
    def __init__(self, root_path="."):
        self.root_path = Path(root_path)
        self.issues = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
    def scan_files(self):
        """Scan all JavaScript files for legacy patterns"""
        js_files = list(self.root_path.glob("**/static/src/js/**/*.js"))
        
        print(f"🔍 Scanning {len(js_files)} JavaScript files...")
        
        for js_file in js_files:
            # Skip library files
            if any(lib in str(js_file) for lib in ['lib/', 'libs/', 'vendor/', '.min.js']):
                continue
                
            issues = self.analyze_file(js_file)
            if issues:
                self.categorize_issues(js_file, issues)
        
        return self.generate_report()
    
    def analyze_file(self, file_path):
        """Analyze a single JavaScript file for legacy patterns"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return []
        
        issues = []
        lines = content.split('\n')
        
        # Check for legacy patterns
        patterns = {
            'var_self_this': {
                'pattern': r'var\s+self\s*=\s*this',
                'severity': 'high',
                'description': 'Legacy context binding pattern'
            },
            'function_callbacks': {
                'pattern': r'\.then\(function\s*\(',
                'severity': 'medium', 
                'description': 'Legacy promise callback pattern'
            },
            'missing_module_declaration': {
                'pattern': r'\/\*\*\s*@odoo-module\s*\*\*\/',
                'severity': 'critical',
                'description': 'Missing modern module declaration',
                'inverse': True  # Check if pattern is NOT found
            },
            'jquery_usage': {
                'pattern': r'\$\(|jQuery',
                'severity': 'low',
                'description': 'Potential jQuery dependency'
            },
            'old_define_syntax': {
                'pattern': r'odoo\.define\s*\(',
                'severity': 'critical',
                'description': 'Legacy odoo.define syntax'
            },
            'var_declarations': {
                'pattern': r'^\s*var\s+\w+',
                'severity': 'low',
                'description': 'Legacy var declarations (should use let/const)'
            }
        }
        
        for line_num, line in enumerate(lines, 1):
            for pattern_name, pattern_info in patterns.items():
                if pattern_info.get('inverse'):
                    # For patterns that should exist (like module declaration)
                    if pattern_name == 'missing_module_declaration' and line_num == 1:
                        if not re.search(pattern_info['pattern'], content):
                            issues.append({
                                'type': pattern_name,
                                'line': 1,
                                'content': '(Missing @odoo-module declaration)',
                                'severity': pattern_info['severity'],
                                'description': pattern_info['description']
                            })
                else:
                    if re.search(pattern_info['pattern'], line):
                        issues.append({
                            'type': pattern_name,
                            'line': line_num,
                            'content': line.strip(),
                            'severity': pattern_info['severity'],
                            'description': pattern_info['description']
                        })
        
        return issues
    
    def categorize_issues(self, file_path, issues):
        """Categorize issues by severity"""
        file_info = {
            'file': str(file_path.relative_to(self.root_path)),
            'issues': issues,
            'total_issues': len(issues),
            'severity_counts': {}
        }
        
        # Count issues by severity
        for issue in issues:
            severity = issue['severity']
            file_info['severity_counts'][severity] = file_info['severity_counts'].get(severity, 0) + 1
        
        # Determine overall file priority
        if any(issue['severity'] == 'critical' for issue in issues):
            priority = 'critical'
        elif len([i for i in issues if i['severity'] == 'high']) >= 3:
            priority = 'critical'  # Multiple high-severity issues
        elif any(issue['severity'] == 'high' for issue in issues):
            priority = 'high'
        elif len(issues) >= 5:
            priority = 'medium'  # Many issues
        else:
            priority = 'medium' if issues else 'low'
        
        self.issues[priority].append(file_info)
    
    def generate_report(self):
        """Generate modernization report"""
        report = {
            'summary': {
                'total_files_scanned': sum(len(files) for files in self.issues.values()),
                'files_needing_attention': sum(len(files) for files in self.issues.values() if files),
                'critical_files': len(self.issues['critical']),
                'high_priority_files': len(self.issues['high']),
                'medium_priority_files': len(self.issues['medium']),
                'low_priority_files': len(self.issues['low'])
            },
            'files_by_priority': self.issues
        }
        
        return report
    
    def print_report(self, report):
        """Print formatted report to console"""
        print("\n" + "="*60)
        print("🚀 JAVASCRIPT MODERNIZATION ANALYSIS REPORT")
        print("="*60)
        
        summary = report['summary']
        print(f"\n📊 SUMMARY:")
        print(f"   Total files analyzed: {summary['total_files_scanned']}")
        print(f"   Files needing attention: {summary['files_needing_attention']}")
        print(f"   🔴 Critical priority: {summary['critical_files']}")
        print(f"   🟠 High priority: {summary['high_priority_files']}")
        print(f"   🟡 Medium priority: {summary['medium_priority_files']}")
        print(f"   🟢 Low priority: {summary['low_priority_files']}")
        
        # Print files by priority
        priority_colors = {
            'critical': '🔴',
            'high': '🟠', 
            'medium': '🟡',
            'low': '🟢'
        }
        
        for priority in ['critical', 'high', 'medium', 'low']:
            files = self.issues[priority]
            if files:
                print(f"\n{priority_colors[priority]} {priority.upper()} PRIORITY FILES:")
                for file_info in files[:5]:  # Show top 5 files per category
                    print(f"   📁 {file_info['file']}")
                    print(f"      Issues: {file_info['total_issues']} ({file_info['severity_counts']})")
                    
                    # Show top 3 issues
                    for issue in file_info['issues'][:3]:
                        print(f"      - Line {issue['line']}: {issue['description']}")
                    
                    if len(file_info['issues']) > 3:
                        print(f"      ... and {len(file_info['issues']) - 3} more issues")
                    print()
                
                if len(files) > 5:
                    print(f"   ... and {len(files) - 5} more files")
        
        print("\n🛠  NEXT STEPS:")
        print("1. Start with CRITICAL priority files")
        print("2. Back up files before modification") 
        print("3. Modernize one file at a time")
        print("4. Test with CloudPepper after each file")
        print("5. Run: python cloudpepper_deployment_final_validation.py")
        
    def save_report(self, report, filename="js_modernization_report.json"):
        """Save detailed report to JSON file"""
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 Detailed report saved to: {filename}")

def main():
    analyzer = JSModernizationAnalyzer()
    report = analyzer.scan_files()
    analyzer.print_report(report)
    analyzer.save_report(report)
    
    # Create flagged files list
    flagged_files = []
    for priority, files in analyzer.issues.items():
        for file_info in files:
            flagged_files.append({
                'file': file_info['file'],
                'priority': priority,
                'issues': file_info['total_issues']
            })
    
    # Sort by priority and issue count
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    flagged_files.sort(key=lambda x: (priority_order[x['priority']], -x['issues']))
    
    print(f"\n🏁 FLAGGED FILES FOR MODERNIZATION ({len(flagged_files)} files):")
    for i, file_info in enumerate(flagged_files[:10], 1):
        priority_icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[file_info['priority']]
        print(f"{i:2}. {priority_icon} {file_info['file']} ({file_info['issues']} issues)")
    
    if len(flagged_files) > 10:
        print(f"    ... and {len(flagged_files) - 10} more files")

if __name__ == "__main__":
    main()
