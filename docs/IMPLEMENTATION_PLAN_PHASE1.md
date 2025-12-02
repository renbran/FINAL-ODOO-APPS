# 🔧 IMPLEMENTATION PLAN - Phase 1 (Critical Fixes)
## Ready-to-Apply Code Changes

**Target**: Reach 88% Score (from 82%)  
**Timeline**: 4 hours development + 2 hours testing  
**Status**: ⚠️ MUST COMPLETE BEFORE DEPLOYMENT

---

## 📋 TASK CHECKLIST

### Task 1: Add payment_status Field ⏱️ 30 min
- [ ] Modify `sale_contract.py` - Add field definition
- [ ] Modify `sale_contract.py` - Add compute method
- [ ] Test field computation
- [ ] Verify no errors in logs

### Task 2: Create Migration Script ⏱️ 1 hour
- [ ] Create directory: `rental_management/migrations/3.4.1/`
- [ ] Create file: `post-migrate.py`
- [ ] Test on database copy
- [ ] Verify existing contracts work

### Task 3: Fix Wizard Field Reference ⏱️ 15 min
- [ ] Modify `property_vendor_wizard.py`
- [ ] Fix field access logic
- [ ] Test wizard validation
- [ ] Verify error messages

### Task 4: Update Module Version ⏱️ 5 min
- [ ] Update `__manifest__.py` version
- [ ] Add upgrade notes

### Task 5: Testing Phase ⏱️ 2 hours
- [ ] Test new contract creation
- [ ] Test existing contract access
- [ ] Test wizard validation
- [ ] Test booking confirmation
- [ ] Verify all workflows

---

## 🔴 FIX #1: Add payment_status Field

### File: `rental_management/models/sale_contract.py`

**Location**: Around line 1145 (inside SaleInvoice class)

**Find this code** (around line 1145):
```python
    # Invoice Type for categorization
    invoice_type = fields.Selection([
        ('booking', 'Booking/Reservation'),
        ('dld_fee', 'DLD Fee'),
        ('admin_fee', 'Admin Fee'),
        ('installment', 'Installment'),
        ('handover', 'Handover Payment'),
        ('completion', 'Completion Payment'),
        ('other', 'Other')
    ], string='Invoice Type', default='installment',
       help='Type of payment for categorization and reporting')
```

**Add AFTER the invoice_type field**:
```python
    # Payment Status (NEW - Required for booking workflow)
    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid')
    ], string='Payment Status', 
       compute='_compute_payment_status',
       store=True,
       help='Payment status of the invoice based on related account.move')
```

**Then add the compute method** (around line 1160, after compute_tax_amount):
```python
    @api.depends('invoice_id', 'invoice_id.payment_state', 'invoice_id.amount_residual', 'invoice_created')
    def _compute_payment_status(self):
        """Compute payment status based on related account.move payment state"""
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

---

## 🔴 FIX #2: Create Migration Script

### Step 1: Create Directory Structure

**Windows PowerShell**:
```powershell
# On CloudPepper server via SSH
ssh root@139.84.163.11

# Create migration directory
cd /var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/rental_management
mkdir -p migrations/3.4.1

