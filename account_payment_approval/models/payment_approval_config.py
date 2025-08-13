from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class PaymentApprovalConfig(models.Model):
    """Payment Approval Configuration Model"""
    _name = 'payment.approval.config'
    _description = 'Payment Approval Configuration'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company', 
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    
    # Approval Thresholds
    outbound_approval_threshold = fields.Float(
        string='Outbound Payment Threshold',
        default=1000.0,
        help="Minimum amount requiring approval for outbound payments"
    )
    
    inbound_approval_threshold = fields.Float(
        string='Inbound Payment Threshold', 
        default=5000.0,
        help="Minimum amount requiring approval for inbound payments"
    )
    
    tier_2_threshold = fields.Float(
        string='Tier 2 Approval Threshold',
        default=10000.0,
        help="Amount requiring second-level approval"
    )
    
    tier_3_threshold = fields.Float(
        string='Tier 3 Approval Threshold',
        default=50000.0,
        help="Amount requiring third-level approval"
    )
    
    # Approver Configuration
    reviewer_ids = fields.Many2many(
        'res.users',
        'payment_config_reviewer_rel',
        'config_id', 'user_id',
        string='Authorized Reviewers',
        domain=[('active', '=', True)]
    )
    
    approver_ids = fields.Many2many(
        'res.users',
        'payment_config_approver_rel', 
        'config_id', 'user_id',
        string='Authorized Approvers',
        domain=[('active', '=', True)]
    )
    
    authorizer_ids = fields.Many2many(
        'res.users',
        'payment_config_authorizer_rel',
        'config_id', 'user_id',
        string='Authorized Authorizers',
        domain=[('active', '=', True)]
    )
    
    # Workflow Settings
    auto_submit_on_create = fields.Boolean(
        string='Auto Submit on Create',
        default=False,
        help="Automatically submit payments for approval when created"
    )
    
    require_signature_all_stages = fields.Boolean(
        string='Require Signature at All Stages',
        default=True,
        help="Require digital signature at each workflow stage"
    )
    
    enable_qr_verification = fields.Boolean(
        string='Enable QR Verification',
        default=True,
        help="Generate QR codes for payment verification"
    )
    
    auto_post_after_qr_validation = fields.Boolean(
        string='Auto Post After QR Validation',
        default=False,
        help="Automatically post payments after QR validation"
    )
    
    # Email Settings
    send_email_notifications = fields.Boolean(
        string='Send Email Notifications',
        default=True,
        help="Send email notifications for workflow changes"
    )
    
    notification_emails = fields.Text(
        string='Notification Email Addresses',
        help="Additional email addresses to notify (comma-separated)"
    )
    
    # Security Settings
    require_2fa_for_authorization = fields.Boolean(
        string='Require 2FA for Authorization',
        default=False,
        help="Require two-factor authentication for final authorization"
    )
    
    log_all_workflow_actions = fields.Boolean(
        string='Log All Workflow Actions',
        default=True,
        help="Log all workflow actions for audit trail"
    )
    
    # QR Settings
    qr_code_expiry_days = fields.Integer(
        string='QR Code Expiry (Days)',
        default=30,
        help="Number of days after which QR codes expire"
    )
    
    qr_max_scan_attempts = fields.Integer(
        string='Max QR Scan Attempts',
        default=10,
        help="Maximum number of QR scan attempts before blocking"
    )
    
    # Bulk Operations
    max_bulk_operations = fields.Integer(
        string='Max Bulk Operations',
        default=50,
        help="Maximum number of payments that can be processed in bulk"
    )
    
    enable_bulk_approvals = fields.Boolean(
        string='Enable Bulk Approvals',
        default=True,
        help="Allow bulk approval operations"
    )
    
    @api.constrains('outbound_approval_threshold', 'inbound_approval_threshold')
    def _check_positive_thresholds(self):
        """Ensure thresholds are positive"""
        for config in self:
            if config.outbound_approval_threshold < 0:
                raise ValidationError(_("Outbound approval threshold must be positive"))
            if config.inbound_approval_threshold < 0:
                raise ValidationError(_("Inbound approval threshold must be positive"))
    
    @api.constrains('tier_2_threshold', 'tier_3_threshold', 'outbound_approval_threshold')
    def _check_tier_progression(self):
        """Ensure tier thresholds are in ascending order"""
        for config in self:
            if config.tier_2_threshold <= config.outbound_approval_threshold:
                raise ValidationError(_("Tier 2 threshold must be greater than basic approval threshold"))
            if config.tier_3_threshold <= config.tier_2_threshold:
                raise ValidationError(_("Tier 3 threshold must be greater than Tier 2 threshold"))
    
    @api.constrains('qr_code_expiry_days', 'qr_max_scan_attempts', 'max_bulk_operations')
    def _check_positive_values(self):
        """Ensure various numeric fields are positive"""
        for config in self:
            if config.qr_code_expiry_days <= 0:
                raise ValidationError(_("QR code expiry days must be positive"))
            if config.qr_max_scan_attempts <= 0:
                raise ValidationError(_("Max QR scan attempts must be positive"))
            if config.max_bulk_operations <= 0:
                raise ValidationError(_("Max bulk operations must be positive"))
    
    @api.model
    def get_company_config(self, company_id=None):
        """Get configuration for a specific company"""
        if not company_id:
            company_id = self.env.company.id
        
        config = self.search([('company_id', '=', company_id)], limit=1)
        if not config:
            # Create default config if none exists
            config = self.create({'company_id': company_id})
        
        return config
    
    def sync_to_system_parameters(self):
        """Sync configuration to system parameters"""
        self.ensure_one()
        
        params = self.env['ir.config_parameter'].sudo()
        
        # Update all system parameters
        params.set_param('account_payment_approval.outbound_approval_threshold', self.outbound_approval_threshold)
        params.set_param('account_payment_approval.inbound_approval_threshold', self.inbound_approval_threshold)
        params.set_param('account_payment_approval.tier_2_threshold', self.tier_2_threshold)
        params.set_param('account_payment_approval.tier_3_threshold', self.tier_3_threshold)
        params.set_param('account_payment_approval.auto_submit_on_create', self.auto_submit_on_create)
        params.set_param('account_payment_approval.require_signature_all_stages', self.require_signature_all_stages)
        params.set_param('account_payment_approval.enable_qr_verification', self.enable_qr_verification)
        params.set_param('account_payment_approval.auto_post_after_qr_validation', self.auto_post_after_qr_validation)
        params.set_param('account_payment_approval.send_email_notifications', self.send_email_notifications)
        params.set_param('account_payment_approval.require_2fa_for_authorization', self.require_2fa_for_authorization)
        params.set_param('account_payment_approval.log_all_workflow_actions', self.log_all_workflow_actions)
        params.set_param('account_payment_approval.qr_code_expiry_days', self.qr_code_expiry_days)
        params.set_param('account_payment_approval.qr_max_scan_attempts', self.qr_max_scan_attempts)
        params.set_param('account_payment_approval.max_bulk_operations', self.max_bulk_operations)
        params.set_param('account_payment_approval.enable_bulk_approvals', self.enable_bulk_approvals)
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to sync to system parameters"""
        configs = super().create(vals_list)
        for config in configs:
            config.sync_to_system_parameters()
        return configs
    
    def write(self, vals):
        """Override write to sync to system parameters"""
        result = super().write(vals)
        for config in self:
            config.sync_to_system_parameters()
        return result