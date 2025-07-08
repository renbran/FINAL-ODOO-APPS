# OSUS Invoice Report - Field Conflict Resolution

## Problem Description
The error `ValueError: File(s) /muk_web_colors/static/src/scss/colors_light.scss not found` is a secondary issue caused by field conflicts in the sale order model.

## Root Cause
Multiple modules are defining the same fields with different types:
- `osus_invoice_report` originally defined `deal_id` as Integer
- `commission_fields` and `advance_commission` define `deal_id` as Float
- This creates a field type conflict that can cascade into view loading issues

## Solution Applied

### 1. Fixed Field Type Conflicts
- Removed conflicting field definitions from `osus_invoice_report/models/sale_order.py`
- The fields are now properly handled by the existing commission modules

### 2. Updated Module Loading Order
- Added `sequence: 100` to manifest to ensure loading after commission modules
- This prevents field definition conflicts

### 3. Simplified Model
- Removed duplicate field definitions
- Let existing commission modules handle field definitions
- OSUS Invoice Report now focuses only on views and reports

## Files Modified

### `models/sale_order.py`
- Removed duplicate field definitions
- Added proper comments explaining field sources

### `__manifest__.py`
- Added loading sequence
- Updated description for better compatibility documentation

## Resolution Steps

### 1. Restart Odoo Server
```bash
# If using systemctl
sudo systemctl restart odoo

# If using docker
docker-compose restart

# If running manually
# Stop the process and restart with your usual command
```

### 2. Update the Module
1. Go to Odoo Apps menu
2. Search for "OSUS Invoice Report"
3. Click "Update" (not "Upgrade")
4. Clear browser cache (Ctrl+F5)

### 3. Verify Resolution
1. Navigate to Sales > Orders
2. Check that the list view loads without errors
3. Verify the "Set to Quotation" button appears
4. Test creating/editing sale orders

## Prevention

### For Future Module Development:
1. **Check existing fields**: Before defining fields, check if they exist in other modules
2. **Use proper dependencies**: Add modules that define fields as dependencies
3. **Field type consistency**: Ensure field types match across modules
4. **Loading sequence**: Use sequence numbers to control module loading order

## Field Sources in Current System

| Field | Source Module | Type |
|-------|---------------|------|
| `booking_date` | commission_fields | Date |
| `deal_id` | commission_fields | Float |
| `sale_value` | commission_fields | Monetary |
| `developer_commission` | commission_fields | Float |
| `buyer_id` | commission_fields | Many2one |
| `project_id` | commission_fields | Many2one |
| `unit_id` | commission_fields | Many2one |

## Troubleshooting

### If Error Persists:
1. **Check module installation order**:
   ```bash
   # In Odoo shell or database
   SELECT name, state, sequence FROM ir_module_module 
   WHERE name IN ('osus_invoice_report', 'commission_fields', 'advance_commission') 
   ORDER BY sequence;
   ```

2. **Manually uninstall and reinstall**:
   - Uninstall OSUS Invoice Report
   - Restart Odoo
   - Reinstall OSUS Invoice Report

3. **Check field conflicts**:
   ```python
   # In Odoo shell
   env['sale.order']._fields.keys()
   # Check for duplicate or conflicting field definitions
   ```

### Alternative Solutions:
1. **Move OSUS views to a separate module** that depends on commission modules
2. **Create a bridge module** that handles field definitions consistently
3. **Use XML field inheritance** instead of Python field definitions

## Contact
For further issues, check:
- Module dependencies in `__manifest__.py`
- Field definitions in commission modules
- View inheritance conflicts in XML files