# Create __init__.py files
touch migrations/__init__.py
touch migrations/3.4.1/__init__.py
```

### Step 2: Create Migration Script

**File**: `rental_management/migrations/3.4.1/post-migrate.py`

```python
# -*- coding: utf-8 -*-
"""
Migration to v3.4.1 - Two-Stage Payment Workflow

This migration updates existing contracts to be compatible with the new
booking requirements system.
"""

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Migrate existing contracts to v3.4.1 two-stage workflow compatibility.
    
    Updates:
    - Set invoice types for existing invoices
    - Ensure old contracts can create installments
    - Recompute booking requirements for all contracts
    """
    _logger.info("=" * 80)
    _logger.info("MIGRATION START: rental_management v3.4.1")
    _logger.info("Two-Stage Payment Workflow - Backward Compatibility Update")
    _logger.info("=" * 80)
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Step 1: Find all existing contracts
    all_contracts = env['property.vendor'].search([
        ('stage', '!=', False)
    ])
    
    _logger.info(f"Found {len(all_contracts)} total contracts in database")
    
    # Step 2: Focus on non-draft contracts (old data)
    old_contracts = all_contracts.filtered(
        lambda c: c.stage in ['booked', 'sold', 'refund', 'cancel', 'locked']
    )
    
    _logger.info(f"Processing {len(old_contracts)} existing (non-draft) contracts")
    
    migrated_count = 0
    error_count = 0
    
    for contract in old_contracts:
        try:
            _logger.info(f"Processing contract: {contract.sold_seq} (Stage: {contract.stage})")
            
            # Update invoice types based on invoice names
            if contract.sale_invoice_ids:
                # Booking invoices
                booking_inv = contract.sale_invoice_ids.filtered(
                    lambda inv: inv.name and any(
                        keyword in inv.name.lower() 
                        for keyword in ['booking', 'reservation', 'reserve']
                    )
                )
                if booking_inv:
                    booking_inv.write({'invoice_type': 'booking'})
                    _logger.info(f"  → Set {len(booking_inv)} invoices as 'booking'")
                
                # DLD Fee invoices
                dld_inv = contract.sale_invoice_ids.filtered(
                    lambda inv: inv.name and 'dld' in inv.name.lower()
                )
                if dld_inv:
                    dld_inv.write({'invoice_type': 'dld_fee'})
                    _logger.info(f"  → Set {len(dld_inv)} invoices as 'dld_fee'")
                
                # Admin Fee invoices
                admin_inv = contract.sale_invoice_ids.filtered(
                    lambda inv: inv.name and 'admin' in inv.name.lower()
                )
                if admin_inv:
                    admin_inv.write({'invoice_type': 'admin_fee'})
                    _logger.info(f"  → Set {len(admin_inv)} invoices as 'admin_fee'")
                
                # Mark remaining as installments
                other_inv = contract.sale_invoice_ids.filtered(
                    lambda inv: not inv.invoice_type or inv.invoice_type == 'installment'
                )
                if other_inv:
                    other_inv.write({'invoice_type': 'installment'})
                    _logger.info(f"  → Set {len(other_inv)} invoices as 'installment'")
            
            # Force recompute of booking requirements
            # For old contracts, this should set requirements_met=True
            contract._compute_booking_requirements_met()
            
            _logger.info(f"  → Booking Requirements Met: {contract.booking_requirements_met}")
            _logger.info(f"  → Can Create Installments: {contract.can_create_installments}")
            
            migrated_count += 1
            
        except Exception as e:
            error_count += 1
            _logger.error(f"ERROR processing contract {contract.sold_seq}: {str(e)}")
            _logger.exception(e)
            continue
    
    # Step 3: Update module version in database
    _logger.info("Updating module version in database...")
    cr.execute("""
        UPDATE ir_module_module 
        SET latest_version = '3.4.1'
        WHERE name = 'rental_management'
    """)
    
    # Step 4: Summary
    _logger.info("=" * 80)
    _logger.info("MIGRATION COMPLETE: rental_management v3.4.1")
    _logger.info(f"Successfully migrated: {migrated_count}/{len(old_contracts)} contracts")
    _logger.info(f"Errors encountered: {error_count}")
    _logger.info("=" * 80)
    
    if error_count > 0:
        _logger.warning(f"⚠️  {error_count} contracts had errors during migration")
        _logger.warning("   Please review logs and fix manually if needed")
    else:
        _logger.info("✅ All contracts migrated successfully")
```

---

## 🔴 FIX #3: Fix Wizard Field Reference

### File: `rental_management/wizard/property_vendor_wizard.py`

**Find this code** (around line 106-139):
```python
    def property_sale_action(self):
        """Create installment plan with booking requirements validation"""
        
        # Check if booking requirements are met
        if not self.customer_id.can_create_installments:
            # Build detailed error message
            status_msg = _("Cannot create installment plan. Booking requirements not met.\n\n")
            # ... rest of validation
```

**Replace with this**:
```python
    def property_sale_action(self):
        """Create installment plan with booking requirements validation"""
        
        # Get the contract from context (active_id is the property.vendor record)
        sell_id = self._context.get('active_id')
        if not sell_id:
            raise ValidationError(_("No contract found. Please open wizard from contract form."))
        
        contract = self.env['property.vendor'].browse(sell_id)
        
        # Check if booking requirements are met
        if not contract.can_create_installments:
            # Build detailed error message with current payment status
            status_msg = _("Cannot create installment plan. Booking requirements not met.\n\n")
            status_msg += _("📋 Required Payments Status:\n")
            status_msg += _("   {} Booking Invoice: {}\n").format(
                "✅" if contract.booking_invoice_paid else "❌",
                "Paid" if contract.booking_invoice_paid else "UNPAID"
            )
            status_msg += _("   {} DLD Fee Invoice: {}\n").format(
                "✅" if contract.dld_invoice_paid else "❌",
                "Paid" if contract.dld_invoice_paid else "UNPAID"
            )
            status_msg += _("   {} Admin Fee Invoice: {}\n").format(
                "✅" if contract.admin_invoice_paid else "❌",
                "Paid" if contract.admin_invoice_paid else "UNPAID"
            )
            status_msg += _("\n📊 Payment Progress: {:.1f}%\n\n").format(contract.booking_payment_progress)
            status_msg += _("⚠️ Please follow these steps:\n")
            status_msg += _("   1. Generate booking invoices (if not already done)\n")
            status_msg += _("   2. Ensure all booking, DLD, and admin fee invoices are PAID\n")
            status_msg += _("   3. Click 'Confirm Booking Paid' button on contract\n")
            status_msg += _("   4. Return here to create installment plan\n")
            
            raise ValidationError(status_msg)
        
        # If validation passes, continue with existing code
        property_id = self.env['product.template'].browse(
            self._context.get('active_id'))
```

---

## 🔴 FIX #4: Update Module Version

### File: `rental_management/__manifest__.py`

**Find this line** (near top of file):
```python
'version': '3.4.0',
```

**Change to**:
```python
'version': '3.4.1',
```

**Optional - Add to description** (around line 10):
```python
'description': """
    Rental Management System
    
    Version 3.4.1 Updates:
    - Two-stage payment workflow (Draft → Booked)
    - Booking requirements validation before installments
    - Payment progress tracking
    - Backward compatibility for existing contracts
