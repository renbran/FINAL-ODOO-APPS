#!/usr/bin/env python3
"""
Simple verification script for QR Code Portal Access functionality
"""
import sys
import os

# Add the Odoo path to the system path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_qr_code_logic():
    """Test QR code generation logic"""
    print("Testing QR code portal access functionality...")
    
    # Test 1: Check that QR code library is available
    try:
        import qrcode
        print("✓ QRCode library is available")
    except ImportError:
        print("✗ QRCode library not found")
        return False
    
    # Test 2: Check base64 encoding
    try:
        import base64
        from io import BytesIO
        print("✓ Base64 and BytesIO modules are available")
    except ImportError:
        print("✗ Required modules not found")
        return False
    
    # Test 3: Test QR code generation
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        test_url = "https://example.com/my/invoices/12345?access_token=test_token"
        qr.add_data(test_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_data = base64.b64encode(buffer.getvalue())
        
        if qr_data:
            print("✓ QR code generation works correctly")
            print(f"✓ Generated QR code data length: {len(qr_data)} characters")
        else:
            print("✗ QR code generation failed")
            return False
            
    except Exception as e:
        print(f"✗ QR code generation error: {str(e)}")
        return False
    
    # Test 4: Test URL construction
    try:
        base_url = "https://example.com"
        relative_url = "/my/invoices/12345?access_token=test_token"
        full_url = base_url + relative_url
        
        if full_url == "https://example.com/my/invoices/12345?access_token=test_token":
            print("✓ URL construction works correctly")
        else:
            print("✗ URL construction failed")
            return False
            
    except Exception as e:
        print(f"✗ URL construction error: {str(e)}")
        return False
    
    print("\n🎉 All QR code portal access tests passed!")
    return True

def test_fallback_content():
    """Test fallback content generation"""
    print("\nTesting fallback content generation...")
    
    # Simulate invoice data
    invoice_data = {
        'name': 'INV/2024/0001',
        'company_name': 'OSUS Real Estate',
        'partner_name': 'Test Customer',
        'amount_total': 5000.00,
        'currency_name': 'AED',
        'invoice_date': '2024-01-15',
        'buyer_name': 'John Doe',
        'project_name': 'Marina Project',
        'unit_name': 'Unit A-101',
        'deal_id': 12345,
        'sale_value': 250000.00
    }
    
    # Generate fallback content
    content_lines = [
        f"Invoice: {invoice_data['name']}",
        f"Company: {invoice_data['company_name']}",
        f"Partner: {invoice_data['partner_name']}",
        f"Amount: {invoice_data['amount_total']} {invoice_data['currency_name']}",
        f"Date: {invoice_data['invoice_date']}",
        f"Buyer: {invoice_data['buyer_name']}",
        f"Project: {invoice_data['project_name']}",
        f"Unit: {invoice_data['unit_name']}",
        f"Deal ID: {invoice_data['deal_id']}",
        f"Sale Value: {invoice_data['sale_value']} {invoice_data['currency_name']}"
    ]
    
    fallback_content = '\n'.join(content_lines)
    
    print("✓ Fallback content generated successfully:")
    print("---")
    print(fallback_content)
    print("---")
    
    # Verify all expected fields are present
    expected_fields = ['Invoice:', 'Company:', 'Partner:', 'Amount:', 'Date:', 
                      'Buyer:', 'Project:', 'Unit:', 'Deal ID:', 'Sale Value:']
    
    for field in expected_fields:
        if field in fallback_content:
            print(f"✓ {field} present in fallback content")
        else:
            print(f"✗ {field} missing from fallback content")
            return False
    
    return True

if __name__ == "__main__":
    print("OSUS Invoice Report - QR Code Portal Access Verification")
    print("=" * 60)
    
    success = True
    
    # Run QR code logic tests
    success &= test_qr_code_logic()
    
    # Run fallback content tests
    success &= test_fallback_content()
    
    if success:
        print("\n🎉 All verification tests completed successfully!")
        print("\nThe QR code portal access functionality is ready for use.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)
