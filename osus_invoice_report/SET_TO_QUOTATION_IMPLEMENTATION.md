# Set to Quotation Button Implementation

## Overview
Added "Set to Quotation" button to both Sale Order and Quotation list views as requested. This button allows users to reset confirmed sale orders back to the quotation (draft) state directly from the list view.

## Implementation Details

### Location
File: `d:\GitHub\osus_main\odoo\custom\osus_invoice_report\views\sale_order_views.xml`

### Changes Made

#### 1. Sale Order Tree View Enhancement
- **View ID**: `view_order_tree_inherit_osus_deal_tracking`
- **Added**: "Set to Quotation" button in tree view header
- **Functionality**: 
  - Calls standard `action_draft` method
  - Only visible when order state is not already 'draft'
  - Includes confirmation dialog for safety

#### 2. Quotation Tree View Enhancement
- **View ID**: `view_quotation_tree_inherit_osus_deal_tracking`
- **Added**: "Set to Quotation" button in tree view header
- **Functionality**: Same as sale order view

### Button Specifications

```xml
<button name="action_draft" string="Set to Quotation" type="object" 
        class="btn-secondary" 
        invisible="state == 'draft'"
        confirm="This will reset the order to quotation state. Are you sure?"/>
```

#### Button Properties:
- **name**: `action_draft` - Standard Odoo method for resetting to draft state
- **string**: "Set to Quotation" - User-friendly label
- **type**: `object` - Calls Python method on selected records
- **class**: `btn-secondary` - Bootstrap styling for secondary action
- **invisible**: `state == 'draft'` - Hidden when order is already in draft state
- **confirm**: User confirmation dialog to prevent accidental resets

### State Field Addition
Added hidden `state` field to both tree views to ensure button visibility conditions work properly:

```xml
<field name="state" optional="hide"/>
```

## User Experience

### When Button is Visible:
- Sale orders in 'sent', 'sale', or 'done' states
- Quotations that have been confirmed or processed

### When Button is Hidden:
- Orders already in 'draft' state
- Prevents redundant actions

### Confirmation Dialog:
- Displays warning: "This will reset the order to quotation state. Are you sure?"
- Prevents accidental state changes
- User can cancel if clicked by mistake

## Business Logic

The button leverages Odoo's standard `action_draft` method which:
1. Resets the sale order state to 'draft'
2. Maintains all order line data and customer information
3. Allows the order to be modified again
4. Updates related records and workflows accordingly

## Integration

This implementation:
- ✅ Uses standard Odoo functionality (`action_draft`)
- ✅ Follows Odoo UI/UX patterns
- ✅ Includes proper safety measures (confirmation dialog)
- ✅ Respects existing view structure and inheritance
- ✅ Available in both Sale Order and Quotation list views as requested
- ✅ Integrates seamlessly with existing OSUS Invoice Report module enhancements

## Testing Recommendations

1. **Functional Testing**:
   - Confirm a quotation to sale order
   - Use "Set to Quotation" button from list view
   - Verify order returns to draft state
   - Confirm order can be modified again

2. **UI Testing**:
   - Check button appears in both sale order and quotation list views
   - Verify button is hidden for draft orders
   - Test confirmation dialog functionality

3. **Permission Testing**:
   - Verify button respects user permissions for sale order modifications
   - Test with different user roles (salesperson, manager, etc.)

## Related Files

- **Main Implementation**: `views/sale_order_views.xml`
- **Active Data Filtering**: See `ACTIVE_DATA_FILTER_IMPLEMENTATION.md` for related changes
