from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.model
    def get_order_status(self, order_id):
        """Get order status information for the widget"""
        try:
            order = self.browse(order_id)
            if not order.exists():
                return {'error': 'Order not found'}
            
            return {
                'status': order.state,
                'status_display': dict(order._fields['state'].selection).get(order.state, order.state),
                'order_id': order.id,
                'name': order.name,
                'partner_name': order.partner_id.name,
                'amount_total': order.amount_total,
                'currency': order.currency_id.name,
            }
        except Exception as e:
            return {'error': str(e)}
    
    def update_status(self, new_status):
        """Update order status safely"""
        try:
            self.ensure_one()
            
            # Map widget statuses to Odoo states
            status_mapping = {
                'approved': 'sale',
                'rejected': 'cancel',
                'draft': 'draft',
                'confirmed': 'sale'
            }
            
            if new_status in status_mapping:
                odoo_state = status_mapping[new_status]
                
                # Validate state transition
                if odoo_state == 'sale' and self.state == 'draft':
                    self.action_confirm()
                elif odoo_state == 'cancel':
                    self.action_cancel()
                else:
                    self.state = odoo_state
                
                return {'success': True, 'new_status': self.state}
            else:
                raise ValidationError(f"Invalid status: {new_status}")
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
