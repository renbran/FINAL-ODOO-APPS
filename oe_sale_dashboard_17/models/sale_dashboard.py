from odoo import models, api, fields, _
from datetime import datetime, timedelta
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class SaleDashboardEnhanced(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _check_field_exists(self, field_name):
        """Check if a field exists in the current model to ensure compatibility"""
        try:
            return field_name in self.env['sale.order']._fields
        except Exception as e:
            _logger.warning(f"Error checking field {field_name}: {e}")
            return False

    @api.model
    def _get_safe_date_field(self):
        """Get the appropriate date field - prioritize booking_date, otherwise date_order"""
        if self._check_field_exists('booking_date'):
            return 'booking_date'
        return 'date_order'

    @api.model
    def _get_safe_amount_field(self, record):
        """Get the best available amount field value with proper error handling"""
        try:
            # Priority 1: amount_total (always available)
            amount_total = record.get('amount_total', 0)
            if amount_total:
                return float(amount_total)
                
            # Priority 2: sale_value (from osus_invoice_report module) as fallback
            if self._check_field_exists('sale_value') and record.get('sale_value'):
                return float(record['sale_value'])
                
            # Fallback: return 0 if no amount found
            return 0.0
        except (ValueError, TypeError) as e:
            _logger.warning(f"Error getting amount from record: {e}")
            return 0.0

    @api.model
    def format_dashboard_value(self, value, currency_code='AED'):
        """
        Format large numbers for dashboard display with K/M/B suffixes in AED currency
        Enhanced with proper currency formatting for UAE market
        """
        try:
            if not value or value == 0:
                return "AED 0"
            
            value = float(value)
            abs_value = abs(value)
            
            if abs_value >= 1_000_000_000:
                formatted = round(value / 1_000_000_000, 2)
                return f"AED {formatted:,.2f}B"
            elif abs_value >= 1_000_000:
                formatted = round(value / 1_000_000, 2)
                return f"AED {formatted:,.2f}M"
            elif abs_value >= 1_000:
                formatted = round(value / 1_000, 1)
                return f"AED {formatted:,.1f}K"
            else:
                return f"AED {value:,.0f}"
        except (ValueError, TypeError) as e:
            _logger.warning(f"Error formatting value {value}: {e}")
            return "AED 0"

    @api.model
    def get_sales_types(self):
        """
        Get available sales types from le_sale_type module
        Returns list of sales types if le_sale_type module is installed
        """
        try:
            if not self._check_field_exists('sale_order_type_id'):
                _logger.info("sale_order_type_id field not found, le_sale_type module may not be installed")
                return []
            
            # Check if le.sale.type model exists
            try:
                SaleType = self.env['le.sale.type']
                sales_types = SaleType.search([])
                return [{
                    'id': st.id,
                    'name': st.name,
                    'code': getattr(st, 'code', ''),
                    'active': getattr(st, 'active', True)
                } for st in sales_types]
            except KeyError:
                # Try alternative model name
                try:
                    SaleOrderType = self.env['sale.order.type']
                    sales_types = SaleOrderType.search([])
                    return [{
                        'id': st.id,
                        'name': st.name,
                        'code': getattr(st, 'code', ''),
                        'active': getattr(st, 'active', True)
                    } for st in sales_types]
                except KeyError:
                    _logger.warning("No sales type model found")
                    return []
                
        except Exception as e:
            _logger.error(f"Error getting sales types: {e}")
            return []

    @api.model
    def get_dashboard_summary_data(self, start_date, end_date, sales_type_ids=None):
        """
        Get comprehensive dashboard summary data with enhanced error handling
        """
        try:
            if not start_date or not end_date:
                raise ValueError("Start date and end date are required")
                
            date_field = self._get_safe_date_field()
            _logger.info(f"Loading dashboard data for {start_date} to {end_date}, using date field: {date_field}")
            
            # Validate dates
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                if start_dt > end_dt:
                    raise ValueError("Start date cannot be after end date")
            except ValueError as e:
                _logger.error(f"Invalid date format: {e}")
                return self._get_sample_dashboard_data()
            
            # Base domain for filtering with safe field checking
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')  # Exclude cancelled orders
            ]
            
            # Only add sales type filter if the field exists and we have valid IDs
            if sales_type_ids and self._check_field_exists('sale_order_type_id'):
                # Validate sales_type_ids
                valid_ids = [int(id) for id in sales_type_ids if str(id).isdigit()]
                if valid_ids:
                    base_domain.append(('sale_order_type_id', 'in', valid_ids))
            
            # Initialize summary data
            summary_data = {}
            total_summary = {
                'draft_count': 0, 'draft_amount': 0,
                'sales_order_count': 0, 'sales_order_amount': 0,
                'invoice_count': 0, 'invoice_amount': 0,
                'total_count': 0, 'total_amount': 0,
                'conversion_rate': 0,
                'avg_deal_size': 0,
                'revenue_growth': 0,
                'pipeline_velocity': 0
            }
            
            # Process by sales types if available
            if self._check_field_exists('sale_order_type_id'):
                sales_types_domain = []
                if sales_type_ids:
                    valid_ids = [int(id) for id in sales_type_ids if str(id).isdigit()]
                    if valid_ids:
                        sales_types_domain = [('id', 'in', valid_ids)]
                
                try:
                    # Try le.sale.type first
                    sales_types = self.env['le.sale.type'].search(sales_types_domain)
                except KeyError:
                    try:
                        # Fallback to sale.order.type
                        sales_types = self.env['sale.order.type'].search(sales_types_domain)
                    except KeyError:
                        sales_types = []
                
                _logger.info(f"Found {len(sales_types)} sales types")
                
                for sales_type in sales_types:
                    type_domain = base_domain + [('sale_order_type_id', '=', sales_type.id)]
                    category_data = self._process_category_data(type_domain, sales_type.name)
                    summary_data[sales_type.name] = category_data
                    
                    # Add to totals
                    for key in ['draft_count', 'draft_amount', 'sales_order_count', 
                               'sales_order_amount', 'invoice_count', 'invoice_amount']:
                        total_summary[key] += category_data.get(key, 0)
            else:
                # Fallback when no sales types available
                _logger.info("No sales types available, using fallback")
                category_data = self._process_category_data(base_domain, 'All Sales')
                summary_data['All Sales'] = category_data
                
                for key in ['draft_count', 'draft_amount', 'sales_order_count', 
                           'sales_order_amount', 'invoice_count', 'invoice_amount']:
                    total_summary[key] += category_data.get(key, 0)
            
            # Calculate totals
            total_summary['total_count'] = (total_summary['draft_count'] + 
                                          total_summary['sales_order_count'] + 
                                          total_summary['invoice_count'])
            total_summary['total_amount'] = (total_summary['draft_amount'] + 
                                           total_summary['sales_order_amount'] + 
                                           total_summary['invoice_amount'])
            
            # Check if we have any data at all
            if total_summary['total_count'] == 0:
                _logger.warning(f"No data found for date range {start_date} to {end_date}")
                return self._get_sample_dashboard_data()
            
            # Calculate enhanced KPIs
            if total_summary['draft_count'] > 0:
                total_summary['conversion_rate'] = (total_summary['invoice_count'] / total_summary['draft_count']) * 100
            
            if total_summary['total_count'] > 0:
                total_summary['avg_deal_size'] = total_summary['total_amount'] / total_summary['total_count']
            
            # Calculate revenue growth and pipeline velocity
            total_summary['revenue_growth'] = self._calculate_revenue_growth(start_date, end_date, sales_type_ids)
            total_summary['pipeline_velocity'] = self._calculate_pipeline_velocity(start_date, end_date, sales_type_ids)
            
            # Add formatted values for dashboard display
            total_summary['formatted_draft_amount'] = self.format_dashboard_value(total_summary['draft_amount'])
            total_summary['formatted_sales_order_amount'] = self.format_dashboard_value(total_summary['sales_order_amount'])
            total_summary['formatted_invoice_amount'] = self.format_dashboard_value(total_summary['invoice_amount'])
            total_summary['formatted_total_amount'] = self.format_dashboard_value(total_summary['total_amount'])
            total_summary['formatted_avg_deal_size'] = self.format_dashboard_value(total_summary['avg_deal_size'])
            
            _logger.info(f"Dashboard data processed successfully: {total_summary['total_count']} total records")
            
            return {
                'categories': summary_data,
                'totals': total_summary,
                'metadata': {
                    'date_field_used': date_field,
                    'has_sales_types': self._check_field_exists('sale_order_type_id'),
                    'has_sale_value': self._check_field_exists('sale_value'),
                    'has_booking_date': self._check_field_exists('booking_date'),
                    'has_agent1_fields': self._check_field_exists('agent1_partner_id') and self._check_field_exists('agent1_amount'),
                    'has_broker_fields': self._check_field_exists('broker_partner_id') and self._check_field_exists('broker_amount'),
                    'start_date': start_date,
                    'end_date': end_date,
                    'sales_type_filter': sales_type_ids or []
                }
            }
            
        except Exception as e:
            _logger.error(f"Error in get_dashboard_summary_data: {str(e)}")
            return self._get_sample_dashboard_data()

    @api.model
    def _get_sample_dashboard_data(self):
        """
        Return enhanced sample dashboard data for demonstration when no real data exists
        """
        return {
            'categories': {
                'Primary Sales': {
                    'draft_count': 15, 'draft_amount': 125000,
                    'formatted_draft_amount': self.format_dashboard_value(125000),
                    'sales_order_count': 8, 'sales_order_amount': 85000,
                    'formatted_sales_order_amount': self.format_dashboard_value(85000),
                    'invoice_count': 5, 'invoice_amount': 67500,
                    'formatted_invoice_amount': self.format_dashboard_value(67500),
                    'total_count': 28, 'total_amount': 277500,
                    'formatted_total_amount': self.format_dashboard_value(277500),
                    'category_name': 'Primary Sales'
                },
                'Exclusive Sales': {
                    'draft_count': 12, 'draft_amount': 180000,
                    'formatted_draft_amount': self.format_dashboard_value(180000),
                    'sales_order_count': 6, 'sales_order_amount': 95000,
                    'formatted_sales_order_amount': self.format_dashboard_value(95000),
                    'invoice_count': 4, 'invoice_amount': 85000,
                    'formatted_invoice_amount': self.format_dashboard_value(85000),
                    'total_count': 22, 'total_amount': 360000,
                    'formatted_total_amount': self.format_dashboard_value(360000),
                    'category_name': 'Exclusive Sales'
                },
                'Secondary Sales': {
                    'draft_count': 8, 'draft_amount': 75000,
                    'formatted_draft_amount': self.format_dashboard_value(75000),
                    'sales_order_count': 4, 'sales_order_amount': 45000,
                    'formatted_sales_order_amount': self.format_dashboard_value(45000),
                    'invoice_count': 3, 'invoice_amount': 32500,
                    'formatted_invoice_amount': self.format_dashboard_value(32500),
                    'total_count': 15, 'total_amount': 152500,
                    'formatted_total_amount': self.format_dashboard_value(152500),
                    'category_name': 'Secondary Sales'
                }
            },
            'totals': {
                'draft_count': 35, 'draft_amount': 380000,
                'formatted_draft_amount': self.format_dashboard_value(380000),
                'sales_order_count': 18, 'sales_order_amount': 225000,
                'formatted_sales_order_amount': self.format_dashboard_value(225000),
                'invoice_count': 12, 'invoice_amount': 185000,
                'formatted_invoice_amount': self.format_dashboard_value(185000),
                'total_count': 65, 'total_amount': 790000,
                'formatted_total_amount': self.format_dashboard_value(790000),
                'conversion_rate': 34.3,
                'avg_deal_size': 12153.85,
                'formatted_avg_deal_size': self.format_dashboard_value(12153.85),
                'revenue_growth': 15.2,
                'pipeline_velocity': 18.5
            },
            'metadata': {
                'date_field_used': self._get_safe_date_field(),
                'has_sales_types': self._check_field_exists('sale_order_type_id'),
                'has_sale_value': self._check_field_exists('sale_value'),
                'has_booking_date': self._check_field_exists('booking_date'),
                'has_agent1_fields': self._check_field_exists('agent1_partner_id') and self._check_field_exists('agent1_amount'),
                'has_broker_fields': self._check_field_exists('broker_partner_id') and self._check_field_exists('broker_amount'),
                'is_sample_data': True
            }
        }

    def _process_category_data(self, base_domain, category_name):
        """Process data for a specific category with enhanced error handling"""
        try:
            # Fields to read with safe checking
            fields_to_read = ['state', 'invoice_status', 'amount_total', 'name']
            if self._check_field_exists('sale_value'):
                fields_to_read.append('sale_value')
            if self._check_field_exists('invoice_amount'):
                fields_to_read.append('invoice_amount')
            if self._check_field_exists('booking_date'):
                fields_to_read.append('booking_date')
            
            # Draft orders (quotations) - use amount_total
            draft_domain = base_domain + [('state', 'in', ['draft', 'sent'])]
            draft_orders = self.search_read(draft_domain, fields_to_read)
            draft_count = len(draft_orders)
            draft_amount = sum(self._get_safe_amount_field(order) for order in draft_orders)
            
            # Confirmed sales orders (sale status) - use amount_total
            so_domain = base_domain + [('state', '=', 'sale'), ('invoice_status', 'in', ['to invoice', 'no', 'upselling'])]
            so_orders = self.search_read(so_domain, fields_to_read)
            so_count = len(so_orders)
            so_amount = sum(self._get_safe_amount_field(order) for order in so_orders)
            
            # Invoiced sales orders - use invoice_amount if available, otherwise amount_total
            invoice_domain = base_domain + [('state', '=', 'sale'), ('invoice_status', '=', 'invoiced')]
            invoice_orders = self.search_read(invoice_domain, fields_to_read)
            invoice_count = len(invoice_orders)
            invoice_amount = 0.0
            
            for order in invoice_orders:
                # Prefer invoice_amount if available
                if self._check_field_exists('invoice_amount') and order.get('invoice_amount'):
                    invoice_amount += float(order['invoice_amount'])
                else:
                    # Try to get actual invoiced amount
                    actual_amount = self._get_actual_invoiced_amount(order.get('name', ''))
                    invoice_amount += actual_amount or self._get_safe_amount_field(order)
            
            # Calculate category totals
            category_total = draft_amount + so_amount + invoice_amount
            
            return {
                'draft_count': draft_count,
                'draft_amount': float(draft_amount),
                'formatted_draft_amount': self.format_dashboard_value(draft_amount),
                'sales_order_count': so_count,
                'sales_order_amount': float(so_amount),
                'formatted_sales_order_amount': self.format_dashboard_value(so_amount),
                'invoice_count': invoice_count,
                'invoice_amount': float(invoice_amount),
                'formatted_invoice_amount': self.format_dashboard_value(invoice_amount),
                'total_count': draft_count + so_count + invoice_count,
                'total_amount': float(category_total),
                'formatted_total_amount': self.format_dashboard_value(category_total),
                'category_name': category_name
            }
            
        except Exception as e:
            _logger.error(f"Error processing category {category_name}: {str(e)}")
            return {
                'draft_count': 0, 'draft_amount': 0.0,
                'formatted_draft_amount': self.format_dashboard_value(0),
                'sales_order_count': 0, 'sales_order_amount': 0.0,
                'formatted_sales_order_amount': self.format_dashboard_value(0),
                'invoice_count': 0, 'invoice_amount': 0.0,
                'formatted_invoice_amount': self.format_dashboard_value(0),
                'total_count': 0, 'total_amount': 0.0,
                'formatted_total_amount': self.format_dashboard_value(0),
                'category_name': category_name
            }

    def _calculate_revenue_growth(self, start_date, end_date, sales_type_ids=None):
        """Calculate revenue growth compared to previous period with error handling"""
        try:
            # Current period revenue
            current_revenue = self._get_period_revenue(start_date, end_date, sales_type_ids)
            
            # Calculate previous period dates
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            period_length = (end_dt - start_dt).days
            
            prev_end_dt = start_dt - timedelta(days=1)
            prev_start_dt = prev_end_dt - timedelta(days=period_length)
            
            # Previous period revenue
            prev_revenue = self._get_period_revenue(
                prev_start_dt.strftime('%Y-%m-%d'), 
                prev_end_dt.strftime('%Y-%m-%d'), 
                sales_type_ids
            )
            
            if prev_revenue > 0:
                growth = ((current_revenue - prev_revenue) / prev_revenue) * 100
                return round(growth, 2)
            
            return 0.0
            
        except Exception as e:
            _logger.error(f"Error calculating revenue growth: {str(e)}")
            return 0.0

    def _get_period_revenue(self, start_date, end_date, sales_type_ids=None):
        """Get total revenue for a specific period with error handling"""
        try:
            date_field = self._get_safe_date_field()
            domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '=', 'sale'),
                ('invoice_status', '=', 'invoiced')
            ]
            
            if sales_type_ids and self._check_field_exists('sale_order_type_id'):
                valid_ids = [int(id) for id in sales_type_ids if str(id).isdigit()]
                if valid_ids:
                    domain.append(('sale_order_type_id', 'in', valid_ids))
            
            fields_to_read = ['amount_total', 'name']
            if self._check_field_exists('sale_value'):
                fields_to_read.append('sale_value')
                
            orders = self.search_read(domain, fields_to_read)
            
            total_revenue = 0.0
            for order in orders:
                actual_amount = self._get_actual_invoiced_amount(order.get('name', ''))
                total_revenue += actual_amount or self._get_safe_amount_field(order)
                
            return float(total_revenue)
            
        except Exception as e:
            _logger.error(f"Error getting period revenue: {str(e)}")
            return 0.0

    def _calculate_pipeline_velocity(self, start_date, end_date, sales_type_ids=None):
        """Calculate average time from quotation to invoice with error handling"""
        try:
            date_field = self._get_safe_date_field()
            domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '=', 'sale'),
                ('invoice_status', '=', 'invoiced')
            ]
            
            if sales_type_ids and self._check_field_exists('sale_order_type_id'):
                valid_ids = [int(id) for id in sales_type_ids if str(id).isdigit()]
                if valid_ids:
                    domain.append(('sale_order_type_id', 'in', valid_ids))
            
            fields_to_read = [date_field, 'date_order', 'confirmation_date']
            orders = self.search_read(domain, fields_to_read)
            
            if not orders:
                return 0.0
            
            total_days = 0
            valid_orders = 0
            
            for order in orders:
                order_date = order.get('confirmation_date') or order.get('date_order')
                invoice_date = order.get(date_field)
                
                if order_date and invoice_date:
                    try:
                        if isinstance(order_date, str):
                            order_dt = datetime.strptime(order_date[:10], '%Y-%m-%d')
                        else:
                            order_dt = order_date
                        
                        if isinstance(invoice_date, str):
                            invoice_dt = datetime.strptime(invoice_date[:10], '%Y-%m-%d')
                        else:
                            invoice_dt = invoice_date
                        
                        days_diff = (invoice_dt - order_dt).days
                        if days_diff >= 0:  # Valid progression
                            total_days += days_diff
                            valid_orders += 1
                    except (ValueError, TypeError) as e:
                        _logger.warning(f"Error processing dates for order {order.get('name', '')}: {e}")
                        continue
            
            return round(total_days / valid_orders, 1) if valid_orders > 0 else 0.0
            
        except Exception as e:
            _logger.error(f"Error calculating pipeline velocity: {str(e)}")
            return 0.0

    def _get_actual_invoiced_amount(self, order_name):
        """Get actual invoiced amount from account.move records with error handling"""
        try:
            if not order_name:
                return 0.0
                
            invoices = self.env['account.move'].search([
                ('invoice_origin', '=', order_name),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted')
            ])
            
            total_amount = 0.0
            for invoice in invoices:
                try:
                    if invoice.move_type == 'out_invoice':
                        total_amount += float(invoice.amount_total or 0)
                    elif invoice.move_type == 'out_refund':
                        total_amount -= float(invoice.amount_total or 0)
                except (ValueError, TypeError) as e:
                    _logger.warning(f"Error processing invoice amount for {invoice.name}: {e}")
                    continue
            
            return total_amount
        except Exception as e:
            _logger.warning(f"Error getting actual invoiced amount for {order_name}: {e}")
            return 0.0

    @api.model
    def get_monthly_fluctuation_data(self, start_date, end_date, sales_type_ids=None):
        """
        Get monthly fluctuation data with enhanced error handling
        """
        try:
            # Validate input dates
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError as e:
                _logger.error(f"Invalid date format: {e}")
                return {
                    'labels': ['Current Period'],
                    'quotations': [0],
                    'sales_orders': [0],
                    'invoiced_sales': [0],
                    'error': 'Invalid date format'
                }
            
            date_field = self._get_safe_date_field()
            
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
                
                # Move to next month
                if current_dt.month == 12:
                    current_dt = current_dt.replace(year=current_dt.year + 1, month=1)
                else:
                    current_dt = current_dt.replace(month=current_dt.month + 1)
            
            # Base domain for filtering
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            # Add sales type filter if available
            if sales_type_ids and self._check_field_exists('sale_order_type_id'):
                valid_ids = [int(id) for id in sales_type_ids if str(id).isdigit()]
                if valid_ids:
                    base_domain.append(('sale_order_type_id', 'in', valid_ids))
            
            # Fields to read
            fields_to_read = [date_field, 'amount_total', 'state', 'invoice_status', 'name']
            if self._check_field_exists('sale_value'):
                fields_to_read.append('sale_value')
            
            # Process each type of order
            self._process_monthly_orders(base_domain, fields_to_read, date_field, monthly_data, 'quotations', [('state', 'in', ['draft', 'sent'])])
            self._process_monthly_orders(base_domain, fields_to_read, date_field, monthly_data, 'sales_orders', [('state', '=', 'sale'), ('invoice_status', 'in', ['to invoice', 'no', 'upselling'])])
            self._process_monthly_orders(base_domain, fields_to_read, date_field, monthly_data, 'invoiced_sales', [('state', '=', 'sale'), ('invoice_status', '=', 'invoiced')])
            
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
                try:
                    for key in monthly_data.keys():
                        if datetime.strptime(key, '%Y-%m').strftime('%b %Y') == label:
                            month_key = key
                            break
                except ValueError:
                    continue
                
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
            _logger.error(f"Error in get_monthly_fluctuation_data: {str(e)}")
            return {
                'labels': ['Current Period'],
                'quotations': [0],
                'sales_orders': [0],
                'invoiced_sales': [0],
                'error': str(e)
            }

    def _process_monthly_orders(self, base_domain, fields_to_read, date_field, monthly_data, order_type, additional_domain):
        """Helper method to process orders by month"""
        try:
            domain = base_domain + additional_domain
            orders = self.search_read(domain, fields_to_read)
            
            for order in orders:
                order_date = order.get(date_field)
                if order_date:
                    try:
                        if isinstance(order_date, str):
                            month_key = datetime.strptime(order_date[:10], '%Y-%m-%d').strftime('%Y-%m')
                        else:
                            month_key = order_date.strftime('%Y-%m')
                        
                        if month_key in monthly_data:
                            monthly_data[month_key][order_type]['count'] += 1
                            
                            # Get amount based on order type
                            if order_type == 'invoiced_sales':
                                # Try to get actual invoiced amount
                                invoiced_amount = self._get_actual_invoiced_amount(order.get('name', ''))
                                amount = invoiced_amount or self._get_safe_amount_field(order)
                            else:
                                amount = self._get_safe_amount_field(order)
                            
                            monthly_data[month_key][order_type]['amount'] += amount
                    except (ValueError, TypeError) as e:
                        _logger.warning(f"Error processing date for order {order.get('name', '')}: {e}")
                        continue
                        
        except Exception as e:
            _logger.error(f"Error processing monthly orders for {order_type}: {str(e)}")

    @api.model
    def get_sales_type_distribution(self, start_date, end_date):
        """
        Get sales type distribution data for pie charts with enhanced error handling
        """
        try:
            date_field = self._get_safe_date_field()
            
            # Base domain excluding cancelled orders
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            # Check if sales type field exists
            if not self._check_field_exists('sale_order_type_id'):
                return {
                    'count_distribution': {'All Sales': 1},
                    'amount_distribution': {'All Sales': 0},
                    'message': 'Sales types not available in this instance'
                }
            
            # Get all sales types
            try:
                sales_types = self.env['le.sale.type'].search([])
            except KeyError:
                try:
                    sales_types = self.env['sale.order.type'].search([])
                except KeyError:
                    return {
                        'count_distribution': {},
                        'amount_distribution': {},
                        'error': 'No sales type model found'
                    }
            
            count_distribution = {}
            amount_distribution = {}
            
            # Fields to read with safe checking
            fields_to_read = ['state', 'invoice_status', 'amount_total', 'name']
            if self._check_field_exists('sale_value'):
                fields_to_read.append('sale_value')
            
            for sales_type in sales_types:
                try:
                    type_domain = base_domain + [('sale_order_type_id', '=', sales_type.id)]
                    
                    # Get all orders for this type
                    orders = self.search_read(type_domain, fields_to_read)
                    
                    total_count = len(orders)
                    total_amount = 0.0
                    
                    for order in orders:
                        # For invoiced orders, try to get actual invoiced amount
                        if order.get('state') == 'sale' and order.get('invoice_status') == 'invoiced':
                            invoiced_amount = self._get_actual_invoiced_amount(order.get('name', ''))
                            amount = invoiced_amount or self._get_safe_amount_field(order)
                        else:
                            amount = self._get_safe_amount_field(order)
                        
                        total_amount += amount
                    
                    if total_count > 0:  # Only include types with data
                        count_distribution[sales_type.name] = total_count
                        amount_distribution[sales_type.name] = total_amount
                        
                except Exception as e:
                    _logger.warning(f"Error processing sales type {sales_type.name}: {e}")
                    continue
            
            return {
                'count_distribution': count_distribution,
                'amount_distribution': amount_distribution
            }
            
        except Exception as e:
            _logger.error(f"Error in get_sales_type_distribution: {str(e)}")
            return {
                'count_distribution': {},
                'amount_distribution': {},
                'error': str(e)
            }

    @api.model 
    def get_top_performers_data(self, start_date, end_date, performer_type='agent', limit=10):
        """
        Get top performing agents or agencies with enhanced error handling
        """
        try:
            # Validate inputs
            if performer_type not in ['agent', 'agency']:
                _logger.error(f"Invalid performer_type: {performer_type}")
                return []
            
            if not isinstance(limit, int) or limit <= 0:
                limit = 10
            
            date_field = self._get_safe_date_field()
            
            # Determine field names based on performer type
            if performer_type == 'agent':
                partner_field = 'agent1_partner_id'
                amount_field = 'agent1_amount'
            else:  # agency
                partner_field = 'broker_partner_id'
                amount_field = 'broker_amount'
            
            # Check if the required fields exist
            if not self._check_field_exists(partner_field) or not self._check_field_exists(amount_field):
                _logger.warning(f"Required fields for {performer_type} not found: {partner_field}, {amount_field}")
                return []

            # Base domain for filtering
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel'),
                (partner_field, '!=', False)
            ]

            # Fields to read
            fields_to_read = [
                partner_field, 'amount_total', amount_field, 
                'state', 'invoice_status', 'name', date_field
            ]
            
            if self._check_field_exists('sale_value'):
                fields_to_read.append('sale_value')
            if self._check_field_exists('price_unit'):
                fields_to_read.append('price_unit')
            if self._check_field_exists('invoice_amount'):
                fields_to_read.append('invoice_amount')
                
            orders = self.search_read(base_domain, fields_to_read)
            
            _logger.info(f"Found {len(orders)} orders for {performer_type} ranking")

            # Group data by partner
            partner_data = {}
            
            for order in orders:
                try:
                    partner_id = order.get(partner_field)
                    if not partner_id:
                        continue
                        
                    # Handle both tuple format (id, name) and plain id
                    if isinstance(partner_id, (tuple, list)) and len(partner_id) >= 2:
                        partner_key = partner_id[0]
                        partner_name = partner_id[1]
                    elif isinstance(partner_id, int):
                        partner_key = partner_id
                        # Get partner name from res.partner model
                        try:
                            partner_rec = self.env['res.partner'].browse(partner_key)
                            partner_name = partner_rec.name if partner_rec.exists() else f"Partner {partner_key}"
                        except Exception:
                            partner_name = f"Partner {partner_key}"
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
                    
                    # Get values with proper validation
                    sales_value = self._get_safe_amount_field(order)
                    commission_value = float(order.get(amount_field) or 0.0)
                    
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
                        
                except Exception as e:
                    _logger.warning(f"Error processing order {order.get('name', '')}: {e}")
                    continue

            # Convert to list and sort
            performers_list = list(partner_data.values())
            
            # Sort by multiple criteria for better ranking
            performers_list.sort(key=lambda x: (
                -float(x.get('total_sales_value', 0)),
                -float(x.get('total_commission', 0)),
                -int(x.get('count', 0))
            ))
            
            _logger.info(f"Returning top {min(len(performers_list), limit)} {performer_type}s")
            return performers_list[:limit]
            
        except Exception as e:
            _logger.error(f"Error in get_top_performers_data: {str(e)}")
            return []

    @api.model
    def get_sales_type_ranking_data(self, start_date, end_date, sales_type_ids=None):
        """
        Get ranking data for sales types with enhanced error handling
        """
        try:
            date_field = self._get_safe_date_field()
            
            # Base domain
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            if sales_type_ids:
                valid_ids = [int(id) for id in sales_type_ids if str(id).isdigit()]
                if valid_ids:
                    base_domain.append(('sale_order_type_id', 'in', valid_ids))
            
            # Get sales types to rank
            try:
                if sales_type_ids:
                    valid_ids = [int(id) for id in sales_type_ids if str(id).isdigit()]
                    sales_types_domain = [('id', 'in', valid_ids)] if valid_ids else []
                else:
                    sales_types_domain = []
                
                try:
                    sales_types = self.env['le.sale.type'].search(sales_types_domain)
                except KeyError:
                    sales_types = self.env['sale.order.type'].search(sales_types_domain)
            except Exception as e:
                _logger.error(f"Error getting sales types: {e}")
                return []
            
            ranking_data = []
            
            for sales_type in sales_types:
                try:
                    type_domain = base_domain + [('sale_order_type_id', '=', sales_type.id)]
                    
                    # Get all orders for this type
                    fields = ['state', 'invoice_status', 'amount_total', 'name']
                    if self._check_field_exists('sale_value'):
                        fields.append('sale_value')
                    
                    orders = self.search_read(type_domain, fields)
                    
                    total_count = len(orders)
                    total_sales_value = 0.0
                    total_amount = 0.0
                    invoiced_count = 0
                    invoiced_amount = 0.0
                    
                    for order in orders:
                        try:
                            sales_value = self._get_safe_amount_field(order)
                            total_sales_value += sales_value
                            total_amount += float(order.get('amount_total', 0))
                            
                            # Calculate invoiced amounts
                            if order.get('state') == 'sale' and order.get('invoice_status') == 'invoiced':
                                invoiced_count += 1
                                actual_invoiced = self._get_actual_invoiced_amount(order.get('name', ''))
                                invoiced_amount += actual_invoiced or sales_value
                        except Exception as e:
                            _logger.warning(f"Error processing order {order.get('name', '')}: {e}")
                            continue
                    
                    # Calculate performance metrics
                    avg_deal_size = total_sales_value / total_count if total_count > 0 else 0
                    invoiced_rate = (invoiced_count / total_count * 100) if total_count > 0 else 0
                    
                    ranking_data.append({
                        'sales_type_name': sales_type.name,
                        'total_count': total_count,
                        'total_sales_value': total_sales_value,
                        'total_amount': total_amount,
                        'invoiced_count': invoiced_count,
                        'invoiced_amount': invoiced_amount,
                        'avg_deal_size': avg_deal_size,
                        'invoiced_rate': invoiced_rate,
                        'performance_score': total_sales_value * 0.4 + invoiced_amount * 0.4 + total_count * 0.2
                    })
                    
                except Exception as e:
                    _logger.warning(f"Error processing sales type {sales_type.name}: {e}")
                    continue
            
            # Sort by performance score (descending)
            ranking_data.sort(key=lambda x: x.get('performance_score', 0), reverse=True)
            
            return ranking_data
            
        except Exception as e:
            _logger.error(f"Error in get_sales_type_ranking_data: {str(e)}")
            return []