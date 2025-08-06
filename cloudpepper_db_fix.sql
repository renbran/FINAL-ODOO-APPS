-- CloudPepper Database Fix for Payment Account Enhanced Module
-- Run this script directly on your CloudPepper PostgreSQL database
-- to resolve the missing res_company columns error

-- Check current columns before making changes
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'res_company' 
AND column_name IN ('voucher_footer_message', 'voucher_terms', 'use_osus_branding')
ORDER BY column_name;

-- Add voucher_footer_message column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'res_company' AND column_name = 'voucher_footer_message'
    ) THEN
        ALTER TABLE res_company 
        ADD COLUMN voucher_footer_message TEXT DEFAULT 'Thank you for your business';
        
        RAISE NOTICE 'SUCCESS: Added voucher_footer_message column to res_company';
    ELSE
        RAISE NOTICE 'INFO: voucher_footer_message column already exists in res_company';
    END IF;
END $$;

-- Add voucher_terms column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'res_company' AND column_name = 'voucher_terms'
    ) THEN
        ALTER TABLE res_company 
        ADD COLUMN voucher_terms TEXT DEFAULT 'This is a computer-generated document. No physical signature or stamp required for system verification.';
        
        RAISE NOTICE 'SUCCESS: Added voucher_terms column to res_company';
    ELSE
        RAISE NOTICE 'INFO: voucher_terms column already exists in res_company';
    END IF;
END $$;

-- Add use_osus_branding column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'res_company' AND column_name = 'use_osus_branding'
    ) THEN
        ALTER TABLE res_company 
        ADD COLUMN use_osus_branding BOOLEAN DEFAULT TRUE;
        
        RAISE NOTICE 'SUCCESS: Added use_osus_branding column to res_company';
    ELSE
        RAISE NOTICE 'INFO: use_osus_branding column already exists in res_company';
    END IF;
END $$;

-- Verify the columns were added successfully
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'res_company' 
AND column_name IN ('voucher_footer_message', 'voucher_terms', 'use_osus_branding')
ORDER BY column_name;

-- Update all existing companies with default values if they're NULL
UPDATE res_company 
SET 
    voucher_footer_message = COALESCE(voucher_footer_message, 'Thank you for your business'),
    voucher_terms = COALESCE(voucher_terms, 'This is a computer-generated document. No physical signature or stamp required for system verification.'),
    use_osus_branding = COALESCE(use_osus_branding, TRUE)
WHERE 
    voucher_footer_message IS NULL 
    OR voucher_terms IS NULL 
    OR use_osus_branding IS NULL;

-- Show final status
SELECT 
    'SUCCESS: Payment Account Enhanced database fix completed' as status,
    COUNT(*) as companies_updated
FROM res_company;