""",
```

---

## 🧪 TESTING CHECKLIST

### Test 1: New Contract Creation
```
1. Create new property booking
2. Fill in customer details
3. Set booking amount (20%)
4. Click "Confirm Booking"
5. ✅ Verify contract stage = 'draft'
6. ✅ Verify 3 invoices generated (booking, DLD, admin)
7. ✅ Verify can_create_installments = False
```

### Test 2: Booking Payment Flow
```
1. Open draft contract
2. Click "Generate Booking Invoices" (if not auto-generated)
3. ✅ Verify 3 invoices created
4. Mark booking invoice as paid
5. Mark DLD invoice as paid
6. Mark admin invoice as paid
7. Click "Confirm Booking Paid"
8. ✅ Verify stage changed to 'booked'
9. ✅ Verify can_create_installments = True
```

### Test 3: Installment Creation
```
1. Open booked contract
2. Click "Create Installment Plan"
3. ✅ Verify wizard opens without error
4. Select payment schedule
5. Click "Create Installments"
6. ✅ Verify installment invoices generated
7. ✅ Verify total amounts correct
```

### Test 4: Existing Contracts (Migration Test)
```
1. Find existing contract (PS/2025/12/00012)
2. Open contract form
3. ✅ Verify can_create_installments = True
4. ✅ Verify no validation errors
5. Try creating installments
6. ✅ Verify works normally
```

### Test 5: Validation Blocking
```
1. Create new draft contract
2. Generate booking invoices
3. Leave invoices unpaid
4. Try to create installments
5. ✅ Verify error message shows
6. ✅ Verify payment status displayed
7. ✅ Verify helpful instructions shown
```

---

## 📊 DEPLOYMENT STEPS

### Step 1: Backup (CRITICAL!)
```powershell
# SSH to CloudPepper
ssh root@139.84.163.11

# Backup database
sudo -u postgres pg_dump scholarixv2 > /tmp/scholarixv2_backup_$(date +%Y%m%d_%H%M%S).sql

# Backup module directory
cd /var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a
tar -czf /tmp/rental_management_backup_$(date +%Y%m%d_%H%M%S).tar.gz rental_management/
```

### Step 2: Apply Code Changes
```powershell
# From local machine, upload modified files
scp rental_management/models/sale_contract.py root@139.84.163.11:/var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/rental_management/models/

scp rental_management/wizard/property_vendor_wizard.py root@139.84.163.11:/var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/rental_management/wizard/

scp rental_management/__manifest__.py root@139.84.163.11:/var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/rental_management/

# Upload migration script
scp -r rental_management/migrations root@139.84.163.11:/var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/rental_management/
```

### Step 3: Upgrade Module
```bash
# On CloudPepper server
sudo systemctl stop odoo

# Run upgrade (this triggers migration)
/opt/odoo/odoo-bin -c /etc/odoo/odoo.conf -d scholarixv2 -u rental_management --stop-after-init

# Check logs for migration output
tail -n 200 /var/log/odoo/odoo.log | grep -A 20 "MIGRATION"

# Restart Odoo
sudo systemctl start odoo
```

### Step 4: Verify Deployment
```bash
# Check service status
sudo systemctl status odoo

# Monitor logs
tail -f /var/log/odoo/odoo.log
```

---

## 🆘 ROLLBACK PROCEDURE

If something goes wrong:

```bash
# Stop Odoo
sudo systemctl stop odoo

# Restore database backup
sudo -u postgres psql -d postgres -c "DROP DATABASE scholarixv2;"
sudo -u postgres psql -d postgres -c "CREATE DATABASE scholarixv2 OWNER odoo_user;"
sudo -u postgres psql -d scholarixv2 < /tmp/scholarixv2_backup_YYYYMMDD_HHMMSS.sql

# Restore module files
cd /var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a
rm -rf rental_management/
tar -xzf /tmp/rental_management_backup_YYYYMMDD_HHMMSS.tar.gz

# Restart Odoo
sudo systemctl start odoo
```

---

## 📈 SUCCESS CRITERIA

After deployment, verify:

- ✅ No errors in Odoo logs
- ✅ Existing contracts accessible
- ✅ New contracts can be created
- ✅ Booking workflow functions
- ✅ Installment validation works
- ✅ No user complaints
- ✅ Migration logs show success

---

## 📞 POST-IMPLEMENTATION

### Immediate Actions:
1. Monitor error logs for 24 hours
2. Test with real users
3. Collect feedback
4. Document any issues

### Short Term (Week 1):
1. Create user training guide
2. Schedule team walkthrough
3. Monitor system performance
4. Plan Phase 2 fixes

### Medium Term (Month 1):
1. Implement Phase 2 improvements
2. Add automated tests
3. Optimize performance
4. Request re-audit

---

**Implementation Lead**: Development Team  
**Deployment Date**: TBD (After testing complete)  
**Estimated Completion**: 6 hours (dev + testing)  
**Go-Live Date**: TBD (After UAT approval)

---

*Document Version*: 1.0  
*Last Updated*: December 2, 2025  
*Status*: READY FOR IMPLEMENTATION
