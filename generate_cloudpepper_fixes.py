#!/usr/bin/env python3
"""
CloudPepper Error Fix Generator
Generates commands to fix CloudPepper system errors
"""

def generate_cloudpepper_fixes():
    """
    Generate fix commands for CloudPepper deployment issues
    """
    
    print("🔧 CloudPepper System Error Fixes")
    print("=" * 60)
    
    print("\n📋 Error Analysis:")
    print("1. Tax Report Vacuum Error - kit.account.tax.report deletion issue")
    print("2. Custom Background Font Error - Missing T1 font files")
    print("3. Autovacuum Issues - Transient model cleanup problems")
    
    print("\n🛠️ CloudPepper Command Line Fixes:")
    print("=" * 40)
    
    print("\n# Fix 1: Disable problematic autovacuum for tax reports")
    print("# Run in Odoo shell on CloudPepper:")
    print("python3 -c \"")
    print("import odoo")
    print("from odoo import api, SUPERUSER_ID")
    print("with api.Environment.manage():")
    print("    with api.Environment(api.Registry('stagingtry'), SUPERUSER_ID, {}) as env:")
    print("        # Disable autovacuum for problematic models")
    print("        env['ir.config_parameter'].sudo().set_param('base.autovacuum_kit_account_tax_report', 'False')")
    print("        # Remove problematic tax reports")
    print("        reports = env['account.report'].sudo().search([('model', '=', 'kit.account.tax.report')])")
    print("        for report in reports:")
    print("            try:")
    print("                variants = env['account.report'].sudo().search([('parent_id', '=', report.id)])")
    print("                variants.sudo().unlink()")
    print("                report.sudo().unlink()")
    print("            except:")
    print("                pass")
    print("        env.cr.commit()")
    print("        print('Tax report vacuum fix applied')")
    print("\"")
    
    print("\n# Fix 2: Disable custom_background module")
    print("# Run in Odoo shell on CloudPepper:")
    print("python3 -c \"")
    print("import odoo")
    print("from odoo import api, SUPERUSER_ID")
    print("with api.Environment.manage():")
    print("    with api.Environment(api.Registry('stagingtry'), SUPERUSER_ID, {}) as env:")
    print("        module = env['ir.module.module'].sudo().search([('name', '=', 'custom_background')])")
    print("        if module and module.state == 'installed':")
    print("            module.button_immediate_uninstall()")
    print("            print('Custom background module uninstalled')")
    print("        env.cr.commit()")
    print("\"")
    
    print("\n# Fix 3: Clean up transient models")
    print("# Run in Odoo shell on CloudPepper:")
    print("python3 -c \"")
    print("import odoo")
    print("from odoo import api, SUPERUSER_ID")
    print("with api.Environment.manage():")
    print("    with api.Environment(api.Registry('stagingtry'), SUPERUSER_ID, {}) as env:")
    print("        # Force cleanup of transient models")
    print("        for model_name in ['kit.account.tax.report', 'account.report.wizard']:")
    print("            try:")
    print("                if model_name in env.registry:")
    print("                    model = env[model_name].sudo()")
    print("                    if hasattr(model, '_transient_clean_rows_older_than'):")
    print("                        model._transient_clean_rows_older_than(3600)")
    print("            except:")
    print("                pass")
    print("        env.cr.commit()")
    print("        print('Transient models cleaned')")
    print("\"")
    
    print("\n🗃️ Alternative: SQL Database Fix")
    print("=" * 40)
    print("If shell access is limited, run the SQL file:")
    print("psql -d stagingtry -f cloudpepper_system_fix.sql")
    
    print("\n✅ After Applying Fixes:")
    print("=" * 40)
    print("1. Restart Odoo service: sudo systemctl restart odoo")
    print("2. Check logs: tail -f /var/log/odoo/odoo.log")
    print("3. Install account_payment_final module")
    print("4. Verify no more vacuum errors in logs")
    
    print("\n🎯 Expected Results:")
    print("✅ No more tax report vacuum errors")
    print("✅ No more custom_background font errors")  
    print("✅ Clean autovacuum operations")
    print("✅ Successful account_payment_final installation")

def check_system_status():
    """
    Generate commands to check system status
    """
    print("\n🔍 System Status Check Commands:")
    print("=" * 40)
    
    print("\n# Check for problematic modules:")
    print("SELECT name, state FROM ir_module_module WHERE name IN ('custom_background', 'kit_account_tax_report');")
    
    print("\n# Check autovacuum configuration:")
    print("SELECT key, value FROM ir_config_parameter WHERE key LIKE '%autovacuum%';")
    
    print("\n# Check for tax report issues:")
    print("SELECT count(*) FROM account_report WHERE model = 'kit.account.tax.report';")
    
    print("\n# Check recent errors in logs:")
    print("tail -n 100 /var/log/odoo/odoo.log | grep -E '(ERROR|CRITICAL)'")

if __name__ == "__main__":
    generate_cloudpepper_fixes()
    check_system_status()
    
    print("\n" + "=" * 60)
    print("🚀 CloudPepper Fix Commands Generated!")
    print("Copy and run the appropriate commands on your CloudPepper instance.")
    print("=" * 60)
