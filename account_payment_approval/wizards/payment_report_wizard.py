# -*- coding: utf-8 -*-
#############################################################################
#
#    Payment Report Generation Wizard
#    Copyright (C) 2025 OSUS Properties
#
#############################################################################

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import base64
import io


class PaymentReportWizard(models.TransientModel):
    """Wizard for generating payment approval reports"""
    _name = 'payment.report.wizard'
    _description = 'Payment Report Generation Wizard'
    
    # ========================================
    # Report Configuration Fields
    # ========================================
    
    report_type = fields.Selection([
        ('approval_summary', 'Approval Summary Report'),
        ('workflow_analysis', 'Workflow Analysis Report'),
        ('performance_metrics', 'Performance Metrics Report'),
        ('compliance_audit', 'Compliance Audit Report'),
        ('payment_voucher', 'Payment Voucher Report'),
        ('approval_history', 'Approval History Report'),
        ('user_activity', 'User Activity Report'),
        ('aging_analysis', 'Aging Analysis Report'),
    ], string='Report Type', required=True, default='approval_summary')
    
    output_format = fields.Selection([
        ('pdf', 'PDF Document'),
        ('xlsx', 'Excel Spreadsheet'),
        ('csv', 'CSV File'),
        ('html', 'HTML Page'),
    ], string='Output Format', required=True, default='pdf')
    
    # Date Range
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=lambda self: fields.Date.subtract(fields.Date.today(), days=30)
    )
    
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=fields.Date.today
    )
    
    # Filters
    company_ids = fields.Many2many(
        'res.company',
        string='Companies',
        default=lambda self: self.env.company
    )
    
    payment_ids = fields.Many2many(
        'account.payment',
        string='Specific Payments',
        help="Leave empty to include all payments in date range"
    )
    
    user_ids = fields.Many2many(
        'res.users',
        string='Users',
        help="Filter by specific users (approvers, creators, etc.)"
    )
    
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
        help="Filter by specific partners"
    )
    
    voucher_states = fields.Many2many(
        'payment.approval.state',
        string='Approval States',
        help="Filter by approval states"
    )
    
    urgency_levels = fields.Selection([
        ('all', 'All Urgency Levels'),
        ('urgent', 'Urgent Only'),
        ('high', 'High Priority'),
        ('medium', 'Medium Priority'),
        ('low', 'Low Priority'),
    ], string='Urgency Filter', default='all')
    
    amount_min = fields.Float(
        string='Minimum Amount',
        help="Minimum payment amount to include"
    )
    
    amount_max = fields.Float(
        string='Maximum Amount',
        help="Maximum payment amount to include (0 for no limit)"
    )
    
    # Report Options
    include_charts = fields.Boolean(
        string='Include Charts',
        default=True,
        help="Include charts and graphs in the report"
    )
    
    include_details = fields.Boolean(
        string='Include Detailed Data',
        default=True,
        help="Include detailed payment data"
    )
    
    include_signatures = fields.Boolean(
        string='Include Digital Signatures',
        default=False,
        help="Include digital signature information"
    )
    
    include_qr_codes = fields.Boolean(
        string='Include QR Codes',
        default=False,
        help="Include QR codes for verification"
    )
    
    group_by = fields.Selection([
        ('none', 'No Grouping'),
        ('state', 'Group by State'),
        ('user', 'Group by User'),
        ('partner', 'Group by Partner'),
        ('date', 'Group by Date'),
        ('amount_range', 'Group by Amount Range'),
        ('urgency', 'Group by Urgency'),
    ], string='Group By', default='state')
    
    # Output Settings
    report_title = fields.Char(
        string='Report Title',
        help="Custom title for the report"
    )
    
    include_logo = fields.Boolean(
        string='Include Company Logo',
        default=True,
        help="Include company logo in report header"
    )
    
    include_watermark = fields.Boolean(
        string='Include Watermark',
        default=False,
        help="Include confidential watermark"
    )
    
    email_report = fields.Boolean(
        string='Email Report',
        default=False,
        help="Email the report to specified recipients"
    )
    
    email_recipients = fields.Char(
        string='Email Recipients',
        help="Comma-separated email addresses"
    )
    
    # Computed Fields
    total_payments_count = fields.Integer(
        string='Total Payments',
        compute='_compute_report_stats',
        help="Total number of payments in the selected criteria"
    )
    
    total_amount = fields.Float(
        string='Total Amount',
        compute='_compute_report_stats',
        help="Total amount of payments in the selected criteria"
    )
    
    # ========================================
    # Computed Methods
    # ========================================
    
    @api.depends('date_from', 'date_to', 'company_ids', 'payment_ids', 'urgency_levels', 'amount_min', 'amount_max')
    def _compute_report_stats(self):
        """Compute report statistics"""
        for wizard in self:
            domain = wizard._get_payment_domain()
            payments = self.env['account.payment'].search(domain)
            
            wizard.total_payments_count = len(payments)
            wizard.total_amount = sum(payments.mapped('amount'))
    
    # ========================================
    # Validation Methods
    # ========================================
    
    @api.constrains('date_from', 'date_to')
    def _check_date_range(self):
        """Validate date range"""
        for wizard in self:
            if wizard.date_from > wizard.date_to:
                raise ValidationError(_("From date cannot be later than To date."))
            
            # Check for reasonable date range (not more than 2 years)
            if (wizard.date_to - wizard.date_from).days > 730:
                raise ValidationError(_(
                    "Date range is too large. Please select a range of 2 years or less."
                ))
    
    @api.constrains('amount_min', 'amount_max')
    def _check_amount_range(self):
        """Validate amount range"""
        for wizard in self:
            if wizard.amount_max > 0 and wizard.amount_min > wizard.amount_max:
                raise ValidationError(_("Minimum amount cannot be greater than maximum amount."))
    
    @api.constrains('email_report', 'email_recipients')
    def _check_email_settings(self):
        """Validate email settings"""
        for wizard in self:
            if wizard.email_report and not wizard.email_recipients:
                raise ValidationError(_("Email recipients are required when emailing the report."))
    
    # ========================================
    # Action Methods
    # ========================================
    
    def action_generate_report(self):
        """Generate and return the report"""
        self.ensure_one()
        
        # Get report data
        report_data = self._prepare_report_data()
        
        # Generate report based on type and format
        if self.output_format == 'pdf':
            return self._generate_pdf_report(report_data)
        elif self.output_format == 'xlsx':
            return self._generate_xlsx_report(report_data)
        elif self.output_format == 'csv':
            return self._generate_csv_report(report_data)
        elif self.output_format == 'html':
            return self._generate_html_report(report_data)
        else:
            raise UserError(_("Unsupported output format: %s") % self.output_format)
    
    def action_preview_report(self):
        """Preview the report data"""
        self.ensure_one()
        
        # Create preview data
        report_data = self._prepare_report_data()
        
        # Create preview wizard
        preview_wizard = self.env['payment.report.preview.wizard'].create({
            'report_wizard_id': self.id,
            'report_data': str(report_data),  # Convert to string for storage
            'preview_html': self._generate_preview_html(report_data),
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Report Preview'),
            'res_model': 'payment.report.preview.wizard',
            'res_id': preview_wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_schedule_report(self):
        """Schedule recurring report generation"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Schedule Report'),
            'res_model': 'payment.report.schedule.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_report_wizard_id': self.id,
                'default_report_type': self.report_type,
                'default_output_format': self.output_format,
            }
        }
    
    # ========================================
    # Report Generation Methods
    # ========================================
    
    def _prepare_report_data(self):
        """Prepare data for report generation"""
        domain = self._get_payment_domain()
        payments = self.env['account.payment'].search(domain)
        
        # Base report data
        report_data = {
            'wizard': self,
            'payments': payments,
            'total_count': len(payments),
            'total_amount': sum(payments.mapped('amount')),
            'date_from': self.date_from,
            'date_to': self.date_to,
            'generation_date': fields.Datetime.now(),
            'generated_by': self.env.user,
            'companies': self.company_ids,
        }
        
        # Add report-specific data
        if self.report_type == 'approval_summary':
            report_data.update(self._get_approval_summary_data(payments))
        elif self.report_type == 'workflow_analysis':
            report_data.update(self._get_workflow_analysis_data(payments))
        elif self.report_type == 'performance_metrics':
            report_data.update(self._get_performance_metrics_data(payments))
        elif self.report_type == 'compliance_audit':
            report_data.update(self._get_compliance_audit_data(payments))
        elif self.report_type == 'payment_voucher':
            report_data.update(self._get_payment_voucher_data(payments))
        elif self.report_type == 'approval_history':
            report_data.update(self._get_approval_history_data(payments))
        elif self.report_type == 'user_activity':
            report_data.update(self._get_user_activity_data(payments))
        elif self.report_type == 'aging_analysis':
            report_data.update(self._get_aging_analysis_data(payments))
        
        return report_data
    
    def _get_payment_domain(self):
        """Build domain for payment search"""
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ]
        
        if self.company_ids:
            domain.append(('company_id', 'in', self.company_ids.ids))
        
        if self.payment_ids:
            domain.append(('id', 'in', self.payment_ids.ids))
        
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        
        if self.urgency_levels != 'all':
            domain.append(('urgency', '=', self.urgency_levels))
        
        if self.amount_min > 0:
            domain.append(('amount', '>=', self.amount_min))
        
        if self.amount_max > 0:
            domain.append(('amount', '<=', self.amount_max))
        
        return domain
    
    # ========================================
    # Report Data Methods
    # ========================================
    
    def _get_approval_summary_data(self, payments):
        """Get data for approval summary report"""
        data = {}
        
        # State distribution
        state_counts = {}
        for payment in payments:
            state = payment.voucher_state
            state_counts[state] = state_counts.get(state, 0) + 1
        data['state_distribution'] = state_counts
        
        # Urgency distribution
        urgency_counts = {}
        for payment in payments:
            urgency = payment.urgency
            urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
        data['urgency_distribution'] = urgency_counts
        
        # Amount ranges
        amount_ranges = {
            '0-1000': 0, '1000-5000': 0, '5000-10000': 0,
            '10000-50000': 0, '50000+': 0
        }
        for payment in payments:
            amount = payment.amount
            if amount < 1000:
                amount_ranges['0-1000'] += 1
            elif amount < 5000:
                amount_ranges['1000-5000'] += 1
            elif amount < 10000:
                amount_ranges['5000-10000'] += 1
            elif amount < 50000:
                amount_ranges['10000-50000'] += 1
            else:
                amount_ranges['50000+'] += 1
        data['amount_ranges'] = amount_ranges
        
        return data
    
    def _get_workflow_analysis_data(self, payments):
        """Get data for workflow analysis report"""
        data = {}
        
        # Approval times by stage
        stage_times = {}
        total_times = []
        
        for payment in payments:
            if hasattr(payment, 'approval_history_ids'):
                history = payment.approval_history_ids.sorted('timestamp')
                prev_time = None
                
                for record in history:
                    if prev_time:
                        duration = (record.timestamp - prev_time).total_seconds() / 3600  # hours
                        stage = record.stage_to
                        if stage not in stage_times:
                            stage_times[stage] = []
                        stage_times[stage].append(duration)
                    prev_time = record.timestamp
                
                # Total workflow time
                if len(history) > 1:
                    total_time = (history[-1].timestamp - history[0].timestamp).total_seconds() / 3600
                    total_times.append(total_time)
        
        # Calculate averages
        data['average_stage_times'] = {
            stage: sum(times) / len(times) if times else 0
            for stage, times in stage_times.items()
        }
        data['average_total_time'] = sum(total_times) / len(total_times) if total_times else 0
        
        return data
    
    def _get_performance_metrics_data(self, payments):
        """Get data for performance metrics report"""
        data = {}
        
        # User performance
        user_stats = {}
        for payment in payments:
            # Creator performance
            creator = payment.create_uid
            if creator not in user_stats:
                user_stats[creator] = {'created': 0, 'approved': 0, 'rejected': 0}
            user_stats[creator]['created'] += 1
            
            # Approver performance
            if payment.approved_by_id:
                approver = payment.approved_by_id
                if approver not in user_stats:
                    user_stats[approver] = {'created': 0, 'approved': 0, 'rejected': 0}
                user_stats[approver]['approved'] += 1
            
            # Rejection tracking
            if payment.voucher_state == 'rejected':
                if payment.rejected_by_id:
                    rejector = payment.rejected_by_id
                    if rejector not in user_stats:
                        user_stats[rejector] = {'created': 0, 'approved': 0, 'rejected': 0}
                    user_stats[rejector]['rejected'] += 1
        
        data['user_performance'] = user_stats
        
        # Daily volumes
        daily_volumes = {}
        for payment in payments:
            date_key = payment.date.strftime('%Y-%m-%d')
            if date_key not in daily_volumes:
                daily_volumes[date_key] = {'count': 0, 'amount': 0}
            daily_volumes[date_key]['count'] += 1
            daily_volumes[date_key]['amount'] += payment.amount
        
        data['daily_volumes'] = daily_volumes
        
        return data
    
    def _get_compliance_audit_data(self, payments):
        """Get data for compliance audit report"""
        data = {}
        
        # Compliance issues
        issues = []
        for payment in payments:
            # Check for missing signatures
            if payment.voucher_state in ['approved', 'authorized', 'posted']:
                if not payment.digital_signature_ids:
                    issues.append({
                        'payment': payment,
                        'issue': 'Missing digital signature',
                        'severity': 'medium'
                    })
            
            # Check for overdue approvals
            if payment.voucher_state in ['submitted', 'under_review', 'approved']:
                # This would need actual time limit calculations
                pass
            
            # Check for policy violations
            if payment.amount > 50000 and payment.urgency == 'low':
                issues.append({
                    'payment': payment,
                    'issue': 'High amount with low urgency may require review',
                    'severity': 'low'
                })
        
        data['compliance_issues'] = issues
        
        return data
    
    def _get_payment_voucher_data(self, payments):
        """Get data for payment voucher report"""
        data = {}
        
        # Detailed payment information for vouchers
        voucher_data = []
        for payment in payments:
            voucher_info = {
                'payment': payment,
                'qr_code': payment.qr_code_token,
                'signatures': payment.digital_signature_ids,
                'history': payment.approval_history_ids.sorted('timestamp'),
                'supporting_docs': [],  # Would link to attachments
            }
            voucher_data.append(voucher_info)
        
        data['voucher_data'] = voucher_data
        
        return data
    
    def _get_approval_history_data(self, payments):
        """Get data for approval history report"""
        data = {}
        
        # Comprehensive history
        all_history = self.env['payment.approval.history']
        for payment in payments:
            if hasattr(payment, 'approval_history_ids'):
                all_history |= payment.approval_history_ids
        
        data['approval_history'] = all_history.sorted('timestamp', reverse=True)
        
        return data
    
    def _get_user_activity_data(self, payments):
        """Get data for user activity report"""
        data = {}
        
        if self.user_ids:
            users = self.user_ids
        else:
            # Get all users involved in the payments
            users = self.env['res.users']
            for payment in payments:
                users |= payment.create_uid
                if payment.approved_by_id:
                    users |= payment.approved_by_id
                if payment.authorized_by_id:
                    users |= payment.authorized_by_id
        
        user_activities = {}
        for user in users:
            activities = {
                'created_payments': payments.filtered(lambda p: p.create_uid == user),
                'approved_payments': payments.filtered(lambda p: p.approved_by_id == user),
                'authorized_payments': payments.filtered(lambda p: p.authorized_by_id == user),
            }
            user_activities[user] = activities
        
        data['user_activities'] = user_activities
        
        return data
    
    def _get_aging_analysis_data(self, payments):
        """Get data for aging analysis report"""
        data = {}
        
        aging_buckets = {
            '0-7 days': [], '8-30 days': [], '31-60 days': [],
            '61-90 days': [], '90+ days': []
        }
        
        today = fields.Date.today()
        for payment in payments:
            if payment.voucher_state not in ['posted', 'cancelled', 'rejected']:
                days_old = (today - payment.date).days
                
                if days_old <= 7:
                    aging_buckets['0-7 days'].append(payment)
                elif days_old <= 30:
                    aging_buckets['8-30 days'].append(payment)
                elif days_old <= 60:
                    aging_buckets['31-60 days'].append(payment)
                elif days_old <= 90:
                    aging_buckets['61-90 days'].append(payment)
                else:
                    aging_buckets['90+ days'].append(payment)
        
        data['aging_buckets'] = aging_buckets
        
        return data
    
    # ========================================
    # Report Format Methods
    # ========================================
    
    def _generate_pdf_report(self, report_data):
        """Generate PDF report"""
        # This would use the reporting engine to generate PDF
        report_name = f'payment_report_{self.report_type}_{fields.Date.today()}'
        
        # Return download action
        return {
            'type': 'ir.actions.report',
            'report_name': 'account_payment_approval.payment_report_template',
            'report_type': 'qweb-pdf',
            'data': report_data,
            'context': self.env.context,
        }
    
    def _generate_xlsx_report(self, report_data):
        """Generate Excel report"""
        # This would use xlsxwriter or similar to generate Excel
        # For now, return a simple action
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Excel Report'),
                'message': _('Excel report generation is not yet implemented.'),
                'type': 'info',
            }
        }
    
    def _generate_csv_report(self, report_data):
        """Generate CSV report"""
        # This would generate CSV data
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('CSV Report'),
                'message': _('CSV report generation is not yet implemented.'),
                'type': 'info',
            }
        }
    
    def _generate_html_report(self, report_data):
        """Generate HTML report"""
        # This would generate HTML report
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('HTML Report'),
                'message': _('HTML report generation is not yet implemented.'),
                'type': 'info',
            }
        }
    
    def _generate_preview_html(self, report_data):
        """Generate HTML preview of report"""
        html = f"""
        <div class="report-preview">
            <h2>{self.report_title or f'{self.report_type.replace("_", " ").title()} Report'}</h2>
            <p><strong>Date Range:</strong> {self.date_from} to {self.date_to}</p>
            <p><strong>Total Payments:</strong> {report_data['total_count']}</p>
            <p><strong>Total Amount:</strong> {report_data['total_amount']:,.2f}</p>
            
            <!-- More detailed preview would go here -->
        </div>
        """
        return html


class PaymentReportPreviewWizard(models.TransientModel):
    """Preview wizard for payment reports"""
    _name = 'payment.report.preview.wizard'
    _description = 'Payment Report Preview Wizard'
    
    report_wizard_id = fields.Many2one(
        'payment.report.wizard',
        string='Report Wizard',
        required=True
    )
    
    report_data = fields.Text(string='Report Data')
    preview_html = fields.Html(string='Preview')
    
    def action_generate_final_report(self):
        """Generate the final report"""
        return self.report_wizard_id.action_generate_report()
    
    def action_back_to_wizard(self):
        """Go back to report wizard"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payment Report Generator'),
            'res_model': 'payment.report.wizard',
            'res_id': self.report_wizard_id.id,
            'view_mode': 'form',
            'target': 'new',
        }
