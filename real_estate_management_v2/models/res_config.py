from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    default_commission_percentage = fields.Float(
        string='Default Commission Percentage',
        default=2.0,
        config_parameter='real_estate_management_v2.default_commission_percentage',
        help="Default percentage for internal commissions"
    )
    
    auto_create_commission = fields.Boolean(
        string='Auto-create Commission on Sale Confirmation',
        config_parameter='real_estate_management_v2.auto_create_commission',
        help="Automatically create internal commission when a property sale is confirmed"
    )
    
    commission_expense_account_id = fields.Many2one(
        'account.account',
        string='Commission Expense Account',
        config_parameter='real_estate_management_v2.commission_expense_account_id',
        domain=[('deprecated', '=', False)],
        help="Default expense account for internal commissions"
    )
    
    commission_journal_id = fields.Many2one(
        'account.journal',
        string='Commission Journal',
        config_parameter='real_estate_management_v2.commission_journal_id',
        domain=[('type', '=', 'general')],
        help="Journal for commission expense entries"
    )