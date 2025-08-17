#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple JavaScript Modernization Audit for Odoo 17
Unicode-safe version for Windows PowerShell
"""

import os
import re
import json
import sys

def find_modules_with_js():
    """Find all modules that contain JavaScript files"""
    modules = []
    
    for item in os.listdir("."):
        item_path = os.path.join(".", item)
        if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "__manifest__.py")):
            # Look for JS files in static directories
            js_files = []
            static_path = os.path.join(item_path, "static")
            if os.path.exists(static_path):
                for root, dirs, files in os.walk(static_path):
                    for file in files:
                        if file.endswith('.js'):
                            js_files.append(os.path.join(root, file))
            
            if js_files:
                modules.append({
                    'name': item,
                    'path': item_path,
                    'js_files': js_files
                })
    
    return modules

def count_issues_in_file(file_path):
    """Count deprecated JavaScript patterns in a file"""
    issues = {
        'jquery_usage': 0,
        'legacy_require': 0,
        'legacy_extend': 0,
        'legacy_define': 0
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Count jQuery usage
            issues['jquery_usage'] = len(re.findall(r'\$\(|\$\.', content))
            
            # Count legacy require syntax
            issues['legacy_require'] = len(re.findall(r'require\s*\(', content))
            
            # Count legacy extend patterns
            issues['legacy_extend'] = len(re.findall(r'\.extend\s*\(', content))
            
            # Count legacy define patterns
            issues['legacy_define'] = len(re.findall(r'odoo\.define\s*\(', content))
            
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
    
    return issues

def main():
    """Main function"""
    print("JavaScript Modernization Audit")
    print("=" * 50)
    
    modules = find_modules_with_js()
    
    if not modules:
        print("No modules with JavaScript files found.")
        return
    
    print(f"Found {len(modules)} modules with JavaScript files")
    print()
    
    module_results = []
    
    for module in modules:
        total_issues = 0
        module_issues = {
            'jquery_usage': 0,
            'legacy_require': 0,
            'legacy_extend': 0,
            'legacy_define': 0
        }
        
        for js_file in module['js_files']:
            file_issues = count_issues_in_file(js_file)
            for key, value in file_issues.items():
                module_issues[key] += value
                total_issues += value
        
        module_results.append({
            'name': module['name'],
            'total_issues': total_issues,
            'js_files': len(module['js_files']),
            'issues': module_issues
        })
    
    # Sort by total issues descending
    module_results.sort(key=lambda x: x['total_issues'], reverse=True)
    
    print("Top 10 Modules by Issue Count:")
    print("-" * 50)
    
    for i, module in enumerate(module_results[:10], 1):
        print(f"{i}. {module['name']}")
        print(f"   Total Issues: {module['total_issues']}")
        print(f"   JS Files: {module['js_files']}")
        if module['issues']['jquery_usage'] > 0:
            print(f"   jQuery usage: {module['issues']['jquery_usage']}")
        if module['issues']['legacy_require'] > 0:
            print(f"   Legacy require: {module['issues']['legacy_require']}")
        if module['issues']['legacy_extend'] > 0:
            print(f"   Legacy extend: {module['issues']['legacy_extend']}")
        if module['issues']['legacy_define'] > 0:
            print(f"   Legacy define: {module['issues']['legacy_define']}")
        print()
    
    # Summary
    total_js_files = sum(m['js_files'] for m in module_results)
    total_issues = sum(m['total_issues'] for m in module_results)
    
    print("Summary:")
    print(f"Total modules with JS: {len(module_results)}")
    print(f"Total JS files: {total_js_files}")
    print(f"Total issues: {total_issues}")

if __name__ == "__main__":
    main()
