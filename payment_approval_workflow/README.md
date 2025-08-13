# Payment Approval Workflow

A comprehensive Odoo 17 module that implements multi-level approval workflows for account payments with QR code verification and digital signatures.

## Features

### Multi-Level Approval Workflows
- **Vendor Payments (Outbound):** Draft → Submitted → Reviewed → Approved → Authorized → Posted
- **Customer Receipts (Inbound):** Draft → Submitted → Reviewed → Approved → Posted
- Sequential approval process with role-based permissions
- Automatic state transitions and validation

### Digital Signatures
- Digital signature capture for each approval level
- Signature storage and display on payment forms
- Enhanced payment receipt reports with signature display
- Audit trail of who signed and when

### QR Code Verification
- Unique verification tokens for each payment
- Public QR verification portal accessible without login
- QR code generation and display on payment forms
- Mobile-friendly verification interface

### Email Notifications
- Professional HTML email templates with company branding
- Automated notifications for each workflow stage
- Action buttons linking directly to payment records
- Customizable email content with company colors (#800020 and gold)

### Security & Access Control
- Four security groups: Reviewer, Approver, Authorizer, Admin
- Hierarchical group membership (Authorizers include Approver permissions)
- Record rules for company-specific access
- Role-based button visibility and permissions

### User Interface Enhancements
- Enhanced payment form with approval status bar
- Smart buttons for journal entries and QR verification
- Signature and QR code tabs in payment forms
- Specialized menu items for approval queues
- Mobile-responsive verification portal

## Installation

1. Copy the module to your Odoo addons directory
2. Install required Python dependencies:
   ```bash
   pip install qrcode[pil]
   ```
3. Update your Odoo apps list
4. Install the "Payment Approval Workflow" module

## Configuration

### Security Groups Setup
1. Go to Settings → Users & Companies → Groups
2. Assign users to the appropriate approval groups:
   - **Payment Reviewer:** Can review submitted payments
   - **Payment Approver:** Can approve reviewed payments (includes Reviewer permissions)
   - **Payment Authorizer:** Can authorize approved vendor payments (includes Approver permissions)
   - **Payment Administrator:** Full module access including reset capabilities

### Email Configuration
- Ensure your mail server is properly configured
- Email templates use company branding and can be customized
- Base URL should be correctly set for QR verification links

## Usage

### For Payment Creators
1. Create a new payment as usual
2. Click "Submit for Review" when ready
3. Payment becomes read-only and enters approval workflow
4. Receive email notifications on status changes

### For Reviewers
1. Access "Payment Approvals → To Review" menu
2. Open submitted payments
3. Click "Review" button to open signature wizard
4. Provide digital signature and optional notes
5. Confirm to move payment to "Reviewed" status

### For Approvers
1. Access "Payment Approvals → To Approve" menu
2. Open reviewed payments
3. Click "Approve" button to open signature wizard
4. Provide digital signature and confirmation
5. Customer payments ready for posting; vendor payments need authorization

### For Authorizers (Vendor Payments Only)
1. Access "Payment Approvals → To Authorize" menu
2. Open approved vendor payments
3. Click "Authorize" button for final approval
4. Provide digital signature for authorization
5. Payment ready for posting

### QR Code Verification
1. QR codes are automatically generated when payments are submitted
2. Scan QR code or visit verification URL
3. Public verification page shows payment details
4. No login required for verification

## Technical Details

### Models Extended
- `account.payment`: Enhanced with approval workflow fields
- New wizard models for signatures and rejection

### Key Fields Added
- `approval_state`: Current approval status
- `verification_token`: Unique token for QR verification
- `*_signature`: Binary fields for digital signatures
- `*_id` and `*_date`: Tracking fields for approvers and dates
- `rejection_reason`: Text field for rejection explanations

### Controllers
- **PaymentVerificationController:** Public QR verification routes
- **PaymentPortalController:** Customer portal integration

### Reports
- Enhanced payment receipt with signatures and QR codes
- Professional formatting with approval information
- Signature display in receipt footer

### Email Templates
- 7 professional email templates for different workflow stages
- HTML styling with company branding
- Dynamic content based on payment type and status

## Customization

### Email Templates
Email templates can be customized in:
`Settings → Technical → Email → Templates`

Look for templates starting with "Payment Approval Workflow"

### Colors and Branding
- Primary color: #800020 (dark red)
- Accent color: #FFD700 (gold)
- CSS files can be modified for different branding

### Workflows
The approval workflow can be extended by:
1. Adding new states to the `approval_state` selection
2. Creating new security groups
3. Implementing additional wizard steps
4. Customizing email notifications

## Troubleshooting

### QR Codes Not Generating
- Ensure `qrcode` Python library is installed
- Check that `web.base.url` is properly configured
- Verify external dependencies in module manifest

### Email Notifications Not Sending
- Check mail server configuration
- Verify email addresses in user profiles
- Check email queue in Settings → Technical → Email

### Permission Issues
- Verify user group assignments
- Check record rules for multi-company setups
- Ensure users have basic accounting access

### Signature Widget Issues
- Ensure web assets are properly loaded
- Check browser compatibility for HTML5 canvas
- Verify signature widget is available in current Odoo version

## Support

For support and customization requests, please refer to the module documentation or contact the development team.

## License

This module is licensed under LGPL-3. See the LICENSE file for more details.

## Changelog

### Version 17.0.1.0.0
- Initial release for Odoo 17
- Multi-level approval workflows
- QR code verification portal
- Digital signature integration
- Professional email notifications
- Enhanced reporting with signatures
