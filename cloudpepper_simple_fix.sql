-- CloudPepper Database Fix for Payment Account Enhanced Module
-- Simple SQL commands to add missing columns to res_company table
-- Run these commands one by one in your CloudPepper database console

-- Step 1: Check current table structure
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'res_company' 
AND column_name IN ('voucher_footer_message', 'voucher_terms', 'use_osus_branding')
ORDER BY column_name;

-- Step 2: Add voucher_footer_message column (run this command)
ALTER TABLE res_company 
ADD COLUMN voucher_footer_message TEXT DEFAULT 'Thank you for your business';

-- Step 3: Add voucher_terms column (run this command)
ALTER TABLE res_company 
ADD COLUMN voucher_terms TEXT DEFAULT 'This is a computer-generated document. No physical signature or stamp required for system verification.';

-- Step 4: Add use_osus_branding column (run this command)
ALTER TABLE res_company 
ADD COLUMN use_osus_branding BOOLEAN DEFAULT TRUE;

-- Step 5: Update existing records with default values
UPDATE res_company 
SET voucher_footer_message = 'Thank you for your business'
WHERE voucher_footer_message IS NULL;

UPDATE res_company 
SET voucher_terms = 'This is a computer-generated document. No physical signature or stamp required for system verification.'
WHERE voucher_terms IS NULL;

UPDATE res_company 
SET use_osus_branding = TRUE
WHERE use_osus_branding IS NULL;

-- Step 6: Verify the changes
SELECT 
    id, 
    name,
    voucher_footer_message,
    voucher_terms,
    use_osus_branding
FROM res_company
LIMIT 5;
