#!/bin/bash

# CloudPepper Emergency Fix for Order Status Override Missing Methods
# This script fixes the ParseError: action_return_to_previous is not a valid action on sale.order

echo "🚨 CLOUDPEPPER EMERGENCY FIX - Order Status Override Missing Methods"
echo "=================================================================="

# Set strict error handling
set -euo pipefail

# Variables
MODULE_NAME="order_status_override"
BACKUP_DIR="/tmp/cloudpepper_backup_$(date +%Y%m%d_%H%M%S)"
ODOO_ADDONS_PATH="/var/odoo/osusbck/extra-addons/odoo17_final.git-6880b7fcd4844"
MODEL_FILE="$ODOO_ADDONS_PATH/$MODULE_NAME/models/sale_order.py"

echo "📁 Working with module: $MODULE_NAME"
echo "📂 Addons path: $ODOO_ADDONS_PATH"

# Create backup
echo "💾 Creating backup..."
mkdir -p "$BACKUP_DIR"
cp -r "$ODOO_ADDONS_PATH/$MODULE_NAME" "$BACKUP_DIR/"
echo "✅ Backup created at: $BACKUP_DIR"

# Check if model file exists
if [ ! -f "$MODEL_FILE" ]; then
    echo "❌ ERROR: Model file not found at $MODEL_FILE"
    exit 1
fi

echo "🔍 Current model file found at: $MODEL_FILE"

# Create the fixed method content
cat > /tmp/missing_methods.py << 'EOF'

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
        
        return True
EOF

# Find the insertion point (after action_submit_for_review method)
echo "🔧 Adding missing methods to model..."

# Use Python to insert the methods after action_submit_for_review
python3 << 'PYTHON_EOF'
import re

# Read the current file
with open('/var/odoo/osusbck/extra-addons/odoo17_final.git-6880b7fcd4844/order_status_override/models/sale_order.py', 'r') as f:
    content = f.read()

# Read the missing methods
with open('/tmp/missing_methods.py', 'r') as f:
    missing_methods = f.read()

# Find the end of action_submit_for_review method
pattern = r'(def action_submit_for_review\(self\):.*?return True)'
match = re.search(pattern, content, re.DOTALL)

if match:
    # Insert missing methods after action_submit_for_review
    new_content = content.replace(match.group(1), match.group(1) + missing_methods)
    
    # Write the updated content
    with open('/var/odoo/osusbck/extra-addons/odoo17_final.git-6880b7fcd4844/order_status_override/models/sale_order.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Missing methods added successfully")
else:
    print("❌ Could not find action_submit_for_review method")
    exit(1)
PYTHON_EOF

# Verify the fix
echo "🔍 Verifying the fix..."
if grep -q "def action_return_to_previous" "$MODEL_FILE" && grep -q "def action_request_documentation" "$MODEL_FILE"; then
    echo "✅ Missing methods successfully added to model"
else
    echo "❌ ERROR: Methods not found after insertion"
    echo "🔄 Restoring backup..."
    cp -r "$BACKUP_DIR/$MODULE_NAME" "$ODOO_ADDONS_PATH/"
    exit 1
fi

# Clean up temporary files
rm -f /tmp/missing_methods.py

echo ""
echo "🎉 EMERGENCY FIX COMPLETED SUCCESSFULLY!"
echo "=================================================================="
echo "✅ Missing methods action_return_to_previous and action_request_documentation added"
echo "✅ Module should now install without ParseError"
echo "💾 Backup available at: $BACKUP_DIR"
echo ""
echo "🔄 Next steps:"
echo "1. Restart Odoo service: sudo systemctl restart odoo"
echo "2. Upgrade the module from Odoo Apps menu"
echo "3. Test the functionality"
echo ""
echo "📝 Changes made:"
echo "- Added action_return_to_previous method with workflow logic"
echo "- Added action_request_documentation method for documentation process"
echo "- Both methods include proper error handling and notifications"
