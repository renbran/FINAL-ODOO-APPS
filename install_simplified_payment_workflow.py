#!/usr/bin/env python3
"""
OSUS Payment Voucher Enhanced - Installation and Testing Script
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and return the result"""
    print(f"\n{'='*50}")
    print(f"🔄 {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: {description}")
            if result.stdout:
                print("Output:", result.stdout)
        else:
            print(f"❌ ERROR: {description}")
            if result.stderr:
                print("Error:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def main():
    """Main installation and testing function"""
    print("🏢 OSUS Payment Voucher Enhanced - Simplified Workflow")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("payment_account_enhanced"):
        print("❌ Error: payment_account_enhanced module not found!")
        print("Please run this script from the Odoo addons directory.")
        sys.exit(1)
    
    print("📂 Module directory found!")
    
    # Docker commands for module installation and testing
    commands = [
        {
            "cmd": "docker-compose ps",
            "desc": "Checking Docker services status"
        },
        {
            "cmd": "docker-compose exec odoo odoo --stop-after-init --update=payment_account_enhanced -d odoo",
            "desc": "Updating payment_account_enhanced module"
        },
        {
            "cmd": "docker-compose exec odoo odoo --test-enable --log-level=test --stop-after-init -d odoo -i payment_account_enhanced",
            "desc": "Running module tests"
        }
    ]
    
    # Run each command
    all_success = True
    for cmd_info in commands:
        success = run_command(cmd_info["cmd"], cmd_info["desc"])
        if not success:
            all_success = False
    
    # Summary
    print(f"\n{'='*60}")
    if all_success:
        print("✅ ALL OPERATIONS COMPLETED SUCCESSFULLY!")
        print_module_summary()
    else:
        print("⚠️  SOME OPERATIONS FAILED!")
        print("Please check the error messages above and try again.")
    print(f"{'='*60}")

def print_module_summary():
    """Print module feature summary"""
    print("""
🎉 OSUS Payment Voucher Enhanced - Simplified Workflow

📋 KEY FEATURES IMPLEMENTED:
═══════════════════════════════════════════════════════

✅ 2-State Simplified Workflow:
   • Draft → Waiting for Approval → Approved & Posted
   
✅ Automatic Voucher Numbers:
   • PV00001, PV00002 for payments
   • RV00001, RV00002 for receipts
   
✅ Organized Notebook Interface:
   💰 Payment Details - All payment information
   ✅ Approval Workflow - Status and approval history
   🔍 QR Code & Verification - Payment verification system
   🏢 Company & Settings - Company info and branding
   
✅ Enhanced User Experience:
   • Color-coded status indicators
   • Real-time status updates
   • Mobile-responsive design
   • OSUS luxury branding
   
✅ Future-Ready Framework:
   • Ready for 4-checkpoint workflow when needed
   • Hidden but available reviewer fields
   • Scalable approval system

🎯 ACCESS YOUR NEW WORKFLOW:
═══════════════════════════════════
1. Go to: Accounting > Payables > OSUS Vouchers
2. Create new payment voucher
3. Fill details in organized tabs
4. Submit for approval
5. Approvers use "Pending Approvals" menu

🚀 Next Steps:
• Test the workflow with actual payments
• Train users on new interface
• Configure approval permissions
• Customize sequences if needed
""")

if __name__ == "__main__":
    main()
