from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    internal_commission_id = fields.Many2one('internal.commission', string='Internal Commission', readonly=True)
    broker_commission_id = fields.Many2one('broker.commission.invoice', string='Broker Commission', readonly=True)
    is_commission_bill = fields.Boolean(string='Is Commission Bill', compute='_compute_is_commission_bill', store=True)

    @api.depends('internal_commission_id', 'broker_commission_id')
    def _compute_is_commission_bill(self):
        for move in self:
            move.is_commission_bill = bool(move.internal_commission_id or move.broker_commission_id)

    def action_view_commission(self):
        self.ensure_one()
        if self.internal_commission_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'internal.commission',
                'res_id': self.internal_commission_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        elif self.broker_commission_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'broker.commission.invoice',
                'res_id': self.broker_commission_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return False