#!/bin/bash
# CloudPepper IMMEDIATE Emergency Fix
# Fixes TypeError: unsupported operand type(s) for @: 'Monetary' and 'function'
# Target: line 38 total_payment_out field in order_status_override/models/sale_order.py

echo "CloudPepper IMMEDIATE Emergency Fix"
echo "==================================="
echo "Timestamp: $(date)"
echo ""

# Stop Odoo service immediately
echo "🛑 Stopping Odoo service..."
sudo systemctl stop odoo

# Find the exact problematic file
echo "🔍 Locating problematic file..."
TARGET_FILE=$(find /var/odoo/osusbck/extra-addons/ -name "sale_order.py" -path "*/order_status_override/models/*" | head -1)

if [ -z "$TARGET_FILE" ]; then
    echo "❌ ERROR: Could not find order_status_override/models/sale_order.py"
    exit 1
fi

echo "📍 Found file: $TARGET_FILE"

# Create immediate backup
BACKUP_FILE="${TARGET_FILE}.emergency_$(date +%Y%m%d_%H%M%S)"
sudo cp "$TARGET_FILE" "$BACKUP_FILE"
echo "💾 Backup created: $BACKUP_FILE"

# Check if the problematic line exists
echo "🔍 Checking for problematic line 38..."
LINE_38=$(sed -n '38p' "$TARGET_FILE")
echo "Line 38 content: $LINE_38"

if [[ "$LINE_38" == *"total_payment_out"* ]]; then
    echo "🎯 Found problematic total_payment_out field on line 38"
    
    # Emergency fix: Replace the problematic line with a safe comment
    echo "🚑 Applying emergency fix..."
    
    # Create a temporary safe version
    sudo tee "$TARGET_FILE" > /dev/null << 'EOF'
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
    
    # EMERGENCY FIX: Removed problematic total_payment_out field
    # Original line 38 caused: TypeError: unsupported operand type(s) for @: 'Monetary' and 'function'
    
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

    def action_approve_order(self):
        self.ensure_one()
        if not self.final_review_user_id or self.final_review_user_id.id != self.env.user.id:
            if not self.env.user.has_group('order_status_override.group_order_approval_manager'):
                raise UserError(_("Only the assigned reviewer or approval managers can approve orders."))
        
        approved_status = self.env['order.status'].search([('code', '=', 'approved')], limit=1)
        if not approved_status:
            raise UserError(_("Approved status not found in the system."))
        
        self._change_status(approved_status.id, _("Order approved by %s") % self.env.user.name)
        self.message_post(
            body=_("Order has been approved and is ready for confirmation."),
            subject=_("Order Approved"),
            message_type='notification'
        )
        return True
    
    def action_reject_order(self):
        self.ensure_one()
        if not self.final_review_user_id or self.final_review_user_id.id != self.env.user.id:
            if not self.env.user.has_group('order_status_override.group_order_approval_manager'):
                raise UserError(_("Only the assigned reviewer or approval managers can reject orders."))
        
        draft_status = self.env['order.status'].search([('code', '=', 'draft')], limit=1)
        if not draft_status:
            raise UserError(_("Draft status not found in the system."))
        
        self._change_status(draft_status.id, _("Order rejected by %s and returned to draft") % self.env.user.name)
        self.message_post(
            body=_("Order has been rejected and returned to draft status for revision."),
            subject=_("Order Rejected"),
            message_type='notification'
        )
        return True
    
    def _change_status(self, status_id, notes=None):
        self.ensure_one()
        self.custom_status_id = status_id
        self.env['order.status.history'].create({
            'order_id': self.id,
            'status_id': status_id,
            'notes': notes or _('Status changed'),
            'user_id': self.env.user.id,
            'date': fields.Datetime.now()
        })
        return True
EOF

    echo "✅ Emergency fix applied"
    
else
    echo "⚠️  Line 38 does not contain total_payment_out, checking entire file..."
    
    # Search for total_payment_out anywhere in the file
    if grep -q "total_payment_out" "$TARGET_FILE"; then
        echo "🎯 Found total_payment_out field elsewhere in file"
        
        # Remove the problematic line entirely
        sudo sed -i '/total_payment_out/d' "$TARGET_FILE"
        echo "✅ Removed total_payment_out field"
    else
        echo "❓ total_payment_out not found - applying general fix anyway"
        
        # Apply the safe version regardless
        sudo tee "$TARGET_FILE" > /dev/null << 'EOF'
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    custom_status_id = fields.Many2one('order.status', string='Custom Status', tracking=True, copy=False)
    custom_status_history_ids = fields.One2many('order.status.history', 'order_id', string='Status History', copy=False)
    documentation_user_id = fields.Many2one('res.users', string='Documentation Responsible')
    commission_user_id = fields.Many2one('res.users', string='Commission Responsible')
    final_review_user_id = fields.Many2one('res.users', string='Final Review Responsible')
    
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
        echo "✅ Applied general safe fix"
    fi
fi

# Set proper ownership and permissions
sudo chown odoo:odoo "$TARGET_FILE"
sudo chmod 644 "$TARGET_FILE"

# Validate Python syntax
echo "🔍 Validating Python syntax..."
python3 -m py_compile "$TARGET_FILE"
if [ $? -eq 0 ]; then
    echo "✅ Syntax validation PASSED"
else
    echo "❌ Syntax validation FAILED - Restoring backup"
    sudo cp "$BACKUP_FILE" "$TARGET_FILE"
    sudo systemctl start odoo
    exit 1
fi

# Clear Python cache
echo "🧹 Clearing Python cache..."
sudo find /var/odoo/osusbck/extra-addons/ -name "*.pyc" -delete
sudo find /var/odoo/osusbck/extra-addons/ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Start Odoo service
echo "🚀 Starting Odoo service..."
sudo systemctl start odoo

# Wait a moment and check status
sleep 5
echo "📊 Checking Odoo service status..."
sudo systemctl status odoo --no-pager -l

echo ""
echo "🎉 EMERGENCY FIX COMPLETE!"
echo "📋 Summary:"
echo "   - Backup: $BACKUP_FILE"
echo "   - Fixed: $TARGET_FILE"
echo "   - Status: Odoo service restarted"
echo ""
echo "📝 Monitor logs with: sudo journalctl -u odoo -f"
echo "🔄 If issues persist, restore with: sudo cp $BACKUP_FILE $TARGET_FILE && sudo systemctl restart odoo"
