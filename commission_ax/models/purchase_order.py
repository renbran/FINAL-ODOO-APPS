from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    description = fields.Char(string="Commission Description")
    origin_so_id = fields.Many2one('sale.order', string="Source Sale Order", readonly=True)
    commission_posted = fields.Boolean(string="Commission Posted", default=False)

    def action_view_source_sale_order(self):
        """Action to view the source sale order."""
        self.ensure_one()
        if not self.origin_so_id:
            raise UserError("No source sale order found for this purchase order.")
        
        return {
            'name': 'Source Sale Order',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.origin_so_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_force_post(self):
        """Manual action to force post the purchase order."""
        for order in self:
            if not order.commission_posted:
                try:
                    if order.state == 'draft':
                        order.button_confirm()
                    order.commission_posted = True
                    _logger.info(f"Commission posted for PO {order.name}")
                except Exception as e:
                    _logger.error(f"Error posting commission for PO {order.name}: {str(e)}")
                    raise UserError(f"Error posting commission: {str(e)}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Commission posted successfully!',
                'type': 'success',
                'sticky': False,
            }
        }

    def _post_purchase_order_on_receipt(self, picking):
        """Post the purchase order when the receipt is recorded or paid."""
        if not self.commission_posted and self.origin_so_id:
            # Check if the picking is done (completed)
            if picking.state == 'done':
                # Check if there are any account moves associated
                if picking.move_ids:
                    try:
                        if self.state == 'draft':
                            self.button_confirm()
                        self.commission_posted = True
                        _logger.info(f"Auto-posted commission for PO {self.name}")
                    except Exception as e:
                        _logger.error(f"Error auto-posting commission for PO {self.name}: {str(e)}")
                        # Don't raise error here to prevent blocking other operations

    @api.model
    def _check_commission_purchase_orders(self):
        """
        Scheduled action to check and post commission purchase orders 
        when their receipts are paid or in payment.
        """
        # Find commission purchase orders not yet posted
        unposted_commission_pos = self.search([
            ('commission_posted', '=', False),
            ('origin_so_id', '!=', False),
            ('state', 'in', ['purchase', 'done'])
        ])
        
        for purchase_order in unposted_commission_pos:
            for picking in purchase_order.picking_ids:
                if picking.state == 'done':
                    purchase_order._post_purchase_order_on_receipt(picking)
                    break  # Only need one completed picking

    @api.model
    def create(self, vals):
        """Override create to set description from origin SO if available."""
        record = super().create(vals)
        if record.origin_so_id and not record.description:
            # Set a default description based on the partner and SO
            partner_name = record.partner_id.name if record.partner_id else "Partner"
            record.description = f"Commission for {partner_name} - SO: {record.origin_so_id.name}"
        return record