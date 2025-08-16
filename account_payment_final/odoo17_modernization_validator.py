#!/usr/bin/env python3
"""
Odoo 17 JavaScript Modernization Validator
Comprehensive validation for account_payment_final module
"""

import os
import re
import json
import subprocess
from pathlib import Path

class Odoo17ModernizationValidator:
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.results = {
            'module_structure': {},
            'javascript_analysis': {},
            'manifest_validation': {},
            'template_validation': {},
            'service_validation': {},
            'error_count': 0,
            'warning_count': 0,
            'success_count': 0
        }
    
    def validate_all(self):
        """Run comprehensive validation"""
        print("🔍 Starting Odoo 17 JavaScript Modernization Validation")
        print("=" * 60)
        
        self.validate_module_structure()
        self.validate_javascript_files()
        self.validate_manifest()
        self.validate_templates()
        self.validate_services()
        self.generate_report()
        
        return self.results
    
    def validate_module_structure(self):
        """Validate modern Odoo 17 module structure"""
        print("\n📁 Validating Module Structure...")
        
        required_dirs = [
            'static/src/js/components',
            'static/src/js/services',
            'static/src/js/utils',
            'static/src/xml',
            'static/src/scss'
        ]
        
        for dir_path in required_dirs:
            full_path = self.module_path / dir_path
            if full_path.exists():
                self.log_success(f"✅ Directory exists: {dir_path}")
            else:
                self.log_warning(f"⚠️  Missing recommended directory: {dir_path}")
        
        # Check for modern file organization
        js_files = list((self.module_path / 'static/src/js').rglob('*.js'))
        organized_files = [f for f in js_files if any(part in str(f) for part in ['components', 'services', 'utils', 'fields', 'views'])]
        
        organization_score = len(organized_files) / len(js_files) * 100 if js_files else 0
        self.results['module_structure']['organization_score'] = organization_score
        
        if organization_score >= 80:
            self.log_success(f"✅ Good file organization: {organization_score:.1f}%")
        else:
            self.log_warning(f"⚠️  Consider better file organization: {organization_score:.1f}%")
    
    def validate_javascript_files(self):
        """Validate JavaScript files for Odoo 17 compliance"""
        print("\n🚀 Validating JavaScript Files...")
        
        js_files = list((self.module_path / 'static/src/js').rglob('*.js'))
        module_files = []
        non_module_files = []
        
        for js_file in js_files:
            content = js_file.read_text(encoding='utf-8', errors='ignore')
            
            # Check for @odoo-module annotation
            if '/** @odoo-module **/' in content:
                module_files.append(js_file)
                self.validate_es6_module(js_file, content)
            else:
                non_module_files.append(js_file)
                self.validate_non_module_file(js_file, content)
        
        self.results['javascript_analysis'] = {
            'total_files': len(js_files),
            'module_files': len(module_files),
            'non_module_files': len(non_module_files),
            'modernization_score': len(module_files) / len(js_files) * 100 if js_files else 0
        }
        
        print(f"📊 JavaScript Analysis:")
        print(f"   - Total files: {len(js_files)}")
        print(f"   - ES6 modules: {len(module_files)}")
        print(f"   - Non-modules: {len(non_module_files)}")
        print(f"   - Modernization: {self.results['javascript_analysis']['modernization_score']:.1f}%")
    
    def validate_es6_module(self, file_path, content):
        """Validate ES6 module compliance"""
        file_name = file_path.name
        
        # Check for modern imports
        modern_patterns = [
            r'import\s+.*from\s+["\'"]@odoo/',
            r'import\s+.*from\s+["\'"]@web/',
            r'export\s+(class|function|const)',
            r'useService\(',
            r'useState\(',
            r'Component\s*\{',
            r'registry\.category'
        ]
        
        modern_count = sum(1 for pattern in modern_patterns if re.search(pattern, content))
        
        # Check for legacy patterns (should be avoided)
        legacy_patterns = [
            r'odoo\.define\(',
            r'require\s*\(\s*["\']web\.',
            r'Widget\.extend',
            r'jQuery\s*\(',
            r'\$\s*\('
        ]
        
        legacy_count = sum(1 for pattern in legacy_patterns if re.search(pattern, content))
        
        if modern_count >= 2 and legacy_count == 0:
            self.log_success(f"✅ Modern ES6 module: {file_name}")
        elif legacy_count > 0:
            self.log_error(f"❌ Contains legacy patterns: {file_name}")
        else:
            self.log_warning(f"⚠️  Partially modernized: {file_name}")
    
    def validate_non_module_file(self, file_path, content):
        """Validate non-module files (should be intentional)"""
        file_name = file_path.name
        
        # Some files are intentionally non-module for compatibility
        acceptable_non_modules = [
            'cloudpepper_clean_fix.js',
            'payment_workflow_safe.js',
            'qr_verification.js'  # Frontend file
        ]
        
        if file_name in acceptable_non_modules:
            self.log_success(f"✅ Intentional non-module: {file_name}")
        else:
            self.log_warning(f"⚠️  Consider converting to module: {file_name}")
    
    def validate_manifest(self):
        """Validate __manifest__.py for modern asset declarations"""
        print("\n📋 Validating Manifest...")
        
        manifest_path = self.module_path / '__manifest__.py'
        if not manifest_path.exists():
            self.log_error("❌ Missing __manifest__.py")
            return
        
        content = manifest_path.read_text(encoding='utf-8')
        
        # Check for modern asset structure
        if "'assets':" in content:
            self.log_success("✅ Uses modern asset declaration")
            
            # Check for proper asset bundles
            bundles = ['web.assets_backend', 'web.assets_frontend', 'web.assets_qweb']
            for bundle in bundles:
                if bundle in content:
                    self.log_success(f"✅ Has {bundle} bundle")
                else:
                    self.log_warning(f"⚠️  Missing {bundle} bundle")
        else:
            self.log_error("❌ Missing modern asset declaration")
        
        # Check for deprecated qweb declarations
        if "'qweb':" in content:
            self.log_error("❌ Contains deprecated 'qweb' declaration")
        else:
            self.log_success("✅ No deprecated qweb declarations")
    
    def validate_templates(self):
        """Validate XML templates for OWL compliance"""
        print("\n📄 Validating Templates...")
        
        xml_files = list((self.module_path / 'static/src/xml').glob('*.xml'))
        
        for xml_file in xml_files:
            content = xml_file.read_text(encoding='utf-8', errors='ignore')
            
            # Check for OWL compliance
            if 'owl="1"' in content:
                self.log_success(f"✅ OWL compliant: {xml_file.name}")
            else:
                self.log_warning(f"⚠️  Missing owl=\"1\": {xml_file.name}")
            
            # Check for modern template patterns
            modern_template_patterns = [
                r't-on-click=',
                r't-model=',
                r't-att-',
                r'role=',
                r'aria-'
            ]
            
            modern_template_count = sum(1 for pattern in modern_template_patterns if re.search(pattern, content))
            
            if modern_template_count >= 2:
                self.log_success(f"✅ Modern template patterns: {xml_file.name}")
    
    def validate_services(self):
        """Validate service implementation"""
        print("\n🔧 Validating Services...")
        
        services_dir = self.module_path / 'static/src/js/services'
        if services_dir.exists():
            service_files = list(services_dir.glob('*.js'))
            
            for service_file in service_files:
                content = service_file.read_text(encoding='utf-8', errors='ignore')
                
                # Check for proper service structure
                if 'registry.category("services").add(' in content:
                    self.log_success(f"✅ Properly registered service: {service_file.name}")
                else:
                    self.log_warning(f"⚠️  Service not properly registered: {service_file.name}")
        else:
            self.log_warning("⚠️  No services directory found")
    
    def generate_report(self):
        """Generate comprehensive report"""
        print("\n" + "=" * 60)
        print("📊 MODERNIZATION REPORT")
        print("=" * 60)
        
        total_checks = self.results['success_count'] + self.results['warning_count'] + self.results['error_count']
        
        print(f"✅ Successful checks: {self.results['success_count']}")
        print(f"⚠️  Warnings: {self.results['warning_count']}")
        print(f"❌ Errors: {self.results['error_count']}")
        print(f"📈 Total checks: {total_checks}")
        
        if total_checks > 0:
            success_rate = self.results['success_count'] / total_checks * 100
            print(f"🎯 Success rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("\n🎉 EXCELLENT! Module is fully modernized for Odoo 17")
            elif success_rate >= 75:
                print("\n👍 GOOD! Module is well modernized with minor improvements needed")
            elif success_rate >= 50:
                print("\n⚠️  MODERATE! Module needs additional modernization work")
            else:
                print("\n❌ POOR! Module requires significant modernization")
        
        # JavaScript modernization score
        js_score = self.results['javascript_analysis'].get('modernization_score', 0)
        print(f"\n🚀 JavaScript Modernization Score: {js_score:.1f}%")
        
        if js_score >= 80:
            print("✅ JavaScript is well modernized")
        else:
            print("⚠️  JavaScript needs more modernization")
    
    def log_success(self, message):
        print(f"  {message}")
        self.results['success_count'] += 1
    
    def log_warning(self, message):
        print(f"  {message}")
        self.results['warning_count'] += 1
    
    def log_error(self, message):
        print(f"  {message}")
        self.results['error_count'] += 1

def main():
    """Main validation function"""
    module_path = os.path.dirname(os.path.abspath(__file__))
    
    validator = Odoo17ModernizationValidator(module_path)
    results = validator.validate_all()
    
    # Save results to JSON for further analysis
    with open('modernization_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: modernization_report.json")
    
    return results['error_count'] == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
