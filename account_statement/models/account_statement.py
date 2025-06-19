from odoo import models, fields

class AccountStatement(models.Model):
    _name = 'account.statement'
    _description = 'Account Statement'

    name = fields.Char(string='Statement Name')
    date = fields.Date(string='Date')
    # ...add more fields as needed...