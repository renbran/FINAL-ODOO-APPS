-- Emergency fix for payment_account_enhanced missing columns
-- Run this script directly on the database to resolve immediate errors

-- Add voucher_footer_message column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'res_company' AND column_name = 'voucher_footer_message'
    ) THEN
        ALTER TABLE res_company 
        ADD COLUMN voucher_footer_message TEXT DEFAULT 'Thank you for your business';
        RAISE NOTICE 'Added voucher_footer_message column to res_company';
    ELSE
        RAISE NOTICE 'voucher_footer_message column already exists in res_company';
    END IF;
END $$;

-- Add voucher_terms column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'res_company' AND column_name = 'voucher_terms'
    ) THEN
        ALTER TABLE res_company 
        ADD COLUMN voucher_terms TEXT DEFAULT 'This is a computer-generated document. No physical signature or stamp required for system verification.';
        RAISE NOTICE 'Added voucher_terms column to res_company';
    ELSE
        RAISE NOTICE 'voucher_terms column already exists in res_company';
    END IF;
END $$;

-- Add use_osus_branding column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'res_company' AND column_name = 'use_osus_branding'
    ) THEN
        ALTER TABLE res_company 
        ADD COLUMN use_osus_branding BOOLEAN DEFAULT TRUE;
        RAISE NOTICE 'Added use_osus_branding column to res_company';
    ELSE
        RAISE NOTICE 'use_osus_branding column already exists in res_company';
    END IF;
END $$;

-- Update module version to trigger Odoo's recognition of the schema changes
UPDATE ir_module_module 
SET latest_version = '17.0.1.0.1'
WHERE name = 'payment_account_enhanced';

RAISE NOTICE 'Payment Account Enhanced database fix completed successfully';
