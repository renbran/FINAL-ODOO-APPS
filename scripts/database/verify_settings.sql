SELECT c.name as company, v.key as layout, pf.name as format, pf.margin_top, pf.margin_bottom, pf.header_spacing 
FROM res_company c 
LEFT JOIN ir_ui_view v ON c.external_report_layout_id=v.id 
LEFT JOIN report_paperformat pf ON c.paperformat_id=pf.id;
