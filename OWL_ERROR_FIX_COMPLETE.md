# OWL Error Fix - Complete Resolution

## 🚨 Issue Identified
```
UncaughtPromiseError > OwlError
EvalError: Can not evaluate python expression: (bool(not reconciled_invoice_ids))
Error: Name 'reconciled_invoice_ids' is not defined
```

## 🔍 Root Cause Analysis
The payment form view was referencing a field `reconciled_invoice_ids` in an invisible condition:
```xml
<button name="action_view_invoice" 
        invisible="not reconciled_invoice_ids">
```

However, this field was not properly defined in the model, causing OWL (Odoo Web Library) to fail when trying to evaluate the Python expression for the button's visibility.

## ✅ Solution Implemented

### 1. Added Missing Model Fields
```python
# Reconciled invoices and bills for smart buttons and visibility
reconciled_invoice_ids = fields.Many2many(
    'account.move',
    string='Reconciled Invoices',
    compute='_compute_reconciled_invoices',
    help="Customer invoices reconciled with this payment"
)

reconciled_bill_ids = fields.Many2many(
    'account.move',
    string='Reconciled Bills', 
    compute='_compute_reconciled_bills',
    help="Vendor bills reconciled with this payment"
)
```

### 2. Added Compute Methods
```python
@api.depends('move_id', 'move_id.line_ids', 'move_id.line_ids.matched_debit_ids', 'move_id.line_ids.matched_credit_ids')
def _compute_reconciled_invoices(self):
    """Compute reconciled customer invoices"""
    for record in self:
        reconciled_invoices = self.env['account.move']
        if record.move_id:
            # Get all reconciled moves from payment lines
            for line in record.move_id.line_ids:
                # Check matched debits and credits
                for partial_rec in line.matched_debit_ids + line.matched_credit_ids:
                    if partial_rec.debit_move_id.move_id.move_type == 'out_invoice':
                        reconciled_invoices |= partial_rec.debit_move_id.move_id
                    elif partial_rec.credit_move_id.move_id.move_type == 'out_invoice':
                        reconciled_invoices |= partial_rec.credit_move_id.move_id
        record.reconciled_invoice_ids = reconciled_invoices

@api.depends('move_id', 'move_id.line_ids', 'move_id.line_ids.matched_debit_ids', 'move_id.line_ids.matched_credit_ids')
def _compute_reconciled_bills(self):
    """Compute reconciled vendor bills"""
    for record in self:
        reconciled_bills = self.env['account.move']
        if record.move_id:
            # Get all reconciled moves from payment lines
            for line in record.move_id.line_ids:
                # Check matched debits and credits
                for partial_rec in line.matched_debit_ids + line.matched_credit_ids:
                    if partial_rec.debit_move_id.move_id.move_type == 'in_invoice':
                        reconciled_bills |= partial_rec.debit_move_id.move_id
                    elif partial_rec.credit_move_id.move_id.move_type == 'in_invoice':
                        reconciled_bills |= partial_rec.credit_move_id.move_id
        record.reconciled_bill_ids = reconciled_bills
```

### 3. Added Hidden Fields to View
```xml
<!-- Hidden Fields for Conditions -->
<field name="state" invisible="1"/>
<field name="payment_type" invisible="1"/>
<field name="is_internal_transfer" invisible="1"/>
<field name="reconciled_invoice_ids" invisible="1"/>
<field name="reconciled_bill_ids" invisible="1"/>
```

## 🎯 Technical Details

### Smart Button Logic
The reconciled invoice fields enable smart buttons to show/hide based on actual reconciliation status:
- **Invoice Button**: Shows only when `reconciled_invoice_ids` contains records
- **Bill Button**: Shows only when `reconciled_bill_ids` contains records

### Reconciliation Detection
The compute methods intelligently detect reconciled documents by:
1. Examining the payment's journal entry (`move_id`)
2. Checking all lines in the journal entry
3. Following matched debit/credit references
4. Filtering by document type (out_invoice for customer invoices, in_invoice for vendor bills)

### OWL Compatibility
- Fields are computed and available for JavaScript evaluation
- Hidden fields provide data without affecting UI layout
- Proper dependencies ensure updates when reconciliation changes

## 📋 Validation Results
✅ **Field References**: All invisible conditions have proper field declarations  
✅ **Model Fields**: Both reconciled_invoice_ids and reconciled_bill_ids defined  
✅ **Compute Methods**: Both _compute_reconciled_invoices and _compute_reconciled_bills implemented  
✅ **XML Syntax**: All view modifications are valid  
✅ **OWL Evaluation**: Error conditions resolved  

## 🚀 Impact & Benefits

### User Experience
- **No More Errors**: OWL evaluation errors eliminated
- **Smart Visibility**: Invoice buttons appear only when relevant
- **Accurate Tracking**: Proper reconciliation status tracking

### Technical Benefits
- **Robust Architecture**: Proper field dependencies and computation
- **Performance**: Computed fields cache results appropriately
- **Maintainability**: Clear separation of concerns with dedicated compute methods

### Business Value
- **Audit Trail**: Clear tracking of which invoices/bills are paid
- **Navigation**: Easy access to related documents via smart buttons
- **Data Integrity**: Accurate reconciliation status across the system

## 🔧 Files Modified
- **models/account_payment.py**: Added field definitions and compute methods
- **views/account_payment_views.xml**: Added hidden field declarations

## ✅ Ready for Deployment
This fix is production-ready and resolves the OWL error while adding valuable reconciliation tracking functionality. The solution maintains backward compatibility and follows Odoo best practices for computed fields and view dependencies.

The payment system now provides accurate reconciliation tracking with proper smart button visibility, eliminating the JavaScript evaluation errors that were preventing normal form operation.
