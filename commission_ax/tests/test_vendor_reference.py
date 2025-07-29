from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError


class TestCommissionVendorReference(TransactionCase):
    """Test cases for commission vendor reference functionality."""

    def setUp(self):
        super().setUp()
        
        # Create test partners
        self.customer = self.env['res.partner'].create({
            'name': 'Test Customer',
            'customer_rank': 1,
        })
        
        self.broker = self.env['res.partner'].create({
            'name': 'Test Broker',
            'supplier_rank': 1,
        })
        
        self.agent = self.env['res.partner'].create({
            'name': 'Test Agent',
            'supplier_rank': 1,
        })
        
        # Create test product
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
            'list_price': 1000.0,
        })

    def test_vendor_reference_population(self):
        """Test that vendor reference is populated from customer reference."""
        customer_ref = "CUST-REF-TEST-001"
        
        # Create sale order with customer reference
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'client_order_ref': customer_ref,
            'broker_partner_id': self.broker.id,
            'broker_commission_type': 'percent_untaxed_total',
            'broker_rate': 2.5,
        })
        
        # Add order line
        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'price_unit': 1000.0,
        })
        
        # Confirm and process commissions
        sale_order.action_confirm()
        sale_order.action_process_commissions()
        
        # Check that purchase orders were created
        self.assertTrue(len(sale_order.purchase_order_ids) > 0, 
                       "Commission purchase orders should be created")
        
        # Check vendor reference population
        for po in sale_order.purchase_order_ids:
            self.assertEqual(po.partner_ref, customer_ref,
                           f"Vendor reference should match customer reference. "
                           f"Expected: {customer_ref}, Got: {po.partner_ref}")
            self.assertEqual(po.origin_so_id.id, sale_order.id,
                           "Purchase order should reference origin sale order")

    def test_vendor_reference_without_customer_ref(self):
        """Test behavior when customer reference is not set."""
        # Create sale order without customer reference
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            # No client_order_ref set
            'agent1_partner_id': self.agent.id,
            'agent1_commission_type': 'fixed',
            'agent1_rate': 100.0,
        })
        
        # Add order line
        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'price_unit': 1000.0,
        })
        
        # Confirm and process commissions
        sale_order.action_confirm()
        sale_order.action_process_commissions()
        
        # Check that purchase orders were created but vendor_ref is not set
        self.assertTrue(len(sale_order.purchase_order_ids) > 0,
                       "Commission purchase orders should be created")
        
        for po in sale_order.purchase_order_ids:
            self.assertFalse(po.partner_ref,
                           "Vendor reference should not be set when customer reference is empty")

    def test_commission_partner_validation(self):
        """Test validation of commission partners."""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'client_order_ref': "TEST-REF",
            'broker_partner_id': self.broker.id,
            'broker_commission_type': 'fixed',
            'broker_rate': 100.0,
        })
        
        # Add order line
        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'price_unit': 1000.0,
        })
        
        # Process commissions
        sale_order.action_confirm()
        sale_order.action_process_commissions()
        
        # Verify commission partners are correctly identified
        commission_partners = sale_order._get_all_commission_partners()
        self.assertIn(self.broker.id, commission_partners,
                     "Broker should be in commission partners list")

    def test_purchase_order_commission_info(self):
        """Test commission information retrieval from purchase orders."""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'client_order_ref': "INFO-TEST-REF",
            'agent1_partner_id': self.agent.id,
            'agent1_commission_type': 'percent_untaxed_total',
            'agent1_rate': 1.5,
        })
        
        # Add order line
        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'price_unit': 1000.0,
        })
        
        # Process commissions
        sale_order.action_confirm()
        sale_order.action_process_commissions()
        
        # Test commission info retrieval
        for po in sale_order.purchase_order_ids:
            commission_info = po._get_commission_info()
            self.assertTrue(commission_info, "Commission info should be available")
            self.assertEqual(commission_info['customer_reference'], "INFO-TEST-REF",
                           "Customer reference should be in commission info")
            self.assertEqual(commission_info['sale_order'].id, sale_order.id,
                           "Sale order should be in commission info")

    def test_multiple_commissions_same_reference(self):
        """Test multiple commission types with same customer reference."""
        customer_ref = "MULTI-COMM-REF-001"
        
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'client_order_ref': customer_ref,
            # Multiple commission types
            'broker_partner_id': self.broker.id,
            'broker_commission_type': 'fixed',
            'broker_rate': 50.0,
            'agent1_partner_id': self.agent.id,
            'agent1_commission_type': 'fixed',
            'agent1_rate': 75.0,
        })
        
        # Add order line
        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'price_unit': 1000.0,
        })
        
        # Process commissions
        sale_order.action_confirm()
        sale_order.action_process_commissions()
        
        # Should create multiple POs
        self.assertEqual(len(sale_order.purchase_order_ids), 2,
                        "Should create 2 commission purchase orders")
        
        # All should have the same vendor reference
        for po in sale_order.purchase_order_ids:
            self.assertEqual(po.partner_ref, customer_ref,
                           "All commission POs should have same vendor reference")

    def test_commission_status_workflow(self):
        """Test commission status workflow."""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'client_order_ref': "STATUS-TEST-REF",
            'broker_partner_id': self.broker.id,
            'broker_commission_type': 'fixed',
            'broker_rate': 100.0,
        })
        
        # Add order line
        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'price_unit': 1000.0,
        })
        
        # Initial status should be draft
        self.assertEqual(sale_order.commission_status, 'draft',
                        "Initial commission status should be draft")
        
        # Confirm sale order
        sale_order.action_confirm()
        
        # Process commissions - should change status to calculated
        sale_order.action_process_commissions()
        self.assertEqual(sale_order.commission_status, 'calculated',
                        "Commission status should be calculated after processing")
        
        # Confirm commissions
        sale_order.action_confirm_commissions()
        self.assertEqual(sale_order.commission_status, 'confirmed',
                        "Commission status should be confirmed")
        
        # Reset commissions
        sale_order.action_reset_commissions()
        self.assertEqual(sale_order.commission_status, 'draft',
                        "Commission status should be draft after reset")
