# Rental Payment Schedule Implementation Guide

## Overview
The rental payment schedule system provides automated invoice generation for rental contracts with support for:
- **Flexible payment frequencies** (monthly, quarterly, bi-annual, annual)
- **Security deposits** (automatically added to first invoice)
- **Recurring maintenance fees** (merged or separate invoices)
- **Recurring utility services** (merged or separate invoices)
- **Days-based date calculation** for precise invoice scheduling

## Implementation Summary

### Models Modified

#### 1. `tenancy.details` (Rental Contracts)
**New Fields:**
- `payment_schedule_id` - Link to predefined payment schedule template
- `use_schedule` - Boolean flag indicating schedule usage

**New Methods:**
- `_onchange_payment_schedule()` - Shows preview of invoice count when schedule is selected
- `action_generate_rent_from_schedule()` - Generates rent invoices based on the payment schedule

### 2. View Updates

#### `tenancy_details_view.xml`
Added payment schedule selector and generation button:
```xml
<field name="payment_schedule_id" readonly="contract_type != 'new_contract'"/>
<button name="action_generate_rent_from_schedule" 
        string="⚡ Generate from Schedule"
        invisible="not payment_schedule_id or contract_type != 'new_contract'"/>
```

## How It Works

### 1. Payment Schedule Template
Rental contracts can select from predefined payment schedules (filtered by `schedule_type='rental'`):
- **2 Months Deposit + 12 Monthly Rent** - Security deposit + 12 monthly payments
- **Quarterly Rental Payments** - 4 quarterly payments
- **Annual Rental Payment** - Single annual payment
- **Custom schedules** - Can be created as needed

### 2. Invoice Generation Process

When "Generate from Schedule" is clicked:

1. **Validation**
   - Checks payment schedule is selected
   - Validates contract start date exists
   - Validates rent amount is set

2. **Clear Existing Invoices**
   - Removes unpaid draft invoices
   - Keeps paid invoices intact

3. **Calculate Base Amounts**
   - Base rent from `total_rent` field
   - Recurring maintenance from `total_maintenance` (if merged)
   - Recurring utilities from `extra_services_ids` monthly services (if merged)

4. **Generate Invoices**
   For each schedule line:
   - Calculate rent portion: `(total_rent × line.percentage) / 100`
   - Determine frequency days: monthly=30, quarterly=90, bi_annual=180, annual=365
   - Calculate invoice date: `start_date + days_after + (installment_number × frequency_days)`
   - Split amount across installments: `line_rent / number_of_installments`
   
   For each installment:
   - Create invoice line with rent amount
   - **Add deposit to first invoice** (if `is_any_deposit=True`)
   - **Add maintenance** (multiplied by period months if merged)
   - **Add utility services** (multiplied by period months if merged)
   - Create `account.move` customer invoice
   - Create `rent.invoice` tracking record

## Usage Examples

### Example 1: Standard Rental with Deposit
**Scenario:** AED 120,000/year rent, 2 months deposit, monthly payments

**Setup:**
1. Create rental contract
2. Set `total_rent` = 10,000 (monthly)
3. Set `is_any_deposit` = True, `deposit_amount` = 20,000
4. Select schedule: "2 Months Deposit + 12 Monthly Rent"
5. Click "Generate from Schedule"

**Result:** 13 invoices
- Invoice 1 (Day 0): AED 30,000 (10,000 rent + 20,000 deposit)
- Invoice 2 (Day 30): AED 10,000
- Invoice 3 (Day 60): AED 10,000
- ... continuing monthly for 12 months

### Example 2: Quarterly with Maintenance
**Scenario:** AED 120,000/year rent, AED 500/month maintenance (merged)

**Setup:**
1. Create rental contract
2. Set `total_rent` = 10,000
3. Set `is_maintenance_service` = True, `total_maintenance` = 500
4. Set `maintenance_service_invoice` = 'merge'
5. Select schedule: "Quarterly Rental Payments"
6. Click "Generate from Schedule"

**Result:** 4 invoices
- Invoice 1 (Day 0): AED 31,500 (30,000 rent + 1,500 maintenance for 3 months)
- Invoice 2 (Day 90): AED 31,500
- Invoice 3 (Day 180): AED 31,500
- Invoice 4 (Day 270): AED 31,500

### Example 3: Custom Schedule with Utilities
**Scenario:** AED 120,000/year, utilities AED 300/month (electricity) + AED 200/month (water)

**Setup:**
1. Create rental contract
2. Set `total_rent` = 120,000
3. Add utility services:
   - Electricity: AED 300/month, service_type='monthly'
   - Water: AED 200/month, service_type='monthly'
