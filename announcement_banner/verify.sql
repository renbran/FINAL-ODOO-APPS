-- Verification SQL script for announcement_banner module
\echo '===================================================================='
\echo 'MODULE STATUS CHECK'
\echo '===================================================================='
SELECT 
    name as "Module Name",
    state as "State",
    latest_version as "Version"
FROM ir_module_module 
WHERE name='announcement_banner';

\echo ''
\echo '===================================================================='
\echo 'VIEW ANALYSIS - Priority Widget Check'
\echo '===================================================================='
SELECT 
    name as "View Name",
    type as "Type",
    id as "View ID",
    CASE 
        WHEN arch_db::text LIKE '%widget="priority"%' THEN '❌ HAS WIDGET - NEEDS FIX'
        ELSE '✅ NO WIDGET - FIXED'
    END as "Priority Widget Status"
FROM ir_ui_view 
WHERE model='announcement.banner' 
ORDER BY type;

\echo ''
\echo '===================================================================='
\echo 'ACTIVE ANNOUNCEMENTS'
\echo '===================================================================='
SELECT 
    id as "ID",
    name as "Title",
    priority as "Priority",
    active as "Active",
    show_once as "Show Once"
FROM announcement_banner 
WHERE active=true 
ORDER BY priority DESC 
LIMIT 10;

\echo ''
\echo '===================================================================='
\echo 'VERIFICATION SUMMARY'
\echo '===================================================================='
\echo 'If Priority Widget Status shows "✅ NO WIDGET - FIXED", the console'
\echo 'error should be resolved. Test in browser:'
\echo '  1. Clear cache (Ctrl+Shift+Delete)'
\echo '  2. Login to https://stagingtry.cloudpepper.site/ (scholarixv2)'
\echo '  3. Open console (F12) and check for errors'
\echo '===================================================================='
