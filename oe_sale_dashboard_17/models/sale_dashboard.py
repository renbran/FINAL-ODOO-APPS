from odoo import models, api, fields, _
from datetime import datetime, timedelta
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class SaleDashboard(models.Model):
    _inherit = 'sale.order'

    @api.model
    def format_dashboard_value(self, value, currency='AED'):
        """
        Format large numbers for dashboard display with K/M/B suffixes and AED currency
        Args:
            value (float/int): The numerical value to format
            currency (str): Currency symbol (default: AED)
        Returns:
            str: Formatted string with appropriate suffix and currency
        """
        if not value or value == 0:
            return f"0 {currency}"
        
        abs_value = abs(value)
        
        if abs_value >= 1_000_000_000:
            formatted = round(value / 1_000_000_000, 2)
            return f"{formatted}B {currency}"
        elif abs_value >= 1_000_000:
            formatted = round(value / 1_000_000, 2)
            return f"{formatted}M {currency}"
        elif abs_value >= 1_000:
            formatted = round(value / 1_000)
            return f"{formatted:.0f}K {currency}"
        else:
            return f"{round(value):,.0f} {currency}"

    @api.model
    def get_sales_order_types(self):
        """
        Get all available sales order types for filtering
        """
        try:
            sales_types = self.env['sale.order.type'].search([])
            return [{
                'id': st.id,
                'name': st.name,
                'code': getattr(st, 'code', ''),
                'active': st.active
            } for st in sales_types]
        except Exception as e:
            _logger.error(f"Error getting sales order types: {e}")
            return []

    @api.model
    def get_dashboard_kpis(self, start_date, end_date, sales_type_ids=None):
        """
        Get main KPI metrics for the dashboard
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            sales_type_ids: List of sales order type IDs to filter by
        """
        try:
            base_domain = [
                ('date_order', '>=', start_date),
                ('date_order', '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            # Add sales type filter if provided
            if sales_type_ids:
                base_domain.append(('sale_order_type_id', 'in', sales_type_ids))
            
            orders = self.search_read(base_domain, [
                'state', 'amount_total', 'invoice_status', 'date_order'
            ])
            
            # Calculate KPIs
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
            _logger.error(f"Error in get_dashboard_kpis: {e}")
            return {
                'total_quotations': 0,
                'total_orders': 0,
                'total_invoiced': 0,
                'total_amount': '0 AED',
                'invoiced_amount': '0 AED',
                'conversion_rate': 0
            }

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

    @api.model 
    def get_top_performers_data(self, start_date, end_date, performer_type='agent', limit=10):
        """
        Get top performing agents or agencies based on sales performance
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering  
            performer_type: 'agent' for agents, 'agency' for agencies
            limit: Number of top performers to return (default 10)
        Returns:
            List of top performers with their metrics
        """
        try:
            # Determine field names based on performer type
            if performer_type == 'agent':
                partner_field = 'agent1_partner_id'
                amount_field = 'agent1_amount'
            elif performer_type == 'agency':
                partner_field = 'broker_partner_id'
                amount_field = 'broker_amount'
            else:
                return []

            # Base domain for filtering
            base_domain = [
                ('booking_date', '>=', start_date),
                ('booking_date', '<=', end_date),
                ('state', '!=', 'cancel'),  # Exclude cancelled orders
                (partner_field, '!=', False)  # Must have agent/broker assigned
            ]

            # Get all orders with the specified criteria  
            # Include all necessary fields for comprehensive ranking
            orders = self.search_read(base_domain, [
                partner_field, 'amount_total', 'sale_value', amount_field, 
                'state', 'invoice_status', 'name', 'booking_date'
            ])
            
            # Debug logging
            import logging
            _logger = logging.getLogger(__name__)
            _logger.info(f"Found {len(orders)} orders for {performer_type} ranking")
            if orders:
                _logger.info(f"Sample order fields: {list(orders[0].keys())}")
                _logger.info(f"Sample order data: {orders[0]}")
                _logger.info(f"Looking for partner field: {partner_field}, amount field: {amount_field}")

            # Group data by partner
            partner_data = {}
            
            for order in orders:
                partner_id = order.get(partner_field)
                if not partner_id:
                    continue
                    
                # Handle both tuple format (id, name) and plain id
                if isinstance(partner_id, tuple) and len(partner_id) == 2:
                    partner_key = partner_id[0]
                    partner_name = partner_id[1]
                elif isinstance(partner_id, (int, list)):
                    partner_key = partner_id[0] if isinstance(partner_id, list) else partner_id
                    # Get partner name from res.partner model
                    partner_rec = self.env['res.partner'].browse(partner_key)
                    partner_name = partner_rec.name if partner_rec.exists() else f"Partner {partner_key}"
                else:
                    continue
                
                if partner_key not in partner_data:
                    partner_data[partner_key] = {
                        'partner_id': partner_key,
                        'partner_name': partner_name,
                        'count': 0,
                        'total_sales_value': 0.0,
                        'total_commission': 0.0,
                        'invoiced_count': 0,
                        'invoiced_sales_value': 0.0,
                        'invoiced_commission': 0.0
                    }
                
                # Get values with proper fallbacks and validation
                sales_value = float(order.get('sale_value') or order.get('amount_total') or 0.0)
                commission_value = float(order.get(amount_field) or 0.0)
                
                # Debug logging for first few records
                if len(partner_data) < 3:
                    _logger.info(f"Processing order {order.get('name')}: sales_value={sales_value}, commission={commission_value}, partner={partner_name}")
                
                # Add to totals
                partner_data[partner_key]['count'] += 1
                partner_data[partner_key]['total_sales_value'] += sales_value
                partner_data[partner_key]['total_commission'] += commission_value
                
                # If invoiced, add to invoiced totals
                if order.get('state') == 'sale' and order.get('invoice_status') == 'invoiced':
                    partner_data[partner_key]['invoiced_count'] += 1
                    
                    # Try to get actual invoiced amount
                    order_name = order.get('name', '')
                    invoiced_amount = self._get_actual_invoiced_amount(order_name)
                    final_sales_value = invoiced_amount or sales_value
                    
                    partner_data[partner_key]['invoiced_sales_value'] += final_sales_value
                    partner_data[partner_key]['invoiced_commission'] += commission_value

            # Convert to list and sort by total sales value (descending), then by commission
            performers_list = list(partner_data.values())
            
            # Sort by multiple criteria for better ranking
            performers_list.sort(key=lambda x: (
                -float(x.get('total_sales_value', 0)),      # Primary: Total sales value (descending)
                -float(x.get('total_commission', 0)),       # Secondary: Total commission (descending) 
                -int(x.get('count', 0))                     # Tertiary: Number of sales (descending)
            ))
            
            # Debug logging
            _logger.info(f"Sorted {len(performers_list)} {performer_type}s. Top 3:")
            for i, performer in enumerate(performers_list[:3]):
                _logger.info(f"  {i+1}. {performer.get('partner_name')} - Sales: {performer.get('total_sales_value')}, Commission: {performer.get('total_commission')}")
            
            # Return top performers limited to the specified count
            top_performers = performers_list[:limit]
            _logger.info(f"Returning top {len(top_performers)} {performer_type}s")
            return top_performers
            
        except Exception as e:
            # Log the error for debugging
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Error in get_top_performers_data: {str(e)}")
            _logger.error(f"Parameters: start_date={start_date}, end_date={end_date}, performer_type={performer_type}, limit={limit}")
            
            # Return empty list instead of error dict for frontend compatibility
            return []

    @api.model
    def get_project_analysis(self, start_date, end_date, sales_type_ids=None):
        """
        Get sales analysis by project for dashboard
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            sales_type_ids: List of sales order type IDs to filter by
        """
        try:
            base_domain = [
                ('date_order', '>=', start_date),
                ('date_order', '<=', end_date),
                ('state', 'in', ['sale', 'done']),
            ]
            
            # Add sales type filter if provided
            if sales_type_ids:
                base_domain.append(('sale_order_type_id', 'in', sales_type_ids))
            
            # Check if project fields exist
            project_field = None
            if 'project_id' in self.env['sale.order']._fields:
                project_field = 'project_id'
            elif 'analytic_account_id' in self.env['sale.order']._fields:
                project_field = 'analytic_account_id'
            
            if not project_field:
                return {
                    'labels': ['No Project Data'],
                    'amounts': [0],
                    'counts': [0]
                }
            
            orders = self.search_read(base_domain, [project_field, 'amount_total'])
            
            project_data = defaultdict(lambda: {'count': 0, 'amount': 0, 'name': ''})
            
            for order in orders:
                if order.get(project_field):
                    project_id = order[project_field][0]
                    project_name = order[project_field][1]
                    amount = order.get('amount_total', 0)
                    
                    project_data[project_id]['count'] += 1
                    project_data[project_id]['amount'] += amount
                    project_data[project_id]['name'] = project_name
                else:
                    # Unassigned projects
                    project_data[0]['count'] += 1
                    project_data[0]['amount'] += order.get('amount_total', 0)
                    project_data[0]['name'] = 'Unassigned'
            
            # Sort by amount and get top projects
            sorted_projects = sorted(project_data.items(), 
                                   key=lambda x: x[1]['amount'], reverse=True)[:10]
            
            labels = [data['name'] for _, data in sorted_projects]
            amounts = [self.format_dashboard_value(data['amount']) for _, data in sorted_projects]
            raw_amounts = [data['amount'] for _, data in sorted_projects]
            counts = [data['count'] for _, data in sorted_projects]
            
            return {
                'labels': labels,
                'amounts': amounts,
                'raw_amounts': raw_amounts,
                'counts': counts
            }
            
        except Exception as e:
            _logger.error(f"Error in get_project_analysis: {e}")
            return {
                'labels': ['No Data'],
                'amounts': ['0 AED'],
                'raw_amounts': [0],
                'counts': [0]
            }

    @api.model
    def get_agent_ranking(self, start_date, end_date, limit=10, sales_type_ids=None):
        """
        Get comprehensive agent ranking with performance metrics
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            limit: Number of top agents to return
            sales_type_ids: List of sales order type IDs to filter by
        """
        try:
            base_domain = [
                ('date_order', '>=', start_date),
                ('date_order', '<=', end_date),
                ('state', '!=', 'cancel'),
            ]
            
            # Add sales type filter if provided
            if sales_type_ids:
                base_domain.append(('sale_order_type_id', 'in', sales_type_ids))
            
            # Check for agent fields
            agent_field = None
            if 'user_id' in self.env['sale.order']._fields:
                agent_field = 'user_id'
            elif 'agent_id' in self.env['sale.order']._fields:
                agent_field = 'agent_id'
            elif 'salesperson_id' in self.env['sale.order']._fields:
                agent_field = 'salesperson_id'
            
            if not agent_field:
                return {
                    'labels': ['No Agent Data'],
                    'performance_scores': [0],
                    'total_sales': [0],
                    'commission_earned': [0]
                }
            
            orders = self.search_read(base_domain, [
                agent_field, 'amount_total', 'state', 'invoice_status'
            ])
            
            agent_data = defaultdict(lambda: {
                'name': '',
                'total_sales': 0,
                'orders_count': 0,
                'invoiced_count': 0,
                'quotations_count': 0,
                'conversion_rate': 0,
                'performance_score': 0
            })
            
            for order in orders:
                if order.get(agent_field):
                    agent_id = order[agent_field][0]
                    agent_name = order[agent_field][1]
                    amount = order.get('amount_total', 0)
                    
                    agent_data[agent_id]['name'] = agent_name
                    agent_data[agent_id]['total_sales'] += amount
                    
                    if order['state'] in ['draft', 'sent']:
                        agent_data[agent_id]['quotations_count'] += 1
                    elif order['state'] == 'sale':
                        agent_data[agent_id]['orders_count'] += 1
                        if order.get('invoice_status') == 'invoiced':
                            agent_data[agent_id]['invoiced_count'] += 1
            
            # Calculate performance metrics
            for agent_id, data in agent_data.items():
                total_deals = data['quotations_count'] + data['orders_count']
                if total_deals > 0:
                    data['conversion_rate'] = (data['orders_count'] / total_deals) * 100
                
                # Performance score: weighted combination of sales, conversion, and invoicing
                sales_score = min(data['total_sales'] / 100000, 100)  # Max 100 points for 100K AED
                conversion_score = data['conversion_rate']  # Already in percentage
                invoicing_score = (data['invoiced_count'] / max(data['orders_count'], 1)) * 100
                
                data['performance_score'] = (sales_score * 0.5 + conversion_score * 0.3 + invoicing_score * 0.2)
            
            # Sort by performance score
            sorted_agents = sorted(agent_data.items(), 
                                 key=lambda x: x[1]['performance_score'], reverse=True)[:limit]
            
            labels = [data['name'] for _, data in sorted_agents]
            performance_scores = [round(data['performance_score'], 1) for _, data in sorted_agents]
            total_sales = [self.format_dashboard_value(data['total_sales']) for _, data in sorted_agents]
            raw_sales = [data['total_sales'] for _, data in sorted_agents]
            
            return {
                'labels': labels,
                'performance_scores': performance_scores,
                'total_sales': total_sales,
                'raw_sales': raw_sales,
                'conversion_rates': [round(data['conversion_rate'], 1) for _, data in sorted_agents]
            }
            
        except Exception as e:
            _logger.error(f"Error in get_agent_ranking: {e}")
            return {
                'labels': ['No Data'],
                'performance_scores': [0],
                'total_sales': ['0 AED'],
                'raw_sales': [0],
                'conversion_rates': [0]
            }

    @api.model
    def get_invoice_status_analysis(self, start_date, end_date, sales_type_ids=None):
        """
        Get detailed invoice status analysis
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            sales_type_ids: List of sales order type IDs to filter by
        """
        try:
            base_domain = [
                ('date_order', '>=', start_date),
                ('date_order', '<=', end_date),
                ('state', '=', 'sale'),  # Only confirmed orders
            ]
            
            # Add sales type filter if provided
            if sales_type_ids:
                base_domain.append(('sale_order_type_id', 'in', sales_type_ids))
            
            orders = self.search_read(base_domain, ['invoice_status', 'amount_total'])
            
            status_data = defaultdict(lambda: {'count': 0, 'amount': 0})
            
            # Status mapping for better display
            status_mapping = {
                'upselling': 'Upselling Opportunity',
                'invoiced': 'Fully Invoiced',
                'to invoice': 'To Invoice',
                'no': 'Nothing to Invoice'
            }
            
            for order in orders:
                status = order.get('invoice_status', 'unknown')
                amount = order.get('amount_total', 0)
                
                display_status = status_mapping.get(status, status.title())
                status_data[display_status]['count'] += 1
                status_data[display_status]['amount'] += amount
            
            # Calculate totals for percentages
            total_amount = sum(data['amount'] for data in status_data.values())
            total_count = sum(data['count'] for data in status_data.values())
            
            # Prepare chart data
            labels = list(status_data.keys())
            amounts = [data['amount'] for data in status_data.values()]
            counts = [data['count'] for data in status_data.values()]
            percentages = [
                round((amount / total_amount * 100), 1) if total_amount > 0 else 0
                for amount in amounts
            ]
            
            # Summary metrics
            invoiced_amount = status_data.get('Fully Invoiced', {}).get('amount', 0)
            pending_amount = sum(
                status_data.get(status, {}).get('amount', 0)
                for status in ['To Invoice', 'Upselling Opportunity']
            )
            
            return {
                'labels': labels,
                'amounts': amounts,
                'counts': counts,
                'percentages': percentages,
                'formatted_amounts': [self.format_dashboard_value(amt) for amt in amounts],
                'summary': {
                    'total_orders': total_count,
                    'total_amount': self.format_dashboard_value(total_amount),
                    'invoiced_amount': self.format_dashboard_value(invoiced_amount),
                    'pending_amount': self.format_dashboard_value(pending_amount),
                    'invoicing_rate': round((invoiced_amount / total_amount * 100), 1) if total_amount > 0 else 0
                }
            }
            
        except Exception as e:
            _logger.error(f"Error in get_invoice_status_analysis: {e}")
            return {
                'labels': ['No Data'],
                'amounts': [0],
                'counts': [0],
                'percentages': [0],
                'formatted_amounts': ['0 AED'],
                'summary': {
                    'total_orders': 0,
                    'total_amount': '0 AED',
                    'invoiced_amount': '0 AED',
                    'pending_amount': '0 AED',
                    'invoicing_rate': 0
                }
            }

    @api.model
    def get_dashboard_data_enhanced(self, params=None):
        """
        Get comprehensive dashboard data with sales type filtering
        Args:
            params: Dictionary containing filters like:
                - start_date: Start date for filtering (default: last 12 months)
                - end_date: End date for filtering (default: today)
                - sales_type_ids: List of sales order type IDs to filter by
        """
        try:
            # Set default parameters
            if not params:
                params = {}
                
            # Default date range: last 12 months
            end_date = params.get('end_date', datetime.now().strftime('%Y-%m-%d'))
            start_date = params.get('start_date', 
                                  (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'))
            sales_type_ids = params.get('sales_type_ids', None)
            
            # Get available sales order types
            sales_types = self.get_sales_order_types()
            
            # Get KPIs
            kpis = self.get_dashboard_kpis(start_date, end_date, sales_type_ids)
            
            # Get monthly data
            monthly_data = self.get_monthly_fluctuation_data(start_date, end_date, sales_type_ids)
            
            # Get sales type distribution
            type_distribution = self.get_sales_type_distribution(start_date, end_date)
            
            # Get project analysis
            project_analysis = self.get_project_analysis(start_date, end_date, sales_type_ids)
            
            # Get agent ranking
            agent_ranking = self.get_agent_ranking(start_date, end_date, 10, sales_type_ids)
            
            # Get invoice status analysis
            invoice_analysis = self.get_invoice_status_analysis(start_date, end_date, sales_type_ids)
            
            # Compile comprehensive response
            response = {
                # Basic info
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'sales_type_filter': sales_type_ids
                },
                
                # Filter options
                'sales_types': sales_types,
                
                # Main KPIs
                'total_sales': kpis.get('total_amount', '0 AED'),
                'monthly_sales': kpis.get('invoiced_amount', '0 AED'),
                'total_customers': kpis.get('total_orders', 0),
                'monthly_orders': kpis.get('total_quotations', 0),
                'conversion_rate': kpis.get('conversion_rate', 0),
                
                # Chart data
                'charts': {
                    'monthly_sales': [
                        {
                            'month': label,
                            'quotations': monthly_data['quotations'][i] if i < len(monthly_data['quotations']) else 0,
                            'sales_orders': monthly_data['sales_orders'][i] if i < len(monthly_data['sales_orders']) else 0,
                            'invoiced_sales': monthly_data['invoiced_sales'][i] if i < len(monthly_data['invoiced_sales']) else 0
                        }
                        for i, label in enumerate(monthly_data.get('labels', []))
                    ],
                    
                    'sales_by_type': [
                        {
                            'type': type_name,
                            'count': type_distribution['count_distribution'].get(type_name, 0),
                            'amount': type_distribution['amount_distribution'].get(type_name, 0)
                        }
                        for type_name in type_distribution.get('count_distribution', {}).keys()
                    ],
                    
                    'project_analysis': [
                        {
                            'project_name': project_analysis['labels'][i] if i < len(project_analysis['labels']) else 'Unknown',
                            'amount': project_analysis['raw_amounts'][i] if i < len(project_analysis['raw_amounts']) else 0,
                            'count': project_analysis['counts'][i] if i < len(project_analysis['counts']) else 0,
                            'formatted_amount': project_analysis['amounts'][i] if i < len(project_analysis['amounts']) else '0 AED'
                        }
                        for i in range(len(project_analysis.get('labels', [])))
                    ],
                    
                    'agent_ranking': [
                        {
                            'agent_name': agent_ranking['labels'][i] if i < len(agent_ranking['labels']) else 'Unknown',
                            'performance_score': agent_ranking['performance_scores'][i] if i < len(agent_ranking['performance_scores']) else 0,
                            'total_sales': agent_ranking['raw_sales'][i] if i < len(agent_ranking['raw_sales']) else 0,
                            'formatted_sales': agent_ranking['total_sales'][i] if i < len(agent_ranking['total_sales']) else '0 AED',
                            'conversion_rate': agent_ranking['conversion_rates'][i] if i < len(agent_ranking['conversion_rates']) else 0
                        }
                        for i in range(len(agent_ranking.get('labels', [])))
                    ],
                    
                    'invoice_status': [
                        {
                            'status': invoice_analysis['labels'][i] if i < len(invoice_analysis['labels']) else 'Unknown',
                            'count': invoice_analysis['counts'][i] if i < len(invoice_analysis['counts']) else 0,
                            'amount': invoice_analysis['amounts'][i] if i < len(invoice_analysis['amounts']) else 0,
                            'percentage': invoice_analysis['percentages'][i] if i < len(invoice_analysis['percentages']) else 0,
                            'formatted_amount': invoice_analysis['formatted_amounts'][i] if i < len(invoice_analysis['formatted_amounts']) else '0 AED'
                        }
                        for i in range(len(invoice_analysis.get('labels', [])))
                    ]
                },
                
                # Summary data
                'summary': {
                    'kpis': kpis,
                    'invoice_summary': invoice_analysis.get('summary', {}),
                    'total_projects': len(project_analysis.get('labels', [])),
                    'total_agents': len(agent_ranking.get('labels', [])),
                    'active_sales_types': len([st for st in sales_types if st.get('active', True)])
                }
            }
            
            return response
            
        except Exception as e:
            _logger.error(f"Error in get_dashboard_data_enhanced: {e}")
            return {
                'period': {
                    'start_date': datetime.now().strftime('%Y-%m-%d'),
                    'end_date': datetime.now().strftime('%Y-%m-%d'),
                    'sales_type_filter': None
                },
                'sales_types': [],
                'total_sales': '0 AED',
                'monthly_sales': '0 AED',
                'total_customers': 0,
                'monthly_orders': 0,
                'conversion_rate': 0,
                'charts': {
                    'monthly_sales': [],
                    'sales_by_type': [],
                    'project_analysis': [],
                    'agent_ranking': [],
                    'invoice_status': []
                },
                'summary': {},
                'error': str(e)
            }
