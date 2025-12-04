#!/bin/bash
sudo -u postgres psql -d scholarixv2 << 'EOSQL'
SELECT id, key, type FROM ir_ui_view WHERE key ILIKE '%sales_offer%';
EOSQL
