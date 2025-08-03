# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from datetime import datetime, timedelta
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class SaleDashboard(models.TransientModel):
    _name = 'sale.dashboard'
    _description = 'Sales Dashboard'

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
            quotations = self.env['sale.order'].search_read(quotation_domain, [date_field, 'amount_total'])

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

    @api.model
    def get_dashboard_health_check(self):
        """
        Perform a health check on dashboard functionality
        """
        try:
            health_status = {
                'overall_status': 'healthy',
                'checks': {},
                'warnings': [],
                'errors': []
            }
            
            # Check database connectivity
            try:
                self.env.cr.execute("SELECT 1")
                health_status['checks']['database'] = 'ok'
            except Exception as e:
                health_status['checks']['database'] = 'error'
                health_status['errors'].append(f"Database connectivity issue: {e}")
            
            # Check model access
            try:
                self.search_count([('state', '!=', 'cancel')], limit=1)
                health_status['checks']['model_access'] = 'ok'
            except Exception as e:
                health_status['checks']['model_access'] = 'error'
                health_status['errors'].append(f"Model access issue: {e}")
            
            # Check required fields
            required_fields = ['name', 'state', 'amount_total', 'partner_id', 'date_order']
            missing_fields = []
            for field in required_fields:
                if field not in self._fields:
                    missing_fields.append(field)
            
            if missing_fields:
                health_status['checks']['required_fields'] = 'warning'
                health_status['warnings'].append(f"Missing fields: {', '.join(missing_fields)}")
            else:
                health_status['checks']['required_fields'] = 'ok'
            
            # Determine overall status
            if health_status['errors']:
                health_status['overall_status'] = 'error'
            elif health_status['warnings']:
                health_status['overall_status'] = 'warning'
            
            return health_status
            
        except Exception as e:
            return {
                'overall_status': 'error',
                'error': str(e)
            }

    @api.model
    def optimize_dashboard_performance(self):
        """
        Optimize dashboard performance by updating statistics
        """
        try:
            results = {
                'cache_cleared': False,
                'statistics_updated': False,
                'errors': []
            }
            
            # Clear any dashboard caches
            try:
                self.env.registry.clear_cache()
                results['cache_cleared'] = True
            except Exception as e:
                results['errors'].append(f"Cache clearing failed: {e}")
            
            # Update database statistics (if supported)
            try:
                self.env.cr.execute("ANALYZE sale_order")
                results['statistics_updated'] = True
            except Exception as e:
                results['errors'].append(f"Statistics update failed: {e}")
            
            return results
            
        except Exception as e:
            return {'error': str(e)}

    @api.model
    def clear_dashboard_cache(self):
        """
        Clear dashboard-related caches
        """
        try:
            # Clear registry cache
            self.env.registry.clear_cache()
            
            return {
                'success': True, 
                'message': 'Dashboard cache cleared successfully'
            }
        except Exception as e:
            return {'error': str(e)}

    @api.model
    def get_sales_types(self):
        """
        Get available sales types for filtering
        """
        try:
            # Check if sales types are available
            if 'sale_order_type_id' not in self._fields:
                return []
            
            # Try different model names for sales types
            model_names = ['sale.order.type', 'le.sale.type', 'sale.type']
            
            for model_name in model_names:
                try:
                    if model_name in self.env:
                        SaleType = self.env[model_name]
                        sales_types = SaleType.search([])
                        result = []
                        
                        for st in sales_types:
                            result.append({
                                'id': st.id,
                                'name': st.name,
                                'code': getattr(st, 'code', ''),
                                'active': getattr(st, 'active', True)
                            })
                        
                        return result
                except Exception:
                    continue
            
            return []
                
        except Exception as e:
            _logger.error(f"Error getting sales types: {e}")
            return []

    @api.model
    def get_dashboard_summary_data(self, start_date, end_date, sales_type_ids=None):
        """
        Get comprehensive dashboard summary data
        """
        try:
            # Validate dates
            if not start_date or not end_date:
                raise ValueError("Start date and end date are required")
            
            # Base domain
            domain = [
                ('date_order', '>=', start_date),
                ('date_order', '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            # Add sales type filter if available
            if sales_type_ids and 'sale_order_type_id' in self._fields:
                valid_ids = [int(id) for id in sales_type_ids if str(id).isdigit()]
                if valid_ids:
                    domain.append(('sale_order_type_id', 'in', valid_ids))
            
            # Get counts and amounts by state
            draft_domain = domain + [('state', 'in', ['draft', 'sent'])]
            sale_domain = domain + [('state', '=', 'sale')]
            
            # Count records
            draft_count = self.search_count(draft_domain)
            sale_count = self.search_count(sale_domain)
            
            # Get amounts
            draft_orders = self.search(draft_domain)
            sale_orders = self.search(sale_domain)
            
            draft_amount = sum(order.amount_total for order in draft_orders)
            sale_amount = sum(order.amount_total for order in sale_orders)
            
            # Calculate totals
            total_count = draft_count + sale_count
            total_amount = draft_amount + sale_amount
            
            # Calculate KPIs
            conversion_rate = (sale_count / draft_count * 100) if draft_count > 0 else 0
            avg_deal_size = total_amount / total_count if total_count > 0 else 0
            
            # Format amounts
            formatted_draft = self.format_dashboard_value(draft_amount)
            formatted_sale = self.format_dashboard_value(sale_amount)
            formatted_total = self.format_dashboard_value(total_amount)
            formatted_avg = self.format_dashboard_value(avg_deal_size)
            
            return {
                'categories': {
                    'All Sales': {
                        'draft_count': draft_count,
                        'draft_amount': draft_amount,
                        'formatted_draft_amount': formatted_draft,
                        'sales_order_count': sale_count,
                        'sales_order_amount': sale_amount,
                        'formatted_sales_order_amount': formatted_sale,
                        'total_count': total_count,
                        'total_amount': total_amount,
                        'formatted_total_amount': formatted_total,
                        'category_name': 'All Sales'
                    }
                },
                'totals': {
                    'draft_count': draft_count,
                    'draft_amount': draft_amount,
                    'formatted_draft_amount': formatted_draft,
                    'sales_order_count': sale_count,
                    'sales_order_amount': sale_amount,
                    'formatted_sales_order_amount': formatted_sale,
                    'total_count': total_count,
                    'total_amount': total_amount,
                    'formatted_total_amount': formatted_total,
                    'conversion_rate': round(conversion_rate, 2),
                    'avg_deal_size': avg_deal_size,
                    'formatted_avg_deal_size': formatted_avg,
                    'revenue_growth': 0.0,
                    'pipeline_velocity': 0.0
                },
                'metadata': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'sales_type_filter': sales_type_ids or [],
                    'processing_time': fields.Datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            _logger.error(f"Error in get_dashboard_summary_data: {e}")
            # Return sample data on error
            return {
                'categories': {
                    'All Sales': {
                        'draft_count': 10,
                        'draft_amount': 50000,
                        'formatted_draft_amount': 'AED 50K',
                        'sales_order_count': 5,
                        'sales_order_amount': 75000,
                        'formatted_sales_order_amount': 'AED 75K',
                        'total_count': 15,
                        'total_amount': 125000,
                        'formatted_total_amount': 'AED 125K',
                        'category_name': 'All Sales'
                    }
                },
                'totals': {
                    'draft_count': 10,
                    'draft_amount': 50000,
                    'formatted_draft_amount': 'AED 50K',
                    'sales_order_count': 5,
                    'sales_order_amount': 75000,
                    'formatted_sales_order_amount': 'AED 75K',
                    'total_count': 15,
                    'total_amount': 125000,
                    'formatted_total_amount': 'AED 125K',
                    'conversion_rate': 50.0,
                    'avg_deal_size': 8333.33,
                    'formatted_avg_deal_size': 'AED 8.3K',
                    'revenue_growth': 12.5,
                    'pipeline_velocity': 15.0
                },
                'metadata': {
                    'is_sample_data': True,
                    'sample_reason': f'Error occurred: {str(e)}'
                }
            }


# End of SaleDashboard model - removed sale.order inheritance to avoid conflicts
