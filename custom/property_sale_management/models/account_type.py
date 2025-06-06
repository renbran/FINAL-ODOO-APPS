from odoo import models, fields

class AccountMoveType(models.Model):
    _name = 'account.move.type'
    _description = 'Invoice Type'
    
    name = fields.Char(string='Type Name', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)