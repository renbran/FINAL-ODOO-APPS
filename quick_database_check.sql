-- Quick Database Check for payment_account_enhanced
-- Run this in PostgreSQL: sudo -u postgres psql testerp

-- Check if any old views still exist
SELECT 'Old payment views still in database:' as status, COUNT(*) as count 
FROM ir_ui_view 
WHERE arch_db LIKE '%payment_account_enhanced%' 
   OR arch_db LIKE '%osus_backend.css%'
   OR arch_db LIKE '%osus_report.css%'
   OR arch_db LIKE '%payment_statusbar.js%';

-- Check web.assets_backend status
SELECT 'web.assets_backend exists:' as status, COUNT(*) as count 
FROM ir_model_data 
WHERE module = 'web' AND name = 'assets_backend';

-- Check for any payment_account_enhanced module records
SELECT 'payment_account_enhanced records:' as status, COUNT(*) as count 
FROM ir_model_data 
WHERE module = 'payment_account_enhanced';

-- If you see:
-- Old payment views: > 0  --> RUN NUCLEAR FIX
-- web.assets_backend: 0   --> RUN NUCLEAR FIX  
-- payment records: > 0    --> RUN NUCLEAR FIX
