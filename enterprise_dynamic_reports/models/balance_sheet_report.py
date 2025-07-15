# -*- coding: utf-8 -*-
# Copyright 2025 OSUS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class EnterpriseBalanceSheetReport(models.TransientModel):
    """Enhanced Balance Sheet Report with enterprise features."""
    
    _name = 'enterprise.balance.sheet.report'
    _inherit = 'financial.report.base'
    _description = 'Enterprise Balance Sheet Report'
    
    show_hierarchy = fields.Boolean(
        string='Show Account Hierarchy',
        default=True,
        help='Display accounts in hierarchical structure'
    )
    
    show_zero_balance = fields.Boolean(
        string='Show Zero Balance Accounts',
        default=False,
        help='Include accounts with zero balance'
    )
    
    group_by_type = fields.Boolean(
        string='Group by Account Type',
        default=True,
        help='Group accounts by their type (Assets, Liabilities, Equity)'
    )
    
    include_initial_balance = fields.Boolean(
        string='Include Initial Balance',
        default=True,
        help='Include opening balance in calculations'
    )
    
    drill_down_level = fields.Selection([
        ('summary', 'Summary Only'),
        ('account_type', 'By Account Type'),
        ('account_group', 'By Account Group'),
        ('account_detail', 'Account Detail'),
        ('move_line', 'Move Line Detail')
    ], string='Detail Level', default='account_type')
    
    @api.model
    def action_generate_report(self):
        """Generate enhanced balance sheet report."""
        try:
            report_data = self._get_balance_sheet_data()
            return {
                'type': 'ir.actions.client',
                'tag': 'enterprise_balance_sheet_report',
                'name': 'Balance Sheet',
                'context': {
                    'report_data': report_data,
                    'report_options': self._get_report_options(),
                }
            }
        except Exception as e:
            _logger.error(f"Error generating balance sheet report: {str(e)}")
            raise UserError(_("Error generating report: %s") % str(e))
    
    def _get_balance_sheet_data(self):
        """Get comprehensive balance sheet data."""
        
        # Get account balances for main period
        current_data = self._get_period_data(self.date_from, self.date_to)
        
        # Get comparison data if enabled
        comparison_data = None
        if self.comparison_mode != 'none':
            comparison_data = self._get_period_data(
                self.comparison_date_from, 
                self.comparison_date_to
            )
        
        # Calculate totals and ratios
        totals = self._calculate_totals(current_data, comparison_data)
        ratios = self._calculate_financial_ratios(current_data)
        
        return {
            'current_period': current_data,
            'comparison_period': comparison_data,
            'totals': totals,
            'ratios': ratios,
            'report_info': self._get_report_info(),
            'has_comparison': self.comparison_mode != 'none',
            'drill_down_level': self.drill_down_level,
        }
    
    def _get_period_data(self, date_from, date_to):
        """Get balance sheet data for a specific period."""
        
        # Asset accounts
        assets_data = self._get_assets_data(date_from, date_to)
        
        # Liability accounts
        liabilities_data = self._get_liabilities_data(date_from, date_to)
        
        # Equity accounts
        equity_data = self._get_equity_data(date_from, date_to)
        
        return {
            'assets': assets_data,
            'liabilities': liabilities_data,
            'equity': equity_data,
            'date_from': date_from,
            'date_to': date_to,
        }
    
    def _get_assets_data(self, date_from, date_to):
        """Get assets data with subcategories."""
        assets_structure = {
            'current_assets': {
                'name': 'Current Assets',
                'account_types': ['asset_cash', 'asset_receivable', 'asset_current'],
                'subcategories': {
                    'cash_and_bank': {
                        'name': 'Cash and Bank',
                        'account_types': ['asset_cash']
                    },
                    'accounts_receivable': {
                        'name': 'Accounts Receivable',
                        'account_types': ['asset_receivable']
                    },
                    'other_current': {
                        'name': 'Other Current Assets',
                        'account_types': ['asset_current']
                    }
                }
            },
            'non_current_assets': {
                'name': 'Non-Current Assets',
                'account_types': ['asset_non_current', 'asset_fixed'],
                'subcategories': {
                    'fixed_assets': {
                        'name': 'Property, Plant & Equipment',
                        'account_types': ['asset_fixed']
                    },
                    'other_non_current': {
                        'name': 'Other Non-Current Assets',
                        'account_types': ['asset_non_current']
                    }
                }
            },
            'prepayments': {
                'name': 'Prepayments',
                'account_types': ['asset_prepayments'],
                'subcategories': {}
            }
        }
        
        return self._build_account_structure(assets_structure, date_from, date_to)
    
    def _get_liabilities_data(self, date_from, date_to):
        """Get liabilities data with subcategories."""
        liabilities_structure = {
            'current_liabilities': {
                'name': 'Current Liabilities',
                'account_types': ['liability_current', 'liability_payable'],
                'subcategories': {
                    'accounts_payable': {
                        'name': 'Accounts Payable',
                        'account_types': ['liability_payable']
                    },
                    'other_current': {
                        'name': 'Other Current Liabilities',
                        'account_types': ['liability_current']
                    }
                }
            },
            'non_current_liabilities': {
                'name': 'Non-Current Liabilities',
                'account_types': ['liability_non_current'],
                'subcategories': {}
            },
            'credit_cards': {
                'name': 'Credit Cards',
                'account_types': ['liability_credit_card'],
                'subcategories': {}
            }
        }
        
        return self._build_account_structure(liabilities_structure, date_from, date_to)
    
    def _get_equity_data(self, date_from, date_to):
        """Get equity data with subcategories."""
        equity_structure = {
            'retained_earnings': {
                'name': 'Retained Earnings',
                'account_types': ['equity'],
                'subcategories': {}
            },
            'unallocated_earnings': {
                'name': 'Current Year Earnings',
                'account_types': ['equity_unaffected'],
                'subcategories': {}
            }
        }
        
        # Add current year profit/loss
        profit_loss = self._calculate_current_year_profit_loss(date_from, date_to)
        equity_structure['current_year_earnings'] = {
            'name': 'Current Year Earnings',
            'balance': profit_loss,
            'formatted_balance': self._format_currency(profit_loss),
            'accounts': [],
            'subcategories': {}
        }
        
        return self._build_account_structure(equity_structure, date_from, date_to)
    
    def _build_account_structure(self, structure, date_from, date_to):
        """Build hierarchical account structure with balances."""
        result = {}
        
        for category_key, category_info in structure.items():
            if 'balance' in category_info:
                # Pre-calculated item (like current year earnings)
                result[category_key] = category_info
                continue
                
            accounts = self._get_accounts_by_type(category_info['account_types'])
            account_balances = self._get_account_balance(accounts, date_from, date_to)
            
            category_balance = 0
            category_accounts = []
            
            # Process subcategories
            subcategories = {}
            if category_info.get('subcategories'):
                for sub_key, sub_info in category_info['subcategories'].items():
                    sub_accounts = self._get_accounts_by_type(sub_info['account_types'])
                    sub_balance = 0
                    sub_account_list = []
                    
                    for account_id, balance_info in account_balances.items():
                        if balance_info['account'].id in sub_accounts.ids:
                            if self.show_zero_balance or balance_info['balance'] != 0:
                                sub_account_list.append({
                                    'id': account_id,
                                    'code': balance_info['account'].code,
                                    'name': balance_info['account'].name,
                                    'balance': balance_info['balance'],
                                    'formatted_balance': balance_info['formatted_balance'],
                                    'account_type': balance_info['account'].account_type,
                                })
                                sub_balance += balance_info['balance']
                    
                    subcategories[sub_key] = {
                        'name': sub_info['name'],
                        'balance': sub_balance,
                        'formatted_balance': self._format_currency(sub_balance),
                        'accounts': sub_account_list
                    }
                    category_balance += sub_balance
            else:
                # No subcategories, add accounts directly
                for account_id, balance_info in account_balances.items():
                    if balance_info['account'].account_type in category_info['account_types']:
                        if self.show_zero_balance or balance_info['balance'] != 0:
                            category_accounts.append({
                                'id': account_id,
                                'code': balance_info['account'].code,
                                'name': balance_info['account'].name,
                                'balance': balance_info['balance'],
                                'formatted_balance': balance_info['formatted_balance'],
                                'account_type': balance_info['account'].account_type,
                            })
                            category_balance += balance_info['balance']
            
            result[category_key] = {
                'name': category_info['name'],
                'balance': category_balance,
                'formatted_balance': self._format_currency(category_balance),
                'accounts': category_accounts,
                'subcategories': subcategories
            }
        
        return result
    
    def _calculate_current_year_profit_loss(self, date_from, date_to):
        """Calculate current year profit/loss."""
        # Get income accounts
        income_accounts = self._get_accounts_by_type(['income', 'income_other'])
        income_balances = self._get_account_balance(income_accounts, date_from, date_to)
        total_income = sum([b['balance'] for b in income_balances.values()])
        
        # Get expense accounts
        expense_accounts = self._get_accounts_by_type(['expense', 'expense_depreciation', 'expense_direct_cost'])
        expense_balances = self._get_account_balance(expense_accounts, date_from, date_to)
        total_expenses = sum([b['balance'] for b in expense_balances.values()])
        
        return total_income - total_expenses
    
    def _calculate_totals(self, current_data, comparison_data=None):
        """Calculate balance sheet totals."""
        totals = {}
        
        # Current period totals
        total_assets = sum([
            cat['balance'] for cat in current_data['assets'].values()
        ])
        total_liabilities = sum([
            cat['balance'] for cat in current_data['liabilities'].values()
        ])
        total_equity = sum([
            cat['balance'] for cat in current_data['equity'].values()
        ])
        
        totals['current'] = {
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'total_liabilities_equity': total_liabilities + total_equity,
            'balance_check': total_assets - (total_liabilities + total_equity),
            'formatted': {
                'total_assets': self._format_currency(total_assets),
                'total_liabilities': self._format_currency(total_liabilities),
                'total_equity': self._format_currency(total_equity),
                'total_liabilities_equity': self._format_currency(total_liabilities + total_equity),
                'balance_check': self._format_currency(total_assets - (total_liabilities + total_equity))
            }
        }
        
        # Comparison period totals
        if comparison_data:
            comp_total_assets = sum([
                cat['balance'] for cat in comparison_data['assets'].values()
            ])
            comp_total_liabilities = sum([
                cat['balance'] for cat in comparison_data['liabilities'].values()
            ])
            comp_total_equity = sum([
                cat['balance'] for cat in comparison_data['equity'].values()
            ])
            
            totals['comparison'] = {
                'total_assets': comp_total_assets,
                'total_liabilities': comp_total_liabilities,
                'total_equity': comp_total_equity,
                'total_liabilities_equity': comp_total_liabilities + comp_total_equity,
                'formatted': {
                    'total_assets': self._format_currency(comp_total_assets),
                    'total_liabilities': self._format_currency(comp_total_liabilities),
                    'total_equity': self._format_currency(comp_total_equity),
                    'total_liabilities_equity': self._format_currency(comp_total_liabilities + comp_total_equity),
                }
            }
            
            # Calculate variances
            totals['variance'] = {
                'total_assets': total_assets - comp_total_assets,
                'total_liabilities': total_liabilities - comp_total_liabilities,
                'total_equity': total_equity - comp_total_equity,
                'total_assets_pct': self._get_percentage_change(total_assets, comp_total_assets),
                'total_liabilities_pct': self._get_percentage_change(total_liabilities, comp_total_liabilities),
                'total_equity_pct': self._get_percentage_change(total_equity, comp_total_equity),
                'formatted': {
                    'total_assets': self._format_currency(total_assets - comp_total_assets),
                    'total_liabilities': self._format_currency(total_liabilities - comp_total_liabilities),
                    'total_equity': self._format_currency(total_equity - comp_total_equity),
                }
            }
        
        return totals
    
    def _calculate_financial_ratios(self, current_data):
        """Calculate key financial ratios."""
        total_assets = sum([cat['balance'] for cat in current_data['assets'].values()])
        total_liabilities = sum([cat['balance'] for cat in current_data['liabilities'].values()])
        total_equity = sum([cat['balance'] for cat in current_data['equity'].values()])
        
        current_assets = current_data['assets'].get('current_assets', {}).get('balance', 0)
        current_liabilities = current_data['liabilities'].get('current_liabilities', {}).get('balance', 0)
        
        ratios = {}
        
        # Current Ratio
        if current_liabilities:
            ratios['current_ratio'] = current_assets / current_liabilities
        else:
            ratios['current_ratio'] = 0
        
        # Debt to Equity Ratio
        if total_equity:
            ratios['debt_to_equity'] = total_liabilities / total_equity
        else:
            ratios['debt_to_equity'] = 0
        
        # Debt to Assets Ratio
        if total_assets:
            ratios['debt_to_assets'] = total_liabilities / total_assets
        else:
            ratios['debt_to_assets'] = 0
        
        # Equity Ratio
        if total_assets:
            ratios['equity_ratio'] = total_equity / total_assets
        else:
            ratios['equity_ratio'] = 0
        
        # Format ratios
        ratios['formatted'] = {
            'current_ratio': f"{ratios['current_ratio']:.2f}",
            'debt_to_equity': f"{ratios['debt_to_equity']:.2f}",
            'debt_to_assets': f"{ratios['debt_to_assets']:.2f}",
            'equity_ratio': f"{ratios['equity_ratio']:.2f}",
        }
        
        return ratios
    
    def _get_report_options(self):
        """Get report configuration options."""
        return {
            'show_hierarchy': self.show_hierarchy,
            'show_zero_balance': self.show_zero_balance,
            'group_by_type': self.group_by_type,
            'include_initial_balance': self.include_initial_balance,
            'drill_down_level': self.drill_down_level,
            'comparison_mode': self.comparison_mode,
            'date_from': self.date_from.strftime('%Y-%m-%d'),
            'date_to': self.date_to.strftime('%Y-%m-%d'),
            'company_name': self.company_id.name,
            'currency_symbol': self.currency_id.symbol,
        }
    
    def _get_report_info(self):
        """Get report header information."""
        return {
            'title': 'Balance Sheet',
            'company_name': self.company_id.name,
            'date_from': self.date_from.strftime('%B %d, %Y'),
            'date_to': self.date_to.strftime('%B %d, %Y'),
            'currency': self.currency_id.name,
            'currency_symbol': self.currency_id.symbol,
            'generated_on': fields.Datetime.now().strftime('%B %d, %Y at %I:%M %p'),
            'generated_by': self.env.user.name,
        }
