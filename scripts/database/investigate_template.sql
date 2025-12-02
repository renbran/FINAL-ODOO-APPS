-- Check all views inheriting external_layout_standard
SELECT v.id, v.name, v.key, v.priority, v.active, v.mode
FROM ir_ui_view v
WHERE v.inherit_id = 202
ORDER BY v.priority DESC;

-- Check if there are other report layouts with higher priority
SELECT v.id, v.name, v.key, v.priority, v.active
FROM ir_ui_view v
WHERE v.key LIKE '%external_layout%'
ORDER BY v.priority DESC;

-- Check company's report layout setting
SELECT c.id, c.name, c.external_report_layout_id, v.key, v.name
FROM res_company c
LEFT JOIN ir_ui_view v ON c.external_report_layout_id = v.id;

-- Check if invoice_report_for_realestate module has conflicting templates
SELECT v.id, v.name, v.key, v.priority, v.active
FROM ir_ui_view v
WHERE v.key LIKE '%osus%' AND v.key LIKE '%invoice%'
ORDER BY v.priority DESC;
