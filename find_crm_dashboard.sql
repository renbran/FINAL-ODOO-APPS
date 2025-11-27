-- Find all CRM dashboard related modules
SELECT name, state, latest_version 
FROM ir_module_module 
WHERE name LIKE '%crm%dashboard%' OR name LIKE '%dashboard%crm%'
ORDER BY name;

-- Check for odoo_crm_dashboard specifically
SELECT name, state, latest_version 
FROM ir_module_module 
WHERE name = 'odoo_crm_dashboard';
