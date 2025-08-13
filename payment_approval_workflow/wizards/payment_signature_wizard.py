from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PaymentSignatureWizard(models.TransientModel):
    _name = 'payment.signature.wizard'
    _description = 'Payment Signature Wizard'

    payment_id = fields.Many2one(
        'account.payment',
        string='Payment',
        required=True,
        readonly=True
    )
    
    action_type = fields.Selection([
        ('review', 'Review'),
        ('approve', 'Approve'),
        ('authorize', 'Authorize'),
    ], string='Action Type', required=True, readonly=True)
    
    signature = fields.Binary(
        string='Digital Signature',
        required=True,
        help="Please provide your digital signature"
    )
    
    notes = fields.Text(
        string='Notes',
        help="Additional notes or comments"
    )

    @api.model
    def default_get(self, fields_list):
        """Set default values"""
        res = super().default_get(fields_list)
        
        # Get payment from context
        payment_id = self.env.context.get('default_payment_id')
        action_type = self.env.context.get('default_action_type')
        
        if payment_id:
            res['payment_id'] = payment_id
        if action_type:
            res['action_type'] = action_type
            
        return res

    def action_confirm_signature(self):
        """Confirm the signature and proceed with the action"""
        self.ensure_one()
        
        if not self.signature:
            raise UserError(_("Digital signature is required."))
        
        payment = self.payment_id
        
        if self.action_type == 'review':
            payment.confirm_review(self.signature)
        elif self.action_type == 'approve':
            payment.confirm_approve(self.signature)
        elif self.action_type == 'authorize':
            payment.confirm_authorize(self.signature)
        
        # Add notes if provided
        if self.notes:
            payment.message_post(
                body=_("Additional notes from %s: %s") % (
                    dict(self._fields['action_type'].selection).get(self.action_type),
                    self.notes
                ),
                subtype_xmlid='mail.mt_note'
            )
        
        return {'type': 'ir.actions.act_window_close'}
