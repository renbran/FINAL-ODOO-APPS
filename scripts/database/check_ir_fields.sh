#!/bin/bash
sudo -u postgres psql -d scholarixv2 << 'EOSQL'
SELECT name, ttype, store FROM ir_model_fields 
WHERE model = 'property.details' AND name IN ('total_customer_obligation', 'dld_fee', 'admin_fee');
EOSQL
