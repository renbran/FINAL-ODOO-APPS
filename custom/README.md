# Custom Sales Order Module

This module extends the Odoo 17 Sales module by adding custom fields and logic to the sales order model.

## Features
- Adds custom fields to sales orders
- Custom create/write logic for custom fields
- Custom menu and views
- REST endpoint for custom sales report
- Demo data and security rules

## Installation
1. Copy the `custom` directory to your Odoo addons path.
2. Update the app list and install the module from the Odoo UI.

## Usage
- Access the new menu under Sales > Custom Sales > Custom Sales Orders.
- Use the `/custom_sales/report` endpoint for a JSON summary (requires authentication).

## Testing
Run Odoo's test suite to execute the included unit and integration tests.

## License
LGPL-3
