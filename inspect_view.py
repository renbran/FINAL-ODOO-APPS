#!/usr/bin/env python3
import xmlrpc.client

# Connect to Odoo
url = 'http://localhost:8069'
db = 'postgres'
username = 'admin'
password = 'admin'

try:
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    
    if uid:
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # Get the sale order form view
        view_id = models.execute_kw(db, uid, password, 'ir.ui.view', 'search', 
                                  [[['name', '=', 'sale.order.form'], ['model', '=', 'sale.order']]], 
                                  {'limit': 1})
        
        if view_id:
            view = models.execute_kw(db, uid, password, 'ir.ui.view', 'read', 
                                   [view_id[0]], {'fields': ['arch_db']})
            print("Sale Order Form View Structure:")
            print(view[0]['arch_db'])
        else:
            print("View not found")
    else:
        print("Authentication failed")
        
except Exception as e:
    print(f"Error: {e}")
    print("Make sure Odoo is running and accessible")
