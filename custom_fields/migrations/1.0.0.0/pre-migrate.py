def migrate(cr, version):
    """Pre-migration cleanup script"""
    # Remove problematic views that might cause conflicts
    cr.execute("""
        DELETE FROM ir_ui_view 
        WHERE name = 'account.move.form.inherit.sale.order.type'
        OR arch_db LIKE '%additional_group%'
        OR arch_db LIKE '%custom_account_move%'
    """)
    
    # Clear view cache
    cr.execute("DELETE FROM ir_model_data WHERE name LIKE '%custom_account_move%'")
    
    # Commit the changes
    cr.commit()
