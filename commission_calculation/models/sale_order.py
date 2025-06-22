from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Commission fields
    commission_status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid')
    ], string='Commission Status', default='draft', copy=False)

    grand_total_commission = fields.Monetary(
        string='Total Commission',
        compute='_compute_grand_total_commission',
        store=True,
        currency_field='currency_id'
    )

    # External commission partners
    broker_partner_id = fields.Many2one('res.partner', string='Broker Partner')
    broker_commission_amount = fields.Monetary(string='Broker Commission', currency_field='currency_id')
    referral_partner_id = fields.Many2one('res.partner', string='Referral Partner')
    referral_commission_amount = fields.Monetary(string='Referral Commission', currency_field='currency_id')
    # Add more external commission fields as needed

    # Internal commission partners
    agent1_id = fields.Many2one('hr.employee', string='Agent 1')
    agent1_commission_amount = fields.Monetary(string='Agent 1 Commission', currency_field='currency_id')
    # Add more internal commission fields as needed

    commission_processed = fields.Boolean(
        string='Commission Processed',
        copy=False,
        help="Indicates if commission POs have been created"
    )

    deal_id = fields.Char(string='Deal ID', help='Unique identifier for the deal associated with this sale order.')

    def action_confirm(self):
        """Override confirm to ensure commission validation"""
        for order in self:
            if order.commission_status == 'draft' and order.grand_total_commission > 0:
                raise UserError(_("Please calculate commissions before confirming the order!"))
        res = super().action_confirm()
        # Automatically create commission POs when order is confirmed
        self._create_commission_pos()
        return res

    def _create_commission_pos(self):
        """Automatically create commission POs when order is confirmed and invoiced"""
        commission_product = self.env.ref('your_module.product_product_commission')
        PurchaseOrder = self.env['purchase.order']

        for order in self:
            if order.commission_processed or not order.invoice_ids:
                continue

            # Prepare commission lines grouped by partner
            partner_commissions = {}

            # External commissions
            if order.broker_partner_id and order.broker_commission_amount > 0:
                partner_commissions.setdefault(order.broker_partner_id, []).append({
                    'amount': order.broker_commission_amount,
                    'description': f"Broker commission for {order.name}"
                })

            if order.referral_partner_id and order.referral_commission_amount > 0:
                partner_commissions.setdefault(order.referral_partner_id, []).append({
                    'amount': order.referral_commission_amount,
                    'description': f"Referral commission for {order.name}"
                })

            # ... [Add other external commission partners] ...

            # Internal commissions
            if order.agent1_id and order.agent1_commission_amount > 0:
                partner = order.agent1_id.address_home_id
                if partner:
                    partner_commissions.setdefault(partner, []).append({
                        'amount': order.agent1_commission_amount,
                        'description': f"Agent 1 commission for {order.name}"
                    })

            # ... [Add other internal commission partners] ...

            # Create POs for each partner
            for partner, commissions in partner_commissions.items():
                po_lines = []
                for comm in commissions:
                    po_lines.append((0, 0, {
                        'product_id': commission_product.id,
                        'name': comm['description'],
                        'product_qty': 1,
                        'price_unit': comm['amount'],
                        'date_planned': fields.Date.today(),
                    }))

                po_vals = {
                    'partner_id': partner.id,
                    'origin': order.name,
                    'order_line': po_lines,
                    'commission_sale_order_id': order.id,
                }
                PurchaseOrder.create(po_vals)

            order.commission_processed = True

    def action_create_commission_po(self):
        """Manual action to create commission POs"""
        self._create_commission_pos()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Commission purchase orders have been created.'),
                'sticky': False,
                'type': 'success',
            }
        }

    @api.depends(
        'broker_commission_amount',
        'referral_commission_amount',
        'agent1_commission_amount',
        # Add other commission amount fields here
    )
    def _compute_grand_total_commission(self):
        for order in self:
            total = 0.0
            total += order.broker_commission_amount or 0.0
            total += order.referral_commission_amount or 0.0
            total += order.agent1_commission_amount or 0.0
            # Add other commission amount fields here
            order.grand_total_commission = total

    @api.model
    def _process_commission_pos_cron(self):
        """Cron job to process commissions for confirmed orders"""
        orders = self.search([
            ('state', '=', 'sale'),
            ('invoice_ids', '!=', False),
            ('commission_processed', '=', False),
            ('commission_status', 'in', ['confirmed', 'paid'])
        ])
        orders._create_commission_pos()