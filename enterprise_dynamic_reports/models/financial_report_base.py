# -*- coding: utf-8 -*-
# Copyright 2025 OSUS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import date_utils

_logger = logging.getLogger(__name__)


class FinancialReportBase(models.AbstractModel):
    """Base model for all financial reports with common functionality."""
    
    _name = 'financial.report.base'
    _description = 'Financial Report Base'
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    
    date_from = fields.Date(
        string='Start Date',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1)
    )
    
    date_to = fields.Date(
        string='End Date',
        required=True,
        default=lambda self: fields.Date.today()
    )
    
    journal_ids = fields.Many2many(
        'account.journal',
        string='Journals',
        help='Leave empty to include all journals'
    )
    
    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
        help='Leave empty to include all accounts'
    )
    
    analytic_account_ids = fields.Many2many(
        'account.analytic.account',
        string='Analytic Accounts',
        help='Filter by analytic accounts'
    )
    
    target_move = fields.Selection([
        ('posted', 'All Posted Entries'),
        ('all', 'All Entries'),
    ], string='Target Moves', required=True, default='posted')
    
    comparison_mode = fields.Selection([
        ('none', 'No Comparison'),
        ('previous_period', 'Previous Period'),
        ('previous_year', 'Previous Year'),
        ('custom', 'Custom Comparison'),
    ], string='Comparison Mode', default='none')
    
    comparison_date_from = fields.Date(string='Comparison Start Date')
    comparison_date_to = fields.Date(string='Comparison End Date')
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id'
    )
    
    @api.onchange('date_from', 'date_to', 'comparison_mode')
    def _onchange_comparison_dates(self):
        """Auto-calculate comparison dates based on mode."""
        if self.comparison_mode == 'previous_period' and self.date_from and self.date_to:
            period_length = (self.date_to - self.date_from).days
            self.comparison_date_to = self.date_from - timedelta(days=1)
            self.comparison_date_from = self.comparison_date_to - timedelta(days=period_length)
        elif self.comparison_mode == 'previous_year' and self.date_from and self.date_to:
            self.comparison_date_from = self.date_from - relativedelta(years=1)
            self.comparison_date_to = self.date_to - relativedelta(years=1)
    
    def _get_move_lines_domain(self, date_from=None, date_to=None):
        """Get domain for account move lines based on report parameters."""
        date_from = date_from or self.date_from
        date_to = date_to or self.date_to
        
        domain = [
            ('company_id', '=', self.company_id.id),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
        ]
        
        if self.target_move == 'posted':
            domain.append(('parent_state', '=', 'posted'))
        
        if self.journal_ids:
            domain.append(('journal_id', 'in', self.journal_ids.ids))
        
        if self.account_ids:
            domain.append(('account_id', 'in', self.account_ids.ids))
            
        if self.analytic_account_ids:
            domain.append(('analytic_distribution', '!=', False))
        
        return domain
    
    def _get_account_balance(self, accounts, date_from=None, date_to=None):
        """Get balance for specific accounts in date range."""
        if not accounts:
            return {}
        
        domain = self._get_move_lines_domain(date_from, date_to)
        domain.append(('account_id', 'in', accounts.ids))
        
        move_lines = self.env['account.move.line'].search(domain)
        
        # Group by account
        account_balances = {}
        for account in accounts:
            account_lines = move_lines.filtered(lambda l: l.account_id == account)
            
            if account.account_type in ('asset_receivable', 'asset_cash', 'asset_current', 
                                      'asset_non_current', 'asset_prepayments', 'asset_fixed'):
                # Assets: Debit increases, Credit decreases
                balance = sum(account_lines.mapped('debit')) - sum(account_lines.mapped('credit'))
            elif account.account_type in ('liability_payable', 'liability_credit_card', 
                                        'liability_current', 'liability_non_current'):
                # Liabilities: Credit increases, Debit decreases
                balance = sum(account_lines.mapped('credit')) - sum(account_lines.mapped('debit'))
            elif account.account_type in ('equity', 'equity_unaffected'):
                # Equity: Credit increases, Debit decreases
                balance = sum(account_lines.mapped('credit')) - sum(account_lines.mapped('debit'))
            elif account.account_type in ('income', 'income_other'):
                # Income: Credit increases, Debit decreases
                balance = sum(account_lines.mapped('credit')) - sum(account_lines.mapped('debit'))
            elif account.account_type in ('expense', 'expense_depreciation', 'expense_direct_cost'):
                # Expenses: Debit increases, Credit decreases
                balance = sum(account_lines.mapped('debit')) - sum(account_lines.mapped('credit'))
            else:
                # Default calculation
                balance = sum(account_lines.mapped('debit')) - sum(account_lines.mapped('credit'))
            
            account_balances[account.id] = {
                'account': account,
                'balance': balance,
                'formatted_balance': self._format_currency(balance),
                'move_lines': account_lines
            }
        
        return account_balances
    
    def _get_accounts_by_type(self, account_types):
        """Get accounts filtered by type(s)."""
        if isinstance(account_types, str):
            account_types = [account_types]
        
        return self.env['account.account'].search([
            ('account_type', 'in', account_types),
            ('company_id', '=', self.company_id.id),
            ('deprecated', '=', False)
        ])
    
    def _format_currency(self, amount):
        """Format amount with company currency."""
        if not amount:
            return '0.00'
        return f"{amount:,.2f}"
    
    def _get_percentage_change(self, current, previous):
        """Calculate percentage change between periods."""
        if not previous:
            return 0.0
        return ((current - previous) / abs(previous)) * 100
    
    def _get_quick_date_filters(self):
        """Get predefined date filter options."""
        today = fields.Date.today()
        return {
            'today': {
                'from': today,
                'to': today,
                'label': 'Today'
            },
            'this_week': {
                'from': today - timedelta(days=today.weekday()),
                'to': today,
                'label': 'This Week'
            },
            'this_month': {
                'from': today.replace(day=1),
                'to': today,
                'label': 'This Month'
            },
            'this_quarter': {
                'from': date_utils.start_of(today, 'quarter'),
                'to': today,
                'label': 'This Quarter'
            },
            'this_year': {
                'from': today.replace(month=1, day=1),
                'to': today,
                'label': 'This Year'
            },
            'last_month': {
                'from': (today.replace(day=1) - timedelta(days=1)).replace(day=1),
                'to': today.replace(day=1) - timedelta(days=1),
                'label': 'Last Month'
            },
            'last_quarter': {
                'from': date_utils.start_of(today - relativedelta(months=3), 'quarter'),
                'to': date_utils.end_of(today - relativedelta(months=3), 'quarter'),
                'label': 'Last Quarter'
            },
            'last_year': {
                'from': today.replace(year=today.year-1, month=1, day=1),
                'to': today.replace(year=today.year-1, month=12, day=31),
                'label': 'Last Year'
            }
        }
    
    @api.model
    def get_report_filters(self):
        """Get available filters for the report."""
        return {
            'companies': [
                {'id': c.id, 'name': c.name} 
                for c in self.env['res.company'].search([])
            ],
            'journals': [
                {'id': j.id, 'name': j.name, 'code': j.code}
                for j in self.env['account.journal'].search([
                    ('company_id', '=', self.company_id.id)
                ])
            ],
            'date_filters': self._get_quick_date_filters(),
            'target_moves': [
                {'key': 'posted', 'label': 'Posted Entries Only'},
                {'key': 'all', 'label': 'All Entries'}
            ],
            'comparison_modes': [
                {'key': 'none', 'label': 'No Comparison'},
                {'key': 'previous_period', 'label': 'Previous Period'},
                {'key': 'previous_year', 'label': 'Previous Year'},
                {'key': 'custom', 'label': 'Custom Period'}
            ]
        }
    
    def action_generate_report(self):
        """Generate the financial report data."""
        # This method should be overridden by specific report models
        raise NotImplementedError("Subclasses must implement action_generate_report method")
    
    def action_export_pdf(self):
        """Export report as PDF."""
        return {
            'type': 'ir.actions.report',
            'report_name': f'enterprise_dynamic_reports.{self._name}_pdf',
            'report_type': 'qweb-pdf',
            'data': self._get_report_data(),
            'context': self.env.context,
        }
    
    def action_export_xlsx(self):
        """Export report as Excel."""
        return {
            'type': 'ir.actions.report',
            'report_name': f'enterprise_dynamic_reports.{self._name}_xlsx',
            'report_type': 'xlsx',
            'data': self._get_report_data(),
            'context': self.env.context,
        }
    
    def _get_report_data(self):
        """Get formatted report data for export."""
        # This method should be overridden by specific report models
        return {}
