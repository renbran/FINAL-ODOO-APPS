# -*- coding: utf-8 -*-
# This module is under copyright of 'OdooElevate'

from odoo import models, api
from datetime import datetime, timedelta
from collections import defaultdict


class SaleDashboard(models.Model):
    _inherit = 'sale.order'

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
            
            # Base domain for filtering
            base_domain = [
                ('booking_date', '>=', start_date),
                ('booking_date', '<=', end_date),
                ('state', '!=', 'cancel')  # Exclude cancelled orders
            ]
            
            if sales_type_ids:
                base_domain.append(('sale_order_type_id', 'in', sales_type_ids))
            
            # Get quotations (draft, sent)
            quotation_domain = base_domain + [('state', 'in', ['draft', 'sent'])]
            quotations = self.search_read(quotation_domain, ['booking_date', 'amount_total', 'sale_value'])
            
            for quote in quotations:
                if quote['booking_date']:
                    month_key = quote['booking_date'].strftime('%Y-%m')
                    if month_key in monthly_data:
                        monthly_data[month_key]['quotations']['count'] += 1
                        monthly_data[month_key]['quotations']['amount'] += quote['sale_value'] or quote['amount_total'] or 0
            
            # Get sales orders (confirmed but not invoiced)
            sales_order_domain = base_domain + [
                ('state', '=', 'sale'),
                ('invoice_status', 'in', ['to invoice', 'no', 'upselling'])
            ]
            sales_orders = self.search_read(sales_order_domain, ['booking_date', 'amount_total', 'sale_value'])
            
            for order in sales_orders:
                if order['booking_date']:
                    month_key = order['booking_date'].strftime('%Y-%m')
                    if month_key in monthly_data:
                        monthly_data[month_key]['sales_orders']['count'] += 1
                        monthly_data[month_key]['sales_orders']['amount'] += order['sale_value'] or order['amount_total'] or 0
            
            # Get invoiced sales
            invoiced_domain = base_domain + [
                ('state', '=', 'sale'),
                ('invoice_status', '=', 'invoiced')
            ]
            invoiced_orders = self.search_read(invoiced_domain, ['booking_date', 'amount_total', 'sale_value', 'name'])
            
            # Get actual invoiced amounts
            for order in invoiced_orders:
                if order['booking_date']:
                    month_key = order['booking_date'].strftime('%Y-%m')
                    if month_key in monthly_data:
                        monthly_data[month_key]['invoiced_sales']['count'] += 1
                        
                        # Try to get actual invoiced amount
                        invoiced_amount = self._get_actual_invoiced_amount(order['name'])
                        amount = invoiced_amount or order['sale_value'] or order['amount_total'] or 0
                        monthly_data[month_key]['invoiced_sales']['amount'] += amount
            
            # Convert to chart format
            result = {
                'labels': month_labels,
                'quotations': [],
                'sales_orders': [],
                'invoiced_sales': []
            }
            
            for label in month_labels:
                # Find the corresponding month data
                month_key = None
                for key in monthly_data.keys():
                    if datetime.strptime(key, '%Y-%m').strftime('%b %Y') == label:
                        month_key = key
                        break
                
                if month_key and month_key in monthly_data:
                    result['quotations'].append(monthly_data[month_key]['quotations']['amount'])
                    result['sales_orders'].append(monthly_data[month_key]['sales_orders']['amount'])
                    result['invoiced_sales'].append(monthly_data[month_key]['invoiced_sales']['amount'])
                else:
                    result['quotations'].append(0)
                    result['sales_orders'].append(0)
                    result['invoiced_sales'].append(0)
            
            return result
            
        except Exception as e:
            # Return default data structure on error
            return {
                'labels': ['Current Period'],
                'quotations': [0],
                'sales_orders': [0],
                'invoiced_sales': [0],
                'error': str(e)
            }
    
    def _get_actual_invoiced_amount(self, order_name):
        """Get actual invoiced amount from account.move records"""
        try:
            invoices = self.env['account.move'].search([
                ('invoice_origin', '=', order_name),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted')
            ])
            
            total_amount = 0.0
            for invoice in invoices:
                if invoice.move_type == 'out_invoice':
                    total_amount += invoice.amount_total
                elif invoice.move_type == 'out_refund':
                    total_amount -= invoice.amount_total
            
            return total_amount
        except:
            return 0.0

    @api.model
    def get_sales_type_distribution(self, start_date, end_date):
        """
        Get sales type distribution data for pie charts
        Returns count and amount distribution by sales type
        """
        try:
            # Base domain excluding cancelled orders
            base_domain = [
                ('booking_date', '>=', start_date),
                ('booking_date', '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            # Get all sales types
            sales_types = self.env['sale.order.type'].search([])
            
            count_distribution = {}
            amount_distribution = {}
            
            for sales_type in sales_types:
                type_domain = base_domain + [('sale_order_type_id', '=', sales_type.id)]
                
                # Get all orders for this type
                orders = self.search_read(type_domain, ['state', 'invoice_status', 'amount_total', 'sale_value', 'name'])
                
                total_count = len(orders)
                total_amount = 0.0
                
                for order in orders:
                    # For invoiced orders, try to get actual invoiced amount
                    if order['state'] == 'sale' and order['invoice_status'] == 'invoiced':
                        invoiced_amount = self._get_actual_invoiced_amount(order['name'])
                        amount = invoiced_amount or order['sale_value'] or order['amount_total'] or 0
                    else:
                        amount = order['sale_value'] or order['amount_total'] or 0
                    
                    total_amount += amount
                
                if total_count > 0:  # Only include types with data
                    count_distribution[sales_type.name] = total_count
                    amount_distribution[sales_type.name] = total_amount
            
            return {
                'count_distribution': count_distribution,
                'amount_distribution': amount_distribution
            }
            
        except Exception as e:
            return {
                'count_distribution': {},
                'amount_distribution': {},
                'error': str(e)
            }
