# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class CustomSalesOrder(models.Model):
    _name = 'custom.sales.order'
    _description = 'Custom Sales Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char(
        string='Order Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )
    
    # Basic order information
    sales_person_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        default=lambda self: self.env.user,
        tracking=True
    )
    
    sales_team_id = fields.Many2one(
        'crm.team',
        string='Sales Team',
        tracking=True
    )
    
    custom_field_3 = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True
    )
    
    customer_type = fields.Selection([
        ('individual', 'Individual'),
        ('company', 'Company'),
        ('government', 'Government'),
        ('ngo', 'NGO')
    ], string='Customer Type', default='individual', tracking=True)
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High')
    ], string='Priority', default='1')
    
    # Dates
    order_date = fields.Datetime(
        string='Order Date',
        default=fields.Datetime.now,
        required=True,
        tracking=True
    )
    
    expected_delivery_date = fields.Date(
        string='Expected Delivery Date',
        tracking=True
    )
    
    actual_delivery_date = fields.Date(
        string='Actual Delivery Date',
        tracking=True
    )
    
    # State management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Quotation Sent'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('delivered', 'Delivered'),
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    # Financial fields
    actual_revenue = fields.Monetary(
        string='Actual Revenue',
        currency_field='currency_id',
        tracking=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # Related sale order
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Related Sale Order',
        readonly=True
    )
    
    # Additional fields that might be referenced in views
    order_lines = fields.One2many(
        'custom.sales.order.line',
        'order_id',
        string='Order Lines'
    )
    
    notes = fields.Text(string='Notes')
    
    # Additional custom fields referenced in views
    custom_field_1 = fields.Char(string='Custom Field 1')
    custom_field_2 = fields.Char(string='Custom Field 2')
    
    estimated_revenue = fields.Monetary(
        string='Estimated Revenue',
        currency_field='currency_id'
    )
    
    profit_margin = fields.Float(
        string='Profit Margin (%)',
        compute='_compute_profit_margin',
        store=True
    )
    
    days_to_delivery = fields.Integer(
        string='Days to Delivery',
        compute='_compute_days_to_delivery'
    )
    
    is_overdue = fields.Boolean(
        string='Is Overdue',
        compute='_compute_is_overdue'
    )
    
    @api.depends('estimated_revenue', 'actual_revenue')
    def _compute_profit_margin(self):
        for record in self:
            if record.estimated_revenue and record.estimated_revenue > 0:
                record.profit_margin = ((record.actual_revenue - record.estimated_revenue) / record.estimated_revenue) * 100
            else:
                record.profit_margin = 0.0
    
    @api.depends('order_date', 'expected_delivery_date')
    def _compute_days_to_delivery(self):
        for record in self:
            if record.order_date and record.expected_delivery_date:
                delta = record.expected_delivery_date - record.order_date.date()
                record.days_to_delivery = delta.days
            else:
                record.days_to_delivery = 0
    
    @api.depends('expected_delivery_date', 'actual_delivery_date', 'state')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for record in self:
            if record.state not in ['delivered', 'invoiced', 'paid', 'cancelled']:
                if record.expected_delivery_date and record.expected_delivery_date < today:
                    record.is_overdue = True
                else:
                    record.is_overdue = False
            else:
                record.is_overdue = False
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('custom.sales.order') or _('New')
        return super().create(vals)
    
    def action_confirm(self):
        """Confirm the custom sales order"""
        self.ensure_one()
        self.state = 'confirmed'
        self.message_post(body=_("Order confirmed"))
        return True
    
    def action_send_quotation(self):
        """Send quotation to customer"""
        self.ensure_one()
        self.state = 'sent'
        self.message_post(body=_("Quotation sent"))
        return True
    
    def action_cancel(self):
        """Cancel the order"""
        self.ensure_one()
        self.state = 'cancelled'
        self.message_post(body=_("Order cancelled"))
        return True
    
    def action_view_sale_order(self):
        """View related sale order"""
        self.ensure_one()
        if self.sale_order_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Sale Order'),
                'view_mode': 'form',
                'res_model': 'sale.order',
                'res_id': self.sale_order_id.id,
                'target': 'current',
            }
        return False


class CustomSalesOrderLine(models.Model):
    _name = 'custom.sales.order.line'
    _description = 'Custom Sales Order Line'
    
    order_id = fields.Many2one(
        'custom.sales.order',
        string='Order',
        required=True,
        ondelete='cascade'
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )
    
    product_uom_qty = fields.Float(
        string='Quantity',
        default=1.0,
        required=True
    )
    
    price_unit = fields.Float(
        string='Unit Price',
        required=True
    )
    
    price_subtotal = fields.Monetary(
        string='Subtotal',
        compute='_compute_price_subtotal',
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        related='order_id.currency_id',
        string='Currency'
    )
    
    @api.depends('product_uom_qty', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.product_uom_qty * line.price_unit
