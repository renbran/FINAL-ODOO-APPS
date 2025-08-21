# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from datetime import datetime, timedelta
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class SaleDashboard(models.TransientModel):
    _name = 'sale.dashboard'
    _description = 'Sales Dashboard - Professional Analytics'

    # Dashboard configuration fields
    start_date = fields.Date(string='Start Date', default=lambda self: fields.Date.today().replace(day=1))
    end_date = fields.Date(string='End Date', default=fields.Date.today)
    sale_type_ids = fields.Many2many('le.sale.type', string='Sale Types', help="Filter by sale types (if module available)")

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
