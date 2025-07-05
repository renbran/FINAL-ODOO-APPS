#!/usr/bin/env python3
"""
Simple test script to validate QR code generation
Usage: python test_qr_generation.py
"""

import sys
import os
import re

# Add the current directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def validate_qr_url(url):
    """Validate that the URL matches the expected pattern"""
    if not url:
        return False, "URL is empty"
    
    # Expected pattern: https://domain.com/my/invoices/ID?access_token=TOKEN
    # Access token can contain letters, numbers, and various special characters
    pattern = r'^https?://[^/]+/my/invoices/\d+\?access_token=[a-zA-Z0-9\-_.]+$'
    
    if re.match(pattern, url):
        return True, "URL format is correct"
    else:
        return False, f"URL format is incorrect. Expected pattern: https://domain.com/my/invoices/ID?access_token=TOKEN, Got: {url}"

def test_url_examples():
    """Test some example URLs"""
    test_urls = [
        "https://osusbrokers.cloudpepper.site/my/invoices/2717?access_token=4fe780e6-afa4-49c0-b539-6ab06055d7bb",
        "https://example.com/my/invoices/123?access_token=abcd-1234-efgh-5678",
        "http://localhost:8069/my/invoices/456?access_token=test-token-123",
        "https://osusbrokers.cloudpepper.site/my/invoices/2717",  # Missing access token
        "https://osusbrokers.cloudpepper.site/invoices/2717?access_token=4fe780e6-afa4-49c0-b539-6ab06055d7bb",  # Wrong path
    ]
    
    print("Testing URL validation:")
    print("=" * 50)
    
    for url in test_urls:
        is_valid, message = validate_qr_url(url)
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"{status}: {message}")
        print(f"  URL: {url}")
        print()

if __name__ == "__main__":
    test_url_examples()
    
    print("\nTo test with actual Odoo data:")
    print("1. Start Odoo server")
    print("2. Run: python -c \"exec(open('osus_invoice_report/setup_qr_config.py').read())\"")
    print("3. Check the generated QR codes in the invoice forms")
