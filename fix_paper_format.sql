-- Update invoice report to use OSUS paper format
UPDATE ir_act_report_xml 
SET paperformat_id = (SELECT id FROM report_paperformat WHERE name = 'OSUS Standard A4' LIMIT 1)
WHERE report_name LIKE '%osus%invoice%';

-- Check current paper formats being used
SELECT 
    r.id,
    r.name,
    r.report_name,
    pf.name as paper_format,
    pf.margin_top,
    pf.margin_bottom,
    pf.header_spacing
FROM ir_act_report_xml r
LEFT JOIN report_paperformat pf ON r.paperformat_id = pf.id
WHERE r.report_name LIKE '%osus%'
ORDER BY r.id;

-- Verify OSUS paper format settings
SELECT id, name, margin_top, margin_bottom, header_spacing, dpi 
FROM report_paperformat 
WHERE name = 'OSUS Standard A4';
