from odoo import models, fields, api
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    description = fields.Char(string="Description")
    origin_so_id = fields.Many2one('sale.order', string="Source SO", readonly=True)
    commission_posted = fields.Boolean(string="Commission Posted", default=False)

    def _post_purchase_order_on_receipt(self, picking):
        """Post the purchase order when the receipt is recorded or paid."""
        self.ensure_one()
        
        if not self.commission_posted and picking.state == 'done':
            # Check if the picking has associated account moves (payments)
            account_moves = picking.account_move_ids.filtered(
                lambda move: move.state in ['in_payment', 'paid']
            )
            
            if account_moves:
                try:
                    self.button_confirm()
                    self.commission_posted = True
                except Exception as e:
                    # Log the error and keep the original state
                    self.env.cr.rollback()
                    self.env.logger.error(f"Error posting commission PO {self.name}: {str(e)}")
                    raise UserError(f"Could not post purchase order {self.name}. Please check the logs.")

    def action_view_picking(self):
        """Override the action_view_picking method to post the purchase order on receipt."""
        res = super(PurchaseOrder, self).action_view_picking()
        for order in self:
            for picking in order.picking_ids:
                order._post_purchase_order_on_receipt(picking)
        return res

    def action_force_post(self):
        """Manual action to force post the purchase order."""
        for order in self:
            if not order.commission_posted:
                try:
                    order.button_confirm()
                    order.commission_posted = True
                except Exception as e:
                    self.env.cr.rollback()
                    raise UserError(f"Could not force post purchase order {order.name}: {str(e)}")
        return True

    @api.model
    def _check_commission_purchase_orders(self):
        """
        Scheduled action to check and post commission purchase orders 
        when their receipts are paid or in payment.
        """
        # Find commission purchase orders not yet posted
        unposted_commission_pos = self.search([
            ('commission_posted', '=', False),
            ('origin_so_id', '!=', False)
        ])
        
        for purchase_order in unposted_commission_pos:
            try:
                for picking in purchase_order.picking_ids:
                    purchase_order._post_purchase_order_on_receipt(picking)
            except Exception as e:
                # Log the error for the specific purchase order
                self.env.logger.error(f"Error processing commission PO {purchase_order.name}: {str(e)}")