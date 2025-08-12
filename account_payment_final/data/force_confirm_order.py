from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

def force_confirm_exclusive_sales_orders(env):
    """
    Force confirm sales orders based on specified criteria:
    - Sales type = exclusive sales (via sale_order_type_id)
    - Created in 2024 until May 31, 2025 (based on booking_date)
    - State = draft or sent (quotation)
    - agent1_partner_id is set
    """
    
    try:
        # Define the date range
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2025, 5, 31, 23, 59, 59)
        
        # Search for sales orders matching the criteria
        domain = [
            ('sale_order_type_id.name', '=', 'exclusive_sales'),  # Sales type field
            ('booking_date', '>=', start_date),
            ('booking_date', '<=', end_date),
            ('state', 'in', ['draft', 'sent']),  # draft or quotation stage
            ('agent1_partner_id', '!=', False),   # agent1_partner_id is set
        ]
        
        # Get the sales order model
        SaleOrder = env['sale.order']
        
        # Search for matching records
        orders_to_confirm = SaleOrder.search(domain)
        
        print(f"Found {len(orders_to_confirm)} sales orders matching criteria")
        
        confirmed_orders = []
        failed_orders = []
        
        # Process each order
        for order in orders_to_confirm:
            try:
                print(f"Processing order {order.name} (ID: {order.id})")
                
                # Force confirm the order
                if order.state == 'draft':
                    # If in draft, first send quotation then confirm
                    order.action_quotation_send()
                
                # Confirm the order (convert to sales order)
                order.action_confirm()
                
                confirmed_orders.append({
                    'id': order.id,
                    'name': order.name,
                    'partner': order.partner_id.name,
                    'amount': order.amount_total,
                    'agent': order.agent1_partner_id.name if order.agent1_partner_id else 'N/A'
                })
                
                print(f"Successfully confirmed order {order.name}")
                
            except Exception as e:
                print(f"Failed to confirm order {order.name}: {str(e)}")
                failed_orders.append({
                    'id': order.id,
                    'name': order.name,
                    'error': str(e)
                })
        
        # Log summary
        print(f"Confirmation complete: {len(confirmed_orders)} successful, {len(failed_orders)} failed")
        
        return {
            'total_found': len(orders_to_confirm),
            'confirmed': confirmed_orders,
            'failed': failed_orders,
            'success_count': len(confirmed_orders),
            'failure_count': len(failed_orders)
        }
        
    except Exception as e:
        print(f"Error in force_confirm_exclusive_sales_orders: {str(e)}")
        raise


# Alternative method using SQL query for better performance with large datasets
def force_confirm_exclusive_sales_orders_sql(env):
    """
    SQL-based approach for better performance with large datasets
    """
    
    try:
        cr = env.cr
        
        # SQL query to find matching orders
        query = """
            SELECT so.id, so.name, so.partner_id, so.amount_total
            FROM sale_order so
            JOIN sale_order_type sot ON so.sale_order_type_id = sot.id
            WHERE sot.name = 'exclusive_sales'
                AND so.booking_date >= '2024-01-01'
                AND so.booking_date <= '2025-05-31 23:59:59'
                AND so.state IN ('draft', 'sent')
                AND so.agent1_partner_id IS NOT NULL
        """
        
        cr.execute(query)
        order_data = cr.fetchall()
        
        print(f"Found {len(order_data)} orders via SQL query")
        
        # Get the actual record objects
        order_ids = [row[0] for row in order_data]
        orders = env['sale.order'].browse(order_ids)
        
        # Process each order (same logic as above)
        confirmed_orders = []
        failed_orders = []
        
        for order in orders:
            try:
                if order.state == 'draft':
                    order.action_quotation_send()
                order.action_confirm()
                
                confirmed_orders.append({
                    'id': order.id,
                    'name': order.name,
                    'partner': order.partner_id.name,
                    'amount': order.amount_total
                })
                
            except Exception as e:
                failed_orders.append({
                    'id': order.id,
                    'name': order.name,
                    'error': str(e)
                })
        
        return {
            'total_found': len(order_data),
            'confirmed': confirmed_orders,
            'failed': failed_orders,
            'success_count': len(confirmed_orders),
            'failure_count': len(failed_orders)
        }
        
    except Exception as e:
        print(f"Error in SQL-based confirmation: {str(e)}")
        raise


# Method to run from Odoo shell
def run_sales_order_confirmation(env):
    """
    Main function to execute the sales order confirmation
    This function accepts env as parameter for shell execution
    """
    
    try:
        # Method 1: Standard search and process
        result = force_confirm_exclusive_sales_orders(env)
        
        print("=" * 50)
        print("SALES ORDER CONFIRMATION RESULTS")
        print("=" * 50)
        print(f"Total orders found: {result['total_found']}")
        print(f"Successfully confirmed: {result['success_count']}")
        print(f"Failed confirmations: {result['failure_count']}")
        
        if result['confirmed']:
            print("\nConfirmed Orders:")
            for order in result['confirmed']:
                print(f"  - {order['name']} | {order['partner']} | ${order['amount']:.2f}")
        
        if result['failed']:
            print("\nFailed Orders:")
            for order in result['failed']:
                print(f"  - {order['name']}: {order['error']}")
        
        return result
        
    except Exception as e:
        print(f"Error executing script: {str(e)}")
        raise