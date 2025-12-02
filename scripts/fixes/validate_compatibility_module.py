#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation Script: crm_ai_field_compatibility Module
====================================================
Validates the emergency compatibility module before deployment.
"""

import os
import sys
import ast
import xml.etree.ElementTree as ET
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def log_success(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def log_error(msg):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")

def log_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")

def log_warn(msg):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")

def validate_module_structure(module_path):
    """Validate module directory structure"""
    print("\n" + "="*70)
    print("MODULE STRUCTURE VALIDATION")
    print("="*70)
    
    required_files = [
        '__init__.py',
        '__manifest__.py',
        'models/__init__.py',
        'models/crm_lead_compatibility.py',
        'views/crm_lead_views_compatibility.xml',
        'README.md'
    ]
    
    errors = []
    
    for file in required_files:
        file_path = module_path / file
        if file_path.exists():
            log_success(f"Found: {file}")
        else:
            log_error(f"Missing: {file}")
            errors.append(f"Missing required file: {file}")
    
    return errors

def validate_manifest(module_path):
    """Validate __manifest__.py"""
    print("\n" + "="*70)
    print("MANIFEST VALIDATION")
    print("="*70)
    
    errors = []
    manifest_path = module_path / '__manifest__.py'
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
            manifest = ast.literal_eval(content)
        
        # Check required keys
        required_keys = ['name', 'version', 'depends', 'data']
        for key in required_keys:
            if key in manifest:
                log_success(f"Manifest key '{key}': {manifest[key]}")
            else:
                log_error(f"Missing manifest key: {key}")
                errors.append(f"Missing manifest key: {key}")
        
        # Validate dependencies
        if 'crm' not in manifest.get('depends', []):
            log_error("Missing dependency: crm")
            errors.append("CRM module must be in depends")
        else:
            log_success("Dependency 'crm' found")
        
        # Validate version format
        version = manifest.get('version', '')
        if version.startswith('17.0.'):
            log_success(f"Valid Odoo 17 version: {version}")
        else:
            log_warn(f"Version may not be Odoo 17 compatible: {version}")
        
    except Exception as e:
        log_error(f"Failed to parse manifest: {str(e)}")
        errors.append(f"Manifest parsing error: {str(e)}")
    
    return errors

def validate_python_syntax(module_path):
    """Validate Python files syntax"""
    print("\n" + "="*70)
    print("PYTHON SYNTAX VALIDATION")
    print("="*70)
    
    errors = []
    
    python_files = list(module_path.rglob('*.py'))
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                ast.parse(content)
            log_success(f"Valid Python syntax: {py_file.name}")
        except SyntaxError as e:
            log_error(f"Syntax error in {py_file.name}: {str(e)}")
            errors.append(f"Python syntax error in {py_file.name}: {str(e)}")
    
    return errors

def validate_xml_syntax(module_path):
    """Validate XML files syntax"""
    print("\n" + "="*70)
    print("XML SYNTAX VALIDATION")
    print("="*70)
    
    errors = []
    
    xml_files = list(module_path.rglob('*.xml'))
    
    for xml_file in xml_files:
        try:
            ET.parse(xml_file)
            log_success(f"Valid XML syntax: {xml_file.name}")
        except ET.ParseError as e:
            log_error(f"XML parse error in {xml_file.name}: {str(e)}")
            errors.append(f"XML parse error in {xml_file.name}: {str(e)}")
    
    return errors

def validate_field_definition(module_path):
    """Validate ai_enrichment_report field definition"""
    print("\n" + "="*70)
    print("FIELD DEFINITION VALIDATION")
    print("="*70)
    
    errors = []
    
    model_file = module_path / 'models' / 'crm_lead_compatibility.py'
    
    try:
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for field definition
        if 'ai_enrichment_report' in content:
            log_success("Field 'ai_enrichment_report' defined")
        else:
            log_error("Field 'ai_enrichment_report' not found")
            errors.append("ai_enrichment_report field not defined")
        
        # Check for compute method
        if '_compute_ai_enrichment_report_compat' in content:
            log_success("Compute method '_compute_ai_enrichment_report_compat' found")
        else:
            log_warn("Compute method not found (may be optional)")
        
        # Check model inheritance
        if "_inherit = 'crm.lead'" in content:
            log_success("Model inherits from 'crm.lead'")
        else:
            log_error("Model does not inherit from 'crm.lead'")
            errors.append("CRM lead inheritance missing")
        
    except Exception as e:
        log_error(f"Failed to validate field definition: {str(e)}")
        errors.append(f"Field validation error: {str(e)}")
    
    return errors

def validate_odoo_17_compliance(module_path):
    """Validate Odoo 17 compliance"""
    print("\n" + "="*70)
    print("ODOO 17 COMPLIANCE CHECK")
    print("="*70)
    
    errors = []
    warnings = []
    
    # Check for deprecated syntax in XML
    xml_files = list(module_path.rglob('*.xml'))
    
    for xml_file in xml_files:
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for deprecated attrs=
            if 'attrs=' in content:
                warnings.append(f"Deprecated 'attrs=' found in {xml_file.name}")
                log_warn(f"Deprecated 'attrs=' found in {xml_file.name}")
            
            # Check for deprecated states=
            if 'states=' in content:
                warnings.append(f"Deprecated 'states=' found in {xml_file.name}")
                log_warn(f"Deprecated 'states=' found in {xml_file.name}")
            
        except Exception as e:
            errors.append(f"Failed to check {xml_file.name}: {str(e)}")
    
    if not warnings:
        log_success("No deprecated Odoo syntax found")
    
    return errors

def main():
    """Main validation function"""
    print("\n" + "="*70)
    print("CRM AI FIELD COMPATIBILITY MODULE VALIDATION")
    print("="*70)
    
    # Get module path
    module_name = 'crm_ai_field_compatibility'
    module_path = Path.cwd() / module_name
    
    if not module_path.exists():
        log_error(f"Module directory not found: {module_path}")
        log_info("Please run this script from FINAL-ODOO-APPS root directory")
        sys.exit(1)
    
    log_info(f"Validating module: {module_path}")
    
    # Run all validations
    all_errors = []
    
    all_errors.extend(validate_module_structure(module_path))
    all_errors.extend(validate_manifest(module_path))
    all_errors.extend(validate_python_syntax(module_path))
    all_errors.extend(validate_xml_syntax(module_path))
    all_errors.extend(validate_field_definition(module_path))
    all_errors.extend(validate_odoo_17_compliance(module_path))
    
    # Summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    if all_errors:
        log_error(f"Found {len(all_errors)} error(s):")
        for i, error in enumerate(all_errors, 1):
            print(f"  {i}. {error}")
        print("\n" + "="*70)
        log_error("❌ VALIDATION FAILED - DO NOT DEPLOY")
        print("="*70)
        sys.exit(1)
    else:
        print("\n" + "="*70)
        log_success("✅ ALL VALIDATIONS PASSED")
        log_success("✅ MODULE IS READY FOR DEPLOYMENT")
        print("="*70)
        print("\nNext steps:")
        print("1. Run deployment script: ./deploy_emergency_ai_fix.sh")
        print("2. Or manually deploy to CloudPepper")
        print("3. Monitor logs after deployment")
        sys.exit(0)

if __name__ == '__main__':
    main()
