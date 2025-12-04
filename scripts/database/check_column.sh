#!/bin/bash
sudo -u postgres psql -d scholarixv2 << 'EOSQL'
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'property_details' AND column_name LIKE '%total_customer%';
EOSQL
