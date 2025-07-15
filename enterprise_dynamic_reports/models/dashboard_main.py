# -*- coding: utf-8 -*-
# Copyright 2025 OSUS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class EnterpriseDashboard(models.Model):
    """Main dashboard controller for enterprise financial reports."""
    
    _name = 'enterprise.dashboard'
    _description = 'Enterprise Financial Dashboard'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _check_company_auto = True

    name = fields.Char(
        string='Dashboard Name',
        required=True,
        tracking=True
    )
    
    is_default = fields.Boolean(
        string='Default Dashboard',
        default=False,
        help='Set as default dashboard for current user'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Owner',
        required=True,
        default=lambda self: self.env.user
    )
    
    theme_mode = fields.Selection([
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme'),
        ('auto', 'Auto (System)')
    ], string='Theme Mode', default='light')
    
    widget_ids = fields.One2many(
        'enterprise.dashboard.widget',
        'dashboard_id',
        string='Widgets'
    )
    
    layout_config = fields.Json(
        string='Layout Configuration',
        default=lambda self: self._default_layout_config()
    )
    
    date_from = fields.Date(
        string='Date From',
        default=lambda self: fields.Date.today().replace(day=1)
    )
    
    date_to = fields.Date(
        string='Date To',
        default=lambda self: fields.Date.today()
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived')
    ], string='State', default='draft', tracking=True)
    
    @api.model
    def _default_layout_config(self):
        """Default dashboard layout configuration."""
        return {
            'grid_size': {'x': 12, 'y': 8},
            'widget_size': {'width': 3, 'height': 2},
            'margin': 10,
            'auto_resize': True
        }
    
    def action_activate(self):
        """Activate the dashboard."""
        self.state = 'active'
        
    def action_archive(self):
        """Archive the dashboard."""
        self.state = 'archived'
        
    @api.model
    def get_dashboard_data(self, dashboard_id=None):
        """Get comprehensive dashboard data for frontend."""
        dashboard = self.browse(dashboard_id) if dashboard_id else self._get_default_dashboard()
        
        if not dashboard:
            return self._create_default_dashboard_data()
            
        return {
            'dashboard_info': {
                'id': dashboard.id,
                'name': dashboard.name,
                'theme_mode': dashboard.theme_mode,
                'layout_config': dashboard.layout_config,
                'date_from': dashboard.date_from,
                'date_to': dashboard.date_to,
            },
            'widgets': self._get_widgets_data(dashboard),
            'kpis': self._get_kpi_data(dashboard),
            'quick_filters': self._get_quick_filters(),
            'recent_reports': self._get_recent_reports(),
        }
    
    def _get_default_dashboard(self):
        """Get user's default dashboard."""
        return self.search([
            ('user_id', '=', self.env.user.id),
            ('is_default', '=', True),
            ('state', '=', 'active')
        ], limit=1)
    
    def _create_default_dashboard_data(self):
        """Create default dashboard if none exists."""
        dashboard = self.create({
            'name': f'{self.env.user.name}\'s Dashboard',
            'is_default': True,
            'state': 'active'
        })
        
        # Create default widgets
        self._create_default_widgets(dashboard)
        
        return self.get_dashboard_data(dashboard.id)
    
    def _create_default_widgets(self, dashboard):
        """Create default widgets for new dashboard."""
        default_widgets = [
            {
                'name': 'Revenue Overview',
                'widget_type': 'revenue_chart',
                'position': {'x': 0, 'y': 0, 'width': 6, 'height': 3},
                'config': {'chart_type': 'line', 'period': 'monthly'}
            },
            {
                'name': 'Expenses Breakdown',
                'widget_type': 'expense_chart',
                'position': {'x': 6, 'y': 0, 'width': 6, 'height': 3},
                'config': {'chart_type': 'pie', 'period': 'monthly'}
            },
            {
                'name': 'Cash Flow',
                'widget_type': 'cashflow_chart',
                'position': {'x': 0, 'y': 3, 'width': 8, 'height': 3},
                'config': {'chart_type': 'bar', 'period': 'weekly'}
            },
            {
                'name': 'Key Metrics',
                'widget_type': 'kpi_cards',
                'position': {'x': 8, 'y': 3, 'width': 4, 'height': 3},
                'config': {'metrics': ['revenue', 'profit', 'expenses', 'margin']}
            }
        ]
        
        for widget_data in default_widgets:
            self.env['enterprise.dashboard.widget'].create({
                'dashboard_id': dashboard.id,
                **widget_data
            })
    
    def _get_widgets_data(self, dashboard):
        """Get widgets data for dashboard."""
        widgets_data = []
        for widget in dashboard.widget_ids:
            widgets_data.append({
                'id': widget.id,
                'name': widget.name,
                'type': widget.widget_type,
                'position': widget.position,
                'config': widget.config,
                'data': widget.get_widget_data()
            })
        return widgets_data
    
    def _get_kpi_data(self, dashboard):
        """Get KPI data for dashboard."""
        date_from = dashboard.date_from
        date_to = dashboard.date_to
        company = dashboard.company_id
        
        # Calculate key financial metrics
        domain = [
            ('company_id', '=', company.id),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('parent_state', '=', 'posted')
        ]
        
        # Revenue calculation
        revenue_domain = domain + [('account_id.account_type', '=', 'income')]
        revenue_lines = self.env['account.move.line'].search(revenue_domain)
        total_revenue = sum(revenue_lines.mapped('credit')) - sum(revenue_lines.mapped('debit'))
        
        # Expense calculation
        expense_domain = domain + [('account_id.account_type', '=', 'expense')]
        expense_lines = self.env['account.move.line'].search(expense_domain)
        total_expenses = sum(expense_lines.mapped('debit')) - sum(expense_lines.mapped('credit'))
        
        # Profit calculation
        profit = total_revenue - total_expenses
        profit_margin = (profit / total_revenue * 100) if total_revenue else 0
        
        # Previous period comparison
        prev_date_from = date_from - relativedelta(months=1)
        prev_date_to = date_to - relativedelta(months=1)
        prev_domain = [
            ('company_id', '=', company.id),
            ('date', '>=', prev_date_from),
            ('date', '<=', prev_date_to),
            ('parent_state', '=', 'posted')
        ]
        
        prev_revenue_lines = self.env['account.move.line'].search(
            prev_domain + [('account_id.account_type', '=', 'income')]
        )
        prev_revenue = sum(prev_revenue_lines.mapped('credit')) - sum(prev_revenue_lines.mapped('debit'))
        
        revenue_growth = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue else 0
        
        return {
            'total_revenue': {
                'value': total_revenue,
                'formatted': self._format_currency(total_revenue),
                'growth': revenue_growth,
                'trend': 'up' if revenue_growth > 0 else 'down'
            },
            'total_expenses': {
                'value': total_expenses,
                'formatted': self._format_currency(total_expenses),
                'trend': 'down' if total_expenses < (total_revenue * 0.7) else 'up'
            },
            'profit': {
                'value': profit,
                'formatted': self._format_currency(profit),
                'trend': 'up' if profit > 0 else 'down'
            },
            'profit_margin': {
                'value': profit_margin,
                'formatted': f'{profit_margin:.1f}%',
                'trend': 'up' if profit_margin > 10 else 'down'
            }
        }
    
    def _get_quick_filters(self):
        """Get quick filter options."""
        return {
            'periods': [
                {'key': 'today', 'label': 'Today'},
                {'key': 'week', 'label': 'This Week'},
                {'key': 'month', 'label': 'This Month'},
                {'key': 'quarter', 'label': 'This Quarter'},
                {'key': 'year', 'label': 'This Year'},
                {'key': 'custom', 'label': 'Custom Range'}
            ],
            'companies': [
                {'id': c.id, 'name': c.name} 
                for c in self.env['res.company'].search([])
            ]
        }
    
    def _get_recent_reports(self):
        """Get recently generated reports."""
        # This would fetch from a reports history model
        return [
            {
                'name': 'Balance Sheet',
                'date': '2025-01-15',
                'type': 'balance_sheet',
                'status': 'completed'
            },
            {
                'name': 'Profit & Loss',
                'date': '2025-01-14',
                'type': 'profit_loss',
                'status': 'completed'
            }
        ]
    
    def _format_currency(self, amount):
        """Format currency with company currency."""
        return f"{self.company_id.currency_id.symbol}{amount:,.2f}"


