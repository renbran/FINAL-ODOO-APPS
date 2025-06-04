from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    description = fields.Char(string="Description")
    origin_so_id = fields.Many2one(
        'sale.order', 
        string="Source SO", 
        readonly=True,
        help="Original Sale Order that generated this commission purchase order"
    )
    commission_posted = fields.Boolean(
        string="Commission Posted", 
        default=False,
        help="Indicates if commission has been posted for this purchase order"
    )

    def _post_purchase_order_on_receipt(self, picking):
        """Post the purchase order when the receipt is recorded or paid."""
        self.ensure_one()
        if not self.commission_posted and self.origin_so_id:
            # Check if the picking is done (completed)
            if picking.state == 'done':
                # Check if the picking has associated account moves (payments)
                account_moves = picking.account_move_ids.filtered(
                    lambda move: move.state in ['posted']
                )
                
                if account_moves:
                    try:
                        if self.state in ['draft', 'sent']:
                            self.button_confirm()
                        self.commission_posted = True
                        _logger.info(f"Commission posted for PO {self.name}")
                    except Exception as e:
                        _logger.error(f"Error posting commission for PO {self.name}: {str(e)}")
                        # Don't raise the error to avoid blocking other operations
                        pass

    def action_view_picking(self):
        """Override the action_view_picking method to post the purchase order on receipt."""
        res = super(PurchaseOrder, self).action_view_picking()
        for order in self:
            if order.origin_so_id:  # Only process commission-related POs
                for picking in order.picking_ids:
                    order._post_purchase_order_on_receipt(picking)
        return res

    def action_force_post(self):
        """Manual action to force post the purchase order."""
        for order in self:
            if not order.commission_posted and order.origin_so_id:
                try:
                    if order.state in ['draft', 'sent']:
                        order.button_confirm()
                    order.commission_posted = True
                    _logger.info(f"Manually posted commission for PO {order.name}")
                except Exception as e:
                    raise UserError(_("Error posting commission: %s") % str(e))
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Commission posted successfully!'),
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model
    def _check_commission_purchase_orders(self):
        """
        Scheduled action to check and post commission purchase orders 
        when their receipts are paid or in payment.
        This method is designed to be called by a cron job.
        """
        # Find commission purchase orders not yet posted
        unposted_commission_pos = self.search([
            ('commission_posted', '=', False),
            ('origin_so_id', '!=', False)
        ])
        
        processed_count = 0
        for purchase_order in unposted_commission_pos:
            try:
                for picking in purchase_order.picking_ids:
                    if picking.state == 'done':
                        purchase_order._post_purchase_order_on_receipt(picking)
                        if purchase_order.commission_posted:
                            processed_count += 1
                            break
            except Exception as e:
                _logger.error(f"Error in scheduled commission check for PO {purchase_order.name}: {str(e)}")
                continue
        
        _logger.info(f"Processed {processed_count} commission purchase orders in scheduled job")
        return processed_count

    def write(self, vals):
        """Override write to handle commission posting logic"""
        result = super(PurchaseOrder, self).write(vals)
        
        # If state changes to purchase or done, check commission posting
        if 'state' in vals and vals['state'] in ['purchase', 'done']:
            for order in self:
                if order.origin_so_id and not order.commission_posted:
                    # Check if any picking is done
                    done_pickings = order.picking_ids.filtered(lambda p: p.state == 'done')
                    if done_pickings:
                        order.commission_posted = True
        
        return result

    @api.model
    def create(self, vals):
        """Override create to handle commission-related purchase orders"""
        result = super(PurchaseOrder, self).create(vals)
        
        # Log creation of commission-related PO
        if result.origin_so_id:
            _logger.info(f"Created commission purchase order {result.name} for SO {result.origin_so_id.name}")
        
        return result