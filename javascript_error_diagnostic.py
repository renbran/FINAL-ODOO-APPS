#!/usr/bin/env python3
"""
JavaScript Error Diagnostic Tool
Identifies and resolves JavaScript loading and execution issues
"""

import os
import ast
import re
import sys

def analyze_javascript_files():
    """Analyze JavaScript files for potential issues."""
    print("🔍 JAVASCRIPT ERROR DIAGNOSTIC")
    print("=" * 60)
    
    js_files = []
    static_path = "order_status_override/static/src/js"
    
    if os.path.exists(static_path):
        for file in os.listdir(static_path):
            if file.endswith('.js'):
                js_files.append(os.path.join(static_path, file))
    
    print(f"📁 Found {len(js_files)} JavaScript files")
    
    issues_found = []
    
    for js_file in js_files:
        print(f"\n🔍 Analyzing: {os.path.basename(js_file)}")
        
        try:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for common issues
            analysis_results = []
            
            # Check for MutationObserver usage
            if 'MutationObserver' in content:
                if 'observe(' in content:
                    if 'typeof MutationObserver' not in content and 'targetNode &&' not in content:
                        analysis_results.append("⚠️ Unsafe MutationObserver usage")
                    else:
                        analysis_results.append("✅ Safe MutationObserver usage")
                else:
                    analysis_results.append("✅ MutationObserver declared but not used")
            else:
                analysis_results.append("✅ No MutationObserver")
            
            # Check for DOM queries
            dom_queries = re.findall(r'document\.querySelector[All]*\(["\']([^"\']+)["\']', content)
            if dom_queries:
                analysis_results.append(f"📊 DOM queries: {len(dom_queries)} selectors")
                # Check for unsafe DOM access
                if 'document.querySelector' in content and 'if (' not in content:
                    analysis_results.append("⚠️ Potential unsafe DOM access")
            
            # Check for OWL imports
            if 'import {' in content and '@odoo/owl' in content:
                analysis_results.append("✅ Proper OWL imports")
            elif 'import {' in content:
                analysis_results.append("✅ ES6 imports used")
            
            # Check for module declaration
            if '/** @odoo-module **/' in content:
                analysis_results.append("✅ Proper Odoo module declaration")
            else:
                analysis_results.append("⚠️ Missing @odoo-module declaration")
            
            # Check file size
            file_size = len(content)
            if file_size > 10000:
                analysis_results.append(f"📊 Large file: {file_size} bytes")
            else:
                analysis_results.append(f"📊 File size: {file_size} bytes")
            
            # Print results
            for result in analysis_results:
                print(f"  {result}")
            
            # Check for syntax issues
            if 'addEventListener(' in content and 'removeEventListener(' not in content:
                analysis_results.append("⚠️ Event listeners added but not removed")
            
            if any("⚠️" in result for result in analysis_results):
                issues_found.append((js_file, analysis_results))
                
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
            issues_found.append((js_file, [f"❌ Read error: {e}"]))
    
    return issues_found

def check_manifest_assets():
    """Check manifest asset references."""
    print(f"\n📋 MANIFEST ASSET VALIDATION")
    print("=" * 40)
    
    try:
        with open('order_status_override/__manifest__.py', 'r') as f:
            manifest = ast.literal_eval(f.read())
        
        assets = manifest.get('assets', {})
        all_files_exist = True
        
        for bundle_name, file_list in assets.items():
            print(f"\n{bundle_name}:")
            for file_path in file_list:
                if os.path.exists(file_path):
                    print(f"  ✅ {os.path.basename(file_path)}")
                else:
                    print(f"  ❌ {file_path} - MISSING")
                    all_files_exist = False
        
        return all_files_exist
        
    except Exception as e:
        print(f"❌ Manifest error: {e}")
        return False

def create_minimal_safe_assets():
    """Create minimal, safe JavaScript files."""
    print(f"\n🔧 CREATING MINIMAL SAFE ASSETS")
    print("=" * 50)
    
    # Create minimal workflow manager
    minimal_workflow = '''/** @odoo-module **/

// Minimal OSUS Workflow Manager - Safe Version
console.log('OSUS Workflow Manager: Loaded (minimal safe version)');

// Export minimal functionality
window.osusWorkflow = {
    version: '17.0.2.0.0',
    status: 'minimal',
    initialized: true
};
'''
    
    # Create minimal commission calculator
    minimal_commission = '''/** @odoo-module **/

// Minimal OSUS Commission Calculator - Safe Version
console.log('OSUS Commission Calculator: Loaded (minimal safe version)');

// Export minimal functionality
window.osusCommission = {
    version: '17.0.2.0.0',
    status: 'minimal',
    initialized: true
};
'''
    
    # Create minimal dashboard
    minimal_dashboard = '''/** @odoo-module **/

// Minimal OSUS Dashboard - Safe Version
console.log('OSUS Dashboard: Loaded (minimal safe version)');

// Export minimal functionality
window.osusDashboard = {
    version: '17.0.2.0.0',
    status: 'minimal',
    initialized: true
};
'''
    
    files_to_create = [
        ('order_status_override/static/src/js/workflow_manager_minimal.js', minimal_workflow),
        ('order_status_override/static/src/js/commission_calculator_minimal.js', minimal_commission),
        ('order_status_override/static/src/js/status_dashboard_minimal.js', minimal_dashboard),
    ]
    
    for file_path, content in files_to_create:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Created: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"  ❌ Failed to create {file_path}: {e}")

def main():
    """Main diagnostic function."""
    print("🚨 JAVASCRIPT ERROR RESOLUTION DIAGNOSTIC")
    print("=" * 80)
    
    # Analyze current JavaScript files
    js_issues = analyze_javascript_files()
    
    # Check manifest assets
    assets_valid = check_manifest_assets()
    
    # Summary
    print(f"\n" + "="*80)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 30)
    
    if js_issues:
        print(f"⚠️ JavaScript issues found in {len(js_issues)} files:")
        for file_path, issues in js_issues:
            print(f"  📄 {os.path.basename(file_path)}:")
            for issue in issues:
                if "⚠️" in issue or "❌" in issue:
                    print(f"    {issue}")
    else:
        print("✅ No JavaScript issues detected")
    
    if assets_valid:
        print("✅ All manifest assets exist")
    else:
        print("❌ Some manifest assets are missing")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if js_issues or not assets_valid:
        print("1. Create minimal safe JavaScript versions")
        print("2. Remove complex DOM manipulation")
        print("3. Use CloudPepper's built-in JavaScript framework")
        create_minimal_safe_assets()
    else:
        print("1. Files appear correct - issue may be server-side")
        print("2. Clear CloudPepper cache and restart Odoo")
        print("3. Check CloudPepper error logs")
    
    return 0 if (not js_issues and assets_valid) else 1

if __name__ == "__main__":
    sys.exit(main())
