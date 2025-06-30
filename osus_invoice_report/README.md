# OSUS Invoice Report Module

A professional Odoo 17 module for generating UAE VAT-compliant tax invoices, bills, and receipts specifically designed for real estate commission businesses.

## Features

### 🧾 Professional Reports
- **Tax Invoice**: UAE VAT-compliant customer invoices
- **Vendor Bills**: Professional vendor bill format
- **Receipt Vouchers**: Payment receipt documents

### 🏢 Real Estate Specific
- Buyer, Project, and Unit tracking
- Commission rate calculations
- Booking date management
- Property-specific invoice layouts

### 💫 Enhanced Functionality
- UK date format (DD/MM/YYYY)
- Amount in words conversion (English)
- Multi-company support
- Professional styling with Bootstrap 5
- Responsive design for different paper sizes
- Custom paper format configuration

### 🎨 Modern UI
- Clean, professional design
- UAE business standard layout
- OSUS Real Estate branding
- Inheritance-safe implementation

## Installation

### Prerequisites
```bash
pip install num2words
```

### Install Module
1. Copy the `osus_invoice_report` folder to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "OSUS Invoice Report" module

### Dependencies
- `account` (Odoo Accounting)
- `base` (Odoo Base)
- `project` (for Project field - optional)

## Usage

### Access Reports
After installation, you'll find new print buttons in the invoice/bill forms:
- **Print OSUS Invoice** (for customer invoices)
- **Print OSUS Bill** (for vendor bills)  
- **Print Receipt** (for any document type)

### Custom Fields
The module adds these fields to `account.move`:
- **Buyer**: The property buyer (res.partner)
- **Project**: Real estate project (project.project)
- **Unit**: Property unit (product.product)
- **Booking Date**: Property booking date
- **Amount in Words**: Auto-calculated amount in English words

### Configuration
The module includes a custom paper format optimized for A4 documents with proper margins for professional printing.

## File Structure

```
osus_invoice_report/
├── __init__.py
├── __manifest__.py
├── README.md
├── data/
│   └── report_paperformat.xml
├── models/
│   ├── __init__.py
│   └── custom_reports.py
├── security/
│   └── ir.model.access.csv
├── static/
│   └── src/
│       └── css/
│           └── report_style.css
└── views/
    ├── account_move_views.xml
    ├── report_invoice.xml
    ├── report_bills.xml
    └── report_receipt.xml
```

## Customization

### Bank Details
To customize bank payment instructions, edit the payment information section in:
- `views/report_invoice.xml` (lines containing bank details)

### Company Branding
- Add your company logo to the external layout
- Customize colors in `static/src/css/report_style.css`
- Modify header/footer content in the report templates

### Additional Fields
To add more real estate fields:
1. Add fields to the `AccountMove` model in `models/custom_reports.py`
2. Update the form view in `views/account_move_views.xml`
3. Include the fields in report templates

## Technical Details

### Models
- **AccountMove**: Extends `account.move` with real estate fields and print methods
- **CustomInvoiceReport**: Report controller for tax invoices
- **CustomBillReport**: Report controller for vendor bills  
- **CustomReceiptReport**: Report controller for receipts

### Security
- Access rights configured for accounting users
- Report printing restricted to appropriate user groups
- Document type validation in print methods

### Inheritance Safe
- Uses proper Odoo inheritance patterns
- Compatible with other accounting modules
- Follows Odoo development best practices

## Troubleshooting

### Common Issues

1. **"num2words not found" error**
   ```bash
   pip install num2words
   ```

2. **Reports not showing**
   - Update module after code changes
   - Check user permissions for accounting

3. **Styling issues**
   - Clear browser cache
   - Update assets in debug mode

4. **Project field not available**
   - Install the `project` module or modify the field definition

### Debug Mode
For development, enable debug mode to see detailed error messages and clear caches more easily.

## Support

This module is designed for OSUS Real Estate Brokerage LLC but can be customized for other real estate businesses.

### Version Compatibility
- Odoo 17.0+
- Python 3.8+
- Modern browsers for report viewing

## License

LGPL-3 License - See Odoo licensing terms.

---

**Author**: OSUS Real Estate  
**Website**: https://www.osus.ae  
**Version**: 17.0.1.0.0
   - The module does not reference any non-existent files (e.g., `custom_report/report/report_template.xml`)
3. **Deployment steps:**
   - Update the module list in Odoo
   - Upgrade the module from the Apps menu
   - If you encounter a file not found error, clear the Odoo cache and restart the Odoo server

## Troubleshooting
- If you see a `FileNotFoundError` for a file not present in this module, check for old references in the database or Odoo cache.
- Remove or fix any such references, then restart the server and upgrade the module again.

## Support
For further assistance, contact OSUS PROPERTIES IT or your Odoo administrator.
