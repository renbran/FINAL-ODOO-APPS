# 🚨 CRITICAL FIXES REQUIRED - Two-Stage Workflow
## Must Implement Before Deployment

**Audit Score**: 82% (Target: 90%)  
**Status**: ❌ NOT PRODUCTION READY  
**Estimated Fix Time**: 4-5 hours

---

## 🔴 BLOCKER #1: Missing payment_status Field

### Problem
Code references `inv.payment_status` but field doesn't exist in `sale.invoice` model!

**Location**: `rental_management/models/sale_contract.py`
- Line 573: `@api.depends` includes 'sale_invoice_ids.payment_status'
- Line 585, 590, 595: Uses `inv.payment_status == 'paid'`
- Lines 803, 818, 833: Sets `'payment_status': 'unpaid'`

### Current Situation
`SaleInvoice` model (line 1113) has:
- ✅ `invoice_created` (Boolean) 
- ✅ `payment_state` (related to account.move.payment_state)
- ❌ `payment_status` - **MISSING!**

### Impact
- **System will crash** when trying to compute booking requirements
- AttributeError: 'sale.invoice' object has no attribute 'payment_status'
- Affects ALL new contracts created

### Fix Required

**Add to `SaleInvoice` model (around line 1145)**:

```python
# After invoice_type field, add:

payment_status = fields.Selection([
    ('unpaid', 'Unpaid'),
    ('partial', 'Partially Paid'),
    ('paid', 'Paid')
], string='Payment Status', 
   compute='_compute_payment_status',
   store=True,
   help='Payment status of the invoice')

@api.depends('invoice_id', 'invoice_id.payment_state', 'invoice_id.amount_residual', 'invoice_created')
def _compute_payment_status(self):
    """Compute payment status based on related account.move"""
    for rec in self:
        if not rec.invoice_created or not rec.invoice_id:
            rec.payment_status = 'unpaid'
        elif rec.invoice_id.payment_state == 'paid':
            rec.payment_status = 'paid'
        elif rec.invoice_id.payment_state in ['partial', 'in_payment']:
            rec.payment_status = 'partial'
        else:
            rec.payment_status = 'unpaid'
```

**Estimated Time**: 30 minutes

---

## 🔴 BLOCKER #2: Backward Compatibility Broken

### Problem
New contracts start in `stage='draft'` but existing contracts in database have various stages.

**Impact on Existing Contracts**:
- ❌ Cannot create installments (validation checks `can_create_installments`)
- ❌ Booking requirements not met (computed as False)
- ❌ Workflow assumes booking already paid (not true for old data)

### Database State
```sql
-- Current contracts in production
SELECT sold_seq, stage, customer_id 
FROM property_vendor 
WHERE stage IN ('booked', 'sold', 'refund');

-- Result: 11+ contracts with old stages
-- PS/2025/12/00012 - stage='booked' (but no booking validation done)
```

### Fix Required

**Create migration script**: `rental_management/migrations/3.4.1/post-migrate.py`

```python
# -*- coding: utf-8 -*-
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Migration to v3.4.1 - Two-Stage Payment Workflow
    
    Updates existing contracts to be compatible with new booking requirements system.
    """
    _logger.info("Starting migration to v3.4.1 - Two-Stage Payment Workflow")
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Step 1: Find all existing contracts that aren't in 'draft'
    contracts = env['property.vendor'].search([
        ('stage', 'in', ['booked', 'sold', 'refund', 'cancel', 'locked'])
    ])
    
    _logger.info(f"Found {len(contracts)} existing contracts to migrate")
    
    migrated_count = 0
    
    for contract in contracts:
        try:
            # For old contracts, assume booking was already paid
            # Set booking requirements to TRUE to allow installment generation
            
            # Update invoice types for existing invoices
            booking_invoices = contract.sale_invoice_ids.filtered(
                lambda inv: inv.name and ('booking' in inv.name.lower() or 'reservation' in inv.name.lower())
            )
            if booking_invoices:
                booking_invoices.write({'invoice_type': 'booking'})
            
            dld_invoices = contract.sale_invoice_ids.filtered(
                lambda inv: inv.name and 'dld' in inv.name.lower()
            )
            if dld_invoices:
                dld_invoices.write({'invoice_type': 'dld_fee'})
            
            admin_invoices = contract.sale_invoice_ids.filtered(
                lambda inv: inv.name and 'admin' in inv.name.lower()
            )
            if admin_invoices:
                admin_invoices.write({'invoice_type': 'admin_fee'})
            
            # Mark all other invoices as installments
            other_invoices = contract.sale_invoice_ids.filtered(
                lambda inv: inv.invoice_type == 'installment' or not inv.invoice_type
            )
            if other_invoices:
                other_invoices.write({'invoice_type': 'installment'})
            
            # Recompute booking requirements (should now be TRUE for old contracts)
            contract._compute_booking_requirements_met()
            
            migrated_count += 1
            
            _logger.info(f"Migrated contract {contract.sold_seq} - Stage: {contract.stage}")
            
        except Exception as e:
            _logger.error(f"Error migrating contract {contract.sold_seq}: {str(e)}")
            continue
    
    _logger.info(f"Migration complete: {migrated_count}/{len(contracts)} contracts migrated successfully")
    
    # Step 2: Update module version
    cr.execute("""
        UPDATE ir_module_module 
        SET latest_version = '3.4.1'
        WHERE name = 'rental_management'
    """)
    
    _logger.info("Migration to v3.4.1 completed")
```

