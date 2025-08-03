# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from datetime import datetime, timedelta
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class SaleDashboardSimple(models.TransientModel):
    _name = 'sale.dashboard'
    _description = 'Sales Dashboard'

    @api.model
    def format_dashboard_value(self, value):
        """Format large numbers for dashboard display with K/M/B suffixes"""
        if not value or value == 0:
            return "0"
        
        abs_value = abs(value)
        
        if abs_value >= 1_000_000_000:
            formatted = round(value / 1_000_000_000, 2)
            return f"{formatted}B"
        elif abs_value >= 1_000_000:
            formatted = round(value / 1_000_000, 2)
            return f"{formatted}M"
        elif abs_value >= 1_000:
            formatted = round(value / 1_000)
            return f"{formatted:.0f}K"
        else:
            return f"{round(value):.0f}"

    @api.model
    def get_sales_performance_data(self, start_date, end_date):
        """Get sales performance data"""
        try:
            _logger.info(f"Getting performance data from {start_date} to {end_date}")
            
            sale_order = self.env['sale.order']
            
            # Base domain
            base_domain = [
                ('date_order', '>=', start_date),
                ('date_order', '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            # Count quotations (draft, sent)
            quotation_count = sale_order.search_count(base_domain + [('state', 'in', ['draft', 'sent'])])
            
            # Count sales orders (sale, done)
            sales_order_count = sale_order.search_count(base_domain + [('state', 'in', ['sale', 'done'])])
            
            # Count invoiced sales
            invoice_count = sale_order.search_count(base_domain + [('invoice_status', 'in', ['invoiced', 'to invoice'])])
            
            # Get total amount
            orders = sale_order.search(base_domain)
            total_amount = sum(order.amount_total for order in orders)
            
            result = {
                'total_quotations': quotation_count,
                'total_orders': sales_order_count,
                'total_invoiced': invoice_count,
                'total_amount': total_amount,
                'quotation_count': quotation_count,
                'sales_order_count': sales_order_count,
                'invoice_count': invoice_count
            }
            
            _logger.info(f"Performance data result: {result}")
            return result
            
        except Exception as e:
            _logger.error(f"Error getting performance data: {e}")
            return {
                'total_quotations': 0,
                'total_orders': 0,
                'total_invoiced': 0,
                'total_amount': 0,
                'quotation_count': 0,
                'sales_order_count': 0,
                'invoice_count': 0
            }

    @api.model
    def get_monthly_fluctuation_data(self, start_date, end_date, sales_type_ids=None):
        """Get monthly fluctuation data"""
        try:
            _logger.info(f"Getting monthly data from {start_date} to {end_date}")
            
            sale_order = self.env['sale.order']
            
            # Parse dates
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Generate monthly buckets
            result = []
            current_dt = start_dt.replace(day=1)
            
            while current_dt <= end_dt:
                month_start = current_dt.strftime('%Y-%m-%d')
                
                # Calculate month end
                if current_dt.month == 12:
                    next_month = current_dt.replace(year=current_dt.year + 1, month=1, day=1)
                else:
                    next_month = current_dt.replace(month=current_dt.month + 1, day=1)
                month_end = (next_month - timedelta(days=1)).strftime('%Y-%m-%d')
                
                # Get orders for this month
                month_domain = [
                    ('date_order', '>=', month_start),
                    ('date_order', '<=', month_end),
                    ('state', '!=', 'cancel')
                ]
                
                orders = sale_order.search(month_domain)
                total_amount = sum(order.amount_total for order in orders)
                
                result.append({
                    'month': current_dt.strftime('%b %Y'),
                    'amount': total_amount,
                    'count': len(orders)
                })
                
                # Move to next month
                if current_dt.month == 12:
                    current_dt = current_dt.replace(year=current_dt.year + 1, month=1)
                else:
                    current_dt = current_dt.replace(month=current_dt.month + 1)
            
            _logger.info(f"Monthly data result: {len(result)} months")
            return result
            
        except Exception as e:
            _logger.error(f"Error getting monthly data: {e}")
            return []

    @api.model
    def get_sales_by_state_data(self, start_date, end_date):
        """Get sales by state data"""
        try:
            _logger.info(f"Getting state data from {start_date} to {end_date}")
            
            sale_order = self.env['sale.order']
            
            # Base domain
            base_domain = [
                ('date_order', '>=', start_date),
                ('date_order', '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            # Count by state
            draft_count = sale_order.search_count(base_domain + [('state', 'in', ['draft', 'sent'])])
            sale_count = sale_order.search_count(base_domain + [('state', '=', 'sale')])
            done_count = sale_order.search_count(base_domain + [('state', '=', 'done')])
            
            result = {
                'labels': ['Draft', 'Sale', 'Done'],
                'counts': [draft_count, sale_count, done_count]
            }
            
            _logger.info(f"State data result: {result}")
            return result
            
        except Exception as e:
            _logger.error(f"Error getting state data: {e}")
            return {
                'labels': ['Draft', 'Sale', 'Done'],
                'counts': [0, 0, 0]
            }

    @api.model
    def get_top_customers_data(self, start_date, end_date, limit=10):
        """Get top customers data"""
        try:
            _logger.info(f"Getting customers data from {start_date} to {end_date}")
            
            sale_order = self.env['sale.order']
            
            # Base domain
            base_domain = [
                ('date_order', '>=', start_date),
                ('date_order', '<=', end_date),
                ('state', '!=', 'cancel'),
                ('partner_id', '!=', False)
            ]
            
            orders = sale_order.search(base_domain)
            
            # Group by customer
            customer_totals = defaultdict(float)
            for order in orders:
                customer_totals[order.partner_id.name] += order.amount_total
            
            # Sort and limit
            sorted_customers = sorted(customer_totals.items(), key=lambda x: x[1], reverse=True)[:limit]
            
            result = {
                'labels': [customer[0] for customer in sorted_customers],
                'amounts': [customer[1] for customer in sorted_customers]
            }
            
            _logger.info(f"Customers data result: {len(result['labels'])} customers")
            return result
            
        except Exception as e:
            _logger.error(f"Error getting customers data: {e}")
            return {
                'labels': [],
                'amounts': []
            }

    @api.model
    def get_sales_team_performance(self, start_date, end_date):
        """Get sales team performance data"""
        try:
            _logger.info(f"Getting team data from {start_date} to {end_date}")
            
            sale_order = self.env['sale.order']
            
            # Base domain
            base_domain = [
                ('date_order', '>=', start_date),
                ('date_order', '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            orders = sale_order.search(base_domain)
            
            # Group by team or user
            team_totals = defaultdict(float)
            for order in orders:
                team_name = 'Unassigned'
                if hasattr(order, 'team_id') and order.team_id:
                    team_name = order.team_id.name
                elif order.user_id:
                    team_name = order.user_id.name
                    
                team_totals[team_name] += order.amount_total
            
            # Sort by performance
            sorted_teams = sorted(team_totals.items(), key=lambda x: x[1], reverse=True)
            
            result = {
                'labels': [team[0] for team in sorted_teams],
                'amounts': [team[1] for team in sorted_teams]
            }
            
            _logger.info(f"Team data result: {len(result['labels'])} teams")
            return result
            
        except Exception as e:
            _logger.error(f"Error getting team data: {e}")
            return {
                'labels': ['Unassigned'],
                'amounts': [0]
            }
