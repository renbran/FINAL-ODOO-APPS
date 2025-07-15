from odoo import models, fields, api
from .financial_report_base import FinancialReportBase
import json
from datetime import datetime, timedelta


class EnterpriseProfitLossReport(FinancialReportBase):
    """Enterprise Profit & Loss Report with advanced analytics"""
    _name = 'enterprise.profit.loss.report'
    _description = 'Enterprise Profit & Loss Report'
    _order = 'date_from desc'

    # Report specific fields
    report_type = fields.Selection([
        ('detailed', 'Detailed'),
        ('summary', 'Summary'),
        ('comparative', 'Comparative Analysis')
    ], string='Report Type', default='detailed')
    
    show_quantities = fields.Boolean('Show Quantities', default=False)
    show_cost_center = fields.Boolean('Show Cost Centers', default=False)
    group_by_month = fields.Boolean('Group by Month', default=False)
    
    # Performance metrics
    gross_profit_margin = fields.Float('Gross Profit Margin (%)', compute='_compute_ratios')
    operating_margin = fields.Float('Operating Margin (%)', compute='_compute_ratios')
    net_profit_margin = fields.Float('Net Profit Margin (%)', compute='_compute_ratios')
    
    @api.depends('report_data')
    def _compute_ratios(self):
        """Compute profitability ratios"""
        for record in self:
            if record.report_data:
                data = json.loads(record.report_data)
                revenue = data.get('total_revenue', 0)
                if revenue:
                    record.gross_profit_margin = (data.get('gross_profit', 0) / revenue) * 100
                    record.operating_margin = (data.get('operating_profit', 0) / revenue) * 100
                    record.net_profit_margin = (data.get('net_profit', 0) / revenue) * 100
                else:
                    record.gross_profit_margin = 0
                    record.operating_margin = 0
                    record.net_profit_margin = 0

    def action_generate_report(self):
        """Generate P&L report data"""
        self.ensure_one()
        
        # Get account data
        revenue_accounts = self.env['account.account'].search([
            ('account_type', '=', 'income'),
            ('company_id', '=', self.company_id.id)
        ])
        
        expense_accounts = self.env['account.account'].search([
            ('account_type', 'in', ['expense', 'expense_depreciation', 'expense_direct_cost']),
            ('company_id', '=', self.company_id.id)
        ])
        
        # Calculate balances
        revenue_data = self._get_account_balances(revenue_accounts)
        expense_data = self._get_account_balances(expense_accounts)
        
        # Organize data by categories
        report_data = {
            'revenue': self._organize_revenue_data(revenue_data),
            'cost_of_sales': self._organize_cogs_data(expense_data),
            'operating_expenses': self._organize_opex_data(expense_data),
            'other_income': self._organize_other_income_data(revenue_data),
            'financial_costs': self._organize_financial_costs_data(expense_data),
            'summary': self._calculate_pl_summary(revenue_data, expense_data)
        }
        
        self.report_data = json.dumps(report_data)
        
        # Return client action to display report
        return {
            'type': 'ir.actions.client',
            'tag': 'enterprise_profit_loss_report',
            'target': 'current',
            'context': {'report_id': self.id}
        }
    
    def _organize_revenue_data(self, accounts_data):
        """Organize revenue accounts by category"""
        revenue_categories = {
            'sales_revenue': [],
            'service_revenue': [],
            'other_revenue': []
        }
        
        for account_data in accounts_data:
            account = account_data['account']
            balance = account_data['balance']
            
            # Categorize based on account code or name
            if 'sales' in account.name.lower() or account.code.startswith('4'):
                revenue_categories['sales_revenue'].append({
                    'account_id': account.id,
                    'account_code': account.code,
                    'account_name': account.name,
                    'balance': abs(balance),  # Revenue is positive
                    'percentage': 0  # Will be calculated later
                })
            elif 'service' in account.name.lower():
                revenue_categories['service_revenue'].append({
                    'account_id': account.id,
                    'account_code': account.code,
                    'account_name': account.name,
                    'balance': abs(balance),
                    'percentage': 0
                })
            else:
                revenue_categories['other_revenue'].append({
                    'account_id': account.id,
                    'account_code': account.code,
                    'account_name': account.name,
                    'balance': abs(balance),
                    'percentage': 0
                })
        
        return revenue_categories
    
    def _organize_cogs_data(self, accounts_data):
        """Organize cost of goods sold"""
        cogs_data = []
        
        for account_data in accounts_data:
            account = account_data['account']
            balance = account_data['balance']
            
            # Filter COGS accounts
            if ('cost' in account.name.lower() and 'goods' in account.name.lower()) or \
               account.code.startswith('5'):
                cogs_data.append({
                    'account_id': account.id,
                    'account_code': account.code,
                    'account_name': account.name,
                    'balance': balance,
                    'percentage': 0
                })
        
        return cogs_data
    
    def _organize_opex_data(self, accounts_data):
        """Organize operating expenses"""
        opex_categories = {
            'administrative': [],
            'selling': [],
            'general': []
        }
        
        for account_data in accounts_data:
            account = account_data['account']
            balance = account_data['balance']
            
            # Skip COGS accounts
            if ('cost' in account.name.lower() and 'goods' in account.name.lower()) or \
               account.code.startswith('5'):
                continue
            
            # Categorize operating expenses
            if any(word in account.name.lower() for word in ['admin', 'office', 'management']):
                opex_categories['administrative'].append({
                    'account_id': account.id,
                    'account_code': account.code,
                    'account_name': account.name,
                    'balance': balance,
                    'percentage': 0
                })
            elif any(word in account.name.lower() for word in ['sales', 'marketing', 'commission']):
                opex_categories['selling'].append({
                    'account_id': account.id,
                    'account_code': account.code,
                    'account_name': account.name,
                    'balance': balance,
                    'percentage': 0
                })
            else:
                opex_categories['general'].append({
                    'account_id': account.id,
                    'account_code': account.code,
                    'account_name': account.name,
                    'balance': balance,
                    'percentage': 0
                })
        
        return opex_categories
    
    def _organize_other_income_data(self, accounts_data):
        """Organize other income"""
        other_income = []
        
        for account_data in accounts_data:
            account = account_data['account']
            balance = account_data['balance']
            
            # Filter other income accounts
            if 'other' in account.name.lower() or 'misc' in account.name.lower():
                other_income.append({
                    'account_id': account.id,
                    'account_code': account.code,
                    'account_name': account.name,
                    'balance': abs(balance),
                    'percentage': 0
                })
        
        return other_income
    
    def _organize_financial_costs_data(self, accounts_data):
        """Organize financial costs"""
        financial_costs = []
        
        for account_data in accounts_data:
            account = account_data['account']
            balance = account_data['balance']
            
            # Filter financial cost accounts
            if any(word in account.name.lower() for word in ['interest', 'finance', 'bank']):
                financial_costs.append({
                    'account_id': account.id,
                    'account_code': account.code,
                    'account_name': account.name,
                    'balance': balance,
                    'percentage': 0
                })
        
        return financial_costs
    
    def _calculate_pl_summary(self, revenue_data, expense_data):
        """Calculate P&L summary figures"""
        total_revenue = sum(abs(data['balance']) for data in revenue_data)
        total_expenses = sum(data['balance'] for data in expense_data)
        
        # Categorize expenses
        cogs = sum(data['balance'] for data in expense_data 
                  if ('cost' in data['account'].name.lower() and 'goods' in data['account'].name.lower()) 
                  or data['account'].code.startswith('5'))
        
        operating_expenses = total_expenses - cogs
        
        gross_profit = total_revenue - cogs
        operating_profit = gross_profit - operating_expenses
        net_profit = operating_profit  # Simplified for basic version
        
        return {
            'total_revenue': total_revenue,
            'cost_of_sales': cogs,
            'gross_profit': gross_profit,
            'operating_expenses': operating_expenses,
            'operating_profit': operating_profit,
            'net_profit': net_profit,
            'currency_symbol': self.company_id.currency_id.symbol,
            'period': f"{self.date_from.strftime('%b %d, %Y')} - {self.date_to.strftime('%b %d, %Y')}"
        }


