#!/usr/bin/env python3
"""
Test Commission Report via XML-RPC
"""
import xmlrpc.client
import base64
import os

url = "http://127.0.0.1:3000"
db = "osusproperties"
username = "salescompliance@osusproperties.com"
password = "OsUs@2025"

print("="*60)
print("COMMISSION REPORT TESTING")
print("="*60)

# Authenticate
common = xmlrpc.client.ServerProxy("{}/xmlrpc/2/common".format(url))
uid = common.authenticate(db, username, password, {})
print(f"Authenticated as UID: {uid}")

if uid:
    models = xmlrpc.client.ServerProxy("{}/xmlrpc/2/object".format(url))
    report = xmlrpc.client.ServerProxy("{}/xmlrpc/2/report".format(url))
    
    # Check commission_ax module status
    modules = models.execute_kw(db, uid, password, "ir.module.module", "search_read",
        [[("name", "=", "commission_ax")]], 
        {"fields": ["name", "state", "installed_version"]})
    print(f"\ncommission_ax module: {modules}")
    
    # Find sale orders with commission data
    orders = models.execute_kw(db, uid, password, "sale.order", "search_read", 
        [[("state", "in", ["sale", "done"])]], 
        {"fields": ["id", "name", "broker_amount", "referrer_amount", "cashback_amount", 
                    "agent1_amount", "agent2_amount", "manager_amount", "director_amount",
                    "amount_total", "amount_untaxed"], "limit": 10})
    
    print(f"\nFound {len(orders)} confirmed sale orders")
    
    # Find orders with commission
    orders_with_commission = []
    for order in orders:
        total_comm = sum([
            order.get("broker_amount") or 0,
            order.get("referrer_amount") or 0,
            order.get("cashback_amount") or 0,
            order.get("agent1_amount") or 0,
            order.get("agent2_amount") or 0,
            order.get("manager_amount") or 0,
            order.get("director_amount") or 0,
        ])
        if total_comm > 0:
            orders_with_commission.append(order)
            print(f"\n  {order['name']}:")
            print(f"    Total Order: {order['amount_total']:,.2f} AED")
            print(f"    Broker: {order.get('broker_amount') or 0:,.2f}")
            print(f"    Referrer: {order.get('referrer_amount') or 0:,.2f}")
            print(f"    Agent1: {order.get('agent1_amount') or 0:,.2f}")
            print(f"    Manager: {order.get('manager_amount') or 0:,.2f}")
            print(f"    Director: {order.get('director_amount') or 0:,.2f}")
            print(f"    TOTAL COMMISSION: {total_comm:,.2f}")
    
    if orders_with_commission:
        # Try to generate report for first order with commission
        test_order = orders_with_commission[0]
        print(f"\n{'='*60}")
        print(f"GENERATING REPORT FOR: {test_order['name']}")
        print(f"{'='*60}")
        
        try:
            # Get report action
            report_action = models.execute_kw(db, uid, password, "ir.actions.report", "search_read",
                [[("report_name", "=", "commission_ax.commission_payout_report_template_professional")]],
                {"fields": ["id", "name", "report_name", "model"]})
            print(f"\nReport action found: {report_action}")
            
            if report_action:
                # Generate PDF
                pdf_data = report.render_report(db, uid, password, 
                    "commission_ax.commission_payout_report_template_professional",
                    [test_order["id"]])
                
                if pdf_data:
                    pdf_content = base64.b64decode(pdf_data[0])
                    filename = f"/tmp/commission_report_{test_order['name'].replace('/', '_')}.pdf"
                    with open(filename, "wb") as f:
                        f.write(pdf_content)
                    print(f"\n✅ SUCCESS! Report generated: {filename}")
                    print(f"   File size: {len(pdf_content):,} bytes")
                else:
                    print("\n❌ Report returned empty data")
        except Exception as e:
            print(f"\n❌ Error generating report: {e}")
            
            # Try alternative method
            try:
                print("\nTrying alternative report generation method...")
                result = models.execute_kw(db, uid, password, "ir.actions.report", "render_qweb_pdf",
                    [[report_action[0]["id"]], [test_order["id"]]])
                print(f"Alternative result: {type(result)}")
            except Exception as e2:
                print(f"Alternative method also failed: {e2}")
    else:
        print("\n⚠️  No orders with commission data found")
        print("Please create a sale order with commission entries to test the report")
        
else:
    print("❌ Authentication failed!")
