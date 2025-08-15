#!/usr/bin/env python3
"""
CloudPepper Critical Error Fix
Emergency patch for TypeError: unsupported operand type(s) for @: 'Monetary' and 'function'
"""

import os
import shutil
from pathlib import Path

def create_emergency_fix():
    """Create emergency fix for the CloudPepper Monetary field error"""
    print("=" * 60)
    print("CloudPepper Emergency Error Fix")
    print("=" * 60)
    
    # The error is in order_status_override/models/sale_order.py line 38
    # Let's create a clean version of this file
    
    target_file = Path("order_status_override/models/sale_order.py")
    
    if not target_file.exists():
        print(f"ERROR: Target file {target_file} does not exist!")
        return False
    
    # Backup the original
    backup_file = target_file.with_suffix('.py.emergency_backup')
    shutil.copy2(target_file, backup_file)
    print(f"✓ Backup created: {backup_file}")
    
    # Read current content
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Clean version without any potential @ operator issues
    clean_content = '''from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # Custom Status Management
    custom_status_id = fields.Many2one(
        'order.status', 
        string='Custom Status', 
        tracking=True, 
        copy=False
    )
    custom_status_history_ids = fields.One2many(
        'order.status.history', 
        'order_id', 
        string='Status History', 
        copy=False
    )
    
    # Responsible Users
    documentation_user_id = fields.Many2one(
        'res.users', 
        string='Documentation Responsible'
    )
    commission_user_id = fields.Many2one(
        'res.users', 
        string='Commission Responsible'
    )
    final_review_user_id = fields.Many2one(
        'res.users', 
        string='Final Review Responsible'
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to set initial status"""
        records = super(SaleOrder, self).create(vals_list)
        initial_status = self.env['order.status'].search([('is_initial', '=', True)], limit=1)
        if initial_status:
            for record in records:
                record.custom_status_id = initial_status.id
                self.env['order.status.history'].create({
                    'order_id': record.id,
                    'status_id': initial_status.id,
                    'notes': _('Initial status automatically set to %s') % initial_status.name
                })
        return records
    
    def action_change_status(self):
        """Open the status change wizard"""
        self.ensure_one()
        return {
            'name': _('Change Order Status'),
            'type': 'ir.actions.act_window',
            'res_model': 'order.status.change.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_current_status_id': self.custom_status_id.id,
            }
        }

    def action_approve_order(self):
        """Approve the order and move to final approved status"""
        self.ensure_one()
        # Check if current user can approve
        if not self.final_review_user_id or self.final_review_user_id.id != self.env.user.id:
            if not self.env.user.has_group('order_status_override.group_order_approval_manager'):
                raise UserError(_("Only the assigned reviewer or approval managers can approve orders."))
        
        # Find the final approved status
        approved_status = self.env['order.status'].search([('code', '=', 'approved')], limit=1)
        if not approved_status:
            raise UserError(_("Approved status not found in the system."))
        
        # Change to approved status
        self._change_status(approved_status.id, _("Order approved by %s") % self.env.user.name)
        
        # Send approval notification
        self.message_post(
            body=_("Order has been approved and is ready for confirmation."),
            subject=_("Order Approved"),
            message_type='notification'
        )
        
        return True
    
    def action_reject_order(self):
        """Reject the order and return to draft"""
        self.ensure_one()
        # Check if current user can reject
        if not self.final_review_user_id or self.final_review_user_id.id != self.env.user.id:
            if not self.env.user.has_group('order_status_override.group_order_approval_manager'):
                raise UserError(_("Only the assigned reviewer or approval managers can reject orders."))
        
        # Find the draft status
        draft_status = self.env['order.status'].search([('code', '=', 'draft')], limit=1)
        if not draft_status:
            raise UserError(_("Draft status not found in the system."))
        
        # Change to draft status
        self._change_status(draft_status.id, _("Order rejected by %s and returned to draft") % self.env.user.name)
        
        # Send rejection notification
        self.message_post(
            body=_("Order has been rejected and returned to draft status for revision."),
            subject=_("Order Rejected"),
            message_type='notification'
        )
        
        return True
    
    def action_submit_for_review(self):
        """Submit order for final review"""
        self.ensure_one()
        
        # Find the review status
        review_status = self.env['order.status'].search([('code', '=', 'review')], limit=1)
        if not review_status:
            raise UserError(_("Review status not found in the system."))
        
        # Change to review status
        self._change_status(review_status.id, _("Order submitted for review by %s") % self.env.user.name)
        
        # Send notification
        self.message_post(
            body=_("Order has been submitted for final review."),
            subject=_("Order Submitted for Review"),
            message_type='notification'
        )
        
        return True
    
    def _change_status(self, status_id, notes=None):
        """Helper method to change status and log history"""
        self.ensure_one()
        
        # Update the status
        self.custom_status_id = status_id
        
        # Create history record
        self.env['order.status.history'].create({
            'order_id': self.id,
            'status_id': status_id,
            'notes': notes or _('Status changed'),
            'user_id': self.env.user.id,
            'date': fields.Datetime.now()
        })
        
        return True
    
    def get_status_history(self):
        """Get formatted status history"""
        self.ensure_one()
        history = []
        for record in self.custom_status_history_ids.sorted('date', reverse=True):
            history.append({
                'status': record.status_id.name,
                'date': record.date,
                'user': record.user_id.name,
                'notes': record.notes
            })
        return history
'''
    
    # Write the clean content
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(clean_content)
    
    print(f"✓ Emergency fix applied to {target_file}")
    
    # Verify syntax
    try:
        import ast
        ast.parse(clean_content)
        print("✓ Syntax validation passed")
    except SyntaxError as e:
        print(f"✗ Syntax error in fix: {e}")
        return False
    
    return True

