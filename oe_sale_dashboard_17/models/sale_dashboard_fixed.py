# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from datetime import datetime, timedelta
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class SaleDashboard(models.Model):
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
    def get_monthly_fluctuation_data(self, start_date, end_date, sales_type_ids=None):
        """
        Get monthly fluctuation data for deal analysis
        Returns data grouped by month for quotations, sales orders, and invoiced sales
        """
        try:
            # Parse dates
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Generate monthly buckets
            monthly_data = defaultdict(lambda: {
                'quotations': {'count': 0, 'amount': 0},
                'sales_orders': {'count': 0, 'amount': 0},
                'invoiced_sales': {'count': 0, 'amount': 0}
            })
            
            # Generate month labels
            current_dt = start_dt.replace(day=1)
            month_labels = []
            
            while current_dt <= end_dt:
                month_key = current_dt.strftime('%Y-%m')
                month_label = current_dt.strftime('%b %Y')
                month_labels.append(month_label)
                monthly_data[month_key]  # Initialize if not exists
                current_dt = current_dt.replace(day=28) + timedelta(days=4)
                current_dt = current_dt.replace(day=1)
            
            # Use safer date field - check availability
            date_field = 'date_order'  # Standard Odoo field
            if 'booking_date' in self.env['sale.order']._fields:
                date_field = 'booking_date'
            
            # Base domain for filtering
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')  # Exclude cancelled orders
            ]

            # Only add sales type filter if the field exists
            if sales_type_ids:
                try:
                    if 'sale_order_type_id' in self.env['sale.order']._fields:
                        base_domain.append(('sale_order_type_id', 'in', sales_type_ids))
                except Exception as e:
                    _logger.warning(f"Sales type filter error: {e}")

            # Get quotations (draft, sent)
            quotation_domain = base_domain + [('state', 'in', ['draft', 'sent'])]
            quotations = self.search_read(quotation_domain, [date_field, 'amount_total'])

            for quote in quotations:
                if quote[date_field]:
                    order_date = quote[date_field]
                    if isinstance(order_date, str):
                        month_key = datetime.strptime(order_date, '%Y-%m-%d').strftime('%Y-%m')
                    else:
                        month_key = order_date.strftime('%Y-%m')
                    
                    if month_key in monthly_data:
                        monthly_data[month_key]['quotations']['count'] += 1
                        monthly_data[month_key]['quotations']['amount'] += quote.get('amount_total', 0)

            # Get sales orders (confirmed)
            sales_order_domain = base_domain + [('state', '=', 'sale')]
            sales_orders = self.search_read(sales_order_domain, [date_field, 'amount_total', 'invoice_status'])

            for order in sales_orders:
                if order[date_field]:
                    order_date = order[date_field]
                    if isinstance(order_date, str):
                        month_key = datetime.strptime(order_date, '%Y-%m-%d').strftime('%Y-%m')
                    else:
                        month_key = order_date.strftime('%Y-%m')
                    
                    if month_key in monthly_data:
                        amount = order.get('amount_total', 0)
                        
                        if order.get('invoice_status') == 'invoiced':
                            monthly_data[month_key]['invoiced_sales']['count'] += 1
                            monthly_data[month_key]['invoiced_sales']['amount'] += amount
                        else:
                            monthly_data[month_key]['sales_orders']['count'] += 1
                            monthly_data[month_key]['sales_orders']['amount'] += amount

            # Convert to chart format
            result = {
                'labels': month_labels,
                'quotations': [],
                'sales_orders': [],
                'invoiced_sales': []
            }
            
            for label in month_labels:
                month_dt = datetime.strptime(label, '%b %Y')
                month_key = month_dt.strftime('%Y-%m')
                
                result['quotations'].append(monthly_data[month_key]['quotations'])
                result['sales_orders'].append(monthly_data[month_key]['sales_orders'])
                result['invoiced_sales'].append(monthly_data[month_key]['invoiced_sales'])
            
            return result
            
        except Exception as e:
            _logger.error(f"Error in get_monthly_fluctuation_data: {e}")
            # Return default structure on error
            return {
                'labels': ['Current Period'],
                'quotations': [{'count': 0, 'amount': 0}],
                'sales_orders': [{'count': 0, 'amount': 0}],
                'invoiced_sales': [{'count': 0, 'amount': 0}],
                'error': str(e)
            }
    
    @api.model
    def get_sales_performance_data(self, start_date, end_date):
        """Get sales performance KPIs"""
        try:
            date_field = 'date_order'
            if 'booking_date' in self.env['sale.order']._fields:
                date_field = 'booking_date'
                
            domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            orders = self.search_read(domain, ['state', 'amount_total', 'invoice_status'])
            
            total_quotations = len([o for o in orders if o['state'] in ['draft', 'sent']])
            total_orders = len([o for o in orders if o['state'] == 'sale'])
            total_invoiced = len([o for o in orders if o['state'] == 'sale' and o.get('invoice_status') == 'invoiced'])
            
            total_amount = sum(o.get('amount_total', 0) for o in orders)
            invoiced_amount = sum(o.get('amount_total', 0) for o in orders 
                                 if o['state'] == 'sale' and o.get('invoice_status') == 'invoiced')
            
            conversion_rate = (total_orders / total_quotations * 100) if total_quotations > 0 else 0
            
            return {
                'total_quotations': total_quotations,
                'total_orders': total_orders,
                'total_invoiced': total_invoiced,
                'total_amount': self.format_dashboard_value(total_amount),
                'invoiced_amount': self.format_dashboard_value(invoiced_amount),
                'conversion_rate': round(conversion_rate, 1)
            }
            
        except Exception as e:
            _logger.error(f"Error in get_sales_performance_data: {e}")
            return {
                'total_quotations': 0,
                'total_orders': 0,
                'total_invoiced': 0,
                'total_amount': '0',
                'invoiced_amount': '0',
                'conversion_rate': 0,
                'error': str(e)
            }

    @api.model
    def get_sales_by_state_data(self, start_date, end_date):
        """Get sales distribution by state for pie chart"""
        try:
            date_field = 'date_order'
            if 'booking_date' in self.env['sale.order']._fields:
                date_field = 'booking_date'
                
            domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            orders = self.search_read(domain, ['state', 'amount_total'])
            
            state_data = defaultdict(lambda: {'count': 0, 'amount': 0})
            
            for order in orders:
                state = order['state']
                amount = order.get('amount_total', 0)
                
                if state in ['draft', 'sent']:
                    state_data['Quotations']['count'] += 1
                    state_data['Quotations']['amount'] += amount
                elif state == 'sale':
                    state_data['Sales Orders']['count'] += 1
                    state_data['Sales Orders']['amount'] += amount
                elif state == 'done':
                    state_data['Completed']['count'] += 1
                    state_data['Completed']['amount'] += amount
            
            labels = list(state_data.keys())
            counts = [state_data[label]['count'] for label in labels]
            amounts = [state_data[label]['amount'] for label in labels]
            
            return {
                'labels': labels,
                'counts': counts,
                'amounts': amounts
            }
            
        except Exception as e:
            _logger.error(f"Error in get_sales_by_state_data: {e}")
            return {
                'labels': ['No Data'],
                'counts': [0],
                'amounts': [0],
                'error': str(e)
            }

    @api.model
    def get_top_customers_data(self, start_date, end_date, limit=10):
        """Get top customers by sales amount"""
        try:
            date_field = 'date_order'
            if 'booking_date' in self.env['sale.order']._fields:
                date_field = 'booking_date'
                
            domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', 'in', ['sale', 'done'])
            ]
            
            orders = self.search_read(domain, ['partner_id', 'amount_total'])
            
            customer_data = defaultdict(lambda: {'count': 0, 'amount': 0, 'name': ''})
            
            for order in orders:
                if order['partner_id']:
                    partner_id = order['partner_id'][0]
                    partner_name = order['partner_id'][1]
                    amount = order.get('amount_total', 0)
                    
                    customer_data[partner_id]['count'] += 1
                    customer_data[partner_id]['amount'] += amount
                    customer_data[partner_id]['name'] = partner_name
            
            # Sort by amount and get top customers
            sorted_customers = sorted(customer_data.items(), 
                                    key=lambda x: x[1]['amount'], reverse=True)[:limit]
            
            labels = [data['name'] for _, data in sorted_customers]
            amounts = [data['amount'] for _, data in sorted_customers]
            counts = [data['count'] for _, data in sorted_customers]
            
            return {
                'labels': labels,
                'amounts': amounts,
                'counts': counts
            }
            
        except Exception as e:
            _logger.error(f"Error in get_top_customers_data: {e}")
            return {
                'labels': ['No Data'],
                'amounts': [0],
                'counts': [0],
                'error': str(e)
            }

    @api.model
    def get_sales_team_performance(self, start_date, end_date):
        """Get sales team performance data"""
        try:
            date_field = 'date_order'
            if 'booking_date' in self.env['sale.order']._fields:
                date_field = 'booking_date'
                
            domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', 'in', ['sale', 'done'])
            ]
            
            # Check if user_id field exists
            fields_to_read = ['amount_total']
            if 'user_id' in self.env['sale.order']._fields:
                fields_to_read.append('user_id')
            
            orders = self.search_read(domain, fields_to_read)
            
            if 'user_id' not in self.env['sale.order']._fields:
                return {
                    'labels': ['Sales Team'],
                    'amounts': [sum(o.get('amount_total', 0) for o in orders)],
                    'counts': [len(orders)]
                }
            
            team_data = defaultdict(lambda: {'count': 0, 'amount': 0, 'name': ''})
            
            for order in orders:
                if order.get('user_id'):
                    user_id = order['user_id'][0]
                    user_name = order['user_id'][1]
                    amount = order.get('amount_total', 0)
                    
                    team_data[user_id]['count'] += 1
                    team_data[user_id]['amount'] += amount
                    team_data[user_id]['name'] = user_name
                else:
                    # Unassigned orders
                    team_data[0]['count'] += 1
                    team_data[0]['amount'] += order.get('amount_total', 0)
                    team_data[0]['name'] = 'Unassigned'
            
            # Sort by amount
            sorted_team = sorted(team_data.items(), 
                               key=lambda x: x[1]['amount'], reverse=True)
            
            labels = [data['name'] for _, data in sorted_team]
            amounts = [data['amount'] for _, data in sorted_team]
            counts = [data['count'] for _, data in sorted_team]
            
            return {
                'labels': labels,
                'amounts': amounts,
                'counts': counts
            }
            
        except Exception as e:
            _logger.error(f"Error in get_sales_team_performance: {e}")
            return {
                'labels': ['Sales Team'],
                'amounts': [0],
                'counts': [0],
                'error': str(e)
            }
