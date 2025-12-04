-- Commission AX Database Migration
-- Add missing commission_id column to account_move table
-- Run this on CloudPepper PostgreSQL database

-- Check if column exists first
DO $$
BEGIN
    -- Check if commission_id column exists
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name='account_move' 
        AND column_name='commission_id'
    ) THEN
        -- Add the column
        ALTER TABLE account_move 
        ADD COLUMN commission_id INTEGER;
        
        RAISE NOTICE 'Added commission_id column to account_move table';
        
        -- Add foreign key constraint
        ALTER TABLE account_move 
        ADD CONSTRAINT account_move_commission_id_fkey 
        FOREIGN KEY (commission_id) 
        REFERENCES commission_ax(id) 
        ON DELETE SET NULL;
        
        RAISE NOTICE 'Added foreign key constraint';
        
        -- Create index for better performance
        CREATE INDEX account_move_commission_id_index 
        ON account_move(commission_id);
        
        RAISE NOTICE 'Created index on commission_id';
        RAISE NOTICE 'Migration completed successfully!';
    ELSE
        RAISE NOTICE 'Column commission_id already exists in account_move table';
    END IF;
END $$;
