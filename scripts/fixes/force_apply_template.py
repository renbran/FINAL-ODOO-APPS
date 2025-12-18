#!/usr/bin/env python3
"""
Force apply OSUS report header/footer template
This script directly updates the database to ensure the template is used
"""

SQL_COMMANDS = """
-- Force update all companies to use the OSUS external layout
UPDATE res_company 
SET external_report_layout_id = (
    SELECT id FROM ir_ui_view 
    WHERE key = 'web.external_layout_standard' 
    LIMIT 1
)
WHERE id IS NOT NULL;

-- Update paper format to be more compact for single page
UPDATE report_paperformat 
SET 
    margin_top = 75,
    margin_bottom = 30,
    header_spacing = 65,
    dpi = 96
WHERE name = 'OSUS Standard A4';

-- Clear any cached report data
DELETE FROM ir_attachment WHERE res_model = 'ir.ui.view' AND name LIKE '%report%';

-- Verify the updates
SELECT 
    c.name as company_name,
    v.key as external_layout_key,
    pf.name as paper_format_name,
    pf.margin_top, pf.margin_bottom, pf.header_spacing
FROM res_company c
LEFT JOIN ir_ui_view v ON c.external_report_layout_id = v.id
LEFT JOIN report_paperformat pf ON c.paperformat_id = pf.id;
"""

print("=" * 80)
print("SQL COMMANDS TO FORCE APPLY OSUS TEMPLATE")
print("=" * 80)
print("\nRun these commands in PostgreSQL to force apply the template:\n")
print("ssh root@139.84.163.11")
print('su - postgres -c "psql osusproperties"')
print("\nThen execute:\n")
print(SQL_COMMANDS)
print("\n" + "=" * 80)
