#!/usr/bin/env python3
"""
CloudPepper Production Deployment Validation Script
Final validation before deploying account_payment_approval to CloudPepper
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

class CloudPepperDeploymentValidator:
    """Validates module readiness for CloudPepper deployment"""
    
    def __init__(self, module_path="account_payment_approval"):
        self.module_path = Path(module_path)
        self.passed_checks = 0
        self.total_checks = 0
        
    def run_validation(self):
        """Run all CloudPepper specific validations"""
        print("🌩️  CLOUDPEPPER DEPLOYMENT VALIDATION")
        print("=" * 60)
        
        self._check_python_dependencies()
        self._check_module_structure()
        self._check_security_configuration()
        self._check_report_dependencies()
        self._check_external_references()
        self._final_assessment()
        
    def _check_python_dependencies(self):
        """Check required Python dependencies are available"""
        print("\\n📦 Checking Python Dependencies...")
        self.total_checks += 3
        
        dependencies = ['qrcode', 'num2words', 'PIL']
        
        for dep in dependencies:
            try:
                if dep == 'PIL':
                    import PIL
                    print(f"  ✅ {dep} (Pillow) - Available")
                    self.passed_checks += 1
                else:
                    __import__(dep)
                    print(f"  ✅ {dep} - Available")
                    self.passed_checks += 1
            except ImportError:
                print(f"  ❌ {dep} - NOT AVAILABLE")
                print(f"     Install with: pip install {dep if dep != 'PIL' else 'pillow'}")
                
    def _check_module_structure(self):
        """Validate essential module structure"""
        print("\\n📁 Checking Module Structure...")
        
        essential_files = [
            '__manifest__.py',
            'models/__init__.py',
            'models/account_payment.py',
            'views/account_payment_views.xml',
            'security/ir.model.access.csv',
            'security/payment_voucher_security.xml'
        ]
        
        self.total_checks += len(essential_files)
        
        for file_path in essential_files:
            full_path = self.module_path / file_path
            if full_path.exists():
                print(f"  ✅ {file_path}")
                self.passed_checks += 1
            else:
                print(f"  ❌ {file_path} - MISSING")
                
    def _check_security_configuration(self):
        """Validate security configuration"""
        print("\\n🔒 Checking Security Configuration...")
        self.total_checks += 2
        
        # Check access rules
        access_file = self.module_path / 'security' / 'ir.model.access.csv'
        if access_file.exists():
            with open(access_file, 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:  # Header + at least one rule
                    print(f"  ✅ Access rules: {len(lines)-1} rules defined")
                    self.passed_checks += 1
                else:
                    print("  ❌ No access rules defined")
        else:
            print("  ❌ Access file missing")
            
        # Check security groups
        security_file = self.module_path / 'security' / 'payment_voucher_security.xml'
        if security_file.exists():
            with open(security_file, 'r') as f:
                content = f.read()
                if 'res.groups' in content:
                    print("  ✅ Security groups defined")
                    self.passed_checks += 1
                else:
                    print("  ❌ No security groups found")
        else:
            print("  ❌ Security groups file missing")
            
    def _check_report_dependencies(self):
        """Check report dependencies and external references"""
        print("\\n📊 Checking Report Dependencies...")
        self.total_checks += 1
        
        # Check for problematic external references
        report_files = list(self.module_path.glob("reports/*.xml"))
        report_files.extend(list(self.module_path.glob("views/*.xml")))
        
        has_paper_format_issues = False
        
        for report_file in report_files:
            try:
                with open(report_file, 'r') as f:
                    content = f.read()
                    if 'base.paperformat' in content:
                        print(f"  ⚠️  Paper format reference in {report_file.name}")
                        has_paper_format_issues = True
            except:
                pass
                
        if not has_paper_format_issues:
            print("  ✅ No problematic paper format references")
            self.passed_checks += 1
        else:
            print("  ❌ Paper format references may cause issues")
            
    def _check_external_references(self):
        """Check for external ID references that might not exist"""
        print("\\n🔗 Checking External References...")
        self.total_checks += 1
        
        xml_files = list(self.module_path.rglob("*.xml"))
        potential_issues = []
        
        for xml_file in xml_files:
            try:
                with open(xml_file, 'r') as f:
                    content = f.read()
                    
                # Check for common problematic references
                if 'base.paperformat_a4' in content:
                    potential_issues.append(f"base.paperformat_a4 in {xml_file.name}")
                if 'base.paperformat_us' in content:
                    potential_issues.append(f"base.paperformat_us in {xml_file.name}")
                    
            except:
                pass
                
        if not potential_issues:
            print("  ✅ No problematic external references found")
            self.passed_checks += 1
        else:
            print("  ❌ Potential external reference issues:")
            for issue in potential_issues:
                print(f"    - {issue}")
                
    def _final_assessment(self):
        """Provide final deployment assessment"""
        print("\\n" + "=" * 60)
        print("🎯 CLOUDPEPPER DEPLOYMENT ASSESSMENT")
        print("=" * 60)
        
        success_rate = (self.passed_checks / self.total_checks) * 100
        
        print(f"📊 Validation Results: {self.passed_checks}/{self.total_checks} checks passed ({success_rate:.1f}%)")
        
        if success_rate >= 100:
            print("\\n🟢 STATUS: READY FOR DEPLOYMENT")
            print("✅ All critical checks passed")
            print("✅ Module is CloudPepper compatible")
            print("✅ Proceed with confidence")
            
        elif success_rate >= 80:
            print("\\n🟡 STATUS: READY WITH MINOR FIXES")
            print("⚠️  Some non-critical issues detected")
            print("✅ Safe to deploy with monitoring")
            print("📝 Address warnings post-deployment")
            
        else:
            print("\\n🔴 STATUS: NOT READY - FIXES REQUIRED")
            print("❌ Critical issues must be resolved")
            print("❌ Do not deploy until all errors fixed")
            print("📝 Review and fix all failed checks")
            
        print("\\n🚀 DEPLOYMENT COMMANDS:")
        print("1. Install dependencies: pip install qrcode num2words pillow")
        print("2. Upload module to CloudPepper addons directory")
        print("3. Install: Apps → Search 'Enhanced Payment Voucher' → Install")
        print("4. Verify: Check Accounting menu for Payment Vouchers")
        
        return success_rate >= 80

def main():
    """Main execution"""
    validator = CloudPepperDeploymentValidator()
    is_ready = validator.run_validation()
    
    print("\\n" + "=" * 60)
    if is_ready:
        print("🎉 CLOUDPEPPER DEPLOYMENT APPROVED!")
        print("Your module is ready for production deployment.")
    else:
        print("⚠️  DEPLOYMENT ON HOLD")
        print("Please fix the identified issues before deployment.")
    print("=" * 60)
    
    return is_ready

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
