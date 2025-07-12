from odoo import models, fields, api, _
from odoo.exceptions import UserError

class InternalCommissionPurchase(models.Model):
    _name = 'internal.commission.purchase'
    _description = 'Internal Commission Purchase'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    internal_commission_id = fields.Many2one('internal.commission', string='Internal Commission', required=True)
    partner_id = fields.Many2one('res.partner', related='internal_commission_id.partner_id', string='Vendor', readonly=True)
    amount = fields.Monetary(related='internal_commission_id.amount', string='Commission Amount', readonly=True)
    currency_id = fields.Many2one(related='internal_commission_id.currency_id', readonly=True)
    
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', readonly=True)
    purchase_order_state = fields.Selection(related='purchase_order_id.state', string='PO Status', readonly=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('po_created', 'PO Created'),
        ('po_confirmed', 'PO Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('internal.commission.purchase') or _('New')
        return super(InternalCommissionPurchase, self).create(vals)

    def action_create_purchase_order(self):
        self.ensure_one()
        if self.purchase_order_id:
            raise UserError(_("Purchase Order already exists for this commission."))

        po_vals = {
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'order_line': [(0, 0, {
                'name': f"Commission for {self.internal_commission_id.display_name}",
                'product_id': self.env.ref('property_sale_management.product_commission_service').id,
                'product_qty': 1,
                'price_unit': self.amount,
            })],
        }
        purchase_order = self.env['purchase.order'].create(po_vals)
        self.write({
            'purchase_order_id': purchase_order.id,
            'state': 'po_created'
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': purchase_order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    @api.model
    def _update_po_status(self):
        for record in self.search([('state', 'in', ['po_created', 'po_confirmed'])]):
            if record.purchase_order_state == 'purchase':
                record.state = 'po_confirmed'
            elif record.purchase_order_state == 'done':
                record.state = 'done'