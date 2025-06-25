-- ====================================================================
-- Odoo 17 Database Migration Fix for NOT NULL Constraint Errors
-- ====================================================================
-- 
-- This script fixes the following errors:
-- - hr_employee: unable to set NOT NULL on column 'agent_id'
-- - hr_employee: unable to set NOT NULL on column 'labour_card_number'
-- - hr_employee: unable to set NOT NULL on column 'salary_card_number'
-- - res_bank: unable to set NOT NULL on column 'routing_code'
--
-- INSTRUCTIONS:
-- 1. Connect to your PostgreSQL database using psql or pgAdmin
-- 2. Replace 'your_database_name' with your actual Odoo database name
-- 3. Run this script before starting Odoo
-- ====================================================================

-- Connect to your database (adjust database name as needed)
-- \c your_database_name;

BEGIN;

-- Display current status
SELECT 'Starting database migration fix...' AS status;

-- ====================================================================
-- 1. Fix res_bank.routing_code field
-- ====================================================================

-- Check if routing_code column exists in res_bank
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'res_bank' AND column_name = 'routing_code'
    ) THEN
        -- Update NULL routing_code values with padded ID
        UPDATE res_bank 
        SET routing_code = LPAD(CAST(id AS TEXT), 9, '0')
        WHERE routing_code IS NULL OR routing_code = '';
        
        RAISE NOTICE 'Updated % rows in res_bank.routing_code', 
            (SELECT COUNT(*) FROM res_bank WHERE routing_code = LPAD(CAST(id AS TEXT), 9, '0'));
    ELSE
        RAISE NOTICE 'Column routing_code does not exist in res_bank table';
    END IF;
END $$;

-- ====================================================================
-- 2. Fix hr_employee fields
-- ====================================================================

-- Check if hr_employee table and required columns exist
DO $$
DECLARE
    agent_col_exists BOOLEAN;
    labour_col_exists BOOLEAN;
    salary_col_exists BOOLEAN;
    default_bank_id INTEGER;
    updated_count INTEGER;
BEGIN
    -- Check if columns exist
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'hr_employee' AND column_name = 'agent_id'
    ) INTO agent_col_exists;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'hr_employee' AND column_name = 'labour_card_number'
    ) INTO labour_col_exists;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'hr_employee' AND column_name = 'salary_card_number'
    ) INTO salary_col_exists;
    
    -- Fix agent_id field
    IF agent_col_exists THEN
        -- Get or create a default bank
        SELECT id INTO default_bank_id FROM res_bank ORDER BY id LIMIT 1;
        
        IF default_bank_id IS NULL THEN
            -- Create a default bank if none exists
            INSERT INTO res_bank (name, routing_code, create_date, write_date, create_uid, write_uid)
            VALUES ('Default Bank', '000000000', NOW(), NOW(), 1, 1)
            RETURNING id INTO default_bank_id;
            
            RAISE NOTICE 'Created default bank with ID: %', default_bank_id;
        END IF;
        
        -- Update NULL agent_id values
        UPDATE hr_employee 
        SET agent_id = default_bank_id 
        WHERE agent_id IS NULL;
        
        GET DIAGNOSTICS updated_count = ROW_COUNT;
        RAISE NOTICE 'Updated % rows in hr_employee.agent_id', updated_count;
    ELSE
        RAISE NOTICE 'Column agent_id does not exist in hr_employee table';
    END IF;
    
    -- Fix labour_card_number field
    IF labour_col_exists THEN
        UPDATE hr_employee 
        SET labour_card_number = LPAD(CAST(id AS TEXT), 14, '0')
        WHERE labour_card_number IS NULL OR labour_card_number = '';
        
        GET DIAGNOSTICS updated_count = ROW_COUNT;
        RAISE NOTICE 'Updated % rows in hr_employee.labour_card_number', updated_count;
    ELSE
        RAISE NOTICE 'Column labour_card_number does not exist in hr_employee table';
    END IF;
    
    -- Fix salary_card_number field
    IF salary_col_exists THEN
        UPDATE hr_employee 
        SET salary_card_number = LPAD(CAST(id AS TEXT), 16, '0')
        WHERE salary_card_number IS NULL OR salary_card_number = '';
        
        GET DIAGNOSTICS updated_count = ROW_COUNT;
        RAISE NOTICE 'Updated % rows in hr_employee.salary_card_number', updated_count;
    ELSE
        RAISE NOTICE 'Column salary_card_number does not exist in hr_employee table';
    END IF;
END $$;

-- ====================================================================
-- 3. Verification queries
-- ====================================================================

-- Verify hr_employee table
DO $$
DECLARE
    null_count INTEGER;
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'hr_employee') THEN
        SELECT COUNT(*) INTO null_count
        FROM hr_employee 
        WHERE agent_id IS NULL 
           OR labour_card_number IS NULL 
           OR salary_card_number IS NULL
           OR labour_card_number = ''
           OR salary_card_number = '';
        
        IF null_count = 0 THEN
            RAISE NOTICE '✅ hr_employee verification: All required fields have values';
        ELSE
            RAISE NOTICE '❌ hr_employee verification: % records still have NULL/empty values', null_count;
        END IF;
    END IF;
END $$;

-- Verify res_bank table
DO $$
DECLARE
    null_count INTEGER;
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'res_bank') THEN
        SELECT COUNT(*) INTO null_count
        FROM res_bank 
        WHERE routing_code IS NULL OR routing_code = '';
        
        IF null_count = 0 THEN
            RAISE NOTICE '✅ res_bank verification: All routing_code fields have values';
        ELSE
            RAISE NOTICE '❌ res_bank verification: % records still have NULL/empty routing_code', null_count;
        END IF;
    END IF;
END $$;

-- Display completion message
SELECT '🎉 Database migration fix completed!' AS status;
SELECT 'You can now start Odoo without NOT NULL constraint errors.' AS message;

-- Commit all changes
COMMIT;

-- ====================================================================
-- Optional: Display summary of affected records
-- ====================================================================

-- Show sample of updated hr_employee records (if table exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'hr_employee') THEN
        RAISE NOTICE 'Sample hr_employee records:';
        -- Note: Cannot use SELECT in DO block, so we just show the notice
    END IF;
END $$;

-- Show sample of updated res_bank records (if table exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'res_bank') THEN
        RAISE NOTICE 'Sample res_bank records:';
        -- Note: Cannot use SELECT in DO block, so we just show the notice
    END IF;
END $$;

-- ====================================================================
-- Manual verification queries (run these separately if needed)
-- ====================================================================

-- Uncomment and run these queries separately to verify the results:

/*
-- Check hr_employee records
SELECT id, name, agent_id, labour_card_number, salary_card_number 
FROM hr_employee 
ORDER BY id 
LIMIT 10;

-- Check res_bank records  
SELECT id, name, routing_code 
FROM res_bank 
ORDER BY id 
LIMIT 10;

-- Count NULL values in hr_employee
SELECT 
    COUNT(*) as total_employees,
    COUNT(CASE WHEN agent_id IS NULL THEN 1 END) as null_agent_id,
    COUNT(CASE WHEN labour_card_number IS NULL OR labour_card_number = '' THEN 1 END) as null_labour_card,
    COUNT(CASE WHEN salary_card_number IS NULL OR salary_card_number = '' THEN 1 END) as null_salary_card
FROM hr_employee;

-- Count NULL values in res_bank
SELECT 
    COUNT(*) as total_banks,
    COUNT(CASE WHEN routing_code IS NULL OR routing_code = '' THEN 1 END) as null_routing_code
FROM res_bank;
*/
