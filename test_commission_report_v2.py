#!/usr/bin/env python3
"""
Commission Report Test Script
Tests the commission_ax module report generation
"""

import xmlrpc.client
import base64
import os
from datetime import datetime

# Server configuration
URL = "http://127.0.0.1:3000"
DB = "osusproperties"
USERNAME = "admin"
PASSWORD = "admin123"

def test_commission_report():
    print("=" * 60)
    print("COMMISSION PAYOUT REPORT TEST")
    print("=" * 60)
    
    # Connect
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    print(f"\nServer: {common.version()['server_version']}")
    
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    if not uid:
        print("ERROR: Authentication failed!")
        return False
    print(f"Authenticated as UID: {uid}")
    
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    
    # Check if commission_ax module is installed
    print("\n1. Checking commission_ax module...")
    module = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
        [[['name', '=', 'commission_ax']]],
        {'fields': ['name', 'state', 'latest_version']}
    )
    if module:
        print(f"   Module: {module[0]['name']}")
        print(f"   State: {module[0]['state']}")
        print(f"   Version: {module[0].get('latest_version', 'N/A')}")
    else:
        print("   ERROR: commission_ax module not found!")
        return False
    
    # Check if report action exists
    print("\n2. Checking report action...")
    report_action = models.execute_kw(DB, uid, PASSWORD, 'ir.actions.report', 'search_read',
        [[['report_name', 'like', 'commission']]],
        {'fields': ['name', 'report_name', 'model', 'report_type']}
    )
    if report_action:
        for r in report_action:
            print(f"   Report: {r['name']}")
            print(f"   Technical Name: {r['report_name']}")
            print(f"   Model: {r['model']}")
            print(f"   Type: {r['report_type']}")
    else:
        print("   No commission reports found!")
    
    # Find sale orders with commission data
    print("\n3. Finding sale orders with commissions...")
    orders = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_read',
        [[['state', 'in', ['sale', 'done']]]],
        {'fields': ['name', 'partner_id', 'amount_total', 'state'], 'limit': 5}
    )
    if orders:
        print(f"   Found {len(orders)} confirmed orders")
        for o in orders[:3]:
            print(f"   - {o['name']}: {o['amount_total']} ({o['state']})")
    else:
        print("   No confirmed orders found")
    
    # Check commission.line records
    print("\n4. Checking commission line records...")
    try:
        comm_lines = models.execute_kw(DB, uid, PASSWORD, 'commission.line', 'search_count', [[]])
        print(f"   Total commission lines: {comm_lines}")
        
        if comm_lines > 0:
            sample = models.execute_kw(DB, uid, PASSWORD, 'commission.line', 'search_read',
                [[]],
                {'fields': ['name', 'amount', 'sale_order_id'], 'limit': 3}
            )
            for s in sample:
                print(f"   - {s.get('name', 'N/A')}: {s.get('amount', 0)}")
    except Exception as e:
        print(f"   Commission line model access error: {e}")
    
    # Try to generate report
    print("\n5. Attempting to generate report...")
    if orders:
        order_id = orders[0]['id']
        try:
            # Find the specific report
            reports = models.execute_kw(DB, uid, PASSWORD, 'ir.actions.report', 'search_read',
                [[['report_name', '=', 'commission_ax.report_commission_payout_professional']]],
                {'fields': ['id', 'name']}
            )
            if reports:
                report_id = reports[0]['id']
                print(f"   Using report: {reports[0]['name']} (ID: {report_id})")
                
                # Generate PDF
                result = models.execute_kw(DB, uid, PASSWORD, 'ir.actions.report', 'render_qweb_pdf',
                    [report_id, [order_id]]
                )
                if result:
                    pdf_data = result[0] if isinstance(result, tuple) else result
                    pdf_bytes = base64.b64decode(pdf_data) if isinstance(pdf_data, str) else pdf_data
                    
                    filename = f"/tmp/commission_report_{orders[0]['name']}.pdf"
                    with open(filename, 'wb') as f:
                        f.write(pdf_bytes)
                    
                    file_size = os.path.getsize(filename)
                    print(f"   SUCCESS! Report generated: {filename}")
                    print(f"   File size: {file_size} bytes")
                    return True
            else:
                print("   Report action not found, trying alternate name...")
                # Try alternate report names
                alt_reports = models.execute_kw(DB, uid, PASSWORD, 'ir.actions.report', 'search_read',
                    [[['report_name', 'like', 'commission_ax%']]],
                    {'fields': ['id', 'name', 'report_name']}
                )
                for r in alt_reports:
                    print(f"   - Found: {r['report_name']}")
        except Exception as e:
            print(f"   Report generation error: {e}")
    
    return False

if __name__ == "__main__":
    success = test_commission_report()
    print("\n" + "=" * 60)
    print("TEST RESULT:", "PASSED" if success else "NEEDS ATTENTION")
    print("=" * 60)
