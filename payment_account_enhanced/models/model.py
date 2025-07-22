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
    
    voucher_number = fields.Char(
        string='Voucher Number',
        readonly=True,
        copy=False,
        help="Unique voucher number for this payment"
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
        # Generate voucher number
        if not vals.get('voucher_number'):
            vals['voucher_number'] = self.env['ir.sequence'].next_by_code('payment.voucher') or _('New')
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
