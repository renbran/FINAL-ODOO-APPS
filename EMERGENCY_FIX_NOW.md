# 🚨 EMERGENCY DATABASE FIX - Execute Immediately

## The Error:
```
psycopg2.errors.InvalidTextRepresentation: invalid input syntax for type integer: "ADMINISTRATOR"
```

## Immediate Solution:

### Step 1: Connect to PostgreSQL and clean the data

```bash
# Connect to your PostgreSQL database
psql -U odoo -d stagingtry

# OR if you need to specify host/port:
# psql -h localhost -p 5432 -U odoo -d stagingtry
```

### Step 2: Execute this SQL cleanup (copy and paste all at once):

```sql
-- Emergency cleanup for account_payment table
BEGIN;

-- Clean up the problematic "ADMINISTRATOR" values in account_payment table
UPDATE account_payment 
SET 
    submitted_by = NULL,
    reviewed_by = NULL,
    approved_by = NULL,
    authorized_by = NULL,
    posted_by = NULL
WHERE 
    (submitted_by IS NOT NULL AND CAST(submitted_by AS TEXT) = 'ADMINISTRATOR')
    OR (reviewed_by IS NOT NULL AND CAST(reviewed_by AS TEXT) = 'ADMINISTRATOR')
    OR (approved_by IS NOT NULL AND CAST(approved_by AS TEXT) = 'ADMINISTRATOR')
    OR (authorized_by IS NOT NULL AND CAST(authorized_by AS TEXT) = 'ADMINISTRATOR')
    OR (posted_by IS NOT NULL AND CAST(posted_by AS TEXT) = 'ADMINISTRATOR');

-- Also clean any other problematic user ID fields
UPDATE account_payment 
SET create_uid = 1 
WHERE create_uid IS NOT NULL AND CAST(create_uid AS TEXT) = 'ADMINISTRATOR';

UPDATE account_payment 
SET write_uid = 1 
WHERE write_uid IS NOT NULL AND CAST(write_uid AS TEXT) = 'ADMINISTRATOR';

-- Check if payment_signatory table exists and clean it too
UPDATE payment_signatory 
SET user_id = NULL
WHERE user_id IS NOT NULL AND CAST(user_id AS TEXT) = 'ADMINISTRATOR';

COMMIT;

-- Exit PostgreSQL
\q
```

### Step 3: Restart Odoo and try installation again

```bash
# Restart Odoo service
systemctl restart odoo

# OR if using a different service manager:
# service odoo restart

# Try installing the module again
./odoo-bin -d stagingtry -i account_payment_final --stop-after-init
```

## Alternative Quick Fix (if the above doesn't work):

If you're still getting errors, you can temporarily drop and recreate the problematic fields:

```sql
-- Connect to database again
psql -U odoo -d stagingtry

-- Remove the problematic columns temporarily
ALTER TABLE account_payment DROP COLUMN IF EXISTS submitted_by;
ALTER TABLE account_payment DROP COLUMN IF EXISTS reviewed_by;
ALTER TABLE account_payment DROP COLUMN IF EXISTS approved_by;
ALTER TABLE account_payment DROP COLUMN IF EXISTS authorized_by;
ALTER TABLE account_payment DROP COLUMN IF EXISTS posted_by;

-- Exit
\q
```

Then try installing the module - it will recreate these fields properly.

## Root Cause:
The database contains string values ("ADMINISTRATOR") in fields that should only contain integer IDs (references to res.users table). Odoo is trying to convert these fields to integers and failing.

Execute the cleanup above and the installation should work!