**Also update `__manifest__.py`**:
```python
'version': '3.4.1',  # Changed from 3.4.0
```

**Estimated Time**: 1 hour (including testing)

---

## 🔴 BLOCKER #3: Wizard Field Reference Error

### Problem
Wizard uses wrong field name to access contract.

**Location**: `rental_management/wizard/property_vendor_wizard.py` line 108

```python
# WRONG - self.customer_id is Many2one to res.partner, not property.vendor
if not self.customer_id.can_create_installments:
```

### Issue
- Wizard's `customer_id` field is `Many2one('res.partner')`
- But code tries to access `can_create_installments` (which is on `property.vendor` model)
- Will raise AttributeError

### Fix Required

**Replace lines 106-139 in `property_vendor_wizard.py`**:

```python
def property_sale_action(self):
    """Create installment plan with booking requirements validation"""
    
    # Get the contract from context
    sell_id = self._context.get('active_id')
    if not sell_id:
        raise ValidationError(_("No contract found in context"))
    
    contract = self.env['property.vendor'].browse(sell_id)
    
    # Check if booking requirements are met
    if not contract.can_create_installments:
        # Build detailed error message
        status_msg = _("Cannot create installment plan. Booking requirements not met.\n\n")
        status_msg += _("Required Payments Status:\n")
        status_msg += _("✅ Booking Invoice: Paid\n") if contract.booking_invoice_paid else _("❌ Booking Invoice: UNPAID\n")
        status_msg += _("✅ DLD Fee Invoice: Paid\n") if contract.dld_invoice_paid else _("❌ DLD Fee Invoice: UNPAID\n")
        status_msg += _("✅ Admin Fee Invoice: Paid\n") if contract.admin_invoice_paid else _("❌ Admin Fee Invoice: UNPAID\n")
        status_msg += _("\nPayment Progress: {:.1f}%\n\n").format(contract.booking_payment_progress)
        status_msg += _("Please follow these steps:\n")
        status_msg += _("1. Generate booking invoices (if not already done)\n")
        status_msg += _("2. Ensure all booking, DLD, and admin fee invoices are paid\n")
        status_msg += _("3. Click 'Confirm Booking Paid' button\n")
        status_msg += _("4. Then create installment plan\n")
        
        raise ValidationError(status_msg)
    
    # Rest of existing code...
    property_id = self.env['product.template'].browse(
        self._context.get('active_id'))
```

**Estimated Time**: 15 minutes

---

## 🟠 HIGH PRIORITY #1: Performance Optimization

### Problem
Compute method triggers too frequently

**Location**: `sale_contract.py` line 572

```python
@api.depends('sale_invoice_ids', 'sale_invoice_ids.invoice_created', 
             'sale_invoice_ids.payment_status', 'sale_invoice_ids.invoice_type',
             'stage', 'dld_fee', 'admin_fee', 'book_price')
def _compute_booking_requirements_met(self):
```

### Issue
- Recomputes on EVERY invoice change (even unrelated invoices)
- If contract has 20 invoices, updating any one triggers full recompute
- Inefficient for large datasets

### Fix Required

**Option A: Add store_compute=True with selective invalidation**
```python
booking_requirements_met = fields.Boolean(
    compute='_compute_booking_requirements_met',
    store=True,  # Cache the result
    help="Are all booking requirements (booking + DLD + admin) paid?"
)
```

**Option B: Reduce dependencies**
```python
# Only depend on relevant invoice fields
@api.depends('sale_invoice_ids.payment_status', 'sale_invoice_ids.invoice_type', 'stage')
def _compute_booking_requirements_met(self):
    # Simplified version
```

**Estimated Time**: 1 hour

---

## 🟠 HIGH PRIORITY #2: Add Rollback Capability

### Problem
No way to revert contract from 'booked' back to 'draft' if payment fails or disputes occur.

### Fix Required

**Add to `PropertyVendor` model (sale_contract.py)**:

```python
def action_revert_to_draft(self):
    """
    Revert contract from 'booked' back to 'draft' stage.
    Only allowed for managers and if no installments generated yet.
    """
    self.ensure_one()
    
    # Security check - only managers can revert
    if not self.env.user.has_group('rental_management.group_property_manager'):
        raise AccessError(_("Only Property Managers can revert contracts to draft stage."))
    
    # Business logic check - cannot revert if installments exist
    installment_invoices = self.sale_invoice_ids.filtered(
        lambda inv: inv.invoice_type == 'installment' and inv.invoice_created
    )
    if installment_invoices:
        raise ValidationError(
            _("Cannot revert to draft. Installment invoices already generated.\n"
              "Number of installments: %d\n\n"
              "Please cancel installment invoices first if reverting is necessary.") 
            % len(installment_invoices)
        )
    
    # Revert stage
    self.write({'stage': 'draft'})
    
    # Log the action
    self.message_post(
        body=_("Contract reverted to Draft stage by %s") % self.env.user.name,
        subject=_("Contract Reverted"),
        message_type='notification'
    )
    
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': _('Contract Reverted'),
            'message': _('Contract has been reverted to Draft stage. Booking invoices remain unchanged.'),
            'type': 'success',
            'sticky': False,
        }
    }
```

