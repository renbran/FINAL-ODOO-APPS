from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    # Add the fields to connect with broker commission and internal commission
    broker_commission_id = fields.Many2one('broker.commission.invoice', string='Broker Commission', 
                                          readonly=True, copy=False)
    internal_commission_id = fields.Many2one('internal.commission', string='Internal Commission', 
                                           readonly=True, copy=False)
    
    # Add the missing type_id field that's causing the error
    type_id = fields.Many2one('account.move.type', string='Invoice Type')