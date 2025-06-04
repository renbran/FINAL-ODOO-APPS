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
            if picking.state == 'done':
                account_moves = picking.account_move_ids.filtered(
                    lambda move: move.state in ['posted']
                )
                
                if account_moves:
                    try:
                        if self.state in ['draft', 'sent']:
                            self.button_confirm()
                        self.commission_posted = True
                        _logger.info("Commission posted for PO %s", self.name)
                    except Exception as e:
                        _logger.error("Error posting commission for PO %s: %s", self.name, str(e))

    def action_view_picking(self):
        res = super().action_view_picking()
        for order in self:
            if order.origin_so_id:
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
                    _logger.info("Manually posted commission for PO %s", order.name)
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
        """Scheduled action to check and post commission purchase orders."""
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
                _logger.error("Error in scheduled commission check for PO %s: %s", purchase_order.name, str(e))
                continue
        
        _logger.info("Processed %s commission purchase orders in scheduled job", processed_count)
        return processed_count