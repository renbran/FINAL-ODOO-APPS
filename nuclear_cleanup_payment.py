
    # EMERGENCY Python script for immediate cleanup
    # Run this in Odoo shell: python odoo-bin shell -d your_database

    # Force uninstall if module exists
    try:
        module = env['ir.module.module'].search([('name', '=', 'payment_account_enhanced')])
        if module:
            if module.state in ['installed', 'to upgrade', 'to remove']:
                print(f"Found module in state: {module.state}")
                module.write({'state': 'to remove'})
                module.button_immediate_uninstall()
                print("Module force-uninstalled")
            module.unlink()
            print("Module record deleted")
        else:
            print("Module not found in registry")
    except Exception as e:
        print(f"Uninstall error (expected): {e}")

    # Nuclear database cleanup
    cleanup_queries = [
        "DELETE FROM ir_model_data WHERE module = 'payment_account_enhanced'",
        "DELETE FROM ir_model_data WHERE module = 'base' AND name = 'module_payment_account_enhanced'",
        "DELETE FROM ir_ui_view WHERE key LIKE 'payment_account_enhanced.%'",
        "DELETE FROM ir_attachment WHERE name LIKE '%.assets_%'",
        "DELETE FROM ir_qweb WHERE arch_db LIKE '%payment_account_enhanced%'"
    ]

    for query in cleanup_queries:
        try:
            env.cr.execute(query)
            print(f"✅ Executed: {query}")
        except Exception as e:
            print(f"❌ Failed: {query} - {e}")

    # Commit changes
    env.cr.commit()

    # Update module list
    env['ir.module.module'].update_list()
    print("🎉 NUCLEAR CLEANUP COMPLETE!")
    print("📋 Now search for 'payment_account_enhanced' and install fresh")
