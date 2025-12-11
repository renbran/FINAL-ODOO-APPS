#!/usr/bin/env python3
import xmlrpc.client

url = 'http://127.0.0.1:3000'
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate('osusproperties', 'admin', 'admin123', {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Check report actions for sale.order
print("Checking Sale Order print options...")
reports = models.execute_kw('osusproperties', uid, 'admin123', 'ir.actions.report', 'search_read',
    [[['model', '=', 'sale.order'], ['binding_model_id', '!=', False]]],
    {'fields': ['id', 'name', 'report_name', 'binding_type']}
)

print(f"\nFound {len(reports)} print options for Sale Orders:")
for r in reports:
    print(f"  - ID {r['id']}: {r['name']}")
    print(f"    Report: {r['report_name']}")
    print(f"    Binding: {r['binding_type']}")
    print()

# Check specifically for commission report
print("\nChecking Commission Report specifically...")
comm_reports = models.execute_kw('osusproperties', uid, 'admin123', 'ir.actions.report', 'search_read',
    [[['report_name', 'like', 'commission']]],
    {'fields': ['id', 'name', 'report_name', 'binding_model_id', 'binding_type', 'groups_id']}
)

for r in comm_reports:
    print(f"  - {r['name']}")
    print(f"    ID: {r['id']}")
    print(f"    Report Name: {r['report_name']}")
    print(f"    Binding Model ID: {r['binding_model_id']}")
    print(f"    Binding Type: {r['binding_type']}")
    print(f"    Groups: {r['groups_id']}")
