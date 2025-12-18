#!/usr/bin/env python3
"""
Commission Report Test - Using report URL
"""

import xmlrpc.client
import requests
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
    
    # Get a sale order with commission data
    print("\n1. Finding a sale order with commission data...")
    orders = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_read',
        [[['state', 'in', ['sale', 'done']]]],
        {'fields': ['id', 'name', 'amount_total', 'broker_amount', 'agent1_amount', 
                    'manager_amount', 'director_amount', 'referrer_amount'], 'limit': 5}
    )
    
    if not orders:
        print("   ERROR: No confirmed orders found!")
        return False
    
    for o in orders:
        total_comm = sum([
            o.get('broker_amount') or 0,
            o.get('agent1_amount') or 0,
            o.get('manager_amount') or 0,
            o.get('director_amount') or 0,
            o.get('referrer_amount') or 0,
        ])
        print(f"   - {o['name']}: Total Commission = {total_comm:,.2f} AED")
    
    order = orders[0]
    print(f"\n   Selected: {order['name']} (ID: {order['id']})")
    
    # Get session via web login
    print("\n2. Creating web session for report download...")
    session = requests.Session()
    
    # Login to get session
    login_url = f"{URL}/web/session/authenticate"
    login_data = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "db": DB,
            "login": USERNAME,
            "password": PASSWORD
        },
        "id": 1
    }
    
    response = session.post(login_url, json=login_data)
    if response.status_code != 200:
        print(f"   ERROR: Login failed with status {response.status_code}")
        return False
    
    result = response.json()
    if result.get('error'):
        print(f"   ERROR: {result['error']}")
        return False
    
    print("   ✅ Session created successfully")
    
    # Generate report PDF via URL
    print(f"\n3. Generating PDF for order {order['name']}...")
    report_url = f"{URL}/report/pdf/enhanced_status.commission_payout_report_template_final/{order['id']}"
    
    response = session.get(report_url)
    
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', '')
        
        if 'pdf' in content_type.lower() or response.content[:4] == b'%PDF':
            filename = f"/tmp/commission_report_{order['name'].replace('/', '_')}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(filename)
            print(f"   ✅ SUCCESS! Report generated!")
            print(f"   File: {filename}")
            print(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            if file_size > 5000:
                print("   ✅ File size looks good - professional report generated!")
            
            return True
        else:
            print(f"   ERROR: Response is not PDF. Content-Type: {content_type}")
            print(f"   First 500 chars: {response.text[:500]}")
            return False
    else:
        print(f"   ERROR: Request failed with status {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        return False

if __name__ == "__main__":
    success = test_report()
    print("\n" + "=" * 60)
    print("TEST RESULT:", "✅ PASSED" if success else "❌ FAILED")
    print("=" * 60)
