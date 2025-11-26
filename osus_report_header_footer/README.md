# OSUS Report Header Footer

## Overview

This module provides standardized, professional headers and footers with OSUS branding for all PDF reports in Odoo 17.

## Features

### 🎨 Professional Branding
- **OSUS Logo**: Displays the OSUS Properties logo in the report header
- **Company Information**: Shows complete company details including address, phone, email, website, and TRN
- **Consistent Styling**: Applies uniform branding across all reports

### 📄 Header Components
- OSUS logo (left-aligned)
- Company name and contact information (right-aligned)
- Decorative separator line in OSUS brand colors

### 📋 Footer Components
- Company contact summary
- Page numbering (Page X of Y)
- Print timestamp
- TRN (Tax Registration Number)
- Professional disclaimer text

### 🎯 Automatic Application
- Overrides the default `web.external_layout_standard` template
- Applies automatically to all PDF reports without individual configuration
- Compatible with existing custom reports

## Installation

1. Copy the module to your Odoo addons directory:
   ```bash
   cp -r osus_report_header_footer /path/to/odoo/addons/
   ```

2. Update the apps list:
   - Go to Apps menu
   - Click "Update Apps List"

3. Install the module:
   - Search for "OSUS Report Header Footer"
   - Click Install

## Configuration

### Paper Format

The module includes a custom paper format (`OSUS Standard A4`) with optimized margins:
- **Top margin**: 90mm (to accommodate header)
- **Bottom margin**: 35mm (to accommodate footer)
- **Left/Right margins**: 7mm
- **Header spacing**: 80mm

The paper format is automatically set as the default for the main company upon installation.

### Customization

#### Changing Logo
Edit `/report/osus_external_layout.xml` and update the image source:
```xml
<img src="https://osusproperties.com/images/osus.png"
     alt="OSUS Properties"
     class="osus-logo"/>
```

To use a local logo instead:
1. Place your logo in `/static/src/img/`
2. Update the src attribute:
```xml
<img t-att-src="'/osus_report_header_footer/static/src/img/your_logo.png'"
     alt="OSUS Properties"
     class="osus-logo"/>
```

#### Customizing Colors
Edit `/static/src/css/report_style.css` and modify the CSS variables:
```css
:root {
    --osus-primary: #004a7c;      /* Primary brand color */
    --osus-secondary: #1a1a1a;    /* Secondary color */
    --osus-text: #333333;          /* Main text color */
    --osus-light-text: #666666;    /* Light text color */
    --osus-border: #cccccc;        /* Border color */
}
```

#### Adjusting Header/Footer Content
Modify the templates in `/report/osus_external_layout.xml`:
- `osus_external_layout_header` - Header template
- `osus_external_layout_footer` - Footer template

## Technical Details

### Module Structure
```
osus_report_header_footer/
├── __init__.py
├── __manifest__.py
├── README.md
├── data/
│   └── report_paperformat.xml      # Paper format configuration
├── report/
│   └── osus_external_layout.xml    # Header/footer templates
├── static/
│   ├── description/
│   │   └── icon.png                # Module icon
│   └── src/
│       ├── css/
│       │   └── report_style.css    # Report styling
│       └── img/                     # Images directory
└── security/
    └── ir.model.access.csv          # Access rights
```

### Dependencies
- `base` - Odoo base module
- `web` - Web framework and report engine
- `account` - Accounting module (for invoice reports)

### Compatibility
- **Odoo Version**: 17.0
- **Python Version**: 3.8+
- **License**: LGPL-3

## Usage

Once installed, all PDF reports will automatically use the OSUS header and footer. No additional configuration is required.

### Testing
To verify the installation:
1. Go to any module with reports (e.g., Invoicing)
2. Open a record (e.g., an invoice)
3. Click Print → Select any report
4. The generated PDF should display OSUS branding in the header and footer

### Affected Reports
This module affects all reports that use the standard external layout, including:
- Invoices and Bills
- Sales Orders and Quotations
- Purchase Orders
- Delivery Orders
- Payment Receipts
- Financial Reports
- HR Reports
- Custom Reports

## Styling Classes

The module provides additional CSS classes for enhanced report styling:

### Tables
```html
<table class="osus-table">
    <thead>
        <tr><th>Column 1</th><th>Column 2</th></tr>
    </thead>
    <tbody>
        <tr><td>Data 1</td><td>Data 2</td></tr>
        <tr class="osus-total-row">
            <td>Total</td><td>$1,000</td>
        </tr>
    </tbody>
</table>
```

### Info Boxes
```html
<div class="osus-info-box">
    Important information here
</div>
```

### Highlights
```html
<div class="osus-highlight">
    Highlighted content
</div>
```

### Address Blocks
```html
<div class="osus-address-block">
    Customer Name<br/>
    Street Address<br/>
    City, Country
</div>
```

### Signature Section
```html
<div class="osus-signature-section">
    <div class="osus-signature-block">
        <div class="osus-signature-line">Authorized Signature</div>
    </div>
</div>
```

## Troubleshooting

### Header/Footer Not Appearing
1. Check if the module is installed and active
2. Verify that reports use `web.external_layout` or `web.external_layout_standard`
3. Clear browser cache and regenerate the report

### Logo Not Displaying
1. Verify the logo URL is accessible
2. Check network connectivity
3. Consider using a local logo file instead of external URL

### Margin Issues
1. Adjust paper format margins in `/data/report_paperformat.xml`
2. Modify header spacing value if header is cut off
3. Test with different page orientations (Portrait/Landscape)

## Support

For issues, questions, or customization requests:
- **Website**: https://osusproperties.com
- **Module Location**: `/home/user/FINAL-ODOO-APPS/osus_report_header_footer`

## Changelog

### Version 17.0.1.0.0 (2025-11-25)
- Initial release
- Custom header with OSUS logo and company information
- Professional footer with contact details and page numbering
- Optimized paper format for A4 reports
- Comprehensive CSS styling
- Support for all standard Odoo reports

## Credits

**Author**: OSUS Properties
**License**: LGPL-3
**Website**: https://osusproperties.com

---

© 2025 OSUS Properties. All rights reserved.
