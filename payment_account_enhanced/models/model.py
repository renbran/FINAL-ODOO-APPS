from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    # Additional fields for voucher
    destination_account_id = fields.Many2one(
        'account.account',
        string='Destination Account',
        domain="[('account_type', 'in', ['asset_receivable', 'liability_payable', 'asset_cash', 'liability_credit_card'])]",
        help="Account where the payment will be posted"
    )
    
    # Override the name field to have a better label for voucher context
    name = fields.Char(
        string='Number',
        readonly=True,
        copy=False,
        help="Payment reference number"
    )
    
    received_by = fields.Char(
        string='Received By',
        help="Person who received the payment"
    )
    
    payment_description = fields.Text(
        string='Payment Description',
        help="Detailed description of the payment"
    )
    
    authorization_code = fields.Char(
        string='Authorization Code',
        help="Authorization code for the payment"
    )
    
    remarks = fields.Text(
        string='Remarks/Memo',
        help="Additional remarks or memo for the payment"
    )
    
    # One2many field for journal items
    line_ids = fields.One2many(
        'account.move.line', 
        'move_id', 
        string='Journal Items',
        related='move_id.line_ids',
        readonly=True,
        help="Journal entries created by this payment"
    )
    
    @api.model
    def create(self, vals):
        # The standard name field will be handled by the parent class
        return super(AccountPayment, self).create(vals)
    
    def action_print_voucher(self):
        """Print payment voucher"""
        return self.env.ref('payment_account_enhanced.action_report_payment_voucher').report_action(self)
    
    @api.onchange('journal_id')
    def _onchange_journal_id_destination_account(self):
        """Set default destination account based on journal"""
        if self.journal_id:
            if self.journal_id.default_account_id:
                self.destination_account_id = self.journal_id.default_account_id.id
