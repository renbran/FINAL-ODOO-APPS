#!/usr/bin/env python3
"""
Announcement Banner Module - Quick Diagnostic Tool
==================================================
This script checks if the announcement_banner module is properly set up
and can be installed/used in Odoo.

Run this from your OSUSAPPS directory:
    python3 announcement_banner/diagnostic.py
"""

import os
import sys
import json
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def check_file_exists(filepath, description):
    """Check if a file exists and report"""
    if os.path.isfile(filepath):
        print(f"  {Colors.GREEN}✓{Colors.END} {description}")
        return True
    else:
        print(f"  {Colors.RED}✗{Colors.END} {description} - NOT FOUND")
        return False

def check_python_syntax(filepath):
    """Check Python file for syntax errors"""
    import py_compile
    try:
        py_compile.compile(filepath, doraise=True)
        return True
    except:
        return False

def check_xml_validity(filepath):
    """Check XML file for validity"""
    try:
        import xml.etree.ElementTree as ET
        ET.parse(filepath)
        return True
    except Exception as e:
        print(f"    Error: {e}")
        return False

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}Announcement Banner Module - Diagnostic Report{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

    module_dir = Path(__file__).parent
    
    # Check 1: Module Directory Structure
    print(f"{Colors.BOLD}1. Module Directory Structure{Colors.END}")
    
    required_files = {
        '__init__.py': 'Main init file',
        '__manifest__.py': 'Module manifest',
        'models/__init__.py': 'Models init file',
        'models/announcement_banner.py': 'Main model file',
        'views/announcement_banner_views.xml': 'View definitions',
        'security/ir.model.access.csv': 'Access rights',
        'static/src/js/announcement_banner.js': 'JavaScript component',
        'static/src/xml/announcement_banner.xml': 'XML template',
        'static/src/css/announcement_banner.css': 'CSS stylesheet',
    }
    
    all_files_exist = True
    for filepath, description in required_files.items():
        full_path = module_dir / filepath
        if not check_file_exists(str(full_path), description):
            all_files_exist = False
    
    # Check 2: Python Syntax
    print(f"\n{Colors.BOLD}2. Python Syntax Check{Colors.END}")
    python_files = [
        '__init__.py',
        'models/__init__.py',
        'models/announcement_banner.py'
    ]
    
    syntax_ok = True
    for filepath in python_files:
        full_path = module_dir / filepath
        if os.path.isfile(full_path):
            if check_python_syntax(str(full_path)):
                print(f"  {Colors.GREEN}✓{Colors.END} {filepath} - Valid Python syntax")
            else:
                print(f"  {Colors.RED}✗{Colors.END} {filepath} - Syntax errors found")
                syntax_ok = False
    
    # Check 3: XML Validity
    print(f"\n{Colors.BOLD}3. XML Validity Check{Colors.END}")
    xml_files = [
        'views/announcement_banner_views.xml',
        'static/src/xml/announcement_banner.xml'
    ]
    
    xml_ok = True
    for filepath in xml_files:
        full_path = module_dir / filepath
        if os.path.isfile(full_path):
            if check_xml_validity(str(full_path)):
                print(f"  {Colors.GREEN}✓{Colors.END} {filepath} - Valid XML")
            else:
                print(f"  {Colors.RED}✗{Colors.END} {filepath} - XML errors found")
                xml_ok = False
    
    # Check 4: Manifest Configuration
    print(f"\n{Colors.BOLD}4. Manifest Configuration{Colors.END}")
    manifest_path = module_dir / '__manifest__.py'
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Basic checks
            checks = {
                "'name'": "Module name defined",
                "'version'": "Version specified",
                "'depends'": "Dependencies listed",
                "'data'": "Data files declared",
                "'assets'": "Assets configured",
                "web.assets_backend": "Backend assets bundle",
            }
            
            for key, description in checks.items():
                if key in content:
                    print(f"  {Colors.GREEN}✓{Colors.END} {description}")
                else:
                    print(f"  {Colors.YELLOW}⚠{Colors.END} {description} - Not found")
    except Exception as e:
        print(f"  {Colors.RED}✗{Colors.END} Error reading manifest: {e}")
    
    # Check 5: Security Configuration
    print(f"\n{Colors.BOLD}5. Security Configuration{Colors.END}")
    access_csv = module_dir / 'security' / 'ir.model.access.csv'
    if os.path.isfile(access_csv):
        with open(access_csv, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Check for required access rules
            models_found = []
            for line in lines[1:]:  # Skip header
                if 'announcement.banner' in line:
                    models_found.append('announcement.banner')
                if 'announcement.banner.log' in line:
                    models_found.append('announcement.banner.log')
            
            if 'announcement.banner' in models_found:
                print(f"  {Colors.GREEN}✓{Colors.END} Access rights for announcement.banner")
            else:
                print(f"  {Colors.RED}✗{Colors.END} Missing access rights for announcement.banner")
            
            if 'announcement.banner.log' in models_found:
                print(f"  {Colors.GREEN}✓{Colors.END} Access rights for announcement.banner.log")
            else:
                print(f"  {Colors.RED}✗{Colors.END} Missing access rights for announcement.banner.log")
    
    # Final Summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Diagnostic Summary{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    if all_files_exist and syntax_ok and xml_ok:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED!{Colors.END}")
        print(f"\n{Colors.GREEN}Your module is ready to install.{Colors.END}\n")
        print("Next steps:")
        print("1. Restart Odoo")
        print("2. Go to Apps → Update Apps List")
        print("3. Search for 'Announcement Banner'")
        print("4. Click Install")
        print("5. Make sure you're logged in as Administrator")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ ISSUES FOUND{Colors.END}")
        print(f"\n{Colors.YELLOW}Please fix the issues above before installing.{Colors.END}\n")
        
        if not all_files_exist:
            print("- Some required files are missing")
        if not syntax_ok:
            print("- Python syntax errors found")
        if not xml_ok:
            print("- XML validation errors found")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Diagnostic cancelled.{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error running diagnostic: {e}{Colors.END}\n")
        sys.exit(1)
