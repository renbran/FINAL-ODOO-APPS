# Payment Approval with Printable Vouchers

## Overview

This module extends the basic Payment Approvals functionality with printable payment voucher reports and enhanced destination account management.

## New Features

### 1. Printable Payment Voucher Report

The module now includes a comprehensive payment voucher report that automatically adjusts based on the payment type:

#### Customer Payments (Inbound)
- **Header**: "CUSTOMER RECEIPT VOUCHER" (centered)
- **Partner Label**: "Customer:"
- **Signature**: "Received By"

#### Vendor Payments (Outbound)  
- **Header**: "VENDOR PAYMENT VOUCHER" (centered)
- **Partner Label**: "Vendor:"
- **Signature**: "Authorized By"

#### Report Contents
- Reference number prominently displayed
- Payment details including amount, currency, payment method
- Destination account information
- Partner information with full address
- Payment status with colored badges
- Amount in words (if available)
- Related invoices table (if applicable)
- Approval information
- Signature lines for Prepared By, Approved By, and Received By/Authorized By

### 2. Enhanced Destination Account Management

- **Visibility**: Destination account field is now visible on the payment form
- **Editability**: Field is editable only in 'draft' and 'rejected' states
- **Required**: Destination account is now required for all payments
- **Security**: Field becomes read-only once payment moves beyond draft/rejected states

### 3. Print Button Integration

- Print Voucher button appears in the payment form header
- Button is available for payments that are not in 'draft' state
- Integrates seamlessly with Odoo's reporting system

## Usage

### Printing Payment Vouchers

1. Navigate to a payment record
2. Ensure the payment is not in 'draft' state
3. Click the "Print Voucher" button in the header
4. The system will generate a PDF voucher with appropriate headers and information

### Managing Destination Accounts

1. Create or edit a payment in 'draft' state
2. Select the appropriate destination account from the dropdown
3. The field becomes read-only after submitting for approval
4. Field becomes editable again if payment is rejected and returned to draft

### Approval Workflow Integration

The voucher system integrates with the existing approval workflow:

1. **Draft**: Create payment, set destination account
2. **Submit for Review**: Payment locked, voucher printable
3. **Approved**: Voucher shows approval information
4. **Posted**: Final voucher with all details confirmed
5. **Rejected**: Returned to draft, destination account editable again

## Technical Implementation

### Files Added/Modified

#### New Files:
- `reports/payment_voucher_report.xml` - Report definition
- `reports/payment_voucher_template.xml` - QWeb template
- `static/src/css/payment_voucher.css` - Styling
- `security/security.xml` - Security groups

#### Modified Files:
- `__manifest__.py` - Added new data files and assets
- `views/account_payment_views.xml` - Added print button and destination account field
- `models/account_payment.py` - Enhanced with utility methods

### Security Groups

- **Payment Approver**: Can approve payments
- **Payment Manager**: Can manage approvals and print vouchers

### Customization Options

The voucher template can be customized by:
1. Modifying the QWeb template in `reports/payment_voucher_template.xml`
2. Adjusting CSS styles in `static/src/css/payment_voucher.css`
3. Adding company-specific branding through Odoo's external layout system

## Installation

1. Install the module through Apps → Update Apps List
2. Search for "Payment Approvals"
3. Install or upgrade the module
4. Configure payment approval settings as needed
5. Assign users to appropriate security groups

## Support

For issues or customization requests, please contact your Odoo administrator or development team.
