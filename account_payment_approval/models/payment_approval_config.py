# -*- coding: utf-8 -*-
#############################################################################
#
#    Payment Approval Configuration Model
#    Copyright (C) 2025 OSUS Properties
#
#############################################################################

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PaymentApprovalConfig(models.Model):
    """Payment Approval Configuration"""
    _name = 'payment.approval.config'
    _description = 'Payment Approval Configuration'
    _order = 'sequence, id'
    
    name = fields.Char(
        string='Configuration Name',
        required=True,
        help="Name for this approval configuration"
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Sequence for ordering configurations"
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help="Only one configuration can be active at a time"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        help="Company for this configuration"
    )
    
    # Approval Thresholds
    payment_approval_threshold = fields.Float(
        string='Payment Approval Threshold',
        default=1000.0,
        help="Minimum amount requiring approval for outbound payments"
    )
    
    receipt_approval_threshold = fields.Float(
        string='Receipt Approval Threshold',
        default=5000.0,
        help="Minimum amount requiring approval for inbound receipts"
    )
    
    transfer_approval_threshold = fields.Float(
        string='Transfer Approval Threshold',
        default=2000.0,
        help="Minimum amount requiring approval for internal transfers"
    )
    
    # Multi-tier Thresholds
    tier_2_threshold = fields.Float(
        string='Tier 2 Threshold',
        default=10000.0,
        help="Amount requiring 2-tier approval"
    )
    
    tier_3_threshold = fields.Float(
        string='Tier 3 Threshold',
        default=50000.0,
        help="Amount requiring 3-tier approval (including authorization)"
    )
    
    # Workflow Settings
    auto_submit_on_create = fields.Boolean(
        string='Auto-submit on Create',
        default=False,
        help="Automatically submit payments for approval when created"
    )
    
    require_signature_all_stages = fields.Boolean(
        string='Require Signatures for All Stages',
        default=True,
        help="Require digital signatures at every approval stage"
    )
    
    enable_qr_verification = fields.Boolean(
        string='Enable QR Verification',
        default=True,
        help="Generate QR codes for payment verification"
    )
    
    enable_email_notifications = fields.Boolean(
        string='Enable Email Notifications',
        default=True,
        help="Send email notifications for approval actions"
    )
    
    # Time Limits
    review_time_limit = fields.Integer(
        string='Review Time Limit (hours)',
        default=24,
        help="Maximum hours for review stage"
    )
    
    approval_time_limit = fields.Integer(
        string='Approval Time Limit (hours)',
        default=48,
        help="Maximum hours for approval stage"
    )
    
    authorization_time_limit = fields.Integer(
        string='Authorization Time Limit (hours)',
        default=72,
        help="Maximum hours for authorization stage"
    )
    
    # Urgency Multipliers
    urgent_multiplier = fields.Float(
        string='Urgent Priority Multiplier',
        default=0.5,
        help="Multiplier for urgent payments (reduces threshold)"
    )
    
    high_multiplier = fields.Float(
        string='High Priority Multiplier',
        default=0.7,
        help="Multiplier for high priority payments"
    )
    
    medium_multiplier = fields.Float(
        string='Medium Priority Multiplier',
        default=1.0,
        help="Multiplier for medium priority payments"
    )
    
    low_multiplier = fields.Float(
        string='Low Priority Multiplier',
        default=1.2,
        help="Multiplier for low priority payments (increases threshold)"
    )
    
    # Additional Settings
    allow_parallel_approval = fields.Boolean(
        string='Allow Parallel Approval',
        default=False,
        help="Allow multiple approvers to act simultaneously"
    )
    
    require_comment_on_reject = fields.Boolean(
        string='Require Comment on Rejection',
        default=True,
        help="Require comment when rejecting payments"
    )
    
    enable_bulk_approval = fields.Boolean(
        string='Enable Bulk Approval',
        default=True,
        help="Allow bulk approval of multiple payments"
    )
    
    max_bulk_approval_count = fields.Integer(
        string='Max Bulk Approval Count',
        default=50,
        help="Maximum number of payments that can be approved in bulk"
    )
    
    # Currency and Amounts
    currency_id = fields.Many2one(
        'res.currency',
        string='Default Currency',
        default=lambda self: self.env.company.currency_id,
        help="Default currency for amount calculations"
    )
    
    # Computed Fields
    payment_approval_threshold_display = fields.Char(
        string='Payment Threshold Display',
        compute='_compute_threshold_displays',
        help="Formatted payment threshold"
    )
    
    tier_2_threshold_display = fields.Char(
        string='Tier 2 Threshold Display',
        compute='_compute_threshold_displays',
        help="Formatted tier 2 threshold"
    )
    
    tier_3_threshold_display = fields.Char(
        string='Tier 3 Threshold Display',
        compute='_compute_threshold_displays',
        help="Formatted tier 3 threshold"
    )
    
    @api.depends('payment_approval_threshold', 'tier_2_threshold', 'tier_3_threshold', 'currency_id')
    def _compute_threshold_displays(self):
        """Format threshold amounts with currency"""
        for record in self:
            currency = record.currency_id or record.env.company.currency_id
            record.payment_approval_threshold_display = currency._format(record.payment_approval_threshold)
            record.tier_2_threshold_display = currency._format(record.tier_2_threshold)
            record.tier_3_threshold_display = currency._format(record.tier_3_threshold)
    
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
    
    @api.constrains('active', 'company_id')
    def _check_single_active_config(self):
        """Ensure only one active configuration per company"""
        for record in self:
            if record.active:
                existing = self.search([
                    ('id', '!=', record.id),
                    ('active', '=', True),
                    ('company_id', '=', record.company_id.id)
                ])
                if existing:
                    raise ValidationError(_(
                        "Only one payment approval configuration can be active per company. "
                        "Please deactivate the existing configuration first."
                    ))
    
    @api.model
    def get_active_config(self, company_id=None):
        """Get the active configuration for a company"""
        if not company_id:
            company_id = self.env.company.id
        
        config = self.search([
            ('active', '=', True),
            ('company_id', '=', company_id)
        ], limit=1)
        
        return config
    
    def action_activate(self):
        """Activate this configuration"""
        # Deactivate other configurations for this company
        other_configs = self.search([
            ('id', '!=', self.id),
            ('company_id', '=', self.company_id.id)
        ])
        other_configs.write({'active': False})
        
        # Activate this configuration
        self.write({'active': True})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Configuration Activated'),
                'message': _('Payment approval configuration "%s" is now active.') % self.name,
                'type': 'success',
            }
        }
    
    def get_effective_threshold(self, voucher_type, urgency_level='medium'):
        """Get effective threshold based on type and urgency"""
        self.ensure_one()
        
        # Base threshold
        if voucher_type == 'payment':
            base_threshold = self.payment_approval_threshold
        elif voucher_type == 'receipt':
            base_threshold = self.receipt_approval_threshold
        elif voucher_type == 'transfer':
            base_threshold = self.transfer_approval_threshold
        else:
            base_threshold = self.payment_approval_threshold
        
        # Apply urgency multiplier
        multiplier_map = {
            'urgent': self.urgent_multiplier,
            'high': self.high_multiplier,
            'medium': self.medium_multiplier,
            'low': self.low_multiplier,
        }
        
        multiplier = multiplier_map.get(urgency_level, 1.0)
        return base_threshold * multiplier
    
    def get_required_tiers(self, amount):
        """Get required approval tiers for given amount"""
        self.ensure_one()
        
        if amount >= self.tier_3_threshold:
            return 3
        elif amount >= self.tier_2_threshold:
            return 2
        elif amount >= self.payment_approval_threshold:
            return 1
        else:
            return 0
    
    def name_get(self):
        """Custom name display"""
        result = []
        for record in self:
            name = record.name
            if record.active:
                name += _(' (Active)')
            if record.company_id:
                name += f' - {record.company_id.name}'
            result.append((record.id, name))
        return result


