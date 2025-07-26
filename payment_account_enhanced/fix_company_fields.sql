-- SQL Script to fix missing company fields in payment_account_enhanced module
-- Run this script directly on your PostgreSQL database

-- Add voucher_footer_message column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='res_company' AND column_name='voucher_footer_message'
    ) THEN
        ALTER TABLE res_company ADD COLUMN voucher_footer_message TEXT;
        UPDATE res_company SET voucher_footer_message = 'Thank you for your business' WHERE voucher_footer_message IS NULL;
        RAISE NOTICE 'Added voucher_footer_message column to res_company';
    ELSE
        RAISE NOTICE 'voucher_footer_message column already exists';
    END IF;
END $$;

-- Add voucher_terms column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='res_company' AND column_name='voucher_terms'
    ) THEN
        ALTER TABLE res_company ADD COLUMN voucher_terms TEXT;
        UPDATE res_company SET voucher_terms = 'This is a computer-generated document. No physical signature or stamp required for system verification.' WHERE voucher_terms IS NULL;
        RAISE NOTICE 'Added voucher_terms column to res_company';
    ELSE
        RAISE NOTICE 'voucher_terms column already exists';
    END IF;
END $$;

-- Add use_osus_branding column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='res_company' AND column_name='use_osus_branding'
    ) THEN
        ALTER TABLE res_company ADD COLUMN use_osus_branding BOOLEAN;
        UPDATE res_company SET use_osus_branding = TRUE WHERE use_osus_branding IS NULL;
        RAISE NOTICE 'Added use_osus_branding column to res_company';
    ELSE
        RAISE NOTICE 'use_osus_branding column already exists';
    END IF;
END $$;

-- Verify the columns exist
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name='res_company' 
AND column_name IN ('voucher_footer_message', 'voucher_terms', 'use_osus_branding')
ORDER BY column_name;
