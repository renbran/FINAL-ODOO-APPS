-- Fix crm_dashboard module installation issue
-- Delete problematic view that references non-existent in_group_146
DELETE FROM ir_ui_view WHERE id = 3996 AND name = 'res.users.view.form.inherit.crm.dashboard';

-- Check if view still exists
SELECT id, name, model FROM ir_ui_view WHERE name LIKE '%crm.dashboard%';

-- Reset module state
UPDATE ir_module_module SET state = 'to install' WHERE name = 'crm_dashboard';