**Add button to view** (`views/sale_contract_view.xml`):
```xml
<button name="action_revert_to_draft" 
        string="Revert to Draft" 
        type="object"
        class="btn-warning"
        invisible="stage != 'booked'"
        groups="rental_management.group_property_manager"
        confirm="Are you sure you want to revert this contract to Draft stage? This should only be done if payment verification is needed."/>
```

**Estimated Time**: 1 hour

---

## 🟠 HIGH PRIORITY #3: Add Security Rules

### Problem
New methods don't have access rights defined.

### Fix Required

**Add to `security/ir.model.access.csv`**:

```csv
# After existing lines, add:
access_property_vendor_booking_user,property.vendor.booking.user,model_property_vendor,rental_management.group_property_user,1,0,0,0
access_property_vendor_booking_manager,property.vendor.booking.manager,model_property_vendor,rental_management.group_property_manager,1,1,1,1
```

**Add method-level security** in `sale_contract.py`:

```python
def action_generate_booking_invoices(self):
    """Generate initial booking invoices (booking + DLD + admin fees)."""
    self.ensure_one()
    
    # Security check
    if not self.env.user.has_group('rental_management.group_property_user'):
        raise AccessError(_("You don't have permission to generate booking invoices."))
    
    # Rest of code...

def action_confirm_booking_paid(self):
    """Confirm all booking requirements are paid and move to 'booked' stage."""
    self.ensure_one()
    
    # Security check - only managers can confirm
    if not self.env.user.has_group('rental_management.group_property_manager'):
        raise AccessError(_("Only Property Managers can confirm booking payments."))
    
    # Rest of code...
```

**Estimated Time**: 30 minutes

---

## 📋 IMPLEMENTATION CHECKLIST

### Phase 1: Critical Fixes (4 hours)
- [ ] Add `payment_status` field to `SaleInvoice` model
- [ ] Test payment_status computation with sample invoices
- [ ] Create migration script (post-migrate.py)
- [ ] Test migration on copy of production database
- [ ] Fix wizard field reference in property_vendor_wizard.py
- [ ] Test wizard with booking validation
- [ ] Update __manifest__.py version to 3.4.1

### Phase 2: High Priority (3.5 hours)
- [ ] Optimize compute method dependencies
- [ ] Add rollback method (action_revert_to_draft)
- [ ] Add rollback button to view
- [ ] Test rollback functionality
- [ ] Add security checks to all new methods
- [ ] Update ir.model.access.csv
- [ ] Test permissions with different user roles

### Phase 3: Testing (2 hours)
- [ ] Unit test: payment_status computation
- [ ] Unit test: booking requirements validation
- [ ] Unit test: stage transitions
- [ ] Integration test: full workflow (draft → booked → sold)
- [ ] Test with existing production contracts
- [ ] Test rollback scenarios
- [ ] Performance test with 50+ invoices per contract

### Phase 4: Deployment Prep (1 hour)
- [ ] Backup production database
- [ ] Create rollback SQL script
- [ ] Test deployment on staging
- [ ] Verify migration script output
- [ ] Prepare deployment announcement
- [ ] Schedule maintenance window

---

## 📊 IMPACT ANALYSIS

### Without Fixes:
- ❌ System crashes on new contract creation
- ❌ Existing contracts cannot create installments
- ❌ No recovery from failed payments
- ❌ Security gaps
- ⚠️ Performance issues at scale

### With Fixes:
- ✅ Stable system operation
- ✅ Backward compatible
- ✅ Production ready
- ✅ Secure and performant
- ✅ Scores 90%+ on audit

---

## 🎯 RECOMMENDATION

**DO NOT DEPLOY** without implementing Phase 1 (Critical Fixes).

**Minimum to Deploy**: Phase 1 + Phase 3 testing  
**Recommended**: Phase 1 + Phase 2 + Phase 3  
**Optimal**: All phases

**Estimated Total Time**: 10.5 hours

---

## 📞 NEXT STEPS

1. **Review this document** with development team
2. **Prioritize fixes** based on deployment timeline
3. **Implement Phase 1** critical fixes
4. **Test thoroughly** on staging environment
5. **Re-run quality audit** to verify 90%+ score
6. **Schedule production deployment**

---

*Document Created*: December 2, 2025  
*Audit Reference*: QUALITY_AUDIT_TWO_STAGE_WORKFLOW.md  
*Target Score*: 90% (Current: 82%)