class PaymentApprovalRule(models.Model):
    """Payment Approval Rules"""
    _name = 'payment.approval.rule'
    _description = 'Payment Approval Rule'
    _order = 'sequence, id'
    
    name = fields.Char(
        string='Rule Name',
        required=True,
        help="Name for this approval rule"
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Rule evaluation order"
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help="Whether this rule is active"
    )
    
    config_id = fields.Many2one(
        'payment.approval.config',
        string='Configuration',
        required=True,
        ondelete='cascade',
        help="Parent configuration"
    )
    
    # Rule Conditions
    partner_ids = fields.Many2many(
        'res.partner',
        string='Specific Partners',
        help="Apply rule only to these partners (empty = all partners)"
    )
    
    partner_category_ids = fields.Many2many(
        'res.partner.category',
        string='Partner Categories',
        help="Apply rule to partners with these categories"
    )
    
    payment_method_ids = fields.Many2many(
        'account.payment.method',
        string='Payment Methods',
        help="Apply rule to these payment methods (empty = all methods)"
    )
    
    journal_ids = fields.Many2many(
        'account.journal',
        string='Journals',
        help="Apply rule to these journals (empty = all journals)"
    )
    
    voucher_types = fields.Selection([
        ('payment', 'Payment Only'),
        ('receipt', 'Receipt Only'),
        ('transfer', 'Transfer Only'),
        ('all', 'All Types'),
    ], string='Voucher Types', default='all',
       help="Types of vouchers this rule applies to")
    
    min_amount = fields.Float(
        string='Minimum Amount',
        default=0.0,
        help="Minimum amount for rule to apply"
    )
    
    max_amount = fields.Float(
        string='Maximum Amount',
        default=0.0,
        help="Maximum amount for rule to apply (0 = no limit)"
    )
    
    # Rule Actions
    force_approval = fields.Boolean(
        string='Force Approval',
        default=False,
        help="Force approval even if amount is below threshold"
    )
    
    skip_approval = fields.Boolean(
        string='Skip Approval',
        default=False,
        help="Skip approval even if amount is above threshold"
    )
    
    custom_tier_count = fields.Integer(
        string='Custom Tier Count',
        default=0,
        help="Override default tier count (0 = use default)"
    )
    
    required_groups = fields.Many2many(
        'res.groups',
        string='Required Approver Groups',
        help="Specific groups required for approval"
    )
    
    notification_template_id = fields.Many2one(
        'mail.template',
        string='Custom Notification Template',
        help="Custom email template for this rule"
    )
    
    # Documentation
    description = fields.Text(
        string='Description',
        help="Description of when and how this rule applies"
    )
    
    @api.constrains('min_amount', 'max_amount')
    def _check_amount_range(self):
        """Validate amount range"""
        for record in self:
            if record.max_amount > 0 and record.min_amount > record.max_amount:
                raise ValidationError(_(
                    "Minimum amount (%s) cannot be greater than maximum amount (%s)"
                ) % (record.min_amount, record.max_amount))
    
    @api.constrains('force_approval', 'skip_approval')
    def _check_approval_actions(self):
        """Ensure force and skip approval are not both enabled"""
        for record in self:
            if record.force_approval and record.skip_approval:
                raise ValidationError(_(
                    "Cannot have both 'Force Approval' and 'Skip Approval' enabled"
                ))
    
    def applies_to_payment(self, payment):
        """Check if this rule applies to a payment"""
        self.ensure_one()
        
        # Check partner
        if self.partner_ids and payment.partner_id not in self.partner_ids:
            return False
        
        # Check partner categories
        if self.partner_category_ids:
            partner_categories = payment.partner_id.category_id
            if not (self.partner_category_ids & partner_categories):
                return False
        
        # Check payment method
        if (self.payment_method_ids and 
            payment.payment_method_line_id.payment_method_id not in self.payment_method_ids):
            return False
        
        # Check journal
        if self.journal_ids and payment.journal_id not in self.journal_ids:
            return False
        
        # Check voucher type
        if self.voucher_types != 'all':
            voucher_type = payment.voucher_type or 'payment'
            if self.voucher_types != voucher_type:
                return False
        
        # Check amount range
        amount = payment.amount
        if amount < self.min_amount:
            return False
        
        if self.max_amount > 0 and amount > self.max_amount:
            return False
        
        return True
    
    def get_rule_action(self, payment):
        """Get the action this rule prescribes for a payment"""
        self.ensure_one()
        
        if not self.applies_to_payment(payment):
            return None
        
        action = {
            'rule_id': self.id,
            'rule_name': self.name,
            'force_approval': self.force_approval,
            'skip_approval': self.skip_approval,
            'custom_tier_count': self.custom_tier_count,
            'required_groups': self.required_groups.ids,
            'notification_template_id': self.notification_template_id.id if self.notification_template_id else None,
        }
        
        return action
