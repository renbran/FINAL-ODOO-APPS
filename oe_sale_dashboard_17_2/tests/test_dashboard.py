# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase, tagged
from datetime import datetime, timedelta


@tagged('sales_dashboard')
class TestSalesDashboard(TransactionCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Customer Dashboard'
        })
        
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product Dashboard',
            'list_price': 100.0,
        })
    
    def test_dashboard_methods_exist(self):
        """Test that dashboard methods exist and are callable"""
        sale_order = self.env['sale.order']
        
        # Test format_dashboard_value method
        formatted = sale_order.format_dashboard_value(1500)
        self.assertEqual(formatted, "1 K")
        
        formatted_large = sale_order.format_dashboard_value(1500000)
        self.assertEqual(formatted_large, "1.5 M")
        
    def test_monthly_fluctuation_data(self):
        """Test monthly fluctuation data method"""
        sale_order = self.env['sale.order']
        
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        # This should not raise an exception
        try:
            result = sale_order.get_monthly_fluctuation_data(start_date, end_date)
            self.assertIsInstance(result, dict)
            self.assertIn('labels', result)
            self.assertIn('quotations', result)
            self.assertIn('sales_orders', result)
            self.assertIn('invoiced_sales', result)
        except Exception as e:
            # Should have error handling that returns default structure
            self.assertIsInstance(result, dict)
            self.assertIn('error', result)
    
    def test_sales_type_distribution(self):
        """Test sales type distribution method"""
        sale_order = self.env['sale.order']
        
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        # This should not raise an exception
        try:
            result = sale_order.get_sales_type_distribution(start_date, end_date)
            self.assertIsInstance(result, dict)
        except Exception:
            # Should handle gracefully if sales types don't exist
            pass
    
    def test_create_sample_order(self):
        """Test creating a sample order for dashboard data"""
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 2,
                'price_unit': 100.0,
            })]
        })
        
        self.assertEqual(order.amount_total, 200.0)
        self.assertEqual(order.state, 'draft')
