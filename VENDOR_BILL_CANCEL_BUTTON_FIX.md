# Vendor Bill Cancellation Button Fix

## Issue Description
The cancellation button was not visible in vendor bills (form and list views) because the `account_payment_approval` module was extending the `account.move` model with new approval states but only providing view modifications for payment views, not for vendor bill views.

## Root Cause Analysis
1. **Model Extension**: The `account_payment_approval` module added new states to `account.move`:
   - `submit_review`: Submit for Review
   - `waiting_approval`: Waiting For Approval  
   - `approved`: Approved
   - `rejected`: Rejected

2. **Missing View Configuration**: The module only had view modifications in `account_payment_views.xml` for payments, but no corresponding views for `account.move` (vendor bills).

3. **Button Visibility Logic**: The standard Odoo button visibility logic was not accounting for the new approval states, causing the cancel button to be hidden.

## Solution Implemented

### 1. Created New View File: `account_move_views.xml`

Added comprehensive view modifications for vendor bills including:

#### Form View Modifications (`view_move_form_inherit_payment_approval`)
- **Cancel Button**: Modified visibility to show in `draft`, `waiting_approval`, and `approved` states for vendor bills
- **Draft Button**: Enhanced to work with `rejected` state for vendor bills
- **New Approval Buttons**: Added approval workflow buttons specifically for vendor bills:
  - Submit for Review (visible in `draft` state)
  - Approve (visible in `waiting_approval` state for authorized users)
  - Reject (visible in `waiting_approval` state for authorized users)

#### Tree View Modifications (`view_move_tree_inherit_payment_approval`)
- **State Field Enhancement**: Added badge widget with color coding:
  - Blue: `waiting_approval`, `submit_review`
  - Green: `approved`
  - Red: `rejected`

#### Search View Enhancements (`view_account_move_filter_inherit_payment_approval`)
- **New Filters**: Added filters for approval states specific to vendor bills
- **Group By**: Added grouping by approval state for vendor bills

### 2. Enhanced Model Methods in `account_move.py`

#### New Methods Added:
- `_is_user_authorized_approver_move()`: Checks if user can approve vendor bills (uses same config as payments)
- `action_submit_review()`: Submits vendor bills for approval
- `approve_transfer()`: Approves vendor bills (authorized users only)
- `reject_transfer()`: Rejects vendor bills (authorized users only)

#### Enhanced Existing Methods:
- `button_cancel()`: Now allows cancellation from new approval states for vendor bills
- `button_draft()`: Enhanced to allow draft transition from rejected state
- `action_post()`: Modified to allow posting from approved state for vendor bills

### 3. Updated Manifest File
Added the new view file to the data section:
```python
'data': [
    'views/res_config_settings_views.xml',
    'views/account_payment_views.xml',
    'views/account_move_views.xml',  # <- New file added
    'data/server_actions.xml',
],
```

## Features Added

### Button Visibility Matrix for Vendor Bills:
| State | Submit Review | Approve | Reject | Cancel | Draft | Post |
|-------|---------------|---------|--------|--------|-------|------|
| Draft | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Waiting Approval | ❌ | ✅* | ✅* | ✅ | ❌ | ❌ |
| Approved | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Rejected | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| Posted | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Cancelled | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |

*Only for authorized approvers

### State Transitions for Vendor Bills:
```
Draft → Submit Review → Waiting Approval → Approve → Approved → Post → Posted
  ↓                          ↓               ↓
Cancel                    Reject          Cancel
  ↓                          ↓               ↓
Cancelled ← Draft ← Rejected              Cancelled
```

## Benefits
1. ✅ **Fixed Cancel Button**: Now visible in vendor bills form and list views
2. ✅ **Consistent Approval Workflow**: Vendor bills now have same approval process as payments
3. ✅ **Enhanced User Experience**: Clear visual indicators and proper button states
4. ✅ **Proper State Management**: All transitions handled correctly
5. ✅ **Authorization Control**: Only authorized users can approve/reject
6. ✅ **Filter & Search**: Easy filtering by approval states

## Configuration
The vendor bill approval system uses the same configuration as payment approval:
- **Settings**: Accounting > Configuration > Settings > Payment Approval
- **Approvers**: Configure single or multiple approvers
- **Amount Threshold**: Same threshold applies to both payments and bills

## Upgrade Notes
- Existing vendor bills will remain in their current states
- New approval states only apply to vendor bills (`in_invoice`, `in_refund`)
- Customer invoices are not affected by this approval workflow
- All existing functionality is preserved

## Testing
After applying this fix:
1. Navigate to Accounting > Vendors > Bills
2. Create a new vendor bill
3. Verify the "Cancel" button is visible in both form and list views
4. Test the approval workflow if configured
5. Ensure all state transitions work correctly