4. Set `extra_service_invoice` = 'merge'
5. Create custom schedule: "20% Booking + 80% Monthly"
   - Line 1: 20% on day 0, one_time
   - Line 2: 80% monthly × 12 starting day 30
6. Click "Generate from Schedule"

**Result:** 13 invoices
- Invoice 1 (Day 0): AED 24,000 (20% booking payment)
- Invoice 2 (Day 30): AED 8,500 (8,000 rent + 300 electricity + 200 water)
- Invoice 3 (Day 60): AED 8,500
- ... continuing monthly

## Additional Fee Handling

### Maintenance Fees
**Merge Scenario** (`maintenance_service_invoice='merge'`):
- Maintenance amount multiplied by period months
- Monthly = 1 month, Quarterly = 3 months, Bi-Annual = 6 months, Annual = 12 months
- Added as separate invoice line with maintenance product

**Separate Scenario** (`maintenance_service_invoice='separate'`):
- Not included in payment schedule generation
- Generated separately via existing maintenance invoice workflow

### Utility Services
**Merge Scenario** (`extra_service_invoice='merge'`):
- Only monthly recurring services included
- Each service multiplied by period months
- Added as individual invoice lines with service products

**Separate Scenario** (`extra_service_invoice='separate'`):
- Not included in payment schedule generation
- Generated separately via existing utility invoice workflow

### Security Deposits
- Always added to **first invoice only**
- Uses deposit product and deposit tax settings
- Amount from `deposit_amount` field
- Clearly labeled in invoice description

## Invoice Tracking

Each generated invoice creates two records:

1. **`account.move`** (Customer Invoice)
   - Standard Odoo invoice
   - Posted automatically if `invoice_post_type='automatically'`
   - Contains all invoice lines (rent + deposit + fees)

2. **`rent.invoice`** (Rental Tracking)
   - Links to tenancy contract
   - Tracks invoice date and amount
   - Stores description with installment details
   - Separates rent_amount from total amount

## Date Calculation Logic

Invoice dates calculated using:
```python
invoice_date = start_date + days_after + (installment_number × frequency_days)
```

**Frequency Days Mapping:**
- `one_time`: 0 days (immediate)
- `monthly`: 30 days
- `quarterly`: 90 days
- `bi_annual`: 180 days
- `annual`: 365 days

**Example:** For "30% Booking + 70% Quarterly" schedule:
- Line 1: 30% on day 0 → Invoice Date: start_date
- Line 2: 17.5% (70%/4) on day 30 → Invoice Date: start_date + 30
- Line 3: 17.5% on day 30 + 90 → Invoice Date: start_date + 120
- Line 4: 17.5% on day 30 + 180 → Invoice Date: start_date + 210
- Line 5: 17.5% on day 30 + 270 → Invoice Date: start_date + 300

## Configuration Settings

### System Parameters
- `rental_management.invoice_post_type`
  - `'automatically'` - Auto-post invoices after generation
  - Other - Leave in draft state

### Tax Configuration
- `instalment_tax` - Apply taxes to rent lines
- `deposit_tax` - Apply taxes to deposit lines
- `service_tax` - Apply taxes to maintenance and utility lines
- `tax_ids` - Tax records to apply

### Product Configuration
- `installment_item_id` - Product for rent line items
- `deposit_item_id` - Product for security deposits
- `maintenance_item_id` - Product for maintenance fees
- Service products - Configured per utility service

## Testing Checklist

### Basic Functionality
- [ ] Create rental contract with payment schedule
- [ ] Generate invoices from schedule
- [ ] Verify invoice count matches schedule
- [ ] Verify invoice dates are correct
- [ ] Verify invoice amounts match rent percentage

### Deposit Handling
- [ ] First invoice includes deposit
- [ ] Subsequent invoices don't include deposit
- [ ] Deposit amount matches `deposit_amount` field
- [ ] Deposit taxes applied correctly

### Maintenance Integration
- [ ] Merged maintenance: fees included in invoices
- [ ] Merged maintenance: multiplied by period months
- [ ] Separate maintenance: not included in schedule generation
- [ ] Maintenance product and taxes applied correctly

### Utility Integration
- [ ] Merged utilities: all monthly services included
- [ ] Merged utilities: multiplied by period months
- [ ] One-time utilities: not included
- [ ] Separate utilities: not included in schedule generation
- [ ] Each service creates separate invoice line

