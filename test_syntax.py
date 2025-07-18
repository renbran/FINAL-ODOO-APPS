#!/usr/bin/env python3
# Quick syntax test for custom_sales module

import ast
import os

def test_python_syntax(filepath):
    """Test if a Python file has valid syntax"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the AST to check syntax
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error reading file: {e}"

def test_xml_syntax(filepath):
    """Test if an XML file is well-formed"""
    try:
        import xml.etree.ElementTree as ET
        ET.parse(filepath)
        return True, None
    except ET.ParseError as e:
        return False, f"XML parse error: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"

# Test Python files
python_files = [
    'custom_sales/controllers/dashboard_controller.py',
    'custom_sales/models/performance_optimizer.py',
    'custom_sales/models/audit_log.py',
    'custom_sales/models/pagination_helper.py',
    'custom_sales/models/chart_config.py',
    'custom_sales/models/kpi_calculator.py',
]

# Test XML files
xml_files = [
    'custom_sales/views/dashboard_error_templates.xml',
    'custom_sales/data/cron_jobs.xml',
]

print("🧪 Testing Custom Sales Module Syntax...")
print("=" * 50)

errors_found = False

# Test Python files
print("\n📝 Testing Python Files:")
for py_file in python_files:
    if os.path.exists(py_file):
        success, error = test_python_syntax(py_file)
        if success:
            print(f"✅ {py_file}")
        else:
            print(f"❌ {py_file}: {error}")
            errors_found = True
    else:
        print(f"⚠️  {py_file}: File not found")

# Test XML files
print("\n📄 Testing XML Files:")
for xml_file in xml_files:
    if os.path.exists(xml_file):
        success, error = test_xml_syntax(xml_file)
        if success:
            print(f"✅ {xml_file}")
        else:
            print(f"❌ {xml_file}: {error}")
            errors_found = True
    else:
        print(f"⚠️  {xml_file}: File not found")

# Test manifest
print("\n📋 Testing Manifest:")
if os.path.exists('custom_sales/__manifest__.py'):
    success, error = test_python_syntax('custom_sales/__manifest__.py')
    if success:
        print("✅ custom_sales/__manifest__.py")
    else:
        print(f"❌ custom_sales/__manifest__.py: {error}")
        errors_found = True
else:
    print("⚠️  custom_sales/__manifest__.py: File not found")

print("\n" + "=" * 50)
if errors_found:
    print("❌ ERRORS FOUND - Fix before deployment!")
    exit(1)
else:
    print("✅ ALL SYNTAX TESTS PASSED - Ready for deployment!")
    exit(0)
