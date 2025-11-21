#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Module Validation Script for announcement_banner
Checks all critical components for production readiness
"""

import os
import sys
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"{Colors.GREEN}✓{Colors.END} {description}: {filepath}")
        return True
    else:
        print(f"{Colors.RED}✗{Colors.END} {description} MISSING: {filepath}")
        return False

def check_file_content(filepath, required_strings, description):
    """Check if file contains required strings"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        missing = []
        for req_str in required_strings:
            if req_str not in content:
                missing.append(req_str)
        
        if not missing:
            print(f"{Colors.GREEN}✓{Colors.END} {description}: All checks passed")
            return True
        else:
            print(f"{Colors.RED}✗{Colors.END} {description}: Missing content:")
            for m in missing:
                print(f"  - {m}")
            return False
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.END} {description}: Error reading file - {e}")
        return False

def main():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Announcement Banner Module Validation{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    module_path = Path(__file__).parent
    results = []
    
    # Check 1: Module structure files
    print(f"\n{Colors.YELLOW}[1] Checking Module Structure...{Colors.END}")
    structure_files = [
        ('__init__.py', 'Root __init__.py'),
        ('__manifest__.py', 'Manifest file'),
        ('models/__init__.py', 'Models __init__.py'),
        ('models/announcement_banner.py', 'Main model file'),
        ('views/announcement_banner_views.xml', 'Views XML'),
        ('security/ir.model.access.csv', 'Access rights CSV'),
        ('static/src/js/announcement_banner.js', 'JavaScript component'),
        ('static/src/xml/announcement_banner.xml', 'OWL template'),
        ('static/src/css/announcement_banner.css', 'CSS styles'),
        ('static/description/icon.png', 'Module icon'),
        ('README.md', 'Documentation'),
    ]
    
    for file, desc in structure_files:
        results.append(check_file_exists(module_path / file, desc))
    
    # Check 2: __manifest__.py content
    print(f"\n{Colors.YELLOW}[2] Validating __manifest__.py...{Colors.END}")
    manifest_checks = [
        "'name':",
        "'version': '17.0.1.1.0'",
        "'depends': ['web', 'base']",
        "'installable': True",
        "web.assets_backend",
        "announcement_banner/static/src/js/announcement_banner.js",
        "announcement_banner/static/src/xml/announcement_banner.xml",
        "announcement_banner/static/src/css/announcement_banner.css",
    ]
    results.append(check_file_content(
        module_path / '__manifest__.py',
        manifest_checks,
        'Manifest configuration'
    ))
    
    # Check 3: Model file
    print(f"\n{Colors.YELLOW}[3] Validating Model...{Colors.END}")
    model_checks = [
        "class AnnouncementBanner(models.Model):",
        "_name = 'announcement.banner'",
        "def get_active_announcements(self):",
        "def mark_as_shown(self, announcement_id):",
        "class AnnouncementBannerLog(models.Model):",
        "_name = 'announcement.banner.log'",
    ]
    results.append(check_file_content(
        module_path / 'models' / 'announcement_banner.py',
        model_checks,
        'Model definitions'
    ))
    
    # Check 4: JavaScript OWL component
    print(f"\n{Colors.YELLOW}[4] Validating JavaScript OWL Component...{Colors.END}")
    js_checks = [
        "/** @odoo-module **/",
        "from \"@odoo/owl\"",
        "export class AnnouncementBanner extends Component",
        "static template = \"announcement_banner.AnnouncementBanner\"",
        "get_active_announcements",
        "mark_as_shown",
        'registry.category("main_components").add',
    ]
    results.append(check_file_content(
        module_path / 'static' / 'src' / 'js' / 'announcement_banner.js',
        js_checks,
        'JavaScript OWL component'
    ))
    
    # Check 5: XML template
    print(f"\n{Colors.YELLOW}[5] Validating OWL Template...{Colors.END}")
    xml_checks = [
        '<t t-name="announcement_banner.AnnouncementBanner">',
        't-if="state.showBanner',
        't-raw="currentAnnouncement.message"',
        'announcement-banner-overlay',
        'announcement-banner-modal',
    ]
    results.append(check_file_content(
        module_path / 'static' / 'src' / 'xml' / 'announcement_banner.xml',
        xml_checks,
        'OWL template'
    ))
    
    # Check 6: CSS styles
    print(f"\n{Colors.YELLOW}[6] Validating CSS Styles...{Colors.END}")
    css_checks = [
        '.announcement-banner-overlay',
        '.announcement-banner-modal',
        '.announcement-content',
        'word-break: normal',
        '.announcement-content img',
        'OSUSAPPS',
        '@media (max-width:',
    ]
    results.append(check_file_content(
        module_path / 'static' / 'src' / 'css' / 'announcement_banner.css',
        css_checks,
        'CSS styles'
    ))
    
    # Check 7: Security access rights
    print(f"\n{Colors.YELLOW}[7] Validating Security Access Rights...{Colors.END}")
    security_checks = [
        'access_announcement_banner_user',
        'access_announcement_banner_manager',
        'access_announcement_banner_log_user',
        'access_announcement_banner_log_manager',
        'model_announcement_banner',
        'model_announcement_banner_log',
    ]
    results.append(check_file_content(
        module_path / 'security' / 'ir.model.access.csv',
        security_checks,
        'Security access rights'
    ))
    
    # Check 8: Views XML
    print(f"\n{Colors.YELLOW}[8] Validating Views XML...{Colors.END}")
    views_checks = [
        '<record id="view_announcement_banner_form"',
        '<record id="view_announcement_banner_tree"',
        '<record id="view_announcement_banner_search"',
        '<record id="action_announcement_banner"',
        '<menuitem id="menu_announcement_banner_root"',
        'widget="html"',
    ]
    results.append(check_file_content(
        module_path / 'views' / 'announcement_banner_views.xml',
        views_checks,
        'Views XML'
    ))
    
    # Check 9: Model imports
    print(f"\n{Colors.YELLOW}[9] Validating Python Imports...{Colors.END}")
    root_init_checks = ['from . import models']
    results.append(check_file_content(
        module_path / '__init__.py',
        root_init_checks,
        'Root __init__.py imports'
    ))
    
    models_init_checks = ['from . import announcement_banner']
    results.append(check_file_content(
        module_path / 'models' / '__init__.py',
        models_init_checks,
        'Models __init__.py imports'
    ))
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Validation Summary{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"Total Checks: {total}")
    print(f"Passed: {Colors.GREEN}{passed}{Colors.END}")
    print(f"Failed: {Colors.RED}{total - passed}{Colors.END}")
    print(f"Success Rate: {percentage:.1f}%\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{'='*60}{Colors.END}")
        print(f"{Colors.GREEN}✓ MODULE IS PRODUCTION READY!{Colors.END}")
        print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.RED}{'='*60}{Colors.END}")
        print(f"{Colors.RED}✗ MODULE HAS ISSUES - PLEASE FIX BEFORE DEPLOYMENT{Colors.END}")
        print(f"{Colors.RED}{'='*60}{Colors.END}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
