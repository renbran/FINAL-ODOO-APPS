#!/bin/bash
# Fix the property.details model fields on the server

echo "=== Step 1: Check database columns ==="
sudo -u postgres psql -d scholarixv2 << 'EOSQL'
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'property_details' 
AND column_name IN ('payment_schedule_id', 'is_payment_plan', 'total_customer_obligation', 'dld_fee', 'admin_fee');
EOSQL

echo ""
echo "=== Step 2: Check ir_model_fields ==="
sudo -u postgres psql -d scholarixv2 << 'EOSQL'
SELECT name, ttype FROM ir_model_fields 
WHERE model = 'property.details' 
AND name IN ('payment_schedule_id', 'is_payment_plan', 'total_customer_obligation', 'dld_fee', 'admin_fee');
EOSQL

echo ""
echo "=== Step 3: Add missing columns if needed ==="
sudo -u postgres psql -d scholarixv2 << 'EOSQL'
-- Add payment_schedule_id if missing
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'property_details' AND column_name = 'payment_schedule_id') THEN
        ALTER TABLE property_details ADD COLUMN payment_schedule_id INTEGER;
        RAISE NOTICE 'Added payment_schedule_id column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'property_details' AND column_name = 'is_payment_plan') THEN
        ALTER TABLE property_details ADD COLUMN is_payment_plan BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added is_payment_plan column';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'property_details' AND column_name = 'total_customer_obligation') THEN
        ALTER TABLE property_details ADD COLUMN total_customer_obligation NUMERIC;
        RAISE NOTICE 'Added total_customer_obligation column';
    END IF;
END $$;
EOSQL

echo ""
echo "=== Step 4: Verify columns now exist ==="
sudo -u postgres psql -d scholarixv2 << 'EOSQL'
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'property_details' 
AND column_name IN ('payment_schedule_id', 'is_payment_plan', 'total_customer_obligation');
EOSQL
