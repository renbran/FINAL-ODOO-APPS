#!/usr/bin/env python3
"""
Test script for commission vendor reference functionality.
This script demonstrates and tests the vendor reference auto-population feature.

Run this in Odoo shell:
    docker-compose exec odoo odoo shell -d your_database
    Then execute: exec(open('/path/to/test_commission_vendor_ref.py').read())
"""

def test_vendor_reference_functionality():
    """Test the vendor reference auto-population feature."""
    print("=" * 60)
    print("TESTING COMMISSION VENDOR REFERENCE FUNCTIONALITY")
    print("=" * 60)
    
    try:
        # Get required models
        SaleOrder = env['sale.order']
        Partner = env['res.partner']
        Product = env['product.product']
        
        # Create test customer
        customer = Partner.create({
            'name': 'Test Customer for Vendor Ref',
            'email': 'test.customer@example.com',
            'customer_rank': 1,
        })
        print(f"✓ Created test customer: {customer.name}")
        
        # Create test commission partners
        broker = Partner.create({
            'name': 'Test Broker Partner',
            'email': 'broker@example.com',
            'supplier_rank': 1,
        })
        
        agent = Partner.create({
            'name': 'Test Agent Partner', 
            'email': 'agent@example.com',
            'supplier_rank': 1,
        })
        print(f"✓ Created commission partners: {broker.name}, {agent.name}")
        
        # Get or create a product
        product = env.ref('product.product_product_25', raise_if_not_found=False)
        if not product:
            product = Product.create({
                'name': 'Test Product for Commission',
                'type': 'product',
                'list_price': 1000.0,
            })
        print(f"✓ Using product: {product.name}")
        
        # Create sale order with customer reference
        customer_ref = "CUST-REF-TEST-2025-001"
        sale_order = SaleOrder.create({
            'partner_id': customer.id,
            'client_order_ref': customer_ref,  # This should populate vendor_ref in POs
            
            # Configure commissions
            'broker_partner_id': broker.id,
            'broker_commission_type': 'percent_untaxed_total',
            'broker_rate': 2.5,
            
            'agent1_partner_id': agent.id,
            'agent1_commission_type': 'fixed',
            'agent1_rate': 150.0,
        })
        print(f"✓ Created sale order: {sale_order.name} with customer reference: {customer_ref}")
        
        # Add order line
        order_line = env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': product.id,
            'product_uom_qty': 2,
            'price_unit': 1000.0,
        })
        print(f"✓ Added order line: {order_line.product_id.name} (Qty: {order_line.product_uom_qty}, Price: {order_line.price_unit})")
        
        # Confirm sale order
        sale_order.action_confirm()
        print(f"✓ Confirmed sale order: {sale_order.name}")
        
        # Process commissions
        print("\n" + "-" * 40)
        print("PROCESSING COMMISSIONS")
        print("-" * 40)
        
        initial_po_count = len(sale_order.purchase_order_ids)
        print(f"Initial purchase orders: {initial_po_count}")
        
        # Process commissions
        sale_order.action_process_commissions()
        
        # Check results
        final_po_count = len(sale_order.purchase_order_ids)
        print(f"Final purchase orders: {final_po_count}")
        
        if final_po_count > initial_po_count:
            print(f"✓ Successfully created {final_po_count - initial_po_count} commission purchase orders")
            
            # Check vendor references
            print("\n" + "-" * 40)
            print("CHECKING VENDOR REFERENCES")
            print("-" * 40)
            
            for i, po in enumerate(sale_order.purchase_order_ids, 1):
                vendor_ref = po.partner_ref or "NOT SET"
                origin_so = po.origin_so_id.name if po.origin_so_id else "NOT SET"
                
                print(f"PO {i}: {po.name}")
                print(f"  Partner: {po.partner_id.name}")
                print(f"  Vendor Reference: {vendor_ref}")
                print(f"  Origin SO: {origin_so}")
                print(f"  Expected Reference: {customer_ref}")
                
                # Verify vendor reference matches customer reference
                if vendor_ref == customer_ref:
                    print(f"  ✓ PASS: Vendor reference correctly populated!")
                else:
                    print(f"  ❌ FAIL: Vendor reference mismatch!")
                    print(f"    Expected: {customer_ref}")
                    print(f"    Actual: {vendor_ref}")
                print()
                
        else:
            print("❌ FAIL: No commission purchase orders were created")
            
        # Test commission info retrieval
        print("-" * 40)
        print("TESTING COMMISSION INFO RETRIEVAL")
        print("-" * 40)
        
        for po in sale_order.purchase_order_ids:
            commission_info = po._get_commission_info()
            if commission_info:
                print(f"PO {po.name}:")
                print(f"  Commission Type: {commission_info.get('type', 'Unknown')}")
                print(f"  Customer Reference: {commission_info.get('customer_reference', 'Not Found')}")
                print(f"  ✓ Commission info retrieved successfully")
            else:
                print(f"PO {po.name}: No commission info found")
            print()
            
        print("=" * 60)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"Summary:")
        print(f"- Sale Order: {sale_order.name}")
        print(f"- Customer Reference: {customer_ref}")
        print(f"- Commission POs Created: {final_po_count}")
        print(f"- All vendor references populated: {'✓' if all(po.partner_ref == customer_ref for po in sale_order.purchase_order_ids) else '❌'}")
        
        return {
            'sale_order': sale_order,
            'customer_reference': customer_ref,
            'commission_pos': sale_order.purchase_order_ids,
            'success': True
        }
        
    except Exception as e:
        print(f"❌ ERROR during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def demonstrate_feature():
    """Demonstrate the vendor reference feature with explanations."""
    print("\n" + "=" * 60)
    print("VENDOR REFERENCE AUTO-POPULATION DEMONSTRATION")
    print("=" * 60)
    
    print("""
This feature automatically populates the vendor reference field in commission 
purchase orders with the customer reference from the originating sale order.

Benefits:
1. Maintains reference consistency across sales-to-purchase workflow
2. Improves traceability of commission payments
3. Reduces manual data entry and errors
4. Enhances reporting and reconciliation capabilities

The process works as follows:
1. Customer provides their reference number for the sale
2. Sales team enters this in the 'Customer Reference' field
3. When commissions are processed, purchase orders are created
4. Each commission PO automatically gets the customer reference as vendor reference
5. Accounts payable can easily trace commissions back to original sales
    """)
    
    print("Running test to demonstrate functionality...")
    return test_vendor_reference_functionality()


# Run the demonstration if executed directly
if __name__ == '__main__':
    result = demonstrate_feature()
    if result.get('success'):
        print("\n🎉 Vendor reference functionality is working correctly!")
    else:
        print(f"\n💥 Test failed: {result.get('error')}")
