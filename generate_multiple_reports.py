#!/usr/bin/env python3
"""
Generate multiple commission reports for testing
"""

import xmlrpc.client
import requests
import os

URL = "http://127.0.0.1:3000"
DB = "osusproperties"
USERNAME = "admin"
PASSWORD = "admin123"

def generate_reports():
    print("=" * 60)
    print("GENERATING MULTIPLE COMMISSION REPORTS")
    print("=" * 60)
    
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    
    # Get orders with highest commission
    orders = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_read',
        [[['state', 'in', ['sale', 'done']]]],
        {'fields': ['id', 'name', 'amount_total', 'broker_amount', 'agent1_amount', 
                    'manager_amount', 'director_amount', 'referrer_amount', 
                    'cashback_amount', 'other_external_amount', 'agent2_amount'], 
         'limit': 10}
    )
    
    # Calculate total commission for each
    for o in orders:
        o['total_commission'] = sum([
            o.get('broker_amount') or 0,
            o.get('agent1_amount') or 0,
            o.get('agent2_amount') or 0,
            o.get('manager_amount') or 0,
            o.get('director_amount') or 0,
            o.get('referrer_amount') or 0,
            o.get('cashback_amount') or 0,
            o.get('other_external_amount') or 0,
        ])
    
    # Sort by total commission
    orders.sort(key=lambda x: x['total_commission'], reverse=True)
    
    print("\nTop 5 orders by commission:")
    for i, o in enumerate(orders[:5]):
        print(f"  {i+1}. {o['name']}: {o['total_commission']:,.2f} AED (Order Total: {o['amount_total']:,.2f})")
    
    # Create session
    session = requests.Session()
    login_url = f"{URL}/web/session/authenticate"
    login_data = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {"db": DB, "login": USERNAME, "password": PASSWORD},
        "id": 1
    }
    session.post(login_url, json=login_data)
    
    # Generate reports for top 3
    print("\nGenerating reports for top 3 orders...")
    generated = []
    
    for order in orders[:3]:
        report_url = f"{URL}/report/pdf/enhanced_status.commission_payout_report_template_final/{order['id']}"
        response = session.get(report_url)
        
        if response.status_code == 200 and response.content[:4] == b'%PDF':
            filename = f"/tmp/commission_{order['name'].replace('/', '_')}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            size = os.path.getsize(filename)
            generated.append((order['name'], filename, size))
            print(f"  ✅ {order['name']}: {size/1024:.1f} KB")
        else:
            print(f"  ❌ {order['name']}: Failed to generate")
    
    print("\n" + "=" * 60)
    print(f"Generated {len(generated)} reports successfully!")
    for name, path, size in generated:
        print(f"  - {path}")
    print("=" * 60)

if __name__ == "__main__":
    generate_reports()
