from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PaymentRejectionWizard(models.TransientModel):
    _name = 'payment.rejection.wizard'
    _description = 'Payment Rejection Wizard'

    payment_id = fields.Many2one(
        'account.payment',
        string='Payment',
        required=True,
        readonly=True
    )
    
    rejection_reason = fields.Text(
        string='Rejection Reason',
        required=True,
        help="Please provide a detailed reason for rejection"
    )

    @api.model
    def default_get(self, fields_list):
        """Set default values"""
        res = super().default_get(fields_list)
        
        # Get payment from context
        payment_id = self.env.context.get('default_payment_id')
        if payment_id:
            res['payment_id'] = payment_id
            
        return res

    def action_confirm_rejection(self):
        """Confirm the rejection with reason"""
        self.ensure_one()
        
        if not self.rejection_reason or not self.rejection_reason.strip():
            raise UserError(_("Rejection reason is required."))
        
        self.payment_id.confirm_reject(self.rejection_reason)
        
        return {'type': 'ir.actions.act_window_close'}
