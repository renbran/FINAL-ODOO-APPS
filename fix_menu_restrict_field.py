#!/usr/bin/env python3
"""
Fix for ir.ui.menu restrict_user_ids field issue

This script helps resolve the "Invalid field ir.ui.menu.restrict_user_ids" error
by providing several solution approaches.
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

def create_database_fix_sql():
    """Create SQL script to manually add the missing field"""
    sql_content = """-- Fix for ir.ui.menu restrict_user_ids field
-- Run this in your PostgreSQL database

-- Check if table exists and add column if missing
DO $$
BEGIN
    -- Add restrict_user_ids column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'ir_ui_menu' AND column_name = 'restrict_user_ids'
    ) THEN
        -- This would be done by Odoo automatically, but we can't add it manually
        -- as it's a Many2many field requiring a bridge table
        RAISE NOTICE 'restrict_user_ids field missing - need to fix via Odoo module upgrade';
    END IF;
END
$$;

-- Temporarily disable the security rule to prevent the error
UPDATE ir_rule 
SET active = false 
WHERE name = 'Restrict Menu from Users' 
  AND model_id = (SELECT id FROM ir_model WHERE model = 'ir.ui.menu');

-- Commit the changes
COMMIT;

RAISE NOTICE 'Security rule disabled. Now upgrade the hide_menu_user module in Odoo.';
"""
    
    with open('fix_menu_restrict_field.sql', 'w') as f:
        f.write(sql_content)
    
    print("Created fix_menu_restrict_field.sql")
    print("Run this SQL script in your PostgreSQL database to disable the problematic rule temporarily.")

def create_temporary_fix_module():
    """Create a temporary fix module to disable the problematic security rule"""
    
    # Create module directory
    fix_module_dir = Path('menu_restrict_fix')
    fix_module_dir.mkdir(exist_ok=True)
    
    # Create __manifest__.py
    manifest_content = '''# -*- coding: utf-8 -*-
{
    'name': 'Menu Restrict Field Fix',
    'version': '17.0.1.0.0',
    'category': 'Base',
    'summary': 'Fix for restrict_user_ids field error in ir.ui.menu',
    'description': """
This module temporarily fixes the restrict_user_ids field error by:
1. Disabling the problematic security rule
2. Ensuring the field is properly created
    """,
    'author': 'System Fix',
    'depends': ['base'],
    'data': [
        'data/fix_security.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
'''
    
    with open(fix_module_dir / '__manifest__.py', 'w') as f:
        f.write(manifest_content)
    
    # Create __init__.py
    with open(fix_module_dir / '__init__.py', 'w') as f:
        f.write('# -*- coding: utf-8 -*-\n')
    
    # Create data directory
    data_dir = fix_module_dir / 'data'
    data_dir.mkdir(exist_ok=True)
    
    # Create fix security XML
    security_fix_content = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Disable the problematic security rule -->
    <record id="hide_menu_user.ir_ui_menu_rule_user" model="ir.rule">
        <field name="active" eval="False"/>
    </record>
</odoo>
'''
    
    with open(data_dir / 'fix_security.xml', 'w') as f:
        f.write(security_fix_content)
    
    print(f"Created temporary fix module in {fix_module_dir}/")
    print("Install this module in Odoo to temporarily disable the problematic security rule.")

def provide_solutions():
    """Provide step-by-step solutions"""
    print("\n=== SOLUTIONS FOR ir.ui.menu restrict_user_ids ERROR ===\n")
    
    print("SOLUTION 1: Quick Fix (Recommended)")
    print("-" * 40)
    print("1. Go to Odoo Apps")
    print("2. Search for 'hide_menu_user'")
    print("3. Uninstall the module completely")
    print("4. Restart Odoo server")
    print("5. If needed, reinstall the module from a clean state")
    
    print("\nSOLUTION 2: Database Fix")
    print("-" * 25)
    print("1. Run the generated SQL script: fix_menu_restrict_field.sql")
    print("2. Go to Odoo Settings > General Settings")
    print("3. Enable Developer Mode")
    print("4. Go to Apps > Update Apps List")
    print("5. Find 'hide_menu_user' module")
    print("6. Click 'Upgrade' to properly install the field")
    
    print("\nSOLUTION 3: Module Fix")
    print("-" * 20)
    print("1. Install the temporary fix module: menu_restrict_fix")
    print("2. This will disable the problematic security rule")
    print("3. Then upgrade the hide_menu_user module")
    print("4. Uninstall the temporary fix module")
    
    print("\nSOLUTION 4: Developer Mode Fix")
    print("-" * 30)
    print("1. Enable Developer Mode in Odoo")
    print("2. Go to Settings > Technical > Security > Record Rules")
    print("3. Search for 'Restrict Menu from Users'")
    print("4. Disable or delete this rule")
    print("5. Upgrade the hide_menu_user module")
    
    print("\nSOLUTION 5: Complete Removal")
    print("-" * 27)
    print("If hide_menu_user is not essential:")
    print("1. Remove it from auto-install modules")
    print("2. Uninstall it completely")
    print("3. Remove the module folder")
    print("4. Restart Odoo")

def main():
    """Main execution function"""
    print("Analyzing ir.ui.menu restrict_user_ids field issue...")
    
    # Check if hide_menu_user module exists
    hide_menu_paths = [
        Path('hide_menu_user'),
        Path('custom/hide_menu_user')
    ]
    
    found_modules = [p for p in hide_menu_paths if p.exists()]
    
    if found_modules:
        print(f"\nFound hide_menu_user module(s) at: {[str(p) for p in found_modules]}")
        print("This module adds restrict_user_ids field to ir.ui.menu")
    else:
        print("\nhide_menu_user module not found in current directory")
    
    # Create fix files
    create_database_fix_sql()
    create_temporary_fix_module()
    
    # Provide solutions
    provide_solutions()
    
    print("\n=== IMMEDIATE ACTION REQUIRED ===")
    print("The error is preventing Odoo from loading properly.")
    print("Choose one of the solutions above to fix it quickly.")
    print("\nMost reliable quick fix:")
    print("1. Access Odoo database directly")
    print("2. Run: UPDATE ir_rule SET active=false WHERE name='Restrict Menu from Users';")
    print("3. Restart Odoo")
    print("4. Then properly upgrade or uninstall hide_menu_user module")

if __name__ == '__main__':
    main()