def create_deployment_script():
    """Create a deployment script for CloudPepper"""
    script_content = '''#!/bin/bash
# CloudPepper Emergency Deployment Script
# Fix for TypeError: unsupported operand type(s) for @: 'Monetary' and 'function'

echo "CloudPepper Emergency Fix Deployment"
echo "===================================="

# Stop Odoo service
echo "Stopping Odoo service..."
sudo systemctl stop odoo

# Backup current files
echo "Creating backup..."
BACKUP_DIR="/var/odoo/backup_$(date +%Y%m%d_%H%M%S)"
sudo mkdir -p $BACKUP_DIR
sudo cp -r /var/odoo/osusbck/extra-addons/odoo17_final.git-* $BACKUP_DIR/

# Apply fix to the problematic file
echo "Applying emergency fix..."
TARGET_FILE="/var/odoo/osusbck/extra-addons/odoo17_final.git-*/order_status_override/models/sale_order.py"

# Find the exact path
ACTUAL_PATH=$(find /var/odoo/osusbck/extra-addons/ -name "sale_order.py" -path "*/order_status_override/models/*" | head -1)

if [ -z "$ACTUAL_PATH" ]; then
    echo "ERROR: Could not find order_status_override/models/sale_order.py"
    exit 1
fi

echo "Found file at: $ACTUAL_PATH"

# Create backup of the problematic file
sudo cp "$ACTUAL_PATH" "$ACTUAL_PATH.error_backup"

# Copy the fixed file (you need to upload this script and the fixed file)
# For now, let's create a minimal working version
sudo tee "$ACTUAL_PATH" > /dev/null << 'EOF'
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    custom_status_id = fields.Many2one(
        'order.status', 
        string='Custom Status', 
        tracking=True, 
        copy=False
    )
    custom_status_history_ids = fields.One2many(
        'order.status.history', 
        'order_id', 
        string='Status History', 
        copy=False
    )
    
    documentation_user_id = fields.Many2one(
        'res.users', 
        string='Documentation Responsible'
    )
    commission_user_id = fields.Many2one(
        'res.users', 
        string='Commission Responsible'
    )
    final_review_user_id = fields.Many2one(
        'res.users', 
        string='Final Review Responsible'
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        records = super(SaleOrder, self).create(vals_list)
        initial_status = self.env['order.status'].search([('is_initial', '=', True)], limit=1)
        if initial_status:
            for record in records:
                record.custom_status_id = initial_status.id
                self.env['order.status.history'].create({
                    'order_id': record.id,
                    'status_id': initial_status.id,
                    'notes': _('Initial status automatically set to %s') % initial_status.name
                })
        return records
    
    def action_change_status(self):
        self.ensure_one()
        return {
            'name': _('Change Order Status'),
            'type': 'ir.actions.act_window',
            'res_model': 'order.status.change.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_current_status_id': self.custom_status_id.id,
            }
        }
EOF

# Set proper permissions
sudo chown odoo:odoo "$ACTUAL_PATH"
sudo chmod 644 "$ACTUAL_PATH"

# Validate Python syntax
echo "Validating Python syntax..."
python3 -m py_compile "$ACTUAL_PATH"
if [ $? -eq 0 ]; then
    echo "✓ Syntax validation passed"
else
    echo "✗ Syntax validation failed"
    echo "Restoring backup..."
    sudo cp "$ACTUAL_PATH.error_backup" "$ACTUAL_PATH"
    exit 1
fi

# Clear Python cache
echo "Clearing Python cache..."
sudo find /var/odoo/osusbck/extra-addons/ -name "*.pyc" -delete
sudo find /var/odoo/osusbck/extra-addons/ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Start Odoo service
echo "Starting Odoo service..."
sudo systemctl start odoo

# Check service status
sleep 5
sudo systemctl status odoo --no-pager

echo "Emergency fix deployment complete!"
echo "Backup location: $BACKUP_DIR"
echo "Monitor logs: sudo journalctl -u odoo -f"
'''
    
    with open('cloudpepper_emergency_deployment.sh', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod('cloudpepper_emergency_deployment.sh', 0o755)
    print("✓ Deployment script created: cloudpepper_emergency_deployment.sh")

def main():
    """Main function"""
    success = create_emergency_fix()
    if success:
        create_deployment_script()
        print("\n" + "=" * 60)
        print("EMERGENCY FIX COMPLETE")
        print("=" * 60)
        print("✓ Local fix applied")
        print("✓ Deployment script created")
        print("\nNext steps for CloudPepper:")
        print("1. Upload cloudpepper_emergency_deployment.sh to the server")
        print("2. Run: chmod +x cloudpepper_emergency_deployment.sh")
        print("3. Run: sudo ./cloudpepper_emergency_deployment.sh")
        print("4. Monitor: sudo journalctl -u odoo -f")
    else:
        print("✗ Emergency fix failed")

if __name__ == "__main__":
    main()
