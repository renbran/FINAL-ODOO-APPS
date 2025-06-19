from odoo import models, fields

class AccountStatement(models.Model):
    _name = 'account.statement'
    _description = 'Account Statement'
    _order = 'date desc, id desc'

    name = fields.Char(string='Statement Name', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    # ...add more fields as needed...