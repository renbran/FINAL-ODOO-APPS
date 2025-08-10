# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class PaymentVerificationLog(models.Model):
    _name = 'payment.verification.log'
    _description = 'Payment Verification Log'
    _order = 'verification_date desc'
    _rec_name = 'display_name'

    # ============================================================================
    # FIELDS
    # ============================================================================
    
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )
    
    verification_date = fields.Datetime(
        string='Verification Date',
        default=fields.Datetime.now,
        required=True
    )
    
    payment_id = fields.Many2one(
        'account.payment',
        string='Payment Voucher',
        required=True,
        ondelete='cascade'
    )
    
    token = fields.Char(
        string='Verification Token',
        required=True,
        help="QR verification token"
    )
    
    ip_address = fields.Char(
        string='IP Address',
        help="IP address of the verifier"
    )
    
    is_successful = fields.Boolean(
        string='Successful',
        default=True,
        help="Whether the verification was successful"
    )
    
    is_api_call = fields.Boolean(
        string='API Call',
        default=False,
        help="Whether this was an API verification call"
    )
    
    action_type = fields.Selection([
        ('view', 'View Voucher'),
        ('verify', 'Verify QR Code'),
        ('download', 'Download PDF'),
        ('api_access', 'API Access'),
    ], string='Action Type', default='view')
    
    country_id = fields.Many2one(
        'res.country',
        string='Country',
        help="Country based on IP geolocation"
    )
    
    city = fields.Char(
        string='City',
        help="City based on IP geolocation"
    )
    
    error_message = fields.Text(
        string='Error Message',
        help="Error message if verification failed"
    )
    
    user_agent = fields.Char(
        string='User Agent',
        help="Browser/device information"
    )
    
    # ============================================================================
    # COMPUTED FIELDS
    # ============================================================================
    
    @api.depends('payment_id', 'action_type', 'verification_date')
    def _compute_display_name(self):
        """Compute display name for better identification"""
        for record in self:
            payment_ref = record.payment_id.voucher_number or record.payment_id.name or 'Unknown'
            action_text = dict(record._fields['action_type'].selection).get(record.action_type, 'Unknown')
            date_str = record.verification_date.strftime('%Y-%m-%d %H:%M') if record.verification_date else 'No Date'
            record.display_name = f"{payment_ref} - {action_text} ({date_str})"
    
    # ============================================================================
    # BUSINESS LOGIC METHODS
    # ============================================================================
    
    def action_view_payment_voucher(self):
        """Open the related payment voucher"""
        self.ensure_one()
        if not self.payment_id:
            raise UserError(_("No payment voucher associated with this log entry."))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payment Voucher'),
            'res_model': 'account.payment',
            'res_id': self.payment_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    @api.model
    def create_verification_log(self, payment_id, token, action_type='view', **kwargs):
        """Create a verification log entry"""
        try:
            vals = {
                'payment_id': payment_id,
                'token': token,
                'action_type': action_type,
                'verification_date': fields.Datetime.now(),
                'is_successful': kwargs.get('is_successful', True),
                'is_api_call': kwargs.get('is_api_call', False),
                'ip_address': kwargs.get('ip_address'),
                'country_id': kwargs.get('country_id'),
                'city': kwargs.get('city'),
                'error_message': kwargs.get('error_message'),
                'user_agent': kwargs.get('user_agent'),
            }
            
            return self.create(vals)
            
        except Exception as e:
            _logger.error(f"Error creating verification log: {e}")
            return False
    
    @api.model
    def get_verification_stats(self, payment_id=None):
        """Get verification statistics"""
        domain = []
        if payment_id:
            domain = [('payment_id', '=', payment_id)]
        
        logs = self.search(domain)
        
        return {
            'total_verifications': len(logs),
            'successful_verifications': len(logs.filtered('is_successful')),
            'api_calls': len(logs.filtered('is_api_call')),
            'unique_ips': len(set(logs.mapped('ip_address')) - {False}),
            'countries': logs.mapped('country_id.name'),
            'action_types': {
                action[0]: len(logs.filtered(lambda l: l.action_type == action[0]))
                for action in self._fields['action_type'].selection
            }
        }


class PaymentVerificationDashboard(models.TransientModel):
    """Transient model for verification dashboard"""
    _name = 'payment.verification.dashboard'
    _description = 'Payment Verification Dashboard'
    
    total_verifications = fields.Integer(string='Total Verifications', readonly=True)
    successful_verifications = fields.Integer(string='Successful Verifications', readonly=True)
    failed_verifications = fields.Integer(string='Failed Verifications', readonly=True)
    api_calls = fields.Integer(string='API Calls', readonly=True)
    unique_ips = fields.Integer(string='Unique IP Addresses', readonly=True)
    
    verification_logs = fields.One2many(
        'payment.verification.log',
        compute='_compute_verification_logs'
    )
    
    @api.depends('total_verifications')
    def _compute_verification_logs(self):
        """Get recent verification logs"""
        for record in self:
            record.verification_logs = self.env['payment.verification.log'].search([], limit=50)
    
    def action_view_verification_logs(self):
        """View all verification logs"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Verification Logs'),
            'res_model': 'payment.verification.log',
            'view_mode': 'tree,form',
            'target': 'current',
        }
    
    def action_regenerate_qr_token(self):
        """Regenerate QR tokens for active payments"""
        active_payments = self.env['account.payment'].search([
            ('approval_state', 'not in', ['draft', 'cancelled'])
        ])
        
        count = 0
        for payment in active_payments:
            if not payment.verification_token:
                payment._generate_verification_token()
                count += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Regenerated tokens for %d payments') % count,
                'type': 'success',
            }
        }