class EnterpriseTrialBalanceReport(FinancialReportBase):
    """Enterprise Trial Balance Report"""
    _name = 'enterprise.trial.balance.report'
    _description = 'Enterprise Trial Balance Report'
    _order = 'date_from desc'

    # Report specific fields
    include_initial_balance = fields.Boolean('Include Initial Balance', default=True)
    show_foreign_currency = fields.Boolean('Show Foreign Currency', default=False)
    group_by_type = fields.Boolean('Group by Account Type', default=True)
    
    def action_generate_report(self):
        """Generate Trial Balance report"""
        self.ensure_one()
        
        # Get all accounts
        domain = [('company_id', '=', self.company_id.id)]
        if self.account_ids:
            domain.append(('id', 'in', self.account_ids.ids))
        
        accounts = self.env['account.account'].search(domain, order='code')
        
        # Calculate balances
        trial_balance_data = []
        total_debit = 0
        total_credit = 0
        
        for account in accounts:
            balance_data = self._get_account_balance_detailed(account)
            
            if not self.show_zero_balance and balance_data['balance'] == 0:
                continue
            
            trial_balance_data.append(balance_data)
            total_debit += balance_data['debit']
            total_credit += balance_data['credit']
        
        # Group by account type if requested
        if self.group_by_type:
            trial_balance_data = self._group_by_account_type(trial_balance_data)
        
        report_data = {
            'accounts': trial_balance_data,
            'totals': {
                'total_debit': total_debit,
                'total_credit': total_credit,
                'balance_check': total_debit - total_credit
            },
            'options': {
                'include_initial_balance': self.include_initial_balance,
                'show_foreign_currency': self.show_foreign_currency,
                'group_by_type': self.group_by_type
            }
        }
        
        self.report_data = json.dumps(report_data)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'enterprise_trial_balance_report',
            'target': 'current',
            'context': {'report_id': self.id}
        }
    
    def _get_account_balance_detailed(self, account):
        """Get detailed balance for an account"""
        domain = [
            ('account_id', '=', account.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id)
        ]
        
        if self.target_move == 'posted':
            domain.append(('move_id.state', '=', 'posted'))
        
        if self.journal_ids:
            domain.append(('journal_id', 'in', self.journal_ids.ids))
        
        move_lines = self.env['account.move.line'].search(domain)
        
        debit = sum(move_lines.mapped('debit'))
        credit = sum(move_lines.mapped('credit'))
        balance = debit - credit
        
        # Get initial balance if requested
        initial_balance = 0
        if self.include_initial_balance:
            initial_domain = [
                ('account_id', '=', account.id),
                ('date', '<', self.date_from),
                ('company_id', '=', self.company_id.id)
            ]
            if self.target_move == 'posted':
                initial_domain.append(('move_id.state', '=', 'posted'))
            
            initial_lines = self.env['account.move.line'].search(initial_domain)
            initial_balance = sum(initial_lines.mapped('debit')) - sum(initial_lines.mapped('credit'))
        
        return {
            'account_id': account.id,
            'account_code': account.code,
            'account_name': account.name,
            'account_type': account.account_type,
            'initial_balance': initial_balance,
            'debit': debit,
            'credit': credit,
            'balance': balance,
            'ending_balance': initial_balance + balance
        }
    
    def _group_by_account_type(self, accounts_data):
        """Group accounts by type"""
        grouped_data = {}
        
        for account_data in accounts_data:
            account_type = account_data['account_type']
            if account_type not in grouped_data:
                grouped_data[account_type] = {
                    'type_name': dict(self.env['account.account']._fields['account_type'].selection)[account_type],
                    'accounts': [],
                    'totals': {
                        'initial_balance': 0,
                        'debit': 0,
                        'credit': 0,
                        'balance': 0,
                        'ending_balance': 0
                    }
                }
            
            grouped_data[account_type]['accounts'].append(account_data)
            grouped_data[account_type]['totals']['initial_balance'] += account_data['initial_balance']
            grouped_data[account_type]['totals']['debit'] += account_data['debit']
            grouped_data[account_type]['totals']['credit'] += account_data['credit']
            grouped_data[account_type]['totals']['balance'] += account_data['balance']
            grouped_data[account_type]['totals']['ending_balance'] += account_data['ending_balance']
        
        return grouped_data
