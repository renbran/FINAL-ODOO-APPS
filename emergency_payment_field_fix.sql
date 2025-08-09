-- Emergency SQL Fix for Account Payment Final Module
-- This script fixes field validation issues during module upgrade
-- Run this in your PostgreSQL database if the module upgrade fails

BEGIN;

-- Check if account_payment table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'account_payment') THEN
        RAISE NOTICE 'account_payment table found, proceeding with fixes...';
        
        -- Add approval_state column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'account_payment' AND column_name = 'approval_state') THEN
            ALTER TABLE account_payment ADD COLUMN approval_state VARCHAR(50) DEFAULT 'draft';
            RAISE NOTICE 'Added approval_state column';
        END IF;
        
        -- Add voucher_number column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'account_payment' AND column_name = 'voucher_number') THEN
            ALTER TABLE account_payment ADD COLUMN voucher_number VARCHAR(100) DEFAULT '/';
            RAISE NOTICE 'Added voucher_number column';
        END IF;
        
        -- Add remarks column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'account_payment' AND column_name = 'remarks') THEN
            ALTER TABLE account_payment ADD COLUMN remarks TEXT;
            RAISE NOTICE 'Added remarks column';
        END IF;
        
        -- Add qr_code column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'account_payment' AND column_name = 'qr_code') THEN
            ALTER TABLE account_payment ADD COLUMN qr_code BYTEA;
            RAISE NOTICE 'Added qr_code column';
        END IF;
        
        -- Add qr_in_report column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'account_payment' AND column_name = 'qr_in_report') THEN
            ALTER TABLE account_payment ADD COLUMN qr_in_report BOOLEAN DEFAULT TRUE;
            RAISE NOTICE 'Added qr_in_report column';
        END IF;
        
        -- Update existing records with proper default values
        UPDATE account_payment 
        SET approval_state = 'draft' 
        WHERE approval_state IS NULL OR approval_state = '';
        
        UPDATE account_payment 
        SET voucher_number = '/' 
        WHERE voucher_number IS NULL OR voucher_number = '';
        
        UPDATE account_payment 
        SET qr_in_report = TRUE 
        WHERE qr_in_report IS NULL;
        
        RAISE NOTICE 'Updated existing records with default values';
        
    ELSE
        RAISE NOTICE 'account_payment table not found - this is normal for fresh installation';
    END IF;
END $$;

-- Clean up any problematic view references
DELETE FROM ir_ui_view WHERE name LIKE '%payment%' AND arch_base LIKE '%voucher_number%' AND model = 'account.payment';

-- Clear cache to ensure clean loading
DELETE FROM ir_attachment WHERE res_model = 'ir.ui.view' AND name LIKE '%account_payment%';

COMMIT;

-- Success message
SELECT 'Emergency fix completed successfully! You can now try to upgrade the module.' AS status;
