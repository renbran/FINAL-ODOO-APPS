# -*- coding: utf-8 -*-
"""
Payment Report Wizard for Enhanced Reporting
Provides options for bulk payment report generation
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PaymentReportWizard(models.TransientModel):
    """
    Wizard for generating multiple payment reports with various options
    """
    _name = 'payment.report.wizard'
    _description = 'Payment Report Generation Wizard'

    payment_ids = fields.Many2many(
        'account.payment',
        string='Payments',
        required=True,
        help="Select payments to include in the report"
    )
    
    report_type = fields.Selection([
        ('enhanced', 'Enhanced Payment Vouchers'),
        ('compact', 'Compact Payment Vouchers'),
        ('summary', 'Professional Summary'),
        ('multiple', 'Multiple Payment Table'),
    ], string='Report Type', default='enhanced', required=True)
    
    include_draft = fields.Boolean(
        string='Include Draft Payments',
        default=False,
        help="Include payments in draft state"
    )
    
    group_by_partner = fields.Boolean(
        string='Group by Partner',
        default=False,
        help="Group payments by partner in the report"
    )
    
    group_by_journal = fields.Boolean(
        string='Group by Payment Method',
        default=False,
        help="Group payments by journal/payment method"
    )
    
    date_from = fields.Date(
        string='Date From',
        help="Filter payments from this date"
    )
    
    date_to = fields.Date(
        string='Date To',
        help="Filter payments to this date"
    )
    
    payment_type = fields.Selection([
        ('all', 'All Payments'),
        ('inbound', 'Received Payments Only'),
        ('outbound', 'Sent Payments Only'),
    ], string='Payment Type Filter', default='all')

    @api.model
    def default_get(self, fields_list):
        """Set default payment IDs from context"""
        defaults = super().default_get(fields_list)
        
        active_ids = self.env.context.get('active_ids', [])
        if active_ids and 'payment_ids' in fields_list:
            # Filter valid payment IDs
            valid_payments = self.env['account.payment'].browse(active_ids).exists()
            defaults['payment_ids'] = [(6, 0, valid_payments.ids)]
        
        return defaults

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Validate date range"""
        for wizard in self:
            if wizard.date_from and wizard.date_to and wizard.date_from > wizard.date_to:
                raise ValidationError(_("Date From cannot be later than Date To"))

    def _get_filtered_payments(self):
        """Get payments based on filters"""
        payments = self.payment_ids
        
        # Filter by draft state
        if not self.include_draft:
            payments = payments.filtered(lambda p: p.state != 'draft')
        
        # Filter by date range
        if self.date_from:
            payments = payments.filtered(lambda p: p.date >= self.date_from)
        if self.date_to:
            payments = payments.filtered(lambda p: p.date <= self.date_to)
        
        # Filter by payment type
        if self.payment_type != 'all':
            payments = payments.filtered(lambda p: p.payment_type == self.payment_type)
        
        return payments

    def action_generate_report(self):
        """Generate the selected report type"""
        self.ensure_one()
        
        payments = self._get_filtered_payments()
        
        if not payments:
            raise ValidationError(_("No payments match the selected criteria"))
        
        # Generate report based on type
        if self.report_type == 'enhanced':
            if len(payments) == 1:
                return payments.action_print_enhanced_voucher()
            else:
                return payments.action_print_multiple_reports()
        
        elif self.report_type == 'compact':
            if len(payments) == 1:
                return payments.action_print_compact_voucher()
            else:
                return payments.action_print_multiple_reports()
        
        elif self.report_type == 'summary':
            if len(payments) == 1:
                return payments.action_print_professional_summary()
            else:
                return payments.action_print_multiple_reports()
        
        elif self.report_type == 'multiple':
            return payments.action_print_multiple_reports()
        
        else:
            raise ValidationError(_("Invalid report type selected"))

    def action_preview_selection(self):
        """Preview the filtered payment selection"""
        self.ensure_one()
        
        payments = self._get_filtered_payments()
        
        return {
            'name': _('Filtered Payments Preview'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', payments.ids)],
            'context': {
                'search_default_group_by_partner': self.group_by_partner,
                'search_default_group_by_journal': self.group_by_journal,
            },
            'target': 'new',
        }
