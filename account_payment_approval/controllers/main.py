# -*- coding: utf-8 -*-
import json
import logging
from odoo import http, fields, _
from odoo.http import request, Response
from odoo.exceptions import AccessError, UserError

_logger = logging.getLogger(__name__)


class PaymentApprovalController(http.Controller):
    """Controller for payment approval operations"""

    @http.route('/payment/approval/dashboard', type='http', auth='user', website=True)
    def payment_approval_dashboard(self, **kwargs):
        """Payment approval dashboard"""
        user = request.env.user
        
        # Get user's approval statistics
        payments = request.env['account.payment'].search([])
        
        stats = {
            'total_payments': len(payments),
            'pending_approval': len(payments.filtered(lambda p: p.voucher_state in ['submitted', 'under_review'])),
            'approved_today': len(payments.filtered(lambda p: p.voucher_state == 'approved' and 
                                                   p.write_date.date() == fields.Date.today())),
            'my_pending': len(payments.filtered(lambda p: p.voucher_state in ['submitted', 'under_review'] and
                                              user.id in (p.assigned_reviewer_ids + p.assigned_approver_ids).ids)),
        }
        
        return request.render('account_payment_approval.payment_approval_dashboard', {
            'stats': stats,
            'user': user,
        })

    @http.route('/payment/approval/bulk', type='json', auth='user', methods=['POST'])
    def bulk_approval_action(self, payment_ids, action, **kwargs):
        """Bulk approval action"""
        try:
            payments = request.env['account.payment'].browse(payment_ids)
            
            if not payments:
                return {'error': _('No payments selected')}
            
            # Check permissions
            if not request.env.user.has_group('account_payment_approval.group_payment_approval_manager'):
                return {'error': _('Insufficient permissions for bulk operations')}
            
            result = {'success': 0, 'failed': 0, 'messages': []}
            
            for payment in payments:
                try:
                    if action == 'approve' and payment.voucher_state == 'under_review':
                        payment.action_approve()
                        result['success'] += 1
                    elif action == 'reject' and payment.voucher_state in ['submitted', 'under_review']:
                        payment.action_reject()
                        result['success'] += 1
                    elif action == 'authorize' and payment.voucher_state == 'approved':
                        payment.action_authorize()
                        result['success'] += 1
                    else:
                        result['failed'] += 1
                        result['messages'].append(f'Payment {payment.name}: Invalid state for {action}')
                except Exception as e:
                    result['failed'] += 1
                    result['messages'].append(f'Payment {payment.name}: {str(e)}')
            
            return result
            
        except Exception as e:
            _logger.error(f"Bulk approval error: {e}")
            return {'error': str(e)}

    @http.route('/payment/approval/stats', type='json', auth='user')
    def payment_approval_stats(self, **kwargs):
        """Get payment approval statistics"""
        try:
            domain = []
            if not request.env.user.has_group('account_payment_approval.group_payment_approval_administrator'):
                # Filter based on user permissions
                user_groups = request.env.user.groups_id
                if request.env.ref('account_payment_approval.group_payment_approval_reviewer') in user_groups:
                    domain.append(('voucher_state', 'in', ['submitted', 'under_review']))
            
            payments = request.env['account.payment'].search(domain)
            
            # Group by state
            states_data = {}
            for state in ['draft', 'submitted', 'under_review', 'approved', 'authorized', 'posted', 'rejected']:
                states_data[state] = len(payments.filtered(lambda p: p.voucher_state == state))
            
            # Monthly data
            monthly_data = []
            for month in range(1, 13):
                month_payments = payments.filtered(lambda p: p.date.month == month if p.date else False)
                monthly_data.append({
                    'month': month,
                    'count': len(month_payments),
                    'amount': sum(month_payments.mapped('amount'))
                })
            
            return {
                'states': states_data,
                'monthly': monthly_data,
                'total_amount': sum(payments.mapped('amount')),
                'avg_processing_time': self._calculate_avg_processing_time(payments)
            }
            
        except Exception as e:
            _logger.error(f"Stats error: {e}")
            return {'error': str(e)}

    def _calculate_avg_processing_time(self, payments):
        """Calculate average processing time in days"""
        processed_payments = payments.filtered(lambda p: p.voucher_state in ['approved', 'authorized', 'posted'])
        if not processed_payments:
            return 0
        
        total_days = 0
        count = 0
        
        for payment in processed_payments:
            if payment.create_date and payment.write_date:
                delta = payment.write_date - payment.create_date
                total_days += delta.days
                count += 1
        
        return total_days / count if count > 0 else 0

    @http.route('/payment/approval/export', type='http', auth='user')
    def export_payment_report(self, **kwargs):
        """Export payment approval report"""
        try:
            # Get filters from kwargs
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to')
            state = kwargs.get('state')
            
            domain = []
            if date_from:
                domain.append(('date', '>=', date_from))
            if date_to:
                domain.append(('date', '<=', date_to))
            if state:
                domain.append(('voucher_state', '=', state))
            
            payments = request.env['account.payment'].search(domain)
            
            # Generate report
            report_data = self._generate_payment_report_data(payments)
            
            # Return as Excel file
            response = request.make_response(
                report_data,
                headers=[
                    ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                    ('Content-Disposition', 'attachment; filename="payment_approval_report.xlsx"')
                ]
            )
            
            return response
            
        except Exception as e:
            _logger.error(f"Export error: {e}")
            return request.redirect('/payment/approval/dashboard?error=' + str(e))

    def _generate_payment_report_data(self, payments):
        """Generate Excel report data"""
        try:
            import io
            import xlsxwriter
            
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Payment Approval Report')
            
            # Headers
            headers = [
                'Payment Reference', 'Partner', 'Amount', 'Currency', 
                'Date', 'State', 'Voucher State', 'Journal',
                'Created By', 'Create Date', 'Last Update'
            ]
            
            # Write headers
            for col, header in enumerate(headers):
                worksheet.write(0, col, header)
            
            # Write data
            for row, payment in enumerate(payments, 1):
                worksheet.write(row, 0, payment.name or '')
                worksheet.write(row, 1, payment.partner_id.name or '')
                worksheet.write(row, 2, payment.amount)
                worksheet.write(row, 3, payment.currency_id.name or '')
                worksheet.write(row, 4, payment.date.strftime('%Y-%m-%d') if payment.date else '')
                worksheet.write(row, 5, payment.state or '')
                worksheet.write(row, 6, payment.voucher_state or '')
                worksheet.write(row, 7, payment.journal_id.name or '')
                worksheet.write(row, 8, payment.create_uid.name or '')
                worksheet.write(row, 9, payment.create_date.strftime('%Y-%m-%d %H:%M') if payment.create_date else '')
                worksheet.write(row, 10, payment.write_date.strftime('%Y-%m-%d %H:%M') if payment.write_date else '')
            
            workbook.close()
            output.seek(0)
            return output.read()
            
        except ImportError:
            # Fallback to CSV if xlsxwriter not available
            return self._generate_csv_report_data(payments)

    def _generate_csv_report_data(self, payments):
        """Generate CSV report data as fallback"""
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            'Payment Reference', 'Partner', 'Amount', 'Currency', 
            'Date', 'State', 'Voucher State', 'Journal'
        ])
        
        # Data
        for payment in payments:
            writer.writerow([
                payment.name or '',
                payment.partner_id.name or '',
                payment.amount,
                payment.currency_id.name or '',
                payment.date.strftime('%Y-%m-%d') if payment.date else '',
                payment.state or '',
                payment.voucher_state or '',
                payment.journal_id.name or ''
            ])
        
        return output.getvalue().encode('utf-8')
