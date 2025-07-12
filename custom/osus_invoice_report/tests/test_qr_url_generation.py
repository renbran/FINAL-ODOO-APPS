"""
Test module for QR Code URL generation
"""
from odoo.tests.common import TransactionCase
import logging
import re

_logger = logging.getLogger(__name__)


class TestQRURLGeneration(TransactionCase):
    """Test cases for QR Code URL generation"""
    
    def setUp(self):
        super().setUp()
        self.AccountMove = self.env['account.move']
        self.partner = self.env['res.partner'].create({
            'name': 'Test Customer',
            'email': 'test@example.com',
        })
        
    def test_qr_code_url_format(self):
        """Test that QR code URL has the correct format"""
        invoice = self.AccountMove.create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'qr_in_report': True,
            'buyer_id': self.partner.id,
            'deal_id': 12345,
            'sale_value': 50000.00,
            'developer_commission': 5.0,
        })
        
        # Get the QR code URL
        qr_url = invoice.get_qr_code_url()
        
        # Verify URL format
        self.assertTrue(qr_url, "QR code URL should be generated")
        
        # Check if it follows the expected pattern
        url_pattern = r'^https?://[^/]+/my/invoices/\d+\?access_token=[a-zA-Z0-9\-_.]+$'
        self.assertTrue(re.match(url_pattern, qr_url), 
                       f"QR code URL should match expected pattern. Got: {qr_url}")
        
    def test_unique_access_tokens(self):
        """Test that different invoices get unique access tokens"""
        invoice1 = self.AccountMove.create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'qr_in_report': True,
        })
        
        invoice2 = self.AccountMove.create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'qr_in_report': True,
        })
        
        url1 = invoice1.get_qr_code_url()
        url2 = invoice2.get_qr_code_url()
        
        # Extract access tokens
        token1 = url1.split('access_token=')[1] if 'access_token=' in url1 else None
        token2 = url2.split('access_token=')[1] if 'access_token=' in url2 else None
        
        self.assertNotEqual(token1, token2, "Different invoices should have different access tokens")
        
    def test_qr_code_regeneration(self):
        """Test that QR code can be regenerated"""
        invoice = self.AccountMove.create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'qr_in_report': True,
        })
        
        # Generate initial QR code
        invoice._compute_qr_code()
        initial_qr = invoice.qr_image
        
        # Regenerate QR code
        invoice.regenerate_qr_code()
        regenerated_qr = invoice.qr_image
        
        # Both should exist (content might be same if URL is same)
        self.assertTrue(initial_qr, "Initial QR code should exist")
        self.assertTrue(regenerated_qr, "Regenerated QR code should exist")
        
    def test_base_url_configuration(self):
        """Test base URL configuration check"""
        # Test the utility method
        is_configured = self.AccountMove._ensure_base_url_configured()
        
        # Should return True or False based on configuration
        self.assertIsInstance(is_configured, bool, "Base URL configuration check should return boolean")
