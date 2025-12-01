#!/bin/bash
cd /var/odoo/scholarixv2

# Check model ID for property.details
sudo -u postgres psql -d scholarixv2 << 'EOSQL'
-- Get the model ID
SELECT id, model FROM ir_model WHERE model = 'property.details';

-- Check if field exists with correct model_id
SELECT f.id, f.name, f.model_id, m.model 
FROM ir_model_fields f 
JOIN ir_model m ON f.model_id = m.id
WHERE f.name = 'total_customer_obligation' AND m.model = 'property.details';
EOSQL
