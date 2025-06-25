from odoo import api, fields, models
from datetime import date


class AccountStatementWizard(models.TransientModel):
    _name = 'account.statement.wizard'
    _description = 'Account Statement Generator'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    date_from = fields.Date(string='From Date', required=True, default=fields.Date.context_today)
    date_to = fields.Date(string='To Date', required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                default=lambda self: self.env.company)
    
    def action_generate_statement(self):
        """Generate the account statement."""
        self.ensure_one()
        vals = {
            'partner_id': self.partner_id.id,
            'date': fields.Date.today(),
            'date_from': self.date_from,
            'date_to': self.date_to,
            'company_id': self.company_id.id,
        }
        statement = self.env['account.statement'].create(vals)
        return {
            'name': 'Account Statement',
            'type': 'ir.actions.act_window',
            'res_model': 'account.statement',
            'res_id': statement.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }
