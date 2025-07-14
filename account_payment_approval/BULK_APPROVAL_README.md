# Account Payment Approval - Bulk Operations Feature

## Overview
This module has been enhanced with comprehensive bulk operations that allow authorized users to process multiple payments at once from the list view.

## New Features

### Bulk Operations Buttons
All buttons are located in the payment list view header:

#### 1. Bulk Approve & Post
- **Function**: Approves and posts multiple selected payments in one action
- **Target**: Payments in "Waiting for Approval" state
- **Access**: Only available to authorized approval users
- **Result**: Payments are approved and automatically posted

#### 2. Bulk Reject
- **Function**: Rejects multiple selected payments
- **Target**: Payments in "Waiting for Approval" state  
- **Access**: Only available to authorized approval users
- **Result**: Payments are set to "Rejected" state and unlocked for editing

#### 3. Bulk Set to Draft
- **Function**: Resets multiple payments back to draft state
- **Target**: Payments in "Rejected" or "Cancelled" state
- **Access**: Available to all users
- **Result**: Payments are reset to "Draft" state and unlocked for editing

### Key Benefits
1. **Efficiency**: Process multiple payments simultaneously instead of one by one
2. **Complete Workflow Coverage**: Handle approve, reject, and draft operations in bulk
3. **Override Singleton Constraint**: All bulk methods safely handle multiple records
4. **Smart Filtering**: Only processes eligible payments and informs users of filtered selections
5. **Error Handling**: Graceful handling of individual payment failures
6. **User Feedback**: Clear notifications about success/failure status

## How to Use

### Bulk Approve & Post
1. Navigate to Accounting > Payments
2. Filter to show "Waiting for Approval" payments
3. Select multiple payments using checkboxes
4. Click "Bulk Approve & Post" button
5. Confirm the action
6. Review the success notification

### Bulk Reject
1. Navigate to Accounting > Payments
2. Filter to show "Waiting for Approval" payments
3. Select multiple payments to reject
4. Click "Bulk Reject" button
5. Confirm the action
6. Payments will be set to "Rejected" state

### Bulk Set to Draft
1. Navigate to Accounting > Payments
2. Filter to show "Rejected" or "Cancelled" payments
3. Select multiple payments to reset
4. Click "Bulk Set to Draft" button
5. Confirm the action
6. Payments will be reset to "Draft" state

## Technical Implementation

### Python Model Enhancement
- Added `bulk_approve_payments()` method for bulk approval and posting
- Added `bulk_reject_payments()` method for bulk rejection
- Added `bulk_draft_payments()` method for bulk draft reset
- All methods handle singleton constraint override
- Individual error handling per payment
- Comprehensive logging for all operations

### View Enhancement
- Extended list view with three header buttons
- Added visual state decorations:
  - Blue: Waiting for Approval
  - Green: Approved/Posted
  - Red: Rejected
  - Gray: Cancelled
- Confirmation dialogs for each bulk operation

### JavaScript Enhancement
- Custom list controller with smart filtering
- Separate handling for each bulk operation type
- Filters selection to only process eligible payments
- User-friendly notifications and warnings

## Error Handling
- If a payment fails during bulk operations, it maintains appropriate state
- Failed payments can be processed individually later
- Detailed error logging for troubleshooting
- User-friendly error messages with operation counts

## Security & Access Control
- Bulk approve and reject: Only authorized approval users
- Bulk draft: Available to all users (for rejected/cancelled payments)
- Respects existing approval workflow and amount limits
- Maintains complete audit trail for all actions

## States and Workflow
The bulk operations respect the existing workflow:

### Bulk Approve & Post
- Source: Waiting for Approval → Approved → Posted
- Automatic posting after approval
- Error handling keeps payments in appropriate recovery state

### Bulk Reject  
- Source: Waiting for Approval → Rejected
- Unlocks payments for editing
- Allows subsequent draft reset

### Bulk Draft
- Source: Rejected or Cancelled → Draft
- Unlocks payments for editing
- Enables workflow restart
