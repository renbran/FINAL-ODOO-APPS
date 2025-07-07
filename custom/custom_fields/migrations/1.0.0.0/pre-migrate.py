def migrate(cr, version):
    """
    Pre-migration script to clean up problematic views
    """
    import logging
    _logger = logging.getLogger(__name__)
    
    _logger.info("Starting pre-migration cleanup for custom_fields module")
    
    try:
        # Delete problematic views by name
        cr.execute("""
            DELETE FROM ir_ui_view 
            WHERE name = 'account.move.form.inherit.sale.order.type'
            OR name ILIKE '%sale.order.type%'
            OR arch_db LIKE '%additional_group%'
            OR arch_db LIKE '%custom_account_move%'
        """)
        _logger.info("Deleted problematic views")
        
        # Clean up external ID records
        cr.execute("""
            DELETE FROM ir_model_data 
            WHERE name = 'view_move_form_inherit_sale_order_type'
            OR name LIKE '%custom_account_move%'
            OR name ILIKE '%sale_order_type%'
        """)
        _logger.info("Cleaned up external ID records")
        
        # Commit the changes
        cr.commit()
        _logger.info("Pre-migration cleanup completed successfully")
        
    except Exception as e:
        _logger.warning("Error during pre-migration cleanup: %s", str(e))
        # Don't fail the migration for cleanup errors
        pass
