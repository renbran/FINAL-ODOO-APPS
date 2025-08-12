#!/usr/bin/env python3
"""
Asset Validation Script for account_payment_approval module
Validates that all assets declared in __manifest__.py actually exist
"""

import os
import sys
from pathlib import Path

def validate_assets():
    """Validate all assets declared in manifest file exist"""
    
    # Get module root directory
    module_root = Path(__file__).parent
    manifest_path = module_root / '__manifest__.py'
    
    print(f"🔍 Validating assets for module at: {module_root}")
    print(f"📋 Reading manifest: {manifest_path}")
    
    if not manifest_path.exists():
        print("❌ ERROR: __manifest__.py not found!")
        return False
    
    # Parse manifest to extract assets
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest_content = f.read()
    
    # Extract asset paths (simple parsing for validation)
    assets_section = False
    asset_files = []
    
    for line in manifest_content.split('\n'):
        line = line.strip()
        
        if "'assets':" in line:
            assets_section = True
            continue
        elif assets_section and line.startswith('}'):
            break
        elif assets_section and line.startswith("'account_payment_approval/"):
            # Extract file path
            path = line.split("'")[1]
            if path.startswith('account_payment_approval/'):
                # Remove module prefix
                file_path = path.replace('account_payment_approval/', '')
                asset_files.append(file_path)
    
    print(f"📁 Found {len(asset_files)} asset files to validate")
    
    # Validate each asset file exists
    missing_files = []
    existing_files = []
    
    for asset_file in asset_files:
        full_path = module_root / asset_file
        
        if full_path.exists():
            existing_files.append(asset_file)
            print(f"✅ {asset_file}")
        else:
            missing_files.append(asset_file)
            print(f"❌ {asset_file} - FILE NOT FOUND")
    
    # Summary
    print(f"\n📊 VALIDATION SUMMARY:")
    print(f"✅ Existing files: {len(existing_files)}")
    print(f"❌ Missing files: {len(missing_files)}")
    
    if missing_files:
        print(f"\n🚨 MISSING FILES:")
        for file in missing_files:
            print(f"   - {file}")
        print(f"\n💡 These files need to be created or the manifest needs to be updated.")
        return False
    else:
        print(f"\n🎉 ALL ASSETS VALIDATED SUCCESSFULLY!")
        return True

def create_missing_placeholder_files():
    """Create placeholder files for missing assets"""
    
    module_root = Path(__file__).parent
    
    # Common missing files and their content
    missing_files = {
        'static/src/js/components/payment_approval_dashboard.js': '''/** @odoo-module **/
// Payment Approval Dashboard Component - Placeholder
import { Component } from "@odoo/owl";

export class PaymentApprovalDashboard extends Component {
    static template = "account_payment_approval.DashboardTemplate";
}
''',
        'static/src/js/fields/voucher_state_field.js': '''/** @odoo-module **/
// Approval State Field Widget - Placeholder
import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";

export class ApprovalStateField extends CharField {
    static template = "account_payment_approval.ApprovalStateField";
}

registry.category("fields").add("voucher_state", ApprovalStateField);
''',
        'static/src/js/widgets/digital_signature_widget.js': '''/** @odoo-module **/
// Digital Signature Widget - Placeholder
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class DigitalSignatureWidget extends Component {
    static template = "account_payment_approval.DigitalSignatureWidget";
}

registry.category("fields").add("digital_signature", DigitalSignatureWidget);
''',
        'static/src/js/widgets/qr_code_widget.js': '''/** @odoo-module **/
// QR Code Widget - Placeholder  
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class QRCodeWidget extends Component {
    static template = "account_payment_approval.QRCodeWidget";
}

registry.category("fields").add("qr_code", QRCodeWidget);
''',
        'static/src/js/widgets/bulk_approval_widget.js': '''/** @odoo-module **/
// Bulk Approval Widget - Placeholder
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class BulkApprovalWidget extends Component {
    static template = "account_payment_approval.BulkApprovalWidget";
}

registry.category("fields").add("bulk_approval", BulkApprovalWidget);
''',
        'static/src/js/views/payment_form_view.js': '''/** @odoo-module **/
// Payment Form View Controller - Placeholder
import { FormController } from "@web/views/form/form_controller";
import { registry } from "@web/core/registry";

export class PaymentFormController extends FormController {
    // Custom payment form enhancements
}

registry.category("views").add("payment_form", {
    ...registry.category("views").get("form"),
    Controller: PaymentFormController,
});
''',
        'static/src/css/payment_approval.css': '''/* Payment Approval Module - Compiled CSS */
/* This file is generated from SCSS sources */

.o_payment_approval {
    /* Base payment approval styles */
}

.o_payment_approval_form {
    /* Form specific styles */
}

.o_payment_approval_dashboard {
    /* Dashboard specific styles */  
}
''',
        'static/src/js/qr_verification.js': '''// QR Verification Frontend Script - Placeholder
document.addEventListener('DOMContentLoaded', function() {
    console.log('QR Verification frontend loaded');
    
    // QR verification portal functionality
    const qrInputs = document.querySelectorAll('.qr-verification-input');
    qrInputs.forEach(input => {
        input.addEventListener('change', function() {
            // Handle QR verification
        });
    });
});
'''
    }
    
    created_files = []
    
    for file_path, content in missing_files.items():
        full_path = module_root / file_path
        
        # Create directory if it doesn't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not full_path.exists():
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            created_files.append(file_path)
            print(f"📝 Created placeholder: {file_path}")
    
    if created_files:
        print(f"\n✨ Created {len(created_files)} placeholder files")
        print("💡 You should now implement the actual functionality in these files")
    
    return created_files

if __name__ == '__main__':
    print("🚀 ODOO 17 ASSET VALIDATION TOOL")
    print("=" * 50)
    
    # Validate assets
    is_valid = validate_assets()
    
    if not is_valid:
        print("\n❓ Would you like to create placeholder files for missing assets? (y/n)")
        response = input().lower().strip()
        
        if response in ['y', 'yes']:
            create_missing_placeholder_files()
            print("\n🔄 Re-running validation...")
            is_valid = validate_assets()
    
    print("=" * 50)
    
    if is_valid:
        print("🎯 RESULT: All assets are properly configured!")
        sys.exit(0)
    else:
        print("⚠️  RESULT: Asset validation failed!")
        sys.exit(1)
