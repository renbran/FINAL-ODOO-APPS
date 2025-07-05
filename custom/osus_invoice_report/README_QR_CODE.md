# QR Code Generation for OSUS Invoice Report

## Overview

This module generates unique QR codes for each invoice, receipt, and bill. The QR codes contain secure portal URLs that allow customers to access their documents directly.

## QR Code URL Format

The generated QR codes contain URLs in the following format:
```
https://osusbrokers.cloudpepper.site/my/invoices/{invoice_id}?access_token={unique_token}
```

For example:
```
https://osusbrokers.cloudpepper.site/my/invoices/2717?access_token=4fe780e6-afa4-49c0-b539-6ab06055d7bb
```

## Features

- **Unique URLs**: Each invoice gets a unique access token
- **Secure Access**: Access tokens provide secure, temporary access to documents
- **Automatic Generation**: QR codes are automatically generated when invoices are created
- **Manual Regeneration**: QR codes can be manually regenerated if needed
- **Fallback Content**: If portal URL generation fails, QR codes contain invoice details

## Configuration

### 1. Set Base URL

Ensure your Odoo instance has the correct base URL configured:

```bash
# In Odoo shell
env['ir.config_parameter'].sudo().set_param('web.base.url', 'https://osusbrokers.cloudpepper.site')
```

### 2. Install Required Dependencies

Make sure the following Python packages are installed:

```bash
pip install qrcode[pil] num2words
```

### 3. Configure Portal Access

Ensure portal access is enabled for customers:
- Go to Settings → Users & Companies → Portal Access
- Enable portal access for customer accounts

## Usage

### Automatic QR Code Generation

QR codes are automatically generated when:
- A new invoice is created
- The `qr_in_report` field is set to `True`
- The invoice has a partner assigned

### Manual QR Code Generation

To manually regenerate a QR code:
1. Open the invoice form
2. Go to the "Deal Tracking" tab
3. Click "Regenerate QR Code" button

### Testing QR Code Generation

1. **Run URL Validation Test**:
   ```bash
   python test_qr_generation.py
   ```

2. **Test with Actual Data**:
   ```bash
   # Start Odoo server
   # Then run in Odoo shell:
   exec(open('osus_invoice_report/setup_qr_config.py').read())
   setup_qr_code_configuration(env)
   test_qr_code_generation(env)
   ```

3. **Run Unit Tests**:
   ```bash
   python -m pytest osus_invoice_report/tests/test_qr_url_generation.py
   ```

## Technical Details

### QR Code Generation Process

1. **URL Generation**: Uses Odoo's built-in `get_portal_url()` method
2. **Fallback Mechanism**: If portal URL fails, uses manual URL construction
3. **Content Fallback**: If URL generation fails completely, includes invoice details
4. **QR Code Creation**: Uses the `qrcode` library to generate PNG images
5. **Storage**: QR code images are stored as binary fields in the database

### Fields Added to Account Move

- `qr_in_report`: Boolean field to enable/disable QR code generation
- `qr_image`: Binary field containing the generated QR code image
- Deal tracking fields: `buyer_id`, `project_id`, `unit_id`, `deal_id`, etc.

### Security Features

- **Access Tokens**: Each QR code contains a unique access token
- **Expiration**: Access tokens can expire based on Odoo configuration
- **Portal Security**: Access is controlled by Odoo's portal security system

## Troubleshooting

### Common Issues

1. **QR Code Not Generated**:
   - Check if `qr_in_report` is enabled
   - Verify base URL is configured correctly
   - Ensure `qrcode` library is installed

2. **Invalid URLs**:
   - Check base URL configuration
   - Verify portal access is enabled
   - Check access token generation

3. **Portal Access Denied**:
   - Verify customer has portal access
   - Check access token validity
   - Ensure invoice is in correct state

### Debug Information

Enable debug logging to see QR code generation details:

```python
import logging
logging.getLogger('osus_invoice_report').setLevel(logging.DEBUG)
```

### Testing URL Format

Use the validation script to test URL formats:

```bash
python test_qr_generation.py
```

## Customization

### Modifying QR Code Content

To customize the QR code content, modify the `_get_portal_url()` method in `custom_invoice.py`.

### Changing QR Code Appearance

Modify the QR code generation parameters in `_generate_qr_code()`:

```python
qr = qrcode.QRCode(
    version=1,                          # Size of QR code
    error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level
    box_size=10,                        # Size of each box
    border=4,                           # Border size
)
```

### Adding Custom Fields

Add additional fields to the invoice model and include them in the QR code content via `_get_qr_content_fallback()`.

## Support

For issues or questions, check the log files for error messages and verify the configuration steps above.

## Deal Tracking Fields in List View

### Available Fields in Invoice List View

The following deal tracking fields are now available in the invoice list view:

- **buyer_id**: The buyer of the property (visible by default)
- **deal_id**: Internal deal reference number (visible by default)
- **booking_date**: Property booking date (visible by default)
- **sale_value**: Total property sale value (visible by default)
- **project_id**: Real estate project name (hidden by default)
- **unit_id**: Specific property unit (hidden by default)
- **developer_commission**: Commission percentage (hidden by default)

### Accessing Deal Tracking Invoice List

1. **Standard Invoice List**: Go to Accounting > Customers > Invoices
2. **Enhanced Deal Tracking List**: Go to Accounting > Receivables > Deal Tracking Invoices

### Customizing Visible Fields

1. Open the invoice list view
2. Click the "Optional Fields" button (⋮) in the top-right corner
3. Check/uncheck the fields you want to show/hide
4. The system will remember your preferences

### Field Positioning

- Deal tracking fields appear after the Partner field
- Booking date appears after the Invoice Date
- Financial fields appear after the Amount Total
- Project information appears after the Currency field
