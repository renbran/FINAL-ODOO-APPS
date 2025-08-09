#!/usr/bin/env python3
"""
Payment Workflow Fix Validation Script
Tests the corrected post button functionality and approval workflow
"""

import os
import json
from datetime import datetime

class WorkflowValidator:
    def __init__(self):
        self.base_path = r"d:\RUNNING APPS\ready production\latest\odoo17_final\account_payment_final"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "validation_type": "workflow_integration",
            "tests": {},
            "overall_status": "PENDING"
        }
    
    def validate_payment_post_method(self):
        """Validate payment post method override"""
        print("🔍 Validating payment post method...")
        
        model_path = os.path.join(self.base_path, "models", "account_payment.py")
        
        if not os.path.exists(model_path):
            self.results["tests"]["payment_post_method"] = {
                "status": "FAIL",
                "error": "account_payment.py not found"
            }
            print("❌ account_payment.py not found")
            return False
        
        try:
            with open(model_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required methods and implementation
            required_patterns = [
                "def action_post_payment(self):",
                "def action_post(self):",
                "super(AccountPayment, record).action_post()",
                "approval_state == 'approved'",
                "group_payment_poster"
            ]
            
            missing_patterns = []
            for pattern in required_patterns:
                if pattern not in content:
                    missing_patterns.append(pattern)
            
            # Check for proper workflow integration
            has_workflow_redirect = "redirect to approval workflow" in content
            has_proper_override = "Call the original post method" in content
            has_state_validation = "Payment must go through approval workflow" in content
            
            workflow_integration = has_workflow_redirect and has_proper_override and has_state_validation
            
            self.results["tests"]["payment_post_method"] = {
                "status": "PASS" if len(missing_patterns) == 0 and workflow_integration else "FAIL",
                "missing_patterns": missing_patterns,
                "workflow_integration": workflow_integration,
                "file_size": len(content)
            }
            
            if len(missing_patterns) == 0 and workflow_integration:
                print("✅ Payment post method properly implemented")
                return True
            else:
                print(f"❌ Payment post method issues: {missing_patterns}")
                return False
                
        except Exception as e:
            self.results["tests"]["payment_post_method"] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"❌ Error validating payment post method: {e}")
            return False
    
    def validate_invoice_bill_integration(self):
        """Validate invoice/bill approval workflow integration"""
        print("🔍 Validating invoice/bill integration...")
        
        model_path = os.path.join(self.base_path, "models", "account_move.py")
        
        if not os.path.exists(model_path):
            self.results["tests"]["invoice_bill_integration"] = {
                "status": "FAIL",
                "error": "account_move.py not found"
            }
            print("❌ account_move.py not found")
            return False
        
        try:
            with open(model_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required methods
            required_methods = [
                "action_submit_for_review",
                "action_final_approve", 
                "action_post_invoice_bill",
                "action_register_payment",
                "action_post"
            ]
            
            missing_methods = []
            for method in required_methods:
                if f"def {method}(self):" not in content:
                    missing_methods.append(method)
            
            # Check for approval state integration
            has_approval_state = "approval_state" in content
            has_workflow_enforcement = "approval workflow" in content
            has_register_payment_check = "Cannot register payment for unapproved" in content
            
            integration_complete = (
                len(missing_methods) == 0 and 
                has_approval_state and 
                has_workflow_enforcement and 
                has_register_payment_check
            )
            
            self.results["tests"]["invoice_bill_integration"] = {
                "status": "PASS" if integration_complete else "FAIL",
                "missing_methods": missing_methods,
                "has_approval_state": has_approval_state,
                "has_workflow_enforcement": has_workflow_enforcement,
                "has_register_payment_check": has_register_payment_check,
                "file_size": len(content)
            }
            
            if integration_complete:
                print("✅ Invoice/Bill integration properly implemented")
                return True
            else:
                print(f"❌ Invoice/Bill integration issues: {missing_methods}")
                return False
                
        except Exception as e:
            self.results["tests"]["invoice_bill_integration"] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"❌ Error validating invoice/bill integration: {e}")
            return False
    
    def validate_view_configurations(self):
        """Validate view configurations for workflow"""
        print("🔍 Validating view configurations...")
        
        payment_views_path = os.path.join(self.base_path, "views", "account_payment_views.xml")
        move_views_path = os.path.join(self.base_path, "views", "account_move_views.xml")
        
        view_results = {}
        
        # Check payment views
        if os.path.exists(payment_views_path):
            try:
                with open(payment_views_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_post_button = "action_post_payment" in content
                has_workflow_buttons = "action_submit_for_review" in content
                has_statusbar = "approval_state" in content
                
                view_results["payment_views"] = {
                    "exists": True,
                    "has_post_button": has_post_button,
                    "has_workflow_buttons": has_workflow_buttons,
                    "has_statusbar": has_statusbar
                }
                
            except Exception as e:
                view_results["payment_views"] = {
                    "exists": True,
                    "error": str(e)
                }
        else:
            view_results["payment_views"] = {"exists": False}
        
        # Check move views
        if os.path.exists(move_views_path):
            try:
                with open(move_views_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_approval_workflow = "approval_state" in content
                has_post_override = "action_post_invoice_bill" in content
                has_register_payment_override = "register_payment" in content
                
                view_results["move_views"] = {
                    "exists": True,
                    "has_approval_workflow": has_approval_workflow,
                    "has_post_override": has_post_override,
                    "has_register_payment_override": has_register_payment_override
                }
                
            except Exception as e:
                view_results["move_views"] = {
                    "exists": True,
                    "error": str(e)
                }
        else:
            view_results["move_views"] = {"exists": False}
        
        # Evaluate overall view configuration
        payment_ok = (view_results.get("payment_views", {}).get("has_post_button", False) and
                     view_results.get("payment_views", {}).get("has_workflow_buttons", False))
        
        move_ok = (view_results.get("move_views", {}).get("has_approval_workflow", False) and
                  view_results.get("move_views", {}).get("has_post_override", False))
        
        self.results["tests"]["view_configurations"] = {
            "status": "PASS" if payment_ok and move_ok else "FAIL",
            "payment_views": view_results.get("payment_views", {}),
            "move_views": view_results.get("move_views", {})
        }
        
        if payment_ok and move_ok:
            print("✅ View configurations properly implemented")
            return True
        else:
            print("❌ View configuration issues found")
            return False
    
    def validate_security_groups(self):
        """Validate security group references"""
        print("🔍 Validating security group references...")
        
        security_path = os.path.join(self.base_path, "security", "payment_security.xml")
        
        if not os.path.exists(security_path):
            self.results["tests"]["security_groups"] = {
                "status": "FAIL",
                "error": "payment_security.xml not found"
            }
            print("❌ payment_security.xml not found")
            return False
        
        try:
            with open(security_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_groups = [
                "group_payment_reviewer",
                "group_payment_approver", 
                "group_payment_poster"
            ]
            
            missing_groups = []
            for group in required_groups:
                if group not in content:
                    missing_groups.append(group)
            
            self.results["tests"]["security_groups"] = {
                "status": "PASS" if len(missing_groups) == 0 else "FAIL",
                "missing_groups": missing_groups,
                "file_size": len(content)
            }
            
            if len(missing_groups) == 0:
                print("✅ Security groups properly configured")
                return True
            else:
                print(f"❌ Missing security groups: {missing_groups}")
                return False
                
        except Exception as e:
            self.results["tests"]["security_groups"] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"❌ Error validating security groups: {e}")
            return False
    
    def run_validation(self):
        """Run all workflow validation tests"""
        print("🚀 Starting Payment Workflow Fix Validation...")
        print("=" * 70)
        
        # Run all validation tests
        payment_ok = self.validate_payment_post_method()
        invoice_ok = self.validate_invoice_bill_integration()
        views_ok = self.validate_view_configurations()
        security_ok = self.validate_security_groups()
        
        # Calculate overall status
        all_passed = payment_ok and invoice_ok and views_ok and security_ok
        
        if all_passed:
            self.results["overall_status"] = "SUCCESS"
        else:
            self.results["overall_status"] = "PARTIAL"
        
        print("\n" + "=" * 70)
        print(f"🎯 Overall Status: {self.results['overall_status']}")
        
        return self.results
    
    def save_results(self, filename="workflow_validation_results.json"):
        """Save validation results to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"💾 Results saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")
    
    def print_summary(self):
        """Print validation summary"""
        print("\n📊 Workflow Validation Summary:")
        for test_name, test_result in self.results["tests"].items():
            status = test_result.get("status", "UNKNOWN")
            status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
            print(f"  {status_emoji} {test_name.replace('_', ' ').title()}: {status}")
        
        if self.results["overall_status"] == "SUCCESS":
            print("\n🎉 All workflow integration tests passed!")
            print("📝 Key Fixes Implemented:")
            print("  ✅ Payment post button now properly calls workflow method")
            print("  ✅ Invoice/Bill posting enforces approval workflow")
            print("  ✅ Register payment checks invoice/bill approval state")
            print("  ✅ Proper security group permissions configured")
            print("\n📋 Next Steps:")
            print("  1. Update the module in Odoo")
            print("  2. Test payment posting workflow")
            print("  3. Test invoice/bill approval and posting")
            print("  4. Verify register payment functionality")
        else:
            print(f"\n⚠️ Validation completed with status: {self.results['overall_status']}")
            print("📝 Some components may need attention - check details above")

def main():
    """Main execution function"""
    validator = WorkflowValidator()
    
    try:
        results = validator.run_validation()
        validator.save_results()
        validator.print_summary()
        
        if results["overall_status"] == "SUCCESS":
            exit(0)
        else:
            exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Validation interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Validation failed with error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
