# Odoo 17 Dynamic Accounting Reports

This module provides dynamic accounting reports compatible with the om_account_accountant_v17 module for Odoo 17 Community Edition.

## Features

- General Ledger Report
- Trial Balance Report
- Partner Ledger Report
- Aged Payable Report
- Aged Receivable Report
- Tax Report
- Cash Book Report
- Bank Book Report
- Balance Sheet Report
- Profit & Loss Report

## Requirements

- Odoo 17 Community Edition
- om_account_accountant_v17 module
- accounting_pdf_reports module
- Python libraries:
  - xlsxwriter
  - python-dateutil

## Installation

1. Install the required Python libraries:
   ```
   pip install xlsxwriter python-dateutil
   ```
   Or use the provided script:
   ```
   # Linux/Mac
   ./install_dependencies.sh
   
   # Windows
   install_dependencies.bat
   ```

2. Copy the module to your Odoo addons folder.

3. Update the app list in Odoo.

4. Install the module "Odoo 17 Dynamic Accounting Reports".

## Usage

After installation, you will find the "Dynamic Reports" menu under Accounting. Select any report type and set the filters according to your requirements.

## Report Types

### General Ledger

Shows all transactions for a specific period with detailed move lines for each account.

### Trial Balance

Provides a summary of account balances with debit, credit, and balance for each account.

### Partner Ledger

Displays all transactions for a specific partner with detailed move lines.

### Aged Reports

- **Aged Payable**: Shows vendor invoices that are due, overdue, or paid.
- **Aged Receivable**: Shows customer invoices that are due, overdue, or paid.

### Tax Report

Provides details of tax amounts collected and paid for a specific period.

### Cash & Bank Books

- **Cash Book**: Shows all cash transactions for a specific period.
- **Bank Book**: Shows all bank transactions for a specific period.

### Financial Reports

- **Balance Sheet**: Shows assets, liabilities, and equity at a specific date.
- **Profit & Loss**: Shows revenue, expenses, and profit/loss for a specific period.

## Support

For support, please contact:
- Email: odoomates@gmail.com
- Website: https://www.walnutit.com

## License

This module is licensed under LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
