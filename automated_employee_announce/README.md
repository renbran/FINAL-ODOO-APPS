# Automated Employee Announcements

## Description
Automatically sends announcement emails to all employees for birthdays and work anniversaries. Also notifies agents for sale order events (invoiced, payment, deal status reminder). Inherits and extends Odoo's automated mail rules.

## Installation
1. Copy the module to your Odoo addons directory
2. Restart Odoo server
3. Update app list and install the module

## Configuration
- Configure mail templates and rules under Employee Announcements > Automated Mail Rules
- Ensure employee records have valid birthday, hire date, and work email fields
- For sale order notifications, ensure agent1_partner_id, partner_id, buyer_id, project_id, unit_id, and price_unit are set on the sale order.

## Usage
- The module will automatically send emails to all employees on birthdays and work anniversaries
- You can manually trigger rules from the Automated Mail Rules menu
- When a sale order is invoiced, the agent1_partner_id will receive an email with a table of the deal (Partner, Buyer, Project, Unit, Price).
- When payment is received on an invoice, agent1_partner_id will receive a payment notification with commission timeline.
- Every day, a cron job checks for sale orders not invoiced after 30 days from booking_date and sends reminders.

## Features
1. **Employee Birthday/Anniversary Announcements** - Automated daily checks and emails
2. **Sale Order Invoiced Notifications** - Triggered when invoice is created
3. **Payment Receipt Notifications** - Triggered when payment is received on invoice
4. **Deal Status Reminders** - Daily cron job for overdue uninvoiced deals (30+ days)

## Dependencies
- base
- hr
- mail
- web
- hr_holidays
- sale_management

## Known Issues
- Employees without work email will not receive announcements
- Make sure mail server is configured in Odoo
- Sale order notification requires agent1_partner_id and related fields to be set; otherwise, the email will not be sent.
- All emails are logged in the chatter for traceability

## Testing
Run tests with: `odoo --test-enable -i automated_employee_announce --stop-after-init`

## Changelog
- 17.0.1.0.0: Initial release with birthday and work anniversary automation
- 17.0.1.1.0: Added sale order invoiced agent notification with HTML table summary
- 17.0.1.2.0: Added payment receipt notifications and deal status reminders with burgundy branding
