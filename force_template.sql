UPDATE report_paperformat SET margin_top=75, margin_bottom=30, header_spacing=65, dpi=96 WHERE name='OSUS Standard A4';
UPDATE res_company SET external_report_layout_id=(SELECT id FROM ir_ui_view WHERE key='web.external_layout_standard' LIMIT 1);
DELETE FROM ir_attachment WHERE res_model='ir.ui.view' AND name LIKE '%report%';
SELECT 'Template forced successfully!' as status;
