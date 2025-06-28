# Enhanced Commission Management System

## Overview
This module provides a comprehensive commission management system for Odoo 17 with advanced features for handling both external and internal commission structures.

## Key Features

### 🎯 Dual Commission Groups
- **Group A (External)**: Broker, Referrer, Cashback, Other External Parties
- **Group B (Internal)**: Agent 1, Agent 2, Manager, Director

### 📊 Multiple Calculation Methods
1. **Price Unit Based**: Commission calculated based on sum of individual line price units
2. **Untaxed Amount Total**: Commission calculated based on total untaxed amount
3. **Fixed Amount**: Direct fixed amount commissions

### 🔄 Auto-Calculation Features
- Enter percentage rate → automatically calculates amount
- Enter amount → automatically calculates percentage rate
- Real-time calculation as you modify values

### 📈 Smart Business Intelligence
- Commission status workflow (Draft → Calculated → Confirmed → Paid)
- Smart buttons showing related purchase orders
- Commission analysis and reporting
- Total commission tracking and company share calculation

### 🛠️ Enhanced User Experience
- Proper field grouping and sorting
- Intuitive form layout with separate tabs for external and internal commissions
- Status bar showing commission workflow progress
- Action buttons for commission lifecycle management

## How to Use

### 1. Basic Setup
1. Create or open a Sale Order
2. Configure the **Commission Calculation Method**:
   - **Price Unit**: For line-item based commissions
   - **Untaxed Total**: For order total based commissions  
   - **Fixed Amount**: For predetermined commission amounts

### 2. External Commissions (Group A)
Configure commissions for external parties:
- **Broker**: External sales broker commission
- **Referrer**: Referral partner compensation
- **Cashback**: Customer cashback amounts
- **Other External**: Any other external party payments

For each external commission:
1. Select the **Partner** (recipient)
2. Enter either **Rate (%)** or **Amount**
3. The system auto-calculates the corresponding field

### 3. Internal Commissions (Group B)
Configure internal team commissions:
- **Agent 1 & Agent 2**: Sales agent commissions
- **Manager**: Sales manager commission
- **Director**: Director level commission

Follow the same process as external commissions.

### 4. Commission Workflow
1. **Calculate Commissions**: Click to compute all commission amounts
2. **Confirm Commissions**: Approve the calculated commissions
3. **Generate Purchase Orders**: Automatically create POs for commission payments
4. **Reset to Draft**: Reset commission status if needed

### 5. Purchase Order Generation
When you click "Generate Purchase Orders":
- The system creates separate purchase orders for each commission recipient
- Each PO contains the appropriate commission product and amount
- POs are linked back to the source sale order for tracking

## Smart Features

### Smart Buttons
- **Purchase Orders**: Shows count and provides quick access to generated commission POs

### Commission Summary
- Real-time totals for external and internal commissions
- Company share calculation (remaining amount after all commissions)
- Net company share tracking

### Status Tracking
- Visual status bar showing commission workflow progress
- Commission processed indicator
- Automatic status updates based on actions

## Technical Details

### New Fields Added
- Commission calculation method selection
- Commission base amount (computed)
- Individual partner fields for each commission type
- Rate and amount fields with auto-calculation
- Commission status and tracking fields
- Purchase order relationship tracking

### Computation Logic
- Base amount calculated based on selected method
- Auto-conversion between rates and amounts
- Real-time total calculations
- Company share computations

### Security
- Proper access controls for different user groups
- Read/write permissions based on sales roles

## Installation & Configuration

1. Install the module through Odoo Apps
2. The module will automatically create demo commission products
3. Configure user permissions as needed
4. Start using the enhanced commission features in your sale orders

## Benefits

✅ **Streamlined Workflow**: Clear process from commission calculation to payment  
✅ **Flexibility**: Multiple calculation methods for different business needs  
✅ **Automation**: Auto-generation of purchase orders for commission payments  
✅ **Transparency**: Complete audit trail and status tracking  
✅ **User-Friendly**: Intuitive interface with smart auto-calculations  
✅ **Comprehensive**: Handles both external and internal commission structures  

## Support
For technical support or feature requests, please contact your system administrator.
