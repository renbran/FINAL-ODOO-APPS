#!/usr/bin/env python3
"""
OSUS Enhanced Workflow - Module Validation Script

This script validates the enhanced sales order workflow implementation
to ensure all components are properly configured and functional.
"""

import os
import sys
import xml.etree.ElementTree as ET
import json

def check_file_exists(filepath, description):
    """Check if a file exists and report status."""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (NOT FOUND)")
        return False

def validate_xml_file(filepath):
    """Validate XML file syntax."""
    try:
        ET.parse(filepath)
        print(f"✅ XML Valid: {filepath}")
        return True
    except ET.ParseError as e:
        print(f"❌ XML Invalid: {filepath} - {e}")
        return False

def validate_module_structure():
    """Validate the complete module structure."""
    print("🔍 OSUS Enhanced Workflow - Module Validation")
    print("=" * 60)
    
    base_path = "order_status_override"
    all_valid = True
    
    # Core module files
    core_files = [
        ("__manifest__.py", "Module manifest"),
        ("models/__init__.py", "Models init"),
        ("models/order_status.py", "Order status model"),
        ("models/sale_order.py", "Enhanced sale order model"),
    ]
    
    # Data files
    data_files = [
        ("data/order_status_data.xml", "Default status data"),
        ("data/email_templates.xml", "Email templates"),
    ]
    
    # View files
    view_files = [
        ("views/assets.xml", "Asset configuration"),
        ("views/order_status_views.xml", "Status management views"),
        ("views/order_views_enhanced.xml", "Enhanced order views"),
        ("views/commission_integration_views.xml", "Commission integration"),
        ("views/dashboard_views.xml", "Dashboard and analytics"),
    ]
    
    # Static assets
    static_files = [
        ("static/src/scss/osus_branding.scss", "OSUS branding styles"),
        ("static/src/scss/workflow_components.scss", "Workflow components"),
        ("static/src/scss/mobile_responsive.scss", "Mobile responsive styles"),
        ("static/src/js/workflow_manager.js", "Workflow manager component"),
        ("static/src/js/commission_calculator.js", "Commission calculator"),
    ]
    
    # Security files
    security_files = [
        ("security/security.xml", "Security groups"),
        ("security/ir.model.access.csv", "Access control"),
    ]
    
    all_files = core_files + data_files + view_files + static_files + security_files
    
    print("📁 File Structure Validation:")
    for filepath, description in all_files:
        full_path = os.path.join(base_path, filepath)
        if not check_file_exists(full_path, description):
            all_valid = False
    
    print("\n🔧 XML File Validation:")
    xml_files = [f for f, _ in data_files + view_files + security_files if f.endswith('.xml')]
    for xml_file in xml_files:
        full_path = os.path.join(base_path, xml_file)
        if os.path.exists(full_path):
            if not validate_xml_file(full_path):
                all_valid = False
    
    return all_valid

def validate_manifest():
    """Validate the module manifest configuration."""
    print("\n📋 Manifest Validation:")
    
    manifest_path = "order_status_override/__manifest__.py"
    if not os.path.exists(manifest_path):
        print("❌ Manifest file not found")
        return False
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required dependencies
        required_deps = ['sale', 'mail', 'commission_ax', 'account', 'web']
        for dep in required_deps:
            if f"'{dep}'" in content:
                print(f"✅ Dependency: {dep}")
            else:
                print(f"❌ Missing dependency: {dep}")
                return False
        
        # Check for asset configuration
        if "'web.assets_backend'" in content:
            print("✅ Backend assets configured")
        else:
            print("❌ Backend assets not configured")
            return False
        
        if "'web.assets_frontend'" in content:
            print("✅ Frontend assets configured")
        else:
            print("⚠️  Frontend assets not configured (optional)")
        
        print("✅ Manifest validation successful")
        return True
        
    except Exception as e:
        print(f"❌ Manifest validation failed: {e}")
        return False

def validate_scss_structure():
    """Validate SCSS file structure and OSUS branding."""
    print("\n🎨 SCSS Structure Validation:")
    
    scss_files = [
        "order_status_override/static/src/scss/osus_branding.scss",
        "order_status_override/static/src/scss/workflow_components.scss",
        "order_status_override/static/src/scss/mobile_responsive.scss",
    ]
    
    all_valid = True
    for scss_file in scss_files:
        if os.path.exists(scss_file):
            with open(scss_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for OSUS brand colors
            if '#800020' in content:  # Wine red
                print(f"✅ OSUS wine red color found in {os.path.basename(scss_file)}")
            else:
                print(f"⚠️  OSUS wine red color not found in {os.path.basename(scss_file)}")
            
            # Check for responsive breakpoints
            if '@media' in content or 'breakpoint' in content:
                print(f"✅ Responsive design found in {os.path.basename(scss_file)}")
            else:
                print(f"ℹ️  No responsive design in {os.path.basename(scss_file)}")
        else:
            print(f"❌ SCSS file not found: {scss_file}")
            all_valid = False
    
    return all_valid

def validate_javascript_components():
    """Validate JavaScript component structure."""
    print("\n⚡ JavaScript Component Validation:")
    
    js_files = [
        "order_status_override/static/src/js/workflow_manager.js",
        "order_status_override/static/src/js/commission_calculator.js",
    ]
    
    all_valid = True
    for js_file in js_files:
        if os.path.exists(js_file):
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for OWL framework usage
            if 'Component' in content or 'owl' in content.lower():
                print(f"✅ OWL framework detected in {os.path.basename(js_file)}")
            else:
                print(f"⚠️  OWL framework not detected in {os.path.basename(js_file)}")
            
            # Check for ES6+ features
            if 'class' in content or 'async' in content or '=>' in content:
                print(f"✅ Modern JavaScript (ES6+) in {os.path.basename(js_file)}")
            else:
                print(f"⚠️  Traditional JavaScript in {os.path.basename(js_file)}")
        else:
            print(f"❌ JavaScript file not found: {js_file}")
            all_valid = False
    
    return all_valid

def generate_validation_report():
    """Generate a comprehensive validation report."""
    print("\n📊 Validation Summary Report:")
    print("=" * 60)
    
    results = {
        'module_structure': validate_module_structure(),
        'manifest': validate_manifest(),
        'scss_structure': validate_scss_structure(),
        'javascript_components': validate_javascript_components(),
    }
    
    print(f"\n🏆 Overall Results:")
    total_checks = len(results)
    passed_checks = sum(results.values())
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {check.replace('_', ' ').title()}: {status}")
    
    print(f"\n📈 Success Rate: {passed_checks}/{total_checks} ({(passed_checks/total_checks)*100:.1f}%)")
    
    if passed_checks == total_checks:
        print("\n🎉 VALIDATION SUCCESSFUL!")
        print("The OSUS Enhanced Workflow module is ready for deployment.")
    else:
        print(f"\n⚠️  VALIDATION INCOMPLETE!")
        print(f"Please address the issues above before deployment.")
    
    return passed_checks == total_checks

if __name__ == "__main__":
    print("🚀 Starting OSUS Enhanced Workflow Validation...")
    success = generate_validation_report()
    sys.exit(0 if success else 1)
