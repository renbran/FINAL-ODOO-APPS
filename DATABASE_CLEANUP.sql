-- Database Cleanup Script for account_payment_final Module
-- Run this script before installing the module to fix data type issues

-- Clean up account_payment table if it exists
DO $$
BEGIN
    -- Check if account_payment table exists
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'account_payment') THEN
        
        -- Clean up any non-numeric values in Many2one fields
        UPDATE account_payment SET submitted_by = NULL WHERE submitted_by IS NOT NULL AND submitted_by::text !~ '^[0-9]+$';
        UPDATE account_payment SET reviewed_by = NULL WHERE reviewed_by IS NOT NULL AND reviewed_by::text !~ '^[0-9]+$';
        UPDATE account_payment SET approved_by = NULL WHERE approved_by IS NOT NULL AND approved_by::text !~ '^[0-9]+$';
        UPDATE account_payment SET authorized_by = NULL WHERE authorized_by IS NOT NULL AND authorized_by::text !~ '^[0-9]+$';
        UPDATE account_payment SET posted_by = NULL WHERE posted_by IS NOT NULL AND posted_by::text !~ '^[0-9]+$';
        UPDATE account_payment SET cancelled_by = NULL WHERE cancelled_by IS NOT NULL AND cancelled_by::text !~ '^[0-9]+$';
        
        -- Clean up standard Odoo fields that might have bad values
        UPDATE account_payment SET create_uid = NULL WHERE create_uid IS NOT NULL AND create_uid::text !~ '^[0-9]+$';
        UPDATE account_payment SET write_uid = NULL WHERE write_uid IS NOT NULL AND write_uid::text !~ '^[0-9]+$';
        UPDATE account_payment SET company_id = NULL WHERE company_id IS NOT NULL AND company_id::text !~ '^[0-9]+$';
        UPDATE account_payment SET journal_id = NULL WHERE journal_id IS NOT NULL AND journal_id::text !~ '^[0-9]+$';
        UPDATE account_payment SET partner_id = NULL WHERE partner_id IS NOT NULL AND partner_id::text !~ '^[0-9]+$';
        
        -- Remove any account_payment records with invalid references
        DELETE FROM account_payment WHERE journal_id IS NOT NULL AND journal_id NOT IN (SELECT id FROM account_journal);
        DELETE FROM account_payment WHERE partner_id IS NOT NULL AND partner_id NOT IN (SELECT id FROM res_partner);
        DELETE FROM account_payment WHERE company_id IS NOT NULL AND company_id NOT IN (SELECT id FROM res_company);
        
        RAISE NOTICE 'account_payment table cleanup completed';
    ELSE
        RAISE NOTICE 'account_payment table does not exist - skipping cleanup';
    END IF;
    
    -- Clean up any existing payment.signatory records if table exists
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'payment_signatory') THEN
        DELETE FROM payment_signatory WHERE user_id IS NOT NULL AND user_id NOT IN (SELECT id FROM res_users);
        DELETE FROM payment_signatory WHERE company_id IS NOT NULL AND company_id NOT IN (SELECT id FROM res_company);
        RAISE NOTICE 'payment_signatory table cleanup completed';
    END IF;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Cleanup script encountered an error but will continue: %', SQLERRM;
END $$;
