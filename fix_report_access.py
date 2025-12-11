#!/usr/bin/env python3
import xmlrpc.client

url = 'http://127.0.0.1:3000'
common = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/common')
uid = common.authenticate('osusproperties', 'admin', 'admin123', {})
models = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/object')

# Check group 525
group = models.execute_kw('osusproperties', uid, 'admin123', 'res.groups', 'search_read',
    [[['id', '=', 525]]],
    {'fields': ['name', 'full_name']}
)
print('Group 525:', group)

# Option to remove restriction - update report to have no group restriction
print('\nRemoving group restriction from Commission Report...')
models.execute_kw('osusproperties', uid, 'admin123', 'ir.actions.report', 'write',
    [[2206], {'groups_id': [(5, 0, 0)]}]  # Clear all groups
)
print('Done! Report should now be visible to all users.')

# Verify
report = models.execute_kw('osusproperties', uid, 'admin123', 'ir.actions.report', 'search_read',
    [[['id', '=', 2206]]],
    {'fields': ['name', 'groups_id']}
)
print('Updated report:', report)
