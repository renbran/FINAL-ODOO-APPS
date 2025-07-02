-- Custom Fields Cleanup SQL Script for Odoo 17
-- This script fixes orphaned references that cause '_unknown' object errors
-- Run this directly in your PostgreSQL database

-- Begin transaction
BEGIN;

-- 1. Fix orphaned sale_order_type_id references in account_move
DO $$
BEGIN
    -- Check if sale_order_type table exists
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'sale_order_type') THEN
        -- Fix orphaned references by setting them to NULL
        UPDATE account_move 
        SET sale_order_type_id = NULL 
        WHERE sale_order_type_id IS NOT NULL 
        AND sale_order_type_id NOT IN (SELECT id FROM sale_order_type);
        
        RAISE NOTICE 'Fixed orphaned sale_order_type_id references in account_move';
    ELSE
        -- If table doesn't exist, set all references to NULL
        UPDATE account_move 
        SET sale_order_type_id = NULL 
        WHERE sale_order_type_id IS NOT NULL;
        
        RAISE NOTICE 'sale_order_type table does not exist, set all references to NULL';
    END IF;
END $$;

-- 2. Fix orphaned project references (product_template)
UPDATE account_move 
SET project = NULL 
WHERE project IS NOT NULL 
AND project NOT IN (SELECT id FROM product_template);

RAISE NOTICE 'Fixed orphaned project references in account_move';

-- 3. Fix orphaned unit references (product_product)
UPDATE account_move 
SET unit = NULL 
WHERE unit IS NOT NULL 
AND unit NOT IN (SELECT id FROM product_product);

RAISE NOTICE 'Fixed orphaned unit references in account_move';

-- 4. Fix orphaned buyer references (res_partner)
UPDATE account_move 
SET buyer = NULL 
WHERE buyer IS NOT NULL 
AND buyer NOT IN (SELECT id FROM res_partner);

RAISE NOTICE 'Fixed orphaned buyer references in account_move';

-- 5. Fix orphaned project_id references (alternative field name)
UPDATE account_move 
SET project_id = NULL 
WHERE project_id IS NOT NULL 
AND project_id NOT IN (SELECT id FROM product_template);

RAISE NOTICE 'Fixed orphaned project_id references in account_move';

-- 6. Fix orphaned unit_id references (alternative field name)
UPDATE account_move 
SET unit_id = NULL 
WHERE unit_id IS NOT NULL 
AND unit_id NOT IN (SELECT id FROM product_product);

RAISE NOTICE 'Fixed orphaned unit_id references in account_move';

-- 7. Fix orphaned buyer_id references (alternative field name)
UPDATE account_move 
SET buyer_id = NULL 
WHERE buyer_id IS NOT NULL 
AND buyer_id NOT IN (SELECT id FROM res_partner);

RAISE NOTICE 'Fixed orphaned buyer_id references in account_move';

-- 8. Clean up duplicate field definitions in ir_model_fields
-- This removes duplicate field definitions that can cause conflicts
DELETE FROM ir_model_fields 
WHERE model = 'account.move' 
AND name IN ('sale_order_type_id', 'project', 'unit', 'buyer', 'project_id', 'unit_id', 'buyer_id')
AND id NOT IN (
    SELECT DISTINCT first_value(id) OVER (PARTITION BY model, name ORDER BY id) 
    FROM ir_model_fields 
    WHERE model = 'account.move' 
    AND name IN ('sale_order_type_id', 'project', 'unit', 'buyer', 'project_id', 'unit_id', 'buyer_id')
);

RAISE NOTICE 'Cleaned up duplicate field definitions';

-- 9. Clean up any orphaned ir_model_data entries
DELETE FROM ir_model_data 
WHERE model = 'sale.order.type' 
AND res_id IS NOT NULL 
AND res_id NOT IN (SELECT id FROM sale_order_type WHERE id IS NOT NULL);

RAISE NOTICE 'Cleaned up orphaned ir_model_data entries';

-- 10. Update statistics to ensure the database optimizer works correctly
ANALYZE account_move;
ANALYZE sale_order_type;
ANALYZE product_template;
ANALYZE product_product;
ANALYZE res_partner;

RAISE NOTICE 'Updated table statistics';

-- Commit the transaction
COMMIT;

RAISE NOTICE 'Custom fields cleanup completed successfully!';