### Edge Cases
- [ ] Contract with no deposit: deposit not added
- [ ] Contract with no maintenance: no maintenance lines
- [ ] Contract with no utilities: no utility lines
- [ ] Regeneration: clears existing unpaid invoices
- [ ] Regeneration: keeps paid invoices
- [ ] Different frequencies: monthly, quarterly, bi-annual, annual

### UI/UX
- [ ] Payment schedule dropdown shows only rental schedules
- [ ] Generate button visible only when schedule selected
- [ ] Generate button hidden after contract activated
- [ ] Success notification shows invoice count
- [ ] Warning shown when schedule selected (invoice preview)

## Deployment Steps

1. **Backup Database**
   ```bash
   pg_dump -U odoo -d database_name > rental_backup_$(date +%Y%m%d).sql
   ```

2. **Upload Module**
   ```bash
   scp -r rental_management/ user@server:/opt/odoo/addons/
   ```

3. **Update Module**
   ```bash
   ssh user@server
   sudo -u odoo odoo -u rental_management -d database_name --stop-after-init
   ```

4. **Restart Odoo**
   ```bash
   sudo systemctl restart odoo
   ```

5. **Clear Browser Cache**
   - Hard refresh (Ctrl+Shift+R)

6. **Verify Installation**
   - Navigate to Rental Management → Configuration → Payment Schedules
   - Verify 6 sample schedules exist (3 sales + 3 rental types)
   - Create test rental contract
   - Select rental payment schedule
   - Generate invoices
   - Verify invoice count and amounts

## Troubleshooting

### Issue: Payment schedules not visible
**Solution:** Check access rights in `ir.model.access.csv`, ensure user has `property_rental_officer` or `property_rental_manager` group

### Issue: Generate button not visible
**Solution:** 
- Ensure payment schedule is selected
- Verify contract is in 'new_contract' state
- Check view XML loaded correctly

### Issue: Wrong invoice amounts
**Solution:**
- Verify total_rent is set correctly
- Check schedule percentages total 100%
- Verify maintenance/utility amounts if merged
- Check tax configuration

### Issue: Wrong invoice dates
**Solution:**
- Verify start_date is set
- Check days_after values in schedule lines
- Verify frequency days mapping

### Issue: Deposit added to all invoices
**Solution:**
- Check deposit only added when `invoice_count == 1`
- Verify is_any_deposit and deposit_amount fields

## Advanced Customization

### Creating Custom Payment Schedules

1. Navigate to: Rental Management → Configuration → Payment Schedules
2. Click "Create"
3. Set fields:
   - **Name**: Descriptive name (e.g., "3 Months Deposit + 6 Bi-Annual")
   - **Schedule Type**: Select "Rental Contract"
   - **Description**: Optional usage notes
4. Add Payment Lines:
   - **Name**: Stage description (e.g., "Security Deposit")
   - **Percentage**: Portion of total rent (e.g., 25% for 3 months deposit on 12-month contract)
   - **Days After**: Days from contract start (0 for immediate)
   - **Frequency**: One-time, Monthly, Quarterly, Bi-Annual, Annual
   - **Installments**: Number of payments for this stage
5. Verify total percentage = 100%
6. Save

### Extending for Custom Fees

To add custom fee types:

1. Add fields to `tenancy.details` model:
   ```python
   custom_fee_amount = fields.Monetary(string="Custom Fee")
   custom_fee_merge = fields.Selection([('merge', 'Merge'), ('separate', 'Separate')])
   custom_fee_item_id = fields.Many2one('product.product', string="Custom Fee Product")
   ```

2. Modify `action_generate_rent_from_schedule()`:
   ```python
   # Add after utility services section
   if self.custom_fee_amount > 0 and self.custom_fee_merge == 'merge':
       custom_fee_line = {
           'product_id': self.custom_fee_item_id.id,
           'name': 'Custom Fee',
           'quantity': period_months,
           'price_unit': self.custom_fee_amount,
       }
       invoice_lines.append((0, 0, custom_fee_line))
   ```

## Related Documentation

- **Payment Schedule Model**: See `rental_management/models/payment_schedule.py`
- **Sale Contract Integration**: See `PAYMENT_SCHEDULE_IMPLEMENTATION_SUMMARY.md`
- **Sample Schedules**: See `rental_management/data/payment_schedule_data.xml`
- **Security Rules**: See `rental_management/security/ir.model.access.csv`

## Support

For issues or questions:
1. Check error logs: `/var/log/odoo/odoo.log`
2. Enable debug mode: URL with `?debug=1`
3. Run validation scripts in module directory
4. Contact module maintainer

---

**Last Updated:** November 28, 2024
**Module Version:** 3.2.7
**Odoo Version:** 17.0
