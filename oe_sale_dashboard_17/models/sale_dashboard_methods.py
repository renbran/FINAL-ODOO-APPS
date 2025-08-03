# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from datetime import datetime, timedelta
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class SaleOrderDashboardExtension(models.Model):
    """
    Extension to sale.order model ONLY for dashboard data methods.
    This provides dashboard methods without modifying the sale order structure.
    """
    _inherit = 'sale.order'

    @api.model
    def format_dashboard_value(self, value):
        """
        Format large numbers for dashboard display with K/M/B suffixes
        Args:
            value (float/int): The numerical value to format
        Returns:
            str: Formatted string with appropriate suffix
        """
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
        """
        Get overall sales performance data
        Returns dictionary with total quotations, orders, invoiced, and amount
        """
        try:
            _logger.info(f"Getting performance data from {start_date} to {end_date}")
            
            domain = [
                ('date_order', '>=', start_date),
                ('date_order', '<=', end_date)
            ]
            
            # Get all relevant orders
            orders = self.search(domain)
            
            # Calculate performance metrics
            total_quotations = len(orders.filtered(lambda o: o.state in ['draft', 'sent']))
            total_orders = len(orders.filtered(lambda o: o.state in ['sale', 'done']))
            total_invoiced = len(orders.filtered(lambda o: o.invoice_status == 'invoiced'))
            total_amount = sum(orders.mapped('amount_total'))
            
            result = {
                'total_quotations': total_quotations,
                'total_orders': total_orders,
                'total_invoiced': total_invoiced,
                'total_amount': total_amount,
                'performance_indicator': 'good' if total_amount > 0 else 'neutral'
            }
            
            _logger.info(f"Performance data result: {result}")
            return result
            
        except Exception as e:
            _logger.error(f"Error in get_sales_performance_data: {str(e)}")
            return {
                'total_quotations': 0,
                'total_orders': 0,
                'total_invoiced': 0,
                'total_amount': 0,
                'performance_indicator': 'neutral',
                'error': str(e)
            }

    @api.model
    def get_monthly_fluctuation_data(self, start_date, end_date, sales_type_ids=None):
        """
        Get monthly fluctuation data for deal analysis
        Returns data grouped by month for quotations, sales orders, and invoiced sales
        """
        try:
            _logger.info(f"Getting monthly data from {start_date} to {end_date}")
            
            # Parse dates
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Generate monthly buckets
            current_date = start_dt.replace(day=1)
            months = []
            quotations = []
            sales_orders = []
            invoiced_sales = []
            
            while current_date <= end_dt:
                month_start = current_date
                month_end = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                
                # Month label
                month_label = current_date.strftime('%b %Y')
                months.append(month_label)
                
                # Query for this month
                month_domain = [
                    ('date_order', '>=', month_start.strftime('%Y-%m-%d')),
                    ('date_order', '<=', month_end.strftime('%Y-%m-%d'))
                ]
                
                month_orders = self.search(month_domain)
                
                # Calculate monthly metrics
                quotation_amount = sum(month_orders.filtered(lambda o: o.state in ['draft', 'sent']).mapped('amount_total'))
                sales_amount = sum(month_orders.filtered(lambda o: o.state in ['sale', 'done']).mapped('amount_total'))
                invoiced_amount = sum(month_orders.filtered(lambda o: o.invoice_status == 'invoiced').mapped('amount_total'))
                
                quotations.append({'amount': quotation_amount})
                sales_orders.append({'amount': sales_amount})
                invoiced_sales.append({'amount': invoiced_amount})
                
                # Move to next month
                current_date = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            
            result = {
                'labels': months,
                'quotations': quotations,
                'sales_orders': sales_orders,
                'invoiced_sales': invoiced_sales
            }
            
            _logger.info(f"Monthly data result: {result}")
            return result
            
        except Exception as e:
            _logger.error(f"Error in get_monthly_fluctuation_data: {str(e)}")
            return {
                'labels': ['No Data'],
                'quotations': [{'amount': 0}],
                'sales_orders': [{'amount': 0}],
                'invoiced_sales': [{'amount': 0}],
                'error': str(e)
            }

    @api.model
    def get_sales_by_state_data(self, start_date, end_date):
        """
        Get sales data grouped by order state
        Returns counts and labels for different sales order states
        """
        try:
            _logger.info(f"Getting state data from {start_date} to {end_date}")
            
            domain = [
                ('date_order', '>=', start_date),
                ('date_order', '<=', end_date)
            ]
            
            orders = self.search(domain)
            
            # State mapping
            state_mapping = {
                'draft': 'Draft',
                'sent': 'Quotation Sent',
                'sale': 'Sales Order',
                'done': 'Delivered',
                'cancel': 'Cancelled'
            }
            
            # Count by state
            state_counts = {}
            for order in orders:
                state = order.state
                if state in state_counts:
                    state_counts[state] += 1
                else:
                    state_counts[state] = 1
            
            # Prepare result
            labels = []
            counts = []
            
            for state, count in state_counts.items():
                if state in state_mapping:
                    labels.append(state_mapping[state])
                    counts.append(count)
            
            # Ensure we have some data
            if not labels:
                labels = ['No Data']
                counts = [0]
            
            result = {
                'labels': labels,
                'counts': counts
            }
            
            _logger.info(f"State data result: {result}")
            return result
            
        except Exception as e:
            _logger.error(f"Error in get_sales_by_state_data: {str(e)}")
            return {
                'labels': ['Error'],
                'counts': [0],
                'error': str(e)
            }

    @api.model
    def get_top_customers_data(self, start_date, end_date, limit=10):
        """
        Get top customers by sales amount
        Returns customer names and their total purchase amounts
        """
        try:
            _logger.info(f"Getting top customers data from {start_date} to {end_date}")
            
            domain = [
                ('date_order', '>=', start_date),
                ('date_order', '<=', end_date),
                ('state', 'in', ['sale', 'done'])
            ]
            
            orders = self.search(domain)
            
            # Group by customer
            customer_totals = {}
            for order in orders:
                customer_name = order.partner_id.name or 'Unknown Customer'
                if customer_name in customer_totals:
                    customer_totals[customer_name] += order.amount_total
                else:
                    customer_totals[customer_name] = order.amount_total
            
            # Sort by amount and get top customers
            sorted_customers = sorted(customer_totals.items(), key=lambda x: x[1], reverse=True)[:limit]
            
            # Prepare result
            labels = [customer[0] for customer in sorted_customers]
            amounts = [customer[1] for customer in sorted_customers]
            
            # Ensure we have some data
            if not labels:
                labels = ['No customers found']
                amounts = [0]
            
            result = {
                'labels': labels,
                'amounts': amounts
            }
            
            _logger.info(f"Top customers result: {result}")
            return result
            
        except Exception as e:
            _logger.error(f"Error in get_top_customers_data: {str(e)}")
            return {
                'labels': ['Error'],
                'amounts': [0],
                'error': str(e)
            }

    @api.model
    def get_sales_team_performance(self, start_date, end_date):
        """
        Get sales team performance data
        Returns team/salesperson names and their total sales amounts
        """
        try:
            _logger.info(f"Getting sales team data from {start_date} to {end_date}")
            
            domain = [
                ('date_order', '>=', start_date),
                ('date_order', '<=', end_date),
                ('state', 'in', ['sale', 'done'])
            ]
            
            orders = self.search(domain)
            
            # Group by salesperson
            team_totals = {}
            for order in orders:
                salesperson_name = order.user_id.name or 'Unassigned'
                if salesperson_name in team_totals:
                    team_totals[salesperson_name] += order.amount_total
                else:
                    team_totals[salesperson_name] = order.amount_total
            
            # Sort by amount
            sorted_team = sorted(team_totals.items(), key=lambda x: x[1], reverse=True)
            
            # Prepare result
            labels = [member[0] for member in sorted_team]
            amounts = [member[1] for member in sorted_team]
            
            # Ensure we have some data
            if not labels:
                labels = ['No sales team data']
                amounts = [0]
            
            result = {
                'labels': labels,
                'amounts': amounts
            }
            
            _logger.info(f"Sales team result: {result}")
            return result
            
        except Exception as e:
            _logger.error(f"Error in get_sales_team_performance: {str(e)}")
            return {
                'labels': ['Error'],
                'amounts': [0],
                'error': str(e)
            }
