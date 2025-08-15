#!/usr/bin/env python3
"""
CloudPepper Emergency Fix for Order Status Override Missing Methods
Fixes: ParseError - action_return_to_previous is not a valid action on sale.order
"""

import os
import sys
import shutil
import datetime
import re

def main():
    print("🚨 CLOUDPEPPER EMERGENCY FIX - Order Status Override Missing Methods")
    print("==================================================================")
    
    # Configuration
    module_name = "order_status_override"
    odoo_addons_path = "/var/odoo/osusbck/extra-addons/odoo17_final.git-6880b7fcd4844"
    model_file = f"{odoo_addons_path}/{module_name}/models/sale_order.py"
    backup_dir = f"/tmp/cloudpepper_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"📁 Working with module: {module_name}")
    print(f"📂 Addons path: {odoo_addons_path}")
    
    try:
        # Create backup
        print("💾 Creating backup...")
        os.makedirs(backup_dir, exist_ok=True)
        shutil.copytree(f"{odoo_addons_path}/{module_name}", f"{backup_dir}/{module_name}")
        print(f"✅ Backup created at: {backup_dir}")
        
        # Check if model file exists
        if not os.path.exists(model_file):
            print(f"❌ ERROR: Model file not found at {model_file}")
            return False
        
        print(f"🔍 Current model file found at: {model_file}")
        
        # Read current file content
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Define missing methods
        missing_methods = '''
    def action_return_to_previous(self):
        """Return order to previous stage in workflow"""
        self.ensure_one()
        
        # Get current status code
        current_code = self.custom_status_id.code
        
        # Define previous status mapping
        previous_status_map = {
            'documentation_progress': 'draft',
            'commission_progress': 'documentation_progress', 
            'final_review': 'commission_progress',
            'review': 'commission_progress'
        }
        
        if current_code not in previous_status_map:
            raise UserError(_("Cannot return to previous stage from current status."))
        
        # Find the previous status
        previous_code = previous_status_map[current_code]
        previous_status = self.env['order.status'].search([('code', '=', previous_code)], limit=1)
        if not previous_status:
            raise UserError(_("Previous status '%s' not found in the system.") % previous_code)
        
        # Change to previous status
        self._change_status(previous_status.id, _("Order returned to previous stage by %s") % self.env.user.name)
        
        # Send notification
        self.message_post(
            body=_("Order has been returned to previous stage: %s") % previous_status.name,
            subject=_("Order Returned to Previous Stage"),
            message_type='notification'
        )
        
        return True

    def action_request_documentation(self):
        """Start the documentation process"""
        self.ensure_one()
        
        # Find the documentation status
        doc_status = self.env['order.status'].search([('code', '=', 'documentation_progress')], limit=1)
        if not doc_status:
            raise UserError(_("Documentation progress status not found in the system."))
        
        # Change to documentation status
        self._change_status(doc_status.id, _("Documentation process started by %s") % self.env.user.name)
        
        # Send notification
        self.message_post(
            body=_("Documentation process has been started."),
            subject=_("Documentation Started"),
            message_type='notification'
        )
        
        return True'''
        
        # Find insertion point after action_submit_for_review
        pattern = r'(def action_submit_for_review\(self\):.*?return True)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            print("❌ ERROR: Could not find action_submit_for_review method")
            return False
        
        print("🔧 Adding missing methods to model...")
        
        # Insert missing methods
        new_content = content.replace(match.group(1), match.group(1) + missing_methods)
        
        # Write updated content
        with open(model_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Verify the fix
        print("🔍 Verifying the fix...")
        with open(model_file, 'r', encoding='utf-8') as f:
            updated_content = f.read()
        
        if ('def action_return_to_previous' in updated_content and 
            'def action_request_documentation' in updated_content):
            print("✅ Missing methods successfully added to model")
        else:
            print("❌ ERROR: Methods not found after insertion")
            print("🔄 Restoring backup...")
            shutil.copytree(f"{backup_dir}/{module_name}", f"{odoo_addons_path}/{module_name}")
            return False
        
        print("")
        print("🎉 EMERGENCY FIX COMPLETED SUCCESSFULLY!")
        print("==================================================================")
        print("✅ Missing methods action_return_to_previous and action_request_documentation added")
        print("✅ Module should now install without ParseError")
        print(f"💾 Backup available at: {backup_dir}")
        print("")
        print("🔄 Next steps:")
        print("1. Restart Odoo service: sudo systemctl restart odoo")
        print("2. Upgrade the module from Odoo Apps menu")
        print("3. Test the functionality")
        print("")
        print("📝 Changes made:")
        print("- Added action_return_to_previous method with workflow logic")
        print("- Added action_request_documentation method for documentation process")
        print("- Both methods include proper error handling and notifications")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        if os.path.exists(backup_dir):
            print("🔄 Restoring backup...")
            try:
                shutil.copytree(f"{backup_dir}/{module_name}", f"{odoo_addons_path}/{module_name}")
                print("✅ Backup restored")
            except Exception as restore_error:
                print(f"❌ Failed to restore backup: {restore_error}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
