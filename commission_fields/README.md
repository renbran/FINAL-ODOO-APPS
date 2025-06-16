# Commission Fields Module for Odoo 17

## Overview
This module extends Odoo 17 Sales, Accounting, and Purchase modules to provide advanced commission management, mapping, and reporting.

## Features
- Commission calculation for internal and external agents, brokers, referrals, cashback, and more
- Consistent commission field mapping between Sales Orders and Invoices
- Dedicated commission tab in Sales and Invoice forms
- Automated purchase order creation for commission payouts
- User-friendly UI with grouped commission fields
- Validation and constraints to ensure data integrity

## Usage
1. **Configure Commission Fields**: On the Sales Order form, fill in all relevant commission fields under the 'Commission' tab.
2. **Calculate Commission**: Use the 'Calculate Commission' button to compute all commission amounts.
3. **Confirm and Pay Commission**: Use the provided actions to confirm and mark commissions as paid.
4. **Generate Purchase Orders**: After confirming and posting invoices, use the action to generate purchase orders for commission recipients.
5. **Review Commission Data**: All commission data is visible on both Sales Orders and Invoices for full traceability.

## Field Mapping
- `deal_id`: Now a Many2one to `sale.order` for relational integrity.
- All related fields (`booking_date`, `buyer_id`, `project_id`, `unit_id`, `sale_value`) are consistently mapped and visible in both Sales and Invoice forms.

## Best Practices
- Always calculate and confirm commissions before confirming the sales order.
- Do not modify commission fields after confirmation unless the commission is reset to draft.
- Use the provided UI actions for all commission-related workflows.

## Testing
- Test all commission flows: creation, calculation, confirmation, payment, and purchase order generation.
- Ensure all commission fields are visible and correctly mapped in both Sales and Invoice forms.

## Support
For issues or feature requests, contact the module maintainer.
