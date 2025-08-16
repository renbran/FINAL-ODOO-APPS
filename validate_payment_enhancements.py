#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Account Payment Final - Enhancement Validation Script
======================================================

This script validates the enhanced payment workflow functionality including:
1. Real-time status updates with onchange events
2. Approval process constraints for payment registration
3. JavaScript and CSS integration
4. Workflow integrity checks

Author: OSUS Properties Development Team
Date: August 17, 2025
"""

import os
import sys
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PaymentWorkflowValidator:
    """Validator for enhanced payment workflow functionality"""
    
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.errors = []
        self.warnings = []
        self.success_count = 0
        
    def log_error(self, message):
        """Log error message"""
        self.errors.append(message)
        logger.error(message)
    
    def log_warning(self, message):
        """Log warning message"""
        self.warnings.append(message)
        logger.warning(message)
    
    def log_success(self, message):
        """Log success message"""
        self.success_count += 1
        logger.info(f"✓ {message}")
    
    def validate_file_exists(self, file_path, description):
        """Check if a file exists"""
        full_path = self.module_path / file_path
        if full_path.exists():
            self.log_success(f"{description} exists: {file_path}")
            return True
        else:
            self.log_error(f"{description} missing: {file_path}")
            return False
    
    def validate_python_syntax(self, file_path):
        """Validate Python file syntax"""
        full_path = self.module_path / file_path
        if not full_path.exists():
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                compile(f.read(), str(full_path), 'exec')
            self.log_success(f"Python syntax valid: {file_path}")
            return True
        except SyntaxError as e:
            self.log_error(f"Python syntax error in {file_path}: {e}")
            return False
    
    def validate_onchange_methods(self, file_path):
        """Check for onchange methods in Python files"""
        full_path = self.module_path / file_path
        if not full_path.exists():
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            onchange_methods = [
                '@api.onchange',
                '_onchange_approval_state',
                '_onchange_state_sync_approval',
                '_onchange_workflow_users',
                '_onchange_amount_validation',
                '_onchange_payment_method_enhanced'
            ]
            
            found_methods = []
            for method in onchange_methods:
                if method in content:
                    found_methods.append(method)
            
            if found_methods:
                self.log_success(f"OnChange methods found in {file_path}: {', '.join(found_methods)}")
                return True
            else:
                self.log_warning(f"No onchange methods found in {file_path}")
                return False
        
        except Exception as e:
            self.log_error(f"Error checking onchange methods in {file_path}: {e}")
            return False
    
    def validate_constraints(self, file_path):
        """Check for constraint methods in Python files"""
        full_path = self.module_path / file_path
        if not full_path.exists():
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            constraint_methods = [
                '@api.constrains',
                '_check_payment_posting_constraints',
                '_check_approval_workflow_integrity'
            ]
            
            found_constraints = []
            for constraint in constraint_methods:
                if constraint in content:
                    found_constraints.append(constraint)
            
            if found_constraints:
                self.log_success(f"Constraint methods found in {file_path}: {', '.join(found_constraints)}")
                return True
            else:
                self.log_warning(f"No constraint methods found in {file_path}")
                return False
        
        except Exception as e:
            self.log_error(f"Error checking constraints in {file_path}: {e}")
            return False
    
    def validate_approval_workflow_override(self, file_path):
        """Check for approval workflow overrides"""
        full_path = self.module_path / file_path
        if not full_path.exists():
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_overrides = [
                'def create(',
                'force_approval_workflow',
                'from_invoice_payment',
                'approval_workflow_required'
            ]
            
            found_overrides = []
            for override in required_overrides:
                if override in content:
                    found_overrides.append(override)
            
            if len(found_overrides) >= 3:
                self.log_success(f"Approval workflow overrides found in {file_path}: {', '.join(found_overrides)}")
                return True
            else:
                self.log_warning(f"Insufficient approval workflow overrides in {file_path}: {', '.join(found_overrides)}")
                return False
        
        except Exception as e:
            self.log_error(f"Error checking approval workflow overrides in {file_path}: {e}")
            return False
    
    def validate_javascript_functionality(self, file_path):
        """Check JavaScript functionality"""
        full_path = self.module_path / file_path
        if not full_path.exists():
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            js_features = [
                'PaymentWorkflowRealtime',
                'onApprovalStateChange',
                'updateWorkflowProgress',
                'setupWorkflowObservers',
                'showStateChangeNotification',
                'refreshWorkflowStatus'
            ]
            
            found_features = []
            for feature in js_features:
                if feature in content:
                    found_features.append(feature)
            
            if len(found_features) >= 4:
                self.log_success(f"JavaScript real-time features found in {file_path}: {', '.join(found_features)}")
                return True
            else:
                self.log_warning(f"Insufficient JavaScript features in {file_path}: {', '.join(found_features)}")
                return False
        
        except Exception as e:
            self.log_error(f"Error checking JavaScript functionality in {file_path}: {e}")
            return False
    
    def validate_css_styling(self, file_path):
        """Check CSS styling for real-time updates"""
        full_path = self.module_path / file_path
        if not full_path.exists():
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            css_features = [
                '.workflow-progress',
                '.progress-step',
                '.payment-notification',
                '@keyframes',
                '.status-badge',
                'transition:'
            ]
            
            found_features = []
            for feature in css_features:
                if feature in content:
                    found_features.append(feature)
            
            if len(found_features) >= 4:
                self.log_success(f"CSS real-time styling found in {file_path}: {', '.join(found_features)}")
                return True
            else:
                self.log_warning(f"Insufficient CSS styling in {file_path}: {', '.join(found_features)}")
                return False
        
        except Exception as e:
            self.log_error(f"Error checking CSS styling in {file_path}: {e}")
            return False
    
    def validate_manifest_assets(self, file_path):
        """Check manifest file for proper asset inclusion"""
        full_path = self.module_path / file_path
        if not full_path.exists():
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_assets = [
                'payment_workflow_realtime.js',
                'realtime_workflow.scss',
                'web.assets_backend'
            ]
            
            found_assets = []
            for asset in required_assets:
                if asset in content:
                    found_assets.append(asset)
            
            if len(found_assets) >= 2:
                self.log_success(f"Required assets found in {file_path}: {', '.join(found_assets)}")
                return True
            else:
                self.log_warning(f"Missing assets in {file_path}: {set(required_assets) - set(found_assets)}")
                return False
        
        except Exception as e:
            self.log_error(f"Error checking manifest assets in {file_path}: {e}")
            return False
    
    def run_validation(self):
        """Run comprehensive validation"""
        logger.info("Starting Account Payment Final Enhancement Validation")
        logger.info("=" * 70)
        
        # 1. Core file existence checks
        logger.info("1. Validating core file structure...")
        core_files = [
            ('models/account_payment.py', 'Enhanced Payment Model'),
            ('models/account_move.py', 'Enhanced Move Model'),
            ('models/account_payment_register.py', 'Payment Register Override'),
            ('static/src/js/payment_workflow_realtime.js', 'Real-time JavaScript'),
            ('static/src/scss/realtime_workflow.scss', 'Real-time CSS'),
            ('__manifest__.py', 'Module Manifest')
        ]
        
        for file_path, description in core_files:
            self.validate_file_exists(file_path, description)
        
        # 2. Python syntax validation
        logger.info("\n2. Validating Python syntax...")
        python_files = [
            'models/account_payment.py',
            'models/account_move.py',
            'models/account_payment_register.py'
        ]
        
        for file_path in python_files:
            self.validate_python_syntax(file_path)
        
        # 3. OnChange method validation
        logger.info("\n3. Validating OnChange methods for real-time updates...")
        self.validate_onchange_methods('models/account_payment.py')
        self.validate_onchange_methods('models/account_move.py')
        
        # 4. Constraint validation
        logger.info("\n4. Validating approval workflow constraints...")
        self.validate_constraints('models/account_payment.py')
        
        # 5. Approval workflow override validation
        logger.info("\n5. Validating approval workflow overrides...")
        self.validate_approval_workflow_override('models/account_payment.py')
        self.validate_approval_workflow_override('models/account_payment_register.py')
        
        # 6. JavaScript functionality validation
        logger.info("\n6. Validating JavaScript real-time functionality...")
        self.validate_javascript_functionality('static/src/js/payment_workflow_realtime.js')
        
        # 7. CSS styling validation
        logger.info("\n7. Validating CSS real-time styling...")
        self.validate_css_styling('static/src/scss/realtime_workflow.scss')
        
        # 8. Manifest asset validation
        logger.info("\n8. Validating manifest asset inclusion...")
        self.validate_manifest_assets('__manifest__.py')
        
        # Generate final report
        self.generate_report()
    
    def generate_report(self):
        """Generate validation report"""
        logger.info("\n" + "=" * 70)
        logger.info("VALIDATION REPORT")
        logger.info("=" * 70)
        
        logger.info(f"✓ Successful validations: {self.success_count}")
        
        if self.warnings:
            logger.info(f"⚠ Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                logger.warning(f"  - {warning}")
        
        if self.errors:
            logger.info(f"✗ Errors: {len(self.errors)}")
            for error in self.errors:
                logger.error(f"  - {error}")
        
        # Overall status
        if not self.errors:
            if not self.warnings:
                logger.info("\n🎉 ALL VALIDATIONS PASSED! Module is ready for production.")
                status = "PASSED"
            else:
                logger.info("\n✅ VALIDATION PASSED with warnings. Review warnings before production.")
                status = "PASSED_WITH_WARNINGS"
        else:
            logger.info("\n❌ VALIDATION FAILED. Please fix errors before deployment.")
            status = "FAILED"
        
        # Save report to file
        report_data = {
            'status': status,
            'timestamp': str(logger.handlers[0].formatter.formatTime(logger.makeRecord('', 0, '', 0, '', (), None), '%Y-%m-%d %H:%M:%S')),
            'success_count': self.success_count,
            'warnings': self.warnings,
            'errors': self.errors
        }
        
        report_file = self.module_path / 'enhancement_validation_report.json'
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"\n📝 Detailed report saved to: {report_file}")
        
        return status == "PASSED"


def main():
    """Main execution function"""
    # Get module path
    if len(sys.argv) > 1:
        module_path = sys.argv[1]
    else:
        module_path = os.path.join(os.path.dirname(__file__), 'account_payment_final')
    
    if not os.path.exists(module_path):
        logger.error(f"Module path does not exist: {module_path}")
        sys.exit(1)
    
    # Run validation
    validator = PaymentWorkflowValidator(module_path)
    success = validator.run_validation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
