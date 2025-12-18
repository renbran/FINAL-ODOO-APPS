#!/usr/bin/env python3
"""
Commission Report Test Script - Generate PDF
"""

import xmlrpc.client
import base64
import os

URL = "http://127.0.0.1:3000"
DB = "osusproperties"
USERNAME = "admin"
PASSWORD = "admin123"

def test_report():
    print("=" * 60)
    print("COMMISSION REPORT PDF GENERATION TEST")
    print("=" * 60)
    
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    print(f"\nServer: {common.version()['server_version']}")
    
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    if not uid:
        print("ERROR: Authentication failed!")
        return False
    print(f"Authenticated as UID: {uid}")
    
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    
    # Find the report action
    print("\n1. Finding report action...")
    reports = models.execute_kw(DB, uid, PASSWORD, 'ir.actions.report', 'search_read',
        [[['report_name', '=', 'enhanced_status.commission_payout_report_template_final']]],
        {'fields': ['id', 'name', 'report_name', 'model']}
    )
    
    if not reports:
        print("   ERROR: Report action not found!")
        return False
    
    report = reports[0]
    print(f"   Found: {report['name']}")
    print(f"   ID: {report['id']}")
    print(f"   Report Name: {report['report_name']}")
    
    # Get a sale order
    print("\n2. Finding a sale order with commission data...")
    orders = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_read',
        [[['state', 'in', ['sale', 'done']]]],
        {'fields': ['id', 'name', 'amount_total', 'broker_amount', 'agent1_amount'], 'limit': 5}
    )
    
    if not orders:
        print("   ERROR: No confirmed orders found!")
        return False
    
    # Find order with commission data
    order = None
    for o in orders:
        has_commission = (o.get('broker_amount') or 0) > 0 or (o.get('agent1_amount') or 0) > 0
        print(f"   - {o['name']}: broker={o.get('broker_amount', 0)}, agent1={o.get('agent1_amount', 0)}")
        if has_commission and not order:
            order = o
    
    if not order:
        order = orders[0]
        print(f"   Using order without commission data: {order['name']}")
    else:
        print(f"   Using order with commission: {order['name']}")
    
    # Generate PDF
    print(f"\n3. Generating PDF for order {order['name']}...")
    try:
        result = models.execute_kw(DB, uid, PASSWORD, 'ir.actions.report', 'render_qweb_pdf',
            [report['id'], [order['id']]]
        )
        
        if result:
            # Result is (pdf_content, report_type)
            pdf_data = result[0] if isinstance(result, (list, tuple)) else result
            
            # Decode if base64
            if isinstance(pdf_data, str):
                pdf_bytes = base64.b64decode(pdf_data)
            else:
                pdf_bytes = pdf_data
            
            filename = f"/tmp/commission_report_{order['name'].replace('/', '_')}.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_bytes)
            
            file_size = os.path.getsize(filename)
            print(f"   ✅ SUCCESS! Report generated!")
            print(f"   File: {filename}")
            print(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # Quick validation
            if file_size < 1000:
                print("   ⚠️  Warning: File seems too small, may be empty or error page")
            elif file_size > 5000:
                print("   ✅ File size looks good!")
            
            return True
        else:
            print("   ERROR: No result from render_qweb_pdf")
            return False
            
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_report()
    print("\n" + "=" * 60)
    print("TEST RESULT:", "✅ PASSED" if success else "❌ FAILED")
    print("=" * 60)