class EnterpriseDashboardWidget(models.Model):
    """Dashboard widget model."""
    
    _name = 'enterprise.dashboard.widget'
    _description = 'Dashboard Widget'
    _order = 'sequence, id'
    
    name = fields.Char(string='Widget Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    
    dashboard_id = fields.Many2one(
        'enterprise.dashboard',
        string='Dashboard',
        required=True,
        ondelete='cascade'
    )
    
    widget_type = fields.Selection([
        ('revenue_chart', 'Revenue Chart'),
        ('expense_chart', 'Expense Chart'),
        ('cashflow_chart', 'Cash Flow Chart'),
        ('kpi_cards', 'KPI Cards'),
        ('balance_sheet_summary', 'Balance Sheet Summary'),
        ('profit_loss_summary', 'P&L Summary'),
        ('aged_receivables', 'Aged Receivables'),
        ('aged_payables', 'Aged Payables'),
        ('top_customers', 'Top Customers'),
        ('top_products', 'Top Products'),
        ('custom_chart', 'Custom Chart')
    ], string='Widget Type', required=True)
    
    position = fields.Json(
        string='Position',
        default=lambda self: {'x': 0, 'y': 0, 'width': 4, 'height': 3}
    )
    
    config = fields.Json(
        string='Widget Configuration',
        default=dict
    )
    
    is_active = fields.Boolean(string='Active', default=True)
    
    def get_widget_data(self):
        """Get data for specific widget type."""
        method_name = f'_get_{self.widget_type}_data'
        if hasattr(self, method_name):
            return getattr(self, method_name)()
        return {}
    
    def _get_revenue_chart_data(self):
        """Get revenue chart data."""
        dashboard = self.dashboard_id
        date_from = dashboard.date_from
        date_to = dashboard.date_to
        
        # Generate monthly revenue data
        data = []
        labels = []
        current_date = date_from
        
        while current_date <= date_to:
            month_start = current_date.replace(day=1)
            month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
            
            domain = [
                ('company_id', '=', dashboard.company_id.id),
                ('date', '>=', month_start),
                ('date', '<=', month_end),
                ('parent_state', '=', 'posted'),
                ('account_id.account_type', '=', 'income')
            ]
            
            lines = self.env['account.move.line'].search(domain)
            revenue = sum(lines.mapped('credit')) - sum(lines.mapped('debit'))
            
            data.append(revenue)
            labels.append(current_date.strftime('%b %Y'))
            
            current_date = month_start + relativedelta(months=1)
        
        return {
            'labels': labels,
            'datasets': [{
                'label': 'Revenue',
                'data': data,
                'borderColor': '#1f77b4',
                'backgroundColor': '#1f77b4',
                'tension': 0.4
            }]
        }
    
    def _get_expense_chart_data(self):
        """Get expense chart data by category."""
        dashboard = self.dashboard_id
        
        # Get expense accounts grouped by type
        expense_accounts = self.env['account.account'].search([
            ('account_type', '=', 'expense'),
            ('company_id', '=', dashboard.company_id.id)
        ])
        
        domain = [
            ('company_id', '=', dashboard.company_id.id),
            ('date', '>=', dashboard.date_from),
            ('date', '<=', dashboard.date_to),
            ('parent_state', '=', 'posted'),
            ('account_id', 'in', expense_accounts.ids)
        ]
        
        # Group by account and calculate totals
        data = []
        labels = []
        colors = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
        
        for i, account in enumerate(expense_accounts[:6]):  # Top 6 categories
            account_domain = domain + [('account_id', '=', account.id)]
            lines = self.env['account.move.line'].search(account_domain)
            expense = sum(lines.mapped('debit')) - sum(lines.mapped('credit'))
            
            if expense > 0:
                data.append(expense)
                labels.append(account.name)
        
        return {
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': colors[:len(data)]
            }]
        }
    
    def _get_kpi_cards_data(self):
        """Get KPI cards data."""
        return self.dashboard_id._get_kpi_data(self.dashboard_id)
