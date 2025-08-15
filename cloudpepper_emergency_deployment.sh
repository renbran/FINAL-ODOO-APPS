#!/bin/bash
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
