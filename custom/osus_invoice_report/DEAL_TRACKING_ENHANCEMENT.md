# Deal Tracking Fields Enhancement

## Overview
This enhancement improves the visibility of deal tracking fields in both the Sales app and Accounting app list views, making it easier to track and manage real estate deals.

## Enhanced Fields
The following deal tracking fields are now more prominently displayed:

### Core Deal Information
- **Booking Date** - Date when the deal was booked
- **Deal ID** - Unique identifier for the deal
- **Sale Value** - Total value of the property sale
- **Developer Commission** - Commission percentage for the deal

### Stakeholder Information
- **Buyer** - The buyer of the property
- **Project** - The real estate project
- **Unit** - The specific property unit

## Sales App Enhancements

### 1. Sale Order List View
- **Booking Date** and **Deal ID** are now visible by default (`optional="show"`)
- **Buyer** and **Project** information prominently displayed after partner field
- **Sale Value** and **Developer Commission** visible after amount total
- **Unit** field available but hidden by default to avoid clutter

### 2. Quotation List View
- Specific enhancement for quotation view with same field visibility
- All deal tracking fields available for quotations (draft/sent orders)
- Enhanced filtering and grouping capabilities

### 3. Enhanced Search & Filtering
#### New Filters:
- "With Deal ID" - Shows orders that have deal IDs
- "With Buyer" - Shows orders with buyer information
- "With Project" - Shows orders linked to projects
- "This Month Bookings" - Shows deals booked in current month
- "Property Deals" - Shows all property-related deals
- "High Value Deals" - Shows deals over 100,000 AED

#### New Grouping Options:
- Group by Buyer
- Group by Project
- Group by Unit
- Group by Booking Date

## Accounting App Enhancements

### 1. Account Move List View
- **Buyer**, **Project**, and **Deal ID** are now visible by default (`optional="show"`)
- **Booking Date** visible after invoice date
- **Sale Value** and **Developer Commission** visible after amount total
- **Unit** field available but hidden by default

### 2. Enhanced Search & Filtering
#### New Filters:
- "With Deal ID" - Shows invoices that have deal IDs
- "With Buyer" - Shows invoices with buyer information
- "With Project" - Shows invoices linked to projects
- "Property Deals" - Shows all property-related invoices

#### New Grouping Options:
- Group by Buyer
- Group by Project
- Group by Unit
- Group by Booking Date

## Technical Implementation

### Files Modified:
1. `osus_invoice_report/views/sale_order_views.xml`
   - Enhanced sale order tree view
   - Enhanced quotation tree view
   - Enhanced search view with filters and grouping

2. `osus_invoice_report/views/account_move_views.xml`
   - Enhanced account move tree view
   - Enhanced search view with filters and grouping

### Field Visibility Strategy:
- **`optional="show"`** - Important fields visible by default but can be hidden
- **`optional="hide"`** - Available fields that users can enable when needed
- Strategic positioning of fields for better readability

## Benefits

### For Sales Teams:
1. **Better Deal Tracking** - Quick visibility of deal status and key information
2. **Improved Filtering** - Find specific deals quickly using new filters
3. **Enhanced Reporting** - Group and analyze deals by various criteria
4. **Faster Decision Making** - Key deal information visible at a glance

### For Accounting Teams:
1. **Deal Context** - See property deal information directly in accounting views
2. **Better Reconciliation** - Connect invoices to specific deals and projects
3. **Commission Tracking** - Monitor commission rates and values
4. **Audit Trail** - Track deal progression from sale to invoice

### For Management:
1. **Dashboard Views** - Use grouping to create instant dashboard views
2. **Performance Analysis** - Track deals by project, buyer, or time period
3. **Commission Oversight** - Monitor commission rates across deals
4. **Revenue Tracking** - Track sale values and booking trends

## Usage Instructions

### Sales App:
1. Go to **Sales > Orders > Orders** or **Sales > Orders > Quotations**
2. Use the **column selector** to show/hide deal tracking fields as needed
3. Apply **filters** from the search bar to find specific types of deals
4. Use **Group By** options to organize deals by buyer, project, etc.

### Accounting App:
1. Go to **Accounting > Customers > Invoices**
2. Use the **column selector** to show/hide deal tracking fields
3. Apply **filters** to find property-related invoices
4. Use **Group By** options to organize by deal criteria

## QR Code Portal Access Enhancement

### Overview
The QR code functionality has been enhanced to provide secure portal access to documents. When users scan the QR code on invoices or other documents, they will be redirected directly to the portal view of that specific document.

### Key Features:
1. **Portal URL Generation** - QR codes now contain secure portal access URLs
2. **Access Token Security** - Each QR code includes a unique access token for secure access
3. **Mobile-Friendly** - QR codes can be scanned with any mobile device
4. **Fallback Support** - If portal URL generation fails, falls back to informational content

### Implementation:
- **Method**: `_get_portal_url()` generates the complete portal URL with access token
- **Security**: Uses Odoo's built-in `get_portal_url()` method for secure access
- **Error Handling**: Graceful fallback to informational QR content if portal access fails
- **Base URL**: Automatically detects the Odoo instance base URL

### Usage:
1. Enable "Show QR Code in Report" on any invoice
2. Generate the PDF report or view the document
3. The QR code can be scanned to access the portal view
4. Users with appropriate permissions can view the document details

## Future Enhancements
- Add deal tracking to other related models (payments, credit notes)
- Implement deal tracking dashboards
- Add automated deal progression workflows
- Enhance reporting with deal tracking analytics
