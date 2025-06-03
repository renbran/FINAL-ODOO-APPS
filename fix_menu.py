def fix_menu(env):
    print("Checking menu structure...")
    try:
        # Clear caches properly using the recommended approach
        env.registry.clear_caches()
        
        # Check for the problematic menu ID 396
        menus = env['ir.ui.menu'].search([('id', '=', 396)])
        if not menus:
            print("Menu with ID 396 not found. It might have been deleted but references remain.")
            
            # Check if there are any menu items referencing this ID
            references = env['ir.ui.menu'].search([('parent_id', '=', 396)])
            if references:
                print(f"Found {len(references)} menu items referencing the missing menu. Fixing...")
                for menu in references:
                    menu.parent_id = False
                    print(f"Removed parent reference from menu: {menu.id} - {menu.name}")
        else:
            print(f"Menu found: {menus.name}, Action: {menus.action}")
            
            # Check if the action exists
            if menus.action:
                action_model, action_id = menus.action.split(',')
                action = env[action_model].browse(int(action_id))
                if not action.exists():
                    print(f"Action {menus.action} referenced by menu {menus.id} does not exist. Fixing...")
                    menus.action = False
                    print(f"Removed invalid action reference from menu: {menus.id} - {menus.name}")
            
        # Check for all broken menu references
        print("\nChecking all menus for broken references...")
        all_menus = env['ir.ui.menu'].search([])
        fixed_count = 0
        
        for menu in all_menus:
            # Check for broken action references
            if menu.action:
                try:
                    action_model, action_id = menu.action.split(',')
                    action = env[action_model].browse(int(action_id))
                    if not action.exists():
                        print(f"Found broken action reference: {menu.id} - {menu.name} -> {menu.action}")
                        menu.action = False
                        fixed_count += 1
                except Exception as e:
                    print(f"Error processing action for menu {menu.id} - {menu.name}: {e}")
                    menu.action = False
                    fixed_count += 1
            
            # Check for broken parent references
            if menu.parent_id and not menu.parent_id.exists():
                print(f"Found broken parent reference: {menu.id} - {menu.name}")
                menu.parent_id = False
                fixed_count += 1
        
        # Rebuild menu structure
        env['ir.ui.menu'].load_menus(env.context.get('lang'))
        
        print(f"\nMenu check completed. Fixed {fixed_count} issues.")
        
        # Commit changes if any fixes were made
        if fixed_count > 0:
            env.cr.commit()
            print("Changes committed to database.")
            
        return True
    except Exception as e:
        print(f"Error during menu check: {e}")
        return False