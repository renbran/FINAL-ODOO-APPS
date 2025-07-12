"""
Test module for QR Code Portal Access functionality
"""
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class TestQRCodePortalAccess(TransactionCase):
    """Test cases for QR Code Portal Access functionality"""
    
    def setUp(self):
        super().setUp()
        self.AccountMove = self.env['account.move']
        self.partner = self.env['res.partner'].create({
            'name': 'Test Customer',
            'email': 'test@example.com',
        })
        
    def test_qr_code_generation_with_portal_url(self):
        """Test that QR code is generated with portal URL"""
        invoice = self.AccountMove.create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'qr_in_report': True,
            'buyer_id': self.partner.id,
            'deal_id': 12345,
            'sale_value': 50000.00,
            'developer_commission': 5.0,
        })
        
        # Trigger QR code computation
        invoice._compute_qr_code()
        
        # Verify QR code was generated
        self.assertTrue(invoice.qr_image, "QR code should be generated when qr_in_report is True")
        
    def test_qr_code_not_generated_when_disabled(self):
        """Test that QR code is not generated when disabled"""
        invoice = self.AccountMove.create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'qr_in_report': False,
        })
        
        # Trigger QR code computation
        invoice._compute_qr_code()
        
        # Verify QR code was not generated
        self.assertFalse(invoice.qr_image, "QR code should not be generated when qr_in_report is False")
        
    def test_portal_url_generation(self):
        """Test that portal URL is generated correctly"""
        invoice = self.AccountMove.create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'name': 'TEST-INV-001',
        })
        
        # Test portal URL generation
        portal_url = invoice._get_portal_url()
        
        # Verify portal URL contains expected elements
        self.assertIn('my/invoices', portal_url, "Portal URL should contain invoice path")
        self.assertIn('access_token', portal_url, "Portal URL should contain access token")
        
    def test_fallback_qr_content(self):
        """Test that fallback QR content is generated when portal URL fails"""
        invoice = self.AccountMove.create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'name': 'TEST-INV-002',
            'buyer_id': self.partner.id,
            'deal_id': 54321,
            'sale_value': 75000.00,
        })
        
        # Test fallback content generation
        fallback_content = invoice._get_qr_content_fallback()
        
        # Verify fallback content includes key information
        self.assertIn('Invoice: TEST-INV-002', fallback_content)
        self.assertIn('Buyer: Test Customer', fallback_content)
        self.assertIn('Deal ID: 54321', fallback_content)
        self.assertIn('Sale Value: 75000.0', fallback_content)
        
    def test_commission_validation(self):
        """Test that commission validation works correctly"""
        invoice = self.AccountMove.create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'developer_commission': 50.0,  # Valid commission
        })
        
        # Should not raise an error
        invoice._check_developer_commission()
        
        # Test invalid commission
        with self.assertRaises(ValidationError):
            invoice.developer_commission = 150.0  # Invalid commission > 100%
            invoice._check_developer_commission()
            
    def test_deal_tracking_fields_integration(self):
        """Test that deal tracking fields are properly integrated"""
        invoice = self.AccountMove.create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'booking_date': '2024-01-15',
            'deal_id': 98765,
            'sale_value': 125000.00,
            'developer_commission': 7.5,
            'buyer_id': self.partner.id,
        })
        
        # Verify all fields are set correctly
        self.assertEqual(str(invoice.booking_date), '2024-01-15')
        self.assertEqual(invoice.deal_id, 98765)
        self.assertEqual(invoice.sale_value, 125000.00)
        self.assertEqual(invoice.developer_commission, 7.5)
        self.assertEqual(invoice.buyer_id, self.partner)
        
    def test_sale_order_population(self):
        """Test that invoice fields are populated from sale order"""
        # Create a sale order first
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'name': 'SO-TEST-001',
            'booking_date': '2024-01-20',
            'deal_id': 11111,
            'sale_value': 95000.00,
            'developer_commission': 6.0,
            'buyer_id': self.partner.id,
        })
        
        # Create invoice data with sale order reference
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'invoice_origin': 'SO-TEST-001',
        }
        
        # Simulate the population process
        AccountMove = self.env['account.move']
        AccountMove._populate_from_sale_order(invoice_vals)
        
        # Verify that deal tracking fields would be populated
        # (Note: This test depends on the sale order existing with the right fields)
        self.assertEqual(invoice_vals.get('deal_id'), 11111)
        self.assertEqual(invoice_vals.get('sale_value'), 95000.00)
