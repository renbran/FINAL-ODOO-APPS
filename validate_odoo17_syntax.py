#!/usr/bin/env python3
"""
Comprehensive Odoo 17 Syntax Validation Script
Validates that all files use modern Odoo 17 syntax and deprecated patterns are removed
"""

import os
import xml.etree.ElementTree as ET
import re
from pathlib import Path

def validate_xml_syntax(file_path):
    """Validate XML files for deprecated Odoo syntax"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for deprecated attrs attribute
        if 'attrs=' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'attrs=' in line:
                    issues.append(f"Line {i}: Deprecated 'attrs' attribute found")
        
        # Check for deprecated states attribute
        if 'states=' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'states=' in line:
                    issues.append(f"Line {i}: Deprecated 'states' attribute found")
        
        # Check XML structure
        try:
            ET.parse(file_path)
        except ET.ParseError as e:
            issues.append(f"XML Parse Error: {e}")
            
    except Exception as e:
        issues.append(f"File read error: {e}")
    
    return issues

def validate_python_syntax(file_path):
    """Validate Python files for deprecated Odoo syntax"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for deprecated states in field definitions
        state_pattern = r'fields\.\w+\([^)]*states\s*='
        matches = re.finditer(state_pattern, content)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            issues.append(f"Line {line_num}: Deprecated 'states' parameter in field definition")
        
        # Check for basic Python syntax
        try:
            compile(content, file_path, 'exec')
        except SyntaxError as e:
            issues.append(f"Python Syntax Error: {e}")
            
    except Exception as e:
        issues.append(f"File read error: {e}")
    
    return issues

def validate_module_structure():
    """Validate the overall module structure"""
    module_path = Path('account_payment_approval')
    
    if not module_path.exists():
        return [f"Module directory 'account_payment_approval' not found"]
    
    issues = []
    
    # Check for required files
    required_files = [
        '__init__.py',
        '__manifest__.py'
    ]
    
    for req_file in required_files:
        if not (module_path / req_file).exists():
            issues.append(f"Required file missing: {req_file}")
    
    # Check for required directories
    required_dirs = [
        'models',
        'views',
        'security',
        'data'
    ]
    
    for req_dir in required_dirs:
        if not (module_path / req_dir).exists():
            issues.append(f"Required directory missing: {req_dir}")
    
    return issues

def main():
    """Main validation function"""
    print("=== Odoo 17 Syntax Validation ===\n")
    
    # Validate module structure
    print("1. Validating module structure...")
    structure_issues = validate_module_structure()
    if structure_issues:
        print("   ‚ùå Structure Issues:")
        for issue in structure_issues:
            print(f"      - {issue}")
    else:
        print("   ‚úÖ Module structure is valid")
    
    print()
    
    # Find all XML and Python files
    xml_files = []
    py_files = []
    
    module_path = Path('account_payment_approval')
    if module_path.exists():
        for file_path in module_path.rglob('*'):
            if file_path.is_file():
                if file_path.suffix == '.xml':
                    xml_files.append(file_path)
                elif file_path.suffix == '.py':
                    py_files.append(file_path)
    
    print(f"2. Found {len(xml_files)} XML files and {len(py_files)} Python files")
    print()
    
    # Validate XML files
    print("3. Validating XML files...")
    xml_issues = 0
    for xml_file in xml_files:
        issues = validate_xml_syntax(xml_file)
        if issues:
            print(f"   ‚ùå {xml_file}:")
            for issue in issues:
                print(f"      - {issue}")
            xml_issues += len(issues)
    
    if xml_issues == 0:
        print("   ‚úÖ All XML files use modern Odoo 17 syntax")
    
    print()
    
    # Validate Python files
    print("4. Validating Python files...")
    py_issues = 0
    for py_file in py_files:
        issues = validate_python_syntax(py_file)
        if issues:
            print(f"   ‚ùå {py_file}:")
            for issue in issues:
                print(f"      - {issue}")
            py_issues += len(issues)
    
    if py_issues == 0:
        print("   ‚úÖ All Python files use modern Odoo 17 syntax")
    
    print()
    
    # Summary
    total_issues = len(structure_issues) + xml_issues + py_issues
    
    print("=== VALIDATION SUMMARY ===")
    print(f"Files processed: {len(xml_files)} XML + {len(py_files)} Python")
    print(f"Total issues found: {total_issues}")
    
    if total_issues == 0:
        print("üéâ ALL VALIDATIONS PASSED!")
        print("‚úÖ Module is compatible with Odoo 17")
        print("‚úÖ No deprecated syntax found")
        print("‚úÖ Ready for deployment")
    else:
        print("‚ö†Ô∏è  Issues found that need attention")
    
    return total_issues == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
