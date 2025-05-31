def fix_menu(env):
    print("Checking menu structure...")
    try:
        menus = env['ir.ui.menu'].search([('id', '=', 396)])
        if not menus:
            print("Menu with ID 396 not found. It might have been deleted but references remain.")
        else:
            print(f"Menu found: {menus.name}, Action: {menus.action}")
            
        # Check if there are any broken menu references
        all_menus = env['ir.ui.menu'].search([])
        for menu in all_menus:
            if menu.action and not env['ir.actions.act_window'].browse(int(menu.action.split(',')[1])).exists():
                print(f"Found broken menu reference: {menu.id} - {menu.name}")
                
        print("Menu check completed.")
    except Exception as e:
        print(f"Error during menu check: {e}")
    
    return True