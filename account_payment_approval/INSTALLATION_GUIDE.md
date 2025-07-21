# Quick Installation Guide

## Module Extension: Payment Voucher Reports

### What's New
- ✅ Printable payment vouchers with proper headings
- ✅ Customer Receipt Voucher vs Vendor Payment Voucher labels
- ✅ Reference number display
- ✅ Destination account visible and editable in draft stage
- ✅ Centered voucher headings

### Files Added
```
account_payment_approval/
├── reports/
│   ├── payment_voucher_report.xml
│   └── payment_voucher_template.xml
├── security/
│   └── security.xml
├── static/src/css/
│   └── payment_voucher.css
└── PAYMENT_VOUCHER_DOCUMENTATION.md
```

### Installation Steps
1. Restart Odoo server
2. Update Apps List
3. Upgrade "Payment Approvals" module
4. Test by creating a payment and printing voucher

### Testing
1. Create a customer payment (inbound)
   - Verify header shows "CUSTOMER RECEIPT VOUCHER"
   - Check destination account is editable in draft
   - Submit for review and print voucher

2. Create a vendor payment (outbound)
   - Verify header shows "VENDOR PAYMENT VOUCHER"
   - Check destination account is editable in draft
   - Submit for review and print voucher

### Support
Contact your Odoo developer for any customizations needed.
