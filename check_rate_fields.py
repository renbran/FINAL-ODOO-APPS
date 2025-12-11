#!/usr/bin/env python3
import xmlrpc.client

url = 'http://127.0.0.1:3000'
common = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/common')
uid = common.authenticate('osusproperties', 'admin', 'admin123', {})
models = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/object')

# Get all commission-related fields from sale.order
fields = models.execute_kw('osusproperties', uid, 'admin123', 'sale.order', 'fields_get',
    [], {'attributes': ['string', 'type']}
)

print('=' * 70)
print('COMMISSION RATE FIELDS IN sale.order')
print('=' * 70)

rate_fields = []
for name, info in sorted(fields.items()):
    if 'rate' in name.lower() or 'percent' in name.lower():
        rate_fields.append((name, info.get('string'), info.get('type')))
        
print('\nRate/Percentage Fields:')
for name, string, ftype in rate_fields:
    print(f'  {name}: "{string}" ({ftype})')

# Get sample data from an order
print('\n' + '=' * 70)
print('SAMPLE DATA FROM ORDER PS/11/4534')
print('=' * 70)

order = models.execute_kw('osusproperties', uid, 'admin123', 'sale.order', 'search_read',
    [[['name', '=', 'PS/11/4534']]],
    {'fields': [f[0] for f in rate_fields] + [
        'broker_amount', 'broker_partner_id',
        'referrer_amount', 'referrer_partner_id',
        'cashback_amount', 'cashback_partner_id',
        'other_external_amount', 'other_external_partner_id',
        'agent1_amount', 'agent1_partner_id',
        'agent2_amount', 'agent2_partner_id',
        'manager_amount', 'manager_partner_id',
        'director_amount', 'director_partner_id',
        'salesperson_commission', 'manager_commission',
        'consultant_comm_percentage', 'manager_comm_percentage',
    ], 'limit': 1}
)

if order:
    o = order[0]
    print('\nExternal Commissions:')
    print(f'  Broker: {o.get("broker_partner_id")} - Amount: {o.get("broker_amount")}')
    for f in rate_fields:
        if 'broker' in f[0]:
            print(f'    {f[0]}: {o.get(f[0])}')
    
    print(f'  Referrer: {o.get("referrer_partner_id")} - Amount: {o.get("referrer_amount")}')
    for f in rate_fields:
        if 'referrer' in f[0]:
            print(f'    {f[0]}: {o.get(f[0])}')
    
    print(f'  Cashback: {o.get("cashback_partner_id")} - Amount: {o.get("cashback_amount")}')
    for f in rate_fields:
        if 'cashback' in f[0]:
            print(f'    {f[0]}: {o.get(f[0])}')
            
    print(f'  Other External: {o.get("other_external_partner_id")} - Amount: {o.get("other_external_amount")}')
    for f in rate_fields:
        if 'other_external' in f[0]:
            print(f'    {f[0]}: {o.get(f[0])}')
    
    print('\nInternal Commissions:')
    print(f'  Manager: {o.get("manager_partner_id")} - Amount: {o.get("manager_amount")}')
    for f in rate_fields:
        if 'manager' in f[0] and 'comm' not in f[0]:
            print(f'    {f[0]}: {o.get(f[0])}')
    
    print(f'  Director: {o.get("director_partner_id")} - Amount: {o.get("director_amount")}')
    for f in rate_fields:
        if 'director' in f[0] and 'comm' not in f[0]:
            print(f'    {f[0]}: {o.get(f[0])}')
    
    print(f'  Agent1: {o.get("agent1_partner_id")} - Amount: {o.get("agent1_amount")}')
    for f in rate_fields:
        if 'agent1' in f[0]:
            print(f'    {f[0]}: {o.get(f[0])}')
    
    print(f'  Agent2: {o.get("agent2_partner_id")} - Amount: {o.get("agent2_amount")}')
    for f in rate_fields:
        if 'agent2' in f[0]:
            print(f'    {f[0]}: {o.get(f[0])}')
    
    print('\nLegacy Commissions:')
    print(f'  Salesperson Commission: {o.get("salesperson_commission")}')
    print(f'  Consultant Comm %: {o.get("consultant_comm_percentage")}')
    print(f'  Manager Commission: {o.get("manager_commission")}')
    print(f'  Manager Comm %: {o.get("manager_comm_percentage")}')
