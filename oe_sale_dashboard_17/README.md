# Sales Dashboard Module - Enhanced Version

This module is under copyright of 'OdooElevate'

## Overview

This enhanced sales dashboard module provides a comprehensive view of sales data with improved filtering capabilities and field selection options.

## Key Features

### 1. Date Range Filtering
- **Start Date & End Date**: Select custom date ranges for filtering sales data
- **Booking Date Reference**: All filtering is now based on `booking_date` instead of `order_date`

### 2. Amount Field Selection
- **Total Amount**: Uses the standard `amount_total` field from sale orders
- **Sale Value**: Uses a custom `sale_value` field that can be customized based on business logic

### 3. Enhanced Sale Order Model
- **booking_date**: New datetime field to track when sales were booked
- **sale_value**: New monetary field for alternative amount calculations
- **Automatic Migration**: Existing orders will have their booking_date initialized from date_order

## Changes Made

### Backend Changes
1. **New Model Fields**:
   - `booking_date`: Datetime field in sale.order model
   - `sale_value`: Monetary field in sale.order model

2. **Data Migration**:
   - Automatic initialization of booking_date for existing records
   - Default booking_date set to current date/time for new records

### Frontend Changes
1. **Date Range Selector**: Replaced single date picker with start/end date inputs
2. **Amount Field Dropdown**: Added dropdown to choose between Total Amount and Sale Value
3. **Simplified Table Layout**: Removed time period columns, showing only Company and Amount
4. **Real-time Updates**: Dashboard updates automatically when filters change

### UI/UX Improvements
1. **Responsive Design**: Better layout for different screen sizes
2. **Modern Styling**: Clean, professional appearance with proper spacing
3. **Loading Indicators**: Clear feedback during data loading
4. **User-friendly Labels**: Clear field names and descriptions

## Installation Notes

1. **Module Dependencies**: Requires `sale_management` module
2. **Field Migration**: The module will automatically migrate existing data on installation
3. **Database Changes**: New fields will be added to the sale_order table

## Usage

1. **Access**: Navigate to Sales → Sales Report from the main menu
2. **Date Range**: Set start and end dates to filter the reporting period
3. **Amount Field**: Choose between "Total Amount" or "Sale Value" for calculations
4. **Real-time Data**: Dashboard updates automatically when filters change

## Customization

The `sale_value` field computation can be customized in the `sale_order.py` model based on specific business requirements. Currently, it mirrors the `amount_total` field but can be modified to implement custom calculation logic.

## Technical Details

- **Module Version**: 17.0.0.1.1
- **Odoo Version**: 17.0
- **Framework**: OWL Components
- **Database**: PostgreSQL compatible
- **License**: AGPL-3

## Support

For technical support and customizations, contact OdooElevate at https://odooelevate.odoo.com/
