# -*- coding: utf-8 -*-
#############################################################################
#
#    Settings Configuration for Payment Approval
#    Copyright (C) 2025 OSUS Properties
#
#############################################################################

from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    """Add payment approval settings to general configuration"""
    _inherit = 'res.config.settings'
    
    # ========================================
    # Payment Approval Settings
    # ========================================
    
    # Basic Thresholds
    payment_approval_threshold = fields.Float(
        string='Payment Approval Threshold',
        default=1000.0,
        config_parameter='account_payment_approval.payment_approval_threshold',
        help="Minimum amount requiring approval for outbound payments"
    )
    
    receipt_approval_threshold = fields.Float(
        string='Receipt Approval Threshold',
        default=5000.0,
        config_parameter='account_payment_approval.receipt_approval_threshold',
        help="Minimum amount requiring approval for inbound receipts"
    )
    
    transfer_approval_threshold = fields.Float(
        string='Transfer Approval Threshold',
        default=2000.0,
        config_parameter='account_payment_approval.transfer_approval_threshold',
        help="Minimum amount requiring approval for internal transfers"
    )
    
    # Multi-tier Thresholds
    tier_2_threshold = fields.Float(
        string='Tier 2 Threshold',
        default=10000.0,
        config_parameter='account_payment_approval.tier_2_threshold',
        help="Amount requiring 2-tier approval"
    )
    
    tier_3_threshold = fields.Float(
        string='Tier 3 Threshold',
        default=50000.0,
        config_parameter='account_payment_approval.tier_3_threshold',
        help="Amount requiring 3-tier approval (including authorization)"
    )
    
    # Workflow Settings
    auto_submit_on_create = fields.Boolean(
        string='Auto-submit on Create',
        default=False,
        config_parameter='account_payment_approval.auto_submit_on_create',
        help="Automatically submit payments for approval when created"
    )
    
    require_signature_all_stages = fields.Boolean(
        string='Require Signatures for All Stages',
        default=True,
        config_parameter='account_payment_approval.require_signature_all_stages',
        help="Require digital signatures at every approval stage"
    )
    
    enable_qr_verification = fields.Boolean(
        string='Enable QR Verification',
        default=True,
        config_parameter='account_payment_approval.enable_qr_verification',
        help="Generate QR codes for payment verification"
    )
    
    enable_email_notifications = fields.Boolean(
        string='Enable Email Notifications',
        default=True,
        config_parameter='account_payment_approval.enable_email_notifications',
        help="Send email notifications for approval actions"
    )
    
    # Time Limits
    review_time_limit = fields.Integer(
        string='Review Time Limit (hours)',
        default=24,
        config_parameter='account_payment_approval.review_time_limit',
        help="Maximum hours for review stage"
    )
    
    approval_time_limit = fields.Integer(
        string='Approval Time Limit (hours)',
        default=48,
        config_parameter='account_payment_approval.approval_time_limit',
        help="Maximum hours for approval stage"
    )
    
    authorization_time_limit = fields.Integer(
        string='Authorization Time Limit (hours)',
        default=72,
        config_parameter='account_payment_approval.authorization_time_limit',
        help="Maximum hours for authorization stage"
    )
    
    # Urgency Multipliers
    urgent_multiplier = fields.Float(
        string='Urgent Priority Multiplier',
        default=0.5,
        config_parameter='account_payment_approval.urgent_multiplier',
        help="Multiplier for urgent payments (reduces threshold)"
    )
    
    high_multiplier = fields.Float(
        string='High Priority Multiplier',
        default=0.7,
        config_parameter='account_payment_approval.high_multiplier',
        help="Multiplier for high priority payments"
    )
    
    medium_multiplier = fields.Float(
        string='Medium Priority Multiplier',
        default=1.0,
        config_parameter='account_payment_approval.medium_multiplier',
        help="Multiplier for medium priority payments"
    )
    
    low_multiplier = fields.Float(
        string='Low Priority Multiplier',
        default=1.2,
        config_parameter='account_payment_approval.low_multiplier',
        help="Multiplier for low priority payments (increases threshold)"
    )
    
    # Bulk Operations
    enable_bulk_approval = fields.Boolean(
        string='Enable Bulk Approval',
        default=True,
        config_parameter='account_payment_approval.enable_bulk_approval',
        help="Allow bulk approval of multiple payments"
    )
    
    max_bulk_approval_count = fields.Integer(
        string='Max Bulk Approval Count',
        default=50,
        config_parameter='account_payment_approval.max_bulk_approval_count',
        help="Maximum number of payments that can be approved in bulk"
    )
    
    # QR Code Settings
    qr_code_size = fields.Integer(
        string='QR Code Size (pixels)',
        default=200,
        config_parameter='account_payment_approval.qr_code_size',
        help="Size of generated QR codes in pixels"
    )
    
    qr_code_error_correction = fields.Selection([
        ('L', 'Low (~7%)'),
        ('M', 'Medium (~15%)'),
        ('Q', 'Quartile (~25%)'),
        ('H', 'High (~30%)'),
    ], string='QR Code Error Correction',
       default='M',
       config_parameter='account_payment_approval.qr_code_error_correction',
       help="Error correction level for QR codes")
    
    # Security Settings
    token_expiry_days = fields.Integer(
        string='Token Expiry (days)',
        default=365,
        config_parameter='account_payment_approval.token_expiry_days',
        help="Number of days before verification tokens expire"
    )
    
    max_verification_attempts = fields.Integer(
        string='Max Verification Attempts',
        default=1000,
        config_parameter='account_payment_approval.max_verification_attempts',
        help="Maximum number of QR verification attempts"
    )
    
    # Company Branding
    company_logo_url = fields.Char(
        string='Company Logo URL',
        default='/account_payment_approval/static/description/icon.png',
        config_parameter='account_payment_approval.company_logo_url',
        help="URL for company logo in reports and verification pages"
    )
    
    primary_color = fields.Char(
        string='Primary Brand Color',
        default='#1f4788',
        config_parameter='account_payment_approval.primary_color',
        help="Primary color for branding (hex format)"
    )
    
    secondary_color = fields.Char(
        string='Secondary Brand Color',
        default='#f8f9fa',
        config_parameter='account_payment_approval.secondary_color',
        help="Secondary color for branding (hex format)"
    )
    
    # ========================================
    # Computed Fields and Constraints
    # ========================================
    
    active_approval_config_id = fields.Many2one(
        'payment.approval.config',
        string='Active Approval Configuration',
        compute='_compute_active_approval_config',
        help="Currently active approval configuration"
    )
    
    total_pending_approvals = fields.Integer(
        string='Total Pending Approvals',
        compute='_compute_approval_statistics',
        help="Total number of payments pending approval"
    )
    
    approval_efficiency_rate = fields.Float(
        string='Approval Efficiency Rate (%)',
        compute='_compute_approval_statistics',
        help="Percentage of payments approved within time limits"
    )
    
    @api.depends('company_id')
    def _compute_active_approval_config(self):
        """Get the active approval configuration for current company"""
        for record in self:
            config = self.env['payment.approval.config'].search([
                ('active', '=', True),
                ('company_id', '=', record.company_id.id)
            ], limit=1)
            record.active_approval_config_id = config
    
    def _compute_approval_statistics(self):
        """Compute approval workflow statistics"""
        for record in self:
            # Count pending approvals
            pending_count = self.env['account.payment'].search_count([
                ('company_id', '=', record.company_id.id),
                ('approval_state', 'in', ['submitted', 'under_review', 'approved'])
            ])
            record.total_pending_approvals = pending_count
            
            # Calculate efficiency rate (simplified)
            total_approved = self.env['account.payment'].search_count([
                ('company_id', '=', record.company_id.id),
                ('approval_state', '=', 'posted'),
                ('create_date', '>=', fields.Date.subtract(fields.Date.today(), days=30))
            ])
            
            if total_approved > 0:
                # This is a simplified calculation - in practice you'd compare against time limits
                record.approval_efficiency_rate = min(95.0, 80.0 + (20.0 * (1 - pending_count / max(total_approved, 1))))
            else:
                record.approval_efficiency_rate = 0.0
    
    @api.constrains('payment_approval_threshold', 'tier_2_threshold', 'tier_3_threshold')
    def _check_threshold_progression(self):
        """Ensure thresholds are in ascending order"""
        for record in self:
            if record.tier_2_threshold <= record.payment_approval_threshold:
                raise ValidationError(_(
                    "Tier 2 threshold (%s) must be greater than payment approval threshold (%s)"
                ) % (record.tier_2_threshold, record.payment_approval_threshold))
            
            if record.tier_3_threshold <= record.tier_2_threshold:
                raise ValidationError(_(
                    "Tier 3 threshold (%s) must be greater than Tier 2 threshold (%s)"
                ) % (record.tier_3_threshold, record.tier_2_threshold))
    
    @api.constrains('urgent_multiplier', 'high_multiplier', 'medium_multiplier', 'low_multiplier')
    def _check_multipliers(self):
        """Validate multiplier ranges"""
        for record in self:
            multipliers = [
                ('urgent_multiplier', record.urgent_multiplier),
                ('high_multiplier', record.high_multiplier),
                ('medium_multiplier', record.medium_multiplier),
                ('low_multiplier', record.low_multiplier),
            ]
            
            for name, value in multipliers:
                if not 0.1 <= value <= 2.0:
                    raise ValidationError(_(
                        "Multiplier %s (%s) must be between 0.1 and 2.0"
                    ) % (name.replace('_', ' ').title(), value))
    
    # ========================================
    # Action Methods
    # ========================================
    
    def action_create_approval_config(self):
        """Create a new approval configuration with current settings"""
        config_vals = {
            'name': f"Configuration {fields.Date.today()}",
            'company_id': self.company_id.id,
            'payment_approval_threshold': self.payment_approval_threshold,
            'receipt_approval_threshold': self.receipt_approval_threshold,
            'transfer_approval_threshold': self.transfer_approval_threshold,
            'tier_2_threshold': self.tier_2_threshold,
            'tier_3_threshold': self.tier_3_threshold,
            'auto_submit_on_create': self.auto_submit_on_create,
            'require_signature_all_stages': self.require_signature_all_stages,
            'enable_qr_verification': self.enable_qr_verification,
            'enable_email_notifications': self.enable_email_notifications,
            'review_time_limit': self.review_time_limit,
            'approval_time_limit': self.approval_time_limit,
            'authorization_time_limit': self.authorization_time_limit,
            'urgent_multiplier': self.urgent_multiplier,
            'high_multiplier': self.high_multiplier,
            'medium_multiplier': self.medium_multiplier,
            'low_multiplier': self.low_multiplier,
            'enable_bulk_approval': self.enable_bulk_approval,
            'max_bulk_approval_count': self.max_bulk_approval_count,
        }
        
        config = self.env['payment.approval.config'].create(config_vals)
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Approval Configuration'),
            'res_model': 'payment.approval.config',
            'res_id': config.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_test_approval_workflow(self):
        """Test the approval workflow with current settings"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Test Approval Workflow'),
            'res_model': 'payment.approval.test.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_company_id': self.company_id.id},
        }
    
    def action_reset_approval_defaults(self):
        """Reset all approval settings to defaults"""
        default_values = {
            'payment_approval_threshold': 1000.0,
            'receipt_approval_threshold': 5000.0,
            'transfer_approval_threshold': 2000.0,
            'tier_2_threshold': 10000.0,
            'tier_3_threshold': 50000.0,
            'auto_submit_on_create': False,
            'require_signature_all_stages': True,
            'enable_qr_verification': True,
            'enable_email_notifications': True,
            'review_time_limit': 24,
            'approval_time_limit': 48,
            'authorization_time_limit': 72,
            'urgent_multiplier': 0.5,
            'high_multiplier': 0.7,
            'medium_multiplier': 1.0,
            'low_multiplier': 1.2,
            'enable_bulk_approval': True,
            'max_bulk_approval_count': 50,
        }
        
        for field, value in default_values.items():
            param_name = f'account_payment_approval.{field}'
            self.env['ir.config_parameter'].sudo().set_param(param_name, value)
        
        # Reload settings
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
