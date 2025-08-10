# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentSignatory(models.Model):
    _name = 'payment.signatory'
    _description = 'Payment Signatory Configuration'
    _order = 'sequence, name'

    name = fields.Char(
        string='Signatory Name',
        required=True,
        help="Name of the signatory"
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        help="User associated with this signatory"
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Contact',
        related='user_id.partner_id',
        store=True,
        readonly=True
    )
    
    title = fields.Char(
        string='Title/Position',
        help="Job title or position of the signatory"
    )
    
    signature = fields.Binary(
        string='Digital Signature',
        help="Digital signature image"
    )
    
    is_active = fields.Boolean(
        string='Active',
        default=True,
        help="Whether this signatory is currently active"
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Order of appearance in forms"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    
    payment_types = fields.Selection([
        ('inbound', 'Receipts Only'),
        ('outbound', 'Payments Only'),
        ('both', 'Both Receipts and Payments'),
    ], string='Applicable For', default='both', required=True)
    
    approval_level = fields.Selection([
        ('reviewer', 'Reviewer'),
        ('approver', 'Approver'),
        ('authorizer', 'Authorizer'),
        ('poster', 'Poster'),
    ], string='Approval Level', required=True)
    
    minimum_amount = fields.Monetary(
        string='Minimum Amount',
        currency_field='currency_id',
        default=0.0,
        help="Minimum amount this signatory can approve (0 = no limit)"
    )
    
    maximum_amount = fields.Monetary(
        string='Maximum Amount',
        currency_field='currency_id',
        default=0.0,
        help="Maximum amount this signatory can approve (0 = no limit)"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    notes = fields.Text(
        string='Notes',
        help="Additional notes about this signatory"
    )

    @api.constrains('minimum_amount', 'maximum_amount')
    def _check_amounts(self):
        """Validate amount ranges"""
        for record in self:
            if record.maximum_amount > 0 and record.minimum_amount > record.maximum_amount:
                raise ValidationError(_("Minimum amount cannot be greater than maximum amount."))

    @api.constrains('user_id', 'company_id', 'approval_level')
    def _check_unique_user_level(self):
        """Ensure one user doesn't have duplicate approval levels for same company"""
        for record in self:
            if record.is_active:
                duplicate = self.search([
                    ('user_id', '=', record.user_id.id),
                    ('company_id', '=', record.company_id.id),
                    ('approval_level', '=', record.approval_level),
                    ('is_active', '=', True),
                    ('id', '!=', record.id)
                ])
                if duplicate:
                    raise ValidationError(
                        _("User %s already has an active %s role for %s.") % (
                            record.user_id.name, 
                            record.approval_level, 
                            record.company_id.name
                        )
                    )

    def name_get(self):
        """Enhanced name display"""
        result = []
        for record in self:
            name = f"{record.name} ({record.approval_level.title()})"
            if record.title:
                name += f" - {record.title}"
            result.append((record.id, name))
        return result

    def can_approve_amount(self, amount):
        """Check if signatory can approve given amount"""
        self.ensure_one()
        if not self.is_active:
            return False
        
        if self.minimum_amount > 0 and amount < self.minimum_amount:
            return False
            
        if self.maximum_amount > 0 and amount > self.maximum_amount:
            return False
            
        return True


class PaymentVerificationLog(models.Model):
    _name = 'payment.verification.log'
    _description = 'Payment Verification Log'
    _order = 'verification_date desc'
    _rec_name = 'payment_reference'

    payment_id = fields.Many2one(
        'account.payment',
        string='Payment',
        required=True,
        ondelete='cascade'
    )
    
    payment_reference = fields.Char(
        string='Payment Reference',
        related='payment_id.name',
        store=True
    )
    
    voucher_number = fields.Char(
        string='Voucher Number',
        related='payment_id.voucher_number',
        store=True
    )
    
    verification_token = fields.Char(
        string='Verification Token',
        required=True
    )
    
    verification_date = fields.Datetime(
        string='Verification Date',
        default=fields.Datetime.now,
        required=True
    )
    
    verified_by_ip = fields.Char(
        string='IP Address',
        help="IP address from where verification was performed"
    )
    
    verified_by_user = fields.Many2one(
        'res.users',
        string='Verified By User',
        help="User who performed the verification (if logged in)"
    )
    
    verification_status = fields.Selection([
        ('valid', 'Valid Payment'),
        ('invalid', 'Invalid Token'),
        ('expired', 'Expired'),
        ('cancelled', 'Payment Cancelled')
    ], string='Verification Status', required=True)
    
    browser_info = fields.Text(
        string='Browser Information',
        help="Browser and device information"
    )
    
    location_info = fields.Char(
        string='Location',
        help="Geographic location if available"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='payment_id.company_id',
        store=True
    )

    def name_get(self):
        """Enhanced name display"""
        result = []
        for record in self:
            name = f"Verification: {record.voucher_number or record.payment_reference}"
            if record.verification_date:
                name += f" on {record.verification_date.strftime('%Y-%m-%d %H:%M')}"
            result.append((record.id, name))
        return result
