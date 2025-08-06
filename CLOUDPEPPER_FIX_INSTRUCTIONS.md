# CloudPepper Database Fix Instructions

## Problem
The error `psycopg2.errors.UndefinedColumn: column res_company.voucher_footer_message does not exist` indicates that the payment_account_enhanced module added fields to the res_company model but the database columns weren't created.

## Solution
Run the following SQL commands in your CloudPepper database console **in order**:

### Step 1: Connect to your CloudPepper Database
1. Log into your CloudPepper control panel
2. Navigate to the PostgreSQL database management
3. Open the SQL console/query editor for your Odoo database

### Step 2: Execute SQL Commands (one by one)

Copy and paste each command separately into your database console:

```sql
-- Add voucher_footer_message column
ALTER TABLE res_company ADD voucher_footer_message TEXT;
```

```sql
-- Add voucher_terms column  
ALTER TABLE res_company ADD voucher_terms TEXT;
```

```sql
-- Add use_osus_branding column
ALTER TABLE res_company ADD use_osus_branding BOOLEAN;
```

```sql
-- Set default values for voucher_footer_message
UPDATE res_company SET voucher_footer_message = 'Thank you for your business' WHERE voucher_footer_message IS NULL;
```

```sql
-- Set default values for voucher_terms
UPDATE res_company SET voucher_terms = 'This is a computer-generated document. No physical signature or stamp required for system verification.' WHERE voucher_terms IS NULL;
```

```sql
-- Set default values for use_osus_branding
UPDATE res_company SET use_osus_branding = TRUE WHERE use_osus_branding IS NULL;
```

### Step 3: Verify the Fix

Run this command to confirm all columns were added:

```sql
SELECT COUNT(*) as total_companies, 
       COUNT(voucher_footer_message) as with_footer, 
       COUNT(voucher_terms) as with_terms, 
       COUNT(use_osus_branding) as with_branding 
FROM res_company;
```

The output should show all counts are equal, meaning all companies have the new fields.

### Step 4: Restart Odoo (if needed)

If you have access to restart Odoo:
1. Stop your Odoo instance
2. Start it again
3. The websocket errors should be resolved

### Step 5: Update Module (optional)

If you can access Odoo after the fix:
1. Go to Apps menu
2. Search for "payment_account_enhanced" 
3. Click "Upgrade" to ensure the module recognizes the new fields

## Expected Result
- The websocket error should disappear
- The payment voucher functionality should work properly
- No more `UndefinedColumn` errors in the logs

## Troubleshooting

**If you get "column already exists" errors:**
- That's normal! It means some columns were already there
- Continue with the remaining commands

**If you get permission errors:**
- Make sure you're connected as a database admin user
- Contact CloudPepper support if needed

**If Odoo still shows errors after the fix:**
- Clear your browser cache
- Restart your Odoo instance
- Check if there are other modules with similar issues

## Files Created for Reference
- `CLOUDPEPPER_FIX.sql` - Individual SQL commands
- `cloudpepper_simple_fix.sql` - Complete script with comments
- `cloudpepper_db_fix.sql` - Advanced PostgreSQL version (alternative)

Contact support if you need assistance with any of these steps.
