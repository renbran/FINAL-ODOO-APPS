# Automated Employee Announcements

## Description
Automatically sends announcement emails to all employees for birthdays and work anniversaries. Inherits and extends Odoo's automated mail rules.

Also notifies the agent1_partner_id via email when a sale order is invoiced, with a beautiful HTML summary of the deal.

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

## Changelog
- 17.0.1.0.0: Initial release with birthday and work anniversary automation
- 17.0.1.1.0: Added sale order invoiced agent notification with HTML table summary
