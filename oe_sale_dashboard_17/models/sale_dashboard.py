# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from datetime import datetime, timedelta
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class SaleDashboard(models.TransientModel):
    _name = 'sale.dashboard'
    _description = 'Sales Dashboard - Professional Analytics with Enhanced Real Estate Features'

    # Dashboard configuration fields
    start_date = fields.Date(string='Start Date', default=lambda self: fields.Date.today().replace(day=1))
    end_date = fields.Date(string='End Date', default=fields.Date.today)
    sale_type_ids = fields.Many2many('sale.order.type', string='Sale Types', help="Filter by sale types from le_sale_type module")
    booking_date_filter = fields.Date(string='Booking Date Filter', help="Filter by specific booking date from real estate module")
    
    # Enhanced filtering for real estate integration
    project_filter_ids = fields.Many2many('product.template', string='Project Filter', help="Filter by projects")
    buyer_filter_ids = fields.Many2many('res.partner', string='Buyer Filter', help="Filter by buyers")

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
    def _get_date_field(self):
        """Get the appropriate date field to use for filtering"""
        sale_order = self.env['sale.order']
        # Check if booking_date field exists (from invoice_report_for_realestate module)
        if hasattr(sale_order, 'booking_date'):
            return 'booking_date'
        return 'date_order'

    @api.model
    def _check_optional_field(self, model_name, field_name):
        """Check if an optional field exists in a model"""
        try:
            model = self.env[model_name]
            return hasattr(model, field_name)
        except Exception:
            return False

    @api.model
    def get_sales_performance_data(self, start_date, end_date, sale_type_ids=None):
        """Get sales performance data with optional sale type filtering"""
        try:
            _logger.info(f"Getting performance data from {start_date} to {end_date}")
            
            sale_order = self.env['sale.order']
            date_field = self._get_date_field()
            
            # Base domain
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            # Add sale type filter if available and requested
            if sale_type_ids and self._check_optional_field('sale.order', 'sale_order_type_id'):
                base_domain.append(('sale_order_type_id', 'in', sale_type_ids))
            
            # Get all sale orders in the date range
            orders = sale_order.search(base_domain)
            
            # Calculate basic metrics
            total_orders = len(orders)
            total_amount = sum(orders.mapped('amount_total'))
            total_quotations = len(orders.filtered(lambda o: o.state in ['draft', 'sent']))
            total_sales = len(orders.filtered(lambda o: o.state in ['sale', 'done']))
            total_invoiced = len(orders.filtered(lambda o: o.invoice_status in ['invoiced', 'upselling']))
            
            return {
                'total_orders': total_orders,
                'total_quotations': total_quotations,
                'total_sales': total_sales,
                'total_invoiced': total_invoiced,
                'total_amount': total_amount,
                'currency_symbol': self.env.company.currency_id.symbol or '$',
                'orders': orders.ids,
                'date_field_used': date_field,
            }
            
        except Exception as e:
            _logger.error(f"Error getting sales performance data: {e}")
            return {
                'total_orders': 0,
                'total_quotations': 0,
                'total_sales': 0,
                'total_invoiced': 0,
                'total_amount': 0,
                'currency_symbol': '$',
                'orders': [],
                'date_field_used': 'date_order',
                'error': str(e),
            }

    @api.model
    def get_monthly_trend_data(self, start_date, end_date, sale_type_ids=None):
        """Get monthly sales trend data"""
        try:
            sale_order = self.env['sale.order']
            date_field = self._get_date_field()
            
            # Base domain
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            # Add sale type filter if available
            if sale_type_ids and self._check_optional_field('sale.order', 'sale_order_type_id'):
                base_domain.append(('sale_order_type_id', 'in', sale_type_ids))
            
            orders = sale_order.search(base_domain)
            
            # Group by month
            monthly_data = defaultdict(lambda: {'count': 0, 'amount': 0})
            
            for order in orders:
                order_date = getattr(order, date_field)
                if order_date:
                    month_key = order_date.strftime('%Y-%m')
                    monthly_data[month_key]['count'] += 1
                    monthly_data[month_key]['amount'] += order.amount_total
            
            # Format for Chart.js
            sorted_months = sorted(monthly_data.keys())
            
            return {
                'labels': [datetime.strptime(month, '%Y-%m').strftime('%b %Y') for month in sorted_months],
                'datasets': [
                    {
                        'label': 'Order Count',
                        'data': [monthly_data[month]['count'] for month in sorted_months],
                        'borderColor': '#4d1a1a',  # OSUS burgundy
                        'backgroundColor': 'rgba(77, 26, 26, 0.1)',
                        'yAxisID': 'y'
                    },
                    {
                        'label': 'Total Amount',
                        'data': [monthly_data[month]['amount'] for month in sorted_months],
                        'borderColor': '#b8a366',  # OSUS gold
                        'backgroundColor': 'rgba(184, 163, 102, 0.1)',
                        'yAxisID': 'y1'
                    }
                ]
            }
            
        except Exception as e:
            _logger.error(f"Error getting monthly trend data: {e}")
            return {
                'labels': [],
                'datasets': [],
                'error': str(e)
            }

    @api.model
    def get_sales_pipeline_data(self, start_date, end_date, sale_type_ids=None):
        """Get sales pipeline data by state"""
        try:
            sale_order = self.env['sale.order']
            date_field = self._get_date_field()
            
            # Base domain
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            # Add sale type filter if available
            if sale_type_ids and self._check_optional_field('sale.order', 'sale_order_type_id'):
                base_domain.append(('sale_order_type_id', 'in', sale_type_ids))
            
            orders = sale_order.search(base_domain)
            
            # Group by state
            pipeline_data = defaultdict(lambda: {'count': 0, 'amount': 0})
            
            state_mapping = {
                'draft': 'Draft',
                'sent': 'Quotation Sent',
                'sale': 'Sales Order',
                'done': 'Locked',
                'cancel': 'Cancelled'
            }
            
            for order in orders:
                state_label = state_mapping.get(order.state, order.state.title())
                pipeline_data[state_label]['count'] += 1
                pipeline_data[state_label]['amount'] += order.amount_total
            
            # Colors for different states (OSUS brand palette)
            colors = [
                '#4d1a1a',  # burgundy
                '#7d1e2d',  # dark burgundy  
                '#b8a366',  # gold
                '#d4c299',  # light gold
                '#cc4d66',  # burgundy light
            ]
            
            labels = list(pipeline_data.keys())
            data = [pipeline_data[label]['count'] for label in labels]
            
            return {
                'labels': labels,
                'datasets': [{
                    'data': data,
                    'backgroundColor': colors[:len(labels)],
                    'borderColor': '#ffffff',
                    'borderWidth': 2
                }]
            }
            
        except Exception as e:
            _logger.error(f"Error getting pipeline data: {e}")
            return {
                'labels': [],
                'datasets': [],
                'error': str(e)
            }

    @api.model
    def get_agent_rankings(self, start_date, end_date, sale_type_ids=None, limit=10):
        """Get agent rankings if commission_ax module is available"""
        try:
            if not self._check_optional_field('sale.order', 'agent1_partner_id'):
                return {'error': 'Agent tracking not available (commission_ax module not installed)'}
            
            sale_order = self.env['sale.order']
            date_field = self._get_date_field()
            
            # Base domain
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel'),
                ('agent1_partner_id', '!=', False)
            ]
            
            # Add sale type filter if available
            if sale_type_ids and self._check_optional_field('sale.order', 'sale_order_type_id'):
                base_domain.append(('sale_order_type_id', 'in', sale_type_ids))
            
            orders = sale_order.search(base_domain)
            
            # Group by agent
            agent_data = defaultdict(lambda: {'count': 0, 'amount': 0, 'name': ''})
            
            for order in orders:
                agent = order.agent1_partner_id
                if agent:
                    agent_data[agent.id]['count'] += 1
                    agent_data[agent.id]['amount'] += order.amount_total
                    agent_data[agent.id]['name'] = agent.name
            
            # Sort by amount and limit
            sorted_agents = sorted(agent_data.items(), key=lambda x: x[1]['amount'], reverse=True)[:limit]
            
            return {
                'rankings': [
                    {
                        'rank': i + 1,
                        'agent_id': agent_id,
                        'name': data['name'],
                        'deal_count': data['count'],
                        'total_amount': data['amount'],
                        'formatted_amount': self.format_dashboard_value(data['amount'])
                    }
                    for i, (agent_id, data) in enumerate(sorted_agents)
                ]
            }
            
        except Exception as e:
            _logger.error(f"Error getting agent rankings: {e}")
            return {'error': str(e)}

    @api.model
    def get_broker_rankings(self, start_date, end_date, sale_type_ids=None, limit=10):
        """Get broker rankings if commission_ax module is available"""
        try:
            if not self._check_optional_field('sale.order', 'broker_partner_id'):
                return {'error': 'Broker tracking not available (commission_ax module not installed)'}
            
            sale_order = self.env['sale.order']
            date_field = self._get_date_field()
            
            # Base domain
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel'),
                ('broker_partner_id', '!=', False)
            ]
            
            # Add sale type filter if available
            if sale_type_ids and self._check_optional_field('sale.order', 'sale_order_type_id'):
                base_domain.append(('sale_order_type_id', 'in', sale_type_ids))
            
            orders = sale_order.search(base_domain)
            
            # Group by broker
            broker_data = defaultdict(lambda: {'count': 0, 'amount': 0, 'name': ''})
            
            for order in orders:
                broker = order.broker_partner_id
                if broker:
                    broker_data[broker.id]['count'] += 1
                    broker_data[broker.id]['amount'] += order.amount_total
                    broker_data[broker.id]['name'] = broker.name
            
            # Sort by amount and limit
            sorted_brokers = sorted(broker_data.items(), key=lambda x: x[1]['amount'], reverse=True)[:limit]
            
            return {
                'rankings': [
                    {
                        'rank': i + 1,
                        'broker_id': broker_id,
                        'name': data['name'],
                        'deal_count': data['count'],
                        'total_amount': data['amount'],
                        'formatted_amount': self.format_dashboard_value(data['amount'])
                    }
                    for i, (broker_id, data) in enumerate(sorted_brokers)
                ]
            }
            
        except Exception as e:
            _logger.error(f"Error getting broker rankings: {e}")
            return {'error': str(e)}

    @api.model
    def get_sale_types(self):
        """Get available sale types if le_sale_type module is available"""
        try:
            if not self._check_optional_field('le.sale.type', 'name'):
                return {'error': 'Sale types not available (le_sale_type module not installed)'}
            
            sale_types = self.env['le.sale.type'].search([])
            
            return {
                'sale_types': [
                    {
                        'id': st.id,
                        'name': st.name,
                        'code': getattr(st, 'code', '') if hasattr(st, 'code') else ''
                    }
                    for st in sale_types
                ]
            }
            
        except Exception as e:
            _logger.error(f"Error getting sale types: {e}")
            return {'error': str(e)}

    @api.model
    def get_dashboard_data(self, start_date=None, end_date=None, sale_type_ids=None):
        """Main method to get all dashboard data"""
        try:
            # Set default dates if not provided
            if not start_date:
                start_date = fields.Date.today().replace(day=1).strftime('%Y-%m-%d')
            if not end_date:
                end_date = fields.Date.today().strftime('%Y-%m-%d')
            
            # Convert string dates to date objects if needed
            if isinstance(start_date, str):
                start_date = fields.Date.from_string(start_date)
            if isinstance(end_date, str):
                end_date = fields.Date.from_string(end_date)
            
            # Get all dashboard data
            performance_data = self.get_sales_performance_data(start_date, end_date, sale_type_ids)
            monthly_trend = self.get_monthly_trend_data(start_date, end_date, sale_type_ids)
            pipeline_data = self.get_sales_pipeline_data(start_date, end_date, sale_type_ids)
            agent_rankings = self.get_agent_rankings(start_date, end_date, sale_type_ids)
            broker_rankings = self.get_broker_rankings(start_date, end_date, sale_type_ids)
            sale_types = self.get_sale_types()
            
            return {
                'performance': performance_data,
                'monthly_trend': monthly_trend,
                'pipeline': pipeline_data,
                'agent_rankings': agent_rankings,
                'broker_rankings': broker_rankings,
                'sale_types': sale_types,
                'date_range': {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'date_field_used': self._get_date_field()
                }
            }
            
        except Exception as e:
            _logger.error(f"Error getting dashboard data: {e}")
            return {
                'error': str(e),
                'performance': {'total_orders': 0, 'total_amount': 0},
                'monthly_trend': {'labels': [], 'datasets': []},
                'pipeline': {'labels': [], 'datasets': []},
                'agent_rankings': {'rankings': []},
                'broker_rankings': {'rankings': []},
                'sale_types': {'sale_types': []}
            }

    @api.model
    def get_filtered_data(self, booking_date=None, sale_order_type_id=None, project_ids=None, buyer_ids=None, start_date=None, end_date=None):
        """
        Enhanced filtering method for real estate and sale type integration.
        Incorporates filtering based on booking_date, sale_order_type_id, projects, and buyers.
        """
        try:
            sale_order = self.env['sale.order']
            
            # Base domain with date range
            domain = []
            
            # Date filtering - prioritize booking_date if available
            date_field = self._get_date_field()
            if start_date:
                domain.append((date_field, '>=', start_date))
            if end_date:
                domain.append((date_field, '<=', end_date))
                
            # Specific booking date filter
            if booking_date and self._check_optional_field('sale.order', 'booking_date'):
                domain.append(('booking_date', '=', booking_date))
            
            # Sale order type filtering (from le_sale_type module)
            if sale_order_type_id and self._check_optional_field('sale.order', 'sale_order_type_id'):
                domain.append(('sale_order_type_id', '=', sale_order_type_id))
            
            # Project filtering (from invoice_report_for_realestate module)
            if project_ids and self._check_optional_field('sale.order', 'project_id'):
                domain.append(('project_id', 'in', project_ids))
                
            # Buyer filtering (from invoice_report_for_realestate module)
            if buyer_ids and self._check_optional_field('sale.order', 'buyer_id'):
                domain.append(('buyer_id', 'in', buyer_ids))
            
            # Exclude cancelled orders
            domain.append(('state', '!=', 'cancel'))
            
            # Search for orders matching criteria
            sales_data = sale_order.search(domain)
            
            _logger.info(f"Filtered data found: {len(sales_data)} orders with domain: {domain}")
            
            return sales_data
            
        except Exception as e:
            _logger.error(f"Error in get_filtered_data: {e}")
            return self.env['sale.order']

    @api.model
    def compute_scorecard_metrics(self, orders=None, booking_date=None, sale_order_type_id=None):
        """
        Enhanced scorecard computation including real estate specific metrics.
        Computes total sales value, total invoiced amount, and total paid amount.
        """
        try:
            if orders is None:
                # Get filtered data if no orders provided
                orders = self.get_filtered_data(
                    booking_date=booking_date,
                    sale_order_type_id=sale_order_type_id
                )
            
            # Basic sales metrics
            total_sales_value = sum(orders.mapped('amount_total'))
            total_orders_count = len(orders)
            average_order_value = total_sales_value / total_orders_count if total_orders_count > 0 else 0
            
            # Real estate specific metrics (if available)
            total_sale_value_realestate = 0
            total_developer_commission = 0
            
            if self._check_optional_field('sale.order', 'sale_value'):
                # Use real estate sale_value field if available
                total_sale_value_realestate = sum(orders.filtered('sale_value').mapped('sale_value'))
                
            if self._check_optional_field('sale.order', 'developer_commission'):
                # Calculate total commission
                for order in orders.filtered('developer_commission'):
                    commission_amount = (order.sale_value or order.amount_total) * (order.developer_commission / 100)
                    total_developer_commission += commission_amount
            
            # Invoice related metrics
            total_invoiced_amount = 0
            total_paid_amount = 0
            
            # Get invoices related to these orders
            invoices = self.env['account.move'].search([
                ('invoice_origin', 'in', orders.mapped('name')),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '!=', 'cancel')
            ])
            
            total_invoiced_amount = sum(invoices.mapped('amount_total'))
            
            # Calculate paid amount from invoice payments
            paid_invoices = invoices.filtered(lambda inv: inv.payment_state in ['paid', 'in_payment'])
            total_paid_amount = sum(paid_invoices.mapped('amount_total'))
            
            # Payment completion rate
            payment_completion_rate = (total_paid_amount / total_invoiced_amount * 100) if total_invoiced_amount > 0 else 0
            
            # Sale type breakdown
            sale_type_breakdown = {}
            if self._check_optional_field('sale.order', 'sale_order_type_id'):
                for order in orders.filtered('sale_order_type_id'):
                    type_name = order.sale_order_type_id.name
                    if type_name not in sale_type_breakdown:
                        sale_type_breakdown[type_name] = {
                            'count': 0, 
                            'amount': 0,
                            'avg_value': 0
                        }
                    sale_type_breakdown[type_name]['count'] += 1
                    sale_type_breakdown[type_name]['amount'] += order.amount_total
                
                # Calculate averages
                for type_data in sale_type_breakdown.values():
                    type_data['avg_value'] = type_data['amount'] / type_data['count'] if type_data['count'] > 0 else 0
            
            # Project performance (if available)
            project_breakdown = {}
            if self._check_optional_field('sale.order', 'project_id'):
                for order in orders.filtered('project_id'):
                    project_name = order.project_id.name
                    if project_name not in project_breakdown:
                        project_breakdown[project_name] = {
                            'count': 0,
                            'amount': 0,
                            'units_sold': 0
                        }
                    project_breakdown[project_name]['count'] += 1
                    project_breakdown[project_name]['amount'] += order.amount_total
                    if hasattr(order, 'unit_id') and order.unit_id:
                        project_breakdown[project_name]['units_sold'] += 1
            
            currency_symbol = self.env.company.currency_id.symbol or '$'
            
            return {
                'total_sales_value': total_sales_value,
                'total_sales_value_formatted': f"{currency_symbol}{self.format_dashboard_value(total_sales_value)}",
                'total_orders_count': total_orders_count,
                'average_order_value': average_order_value,
                'average_order_value_formatted': f"{currency_symbol}{self.format_dashboard_value(average_order_value)}",
                'total_invoiced_amount': total_invoiced_amount,
                'total_invoiced_amount_formatted': f"{currency_symbol}{self.format_dashboard_value(total_invoiced_amount)}",
                'total_paid_amount': total_paid_amount,
                'total_paid_amount_formatted': f"{currency_symbol}{self.format_dashboard_value(total_paid_amount)}",
                'payment_completion_rate': round(payment_completion_rate, 2),
                'total_sale_value_realestate': total_sale_value_realestate,
                'total_sale_value_realestate_formatted': f"{currency_symbol}{self.format_dashboard_value(total_sale_value_realestate)}",
                'total_developer_commission': total_developer_commission,
                'total_developer_commission_formatted': f"{currency_symbol}{self.format_dashboard_value(total_developer_commission)}",
                'sale_type_breakdown': sale_type_breakdown,
                'project_breakdown': project_breakdown,
                'currency_symbol': currency_symbol,
                'orders_analyzed': len(orders),
            }
            
        except Exception as e:
            _logger.error(f"Error computing scorecard metrics: {e}")
            return {
                'total_sales_value': 0,
                'total_invoiced_amount': 0,
                'total_paid_amount': 0,
                'error': str(e)
            }

    @api.model  
    def generate_enhanced_charts(self, orders=None, chart_types=None):
        """
        Generate enhanced charts for visualization including trends and comparisons.
        Utilizes booking_date for date-related visuals and sale_order_type_id for categorization.
        """
        try:
            if orders is None:
                orders = self.get_filtered_data()
                
            if chart_types is None:
                chart_types = ['trends', 'comparison', 'real_estate_specific']
            
            charts_data = {}
            
            # 1. Trends Chart - Sales over time using booking_date
            if 'trends' in chart_types:
                trends_data = self._generate_trends_chart(orders)
                charts_data['trends_chart'] = trends_data
            
            # 2. Comparison Chart - Sale types comparison
            if 'comparison' in chart_types:
                comparison_data = self._generate_comparison_chart(orders)
                charts_data['comparison_chart'] = comparison_data
                
            # 3. Real Estate Specific Charts
            if 'real_estate_specific' in chart_types:
                real_estate_data = self._generate_real_estate_charts(orders)
                charts_data.update(real_estate_data)
            
            return charts_data
            
        except Exception as e:
            _logger.error(f"Error generating enhanced charts: {e}")
            return {'error': str(e)}

    def _generate_trends_chart(self, orders):
        """Generate trends chart using booking_date if available"""
        try:
            date_field = 'booking_date' if self._check_optional_field('sale.order', 'booking_date') else 'date_order'
            
            # Group orders by month
            monthly_trends = defaultdict(lambda: {'count': 0, 'amount': 0})
            
            for order in orders:
                order_date = getattr(order, date_field)
                if order_date:
                    month_key = order_date.strftime('%Y-%m')
                    monthly_trends[month_key]['count'] += 1
                    monthly_trends[month_key]['amount'] += order.amount_total
            
            # Prepare Chart.js data
            sorted_months = sorted(monthly_trends.keys())
            
            return {
                'type': 'line',
                'data': {
                    'labels': [datetime.strptime(month, '%Y-%m').strftime('%b %Y') for month in sorted_months],
                    'datasets': [
                        {
                            'label': 'Sales Count',
                            'data': [monthly_trends[month]['count'] for month in sorted_months],
                            'borderColor': '#800020',  # OSUS Burgundy
                            'backgroundColor': 'rgba(128, 0, 32, 0.1)',
                            'yAxisID': 'y'
                        },
                        {
                            'label': 'Sales Amount',
                            'data': [monthly_trends[month]['amount'] for month in sorted_months],
                            'borderColor': '#FFD700',  # OSUS Gold
                            'backgroundColor': 'rgba(255, 215, 0, 0.1)',
                            'yAxisID': 'y1'
                        }
                    ]
                },
                'options': {
                    'responsive': True,
                    'scales': {
                        'y': {
                            'type': 'linear',
                            'display': True,
                            'position': 'left',
                            'title': {'display': True, 'text': 'Sales Count'}
                        },
                        'y1': {
                            'type': 'linear',
                            'display': True,
                            'position': 'right',
                            'title': {'display': True, 'text': 'Sales Amount'},
                            'grid': {'drawOnChartArea': False}
                        }
                    }
                }
            }
            
        except Exception as e:
            _logger.error(f"Error generating trends chart: {e}")
            return {'error': str(e)}

    def _generate_comparison_chart(self, orders):
        """Generate comparison chart by sale order type"""
        try:
            if not self._check_optional_field('sale.order', 'sale_order_type_id'):
                return {'error': 'Sale order type field not available'}
                
            type_data = defaultdict(lambda: {'count': 0, 'amount': 0})
            
            for order in orders.filtered('sale_order_type_id'):
                type_name = order.sale_order_type_id.name
                type_data[type_name]['count'] += 1
                type_data[type_name]['amount'] += order.amount_total
            
            if not type_data:
                return {'error': 'No data with sale order types found'}
            
            labels = list(type_data.keys())
            counts = [type_data[label]['count'] for label in labels]
            amounts = [type_data[label]['amount'] for label in labels]
            
            # OSUS color palette
            colors = ['#800020', '#FFD700', '#8B0000', '#DAA520', '#A0522D', '#CD853F']
            
            return {
                'type': 'doughnut',
                'data': {
                    'labels': labels,
                    'datasets': [
                        {
                            'label': 'Sales by Type',
                            'data': amounts,
                            'backgroundColor': colors[:len(labels)],
                            'borderColor': '#FFFFFF',
                            'borderWidth': 2
                        }
                    ]
                },
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {'position': 'bottom'},
                        'title': {'display': True, 'text': 'Sales Distribution by Type'}
                    }
                }
            }
            
        except Exception as e:
            _logger.error(f"Error generating comparison chart: {e}")
            return {'error': str(e)}

    def _generate_real_estate_charts(self, orders):
        """Generate real estate specific charts"""
        try:
            charts = {}
            
            # Project performance chart
            if self._check_optional_field('sale.order', 'project_id'):
                project_data = defaultdict(lambda: {'count': 0, 'amount': 0, 'units': 0})
                
                for order in orders.filtered('project_id'):
                    project_name = order.project_id.name
                    project_data[project_name]['count'] += 1
                    project_data[project_name]['amount'] += order.amount_total
                    if hasattr(order, 'unit_id') and order.unit_id:
                        project_data[project_name]['units'] += 1
                
                if project_data:
                    charts['project_performance'] = {
                        'type': 'bar',
                        'data': {
                            'labels': list(project_data.keys()),
                            'datasets': [
                                {
                                    'label': 'Sales Amount',
                                    'data': [project_data[proj]['amount'] for proj in project_data.keys()],
                                    'backgroundColor': '#800020',
                                    'borderColor': '#5a001a',
                                    'borderWidth': 1
                                }
                            ]
                        },
                        'options': {
                            'responsive': True,
                            'plugins': {
                                'title': {'display': True, 'text': 'Project Performance'}
                            }
                        }
                    }
            
            # Commission analysis chart (if available)
            if self._check_optional_field('sale.order', 'developer_commission'):
                commission_ranges = {'0-5%': 0, '5-10%': 0, '10-15%': 0, '15%+': 0}
                
                for order in orders.filtered('developer_commission'):
                    commission = order.developer_commission
                    if commission <= 5:
                        commission_ranges['0-5%'] += 1
                    elif commission <= 10:
                        commission_ranges['5-10%'] += 1
                    elif commission <= 15:
                        commission_ranges['10-15%'] += 1
                    else:
                        commission_ranges['15%+'] += 1
                
                charts['commission_analysis'] = {
                    'type': 'pie',
                    'data': {
                        'labels': list(commission_ranges.keys()),
                        'datasets': [
                            {
                                'data': list(commission_ranges.values()),
                                'backgroundColor': ['#800020', '#FFD700', '#8B0000', '#DAA520'],
                                'borderWidth': 2
                            }
                        ]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {'display': True, 'text': 'Commission Distribution'}
                        }
                    }
                }
            
            return charts
            
        except Exception as e:
            _logger.error(f"Error generating real estate charts: {e}")
            return {'error': str(e)}

    @api.model
    def get_enhanced_dashboard_data(self, start_date, end_date, filters=None):
        """
        Get comprehensive enhanced dashboard data with real estate integration.
        Combines all enhanced features including filtering, scorecard, and charts.
        """
        try:
            filters = filters or {}
            
            # Get filtered orders based on enhanced criteria
            filtered_orders = self.get_filtered_data(
                booking_date=filters.get('booking_date'),
                sale_order_type_id=filters.get('sale_order_type_id'),
                project_ids=filters.get('project_ids'),
                buyer_ids=filters.get('buyer_ids'),
                start_date=start_date,
                end_date=end_date
            )
            
            # Compute enhanced scorecard metrics
            scorecard_metrics = self.compute_scorecard_metrics(
                orders=filtered_orders,
                booking_date=filters.get('booking_date'),
                sale_order_type_id=filters.get('sale_order_type_id')
            )
            
            # Generate enhanced charts
            charts_data = self.generate_enhanced_charts(
                orders=filtered_orders,
                chart_types=['trends', 'comparison', 'real_estate_specific']
            )
            
            # Get existing dashboard data for compatibility
            base_dashboard_data = self.get_dashboard_data(start_date, end_date, filters.get('sale_type_ids'))
            
            # Combine all data
            enhanced_data = {
                'enhanced_scorecard': scorecard_metrics,
                'enhanced_charts': charts_data,
                'filtered_orders_count': len(filtered_orders),
                'applied_filters': filters,
                'base_dashboard': base_dashboard_data,
                'integration_status': {
                    'le_sale_type_available': self._check_optional_field('sale.order', 'sale_order_type_id'),
                    'real_estate_available': self._check_optional_field('sale.order', 'booking_date'),
                    'project_field_available': self._check_optional_field('sale.order', 'project_id'),
                    'buyer_field_available': self._check_optional_field('sale.order', 'buyer_id'),
                    'commission_field_available': self._check_optional_field('sale.order', 'developer_commission'),
                }
            }
            
            return enhanced_data
            
        except Exception as e:
            _logger.error(f"Error getting enhanced dashboard data: {e}")
            return {'error': str(e), 'enhanced_scorecard': {}, 'enhanced_charts': {}}
