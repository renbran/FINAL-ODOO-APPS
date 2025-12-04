-- Check OSUS template status
SELECT 
    v.id,
    v.name,
    v.key,
    v.active,
    v.mode,
    v.priority,
    v.inherit_id,
    parent.key as parent_key
FROM ir_ui_view v
LEFT JOIN ir_ui_view parent ON v.inherit_id = parent.id
WHERE v.key LIKE '%osus%' OR v.name LIKE '%OSUS%'
ORDER BY v.priority DESC;

-- Check if there are other views inheriting web.external_layout_standard
SELECT 
    v.id,
    v.name,
    v.key,
    v.priority,
    v.active,
    v.mode
FROM ir_ui_view v
WHERE v.inherit_id = (SELECT id FROM ir_ui_view WHERE key = 'web.external_layout_standard' LIMIT 1)
ORDER BY v.priority DESC
LIMIT 20;

-- Check company's external_report_layout_id
SELECT 
    c.name as company_name,
    c.external_report_layout_id,
    v.key as layout_key,
    v.name as layout_name
FROM res_company c
LEFT JOIN ir_ui_view v ON c.external_report_layout_id = v.id
WHERE c.id = 1;
