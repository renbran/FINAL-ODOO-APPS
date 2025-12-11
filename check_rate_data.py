#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(dbname='osusproperties', user='odoo', password='odoo', host='localhost')
cur = conn.cursor()

# Check rate fields for orders with manager or agent amounts
cur.execute('''
    SELECT id, name, 
           manager_rate, manager_amount, 
           agent1_rate, agent1_amount,
           director_rate, director_amount
    FROM sale_order 
    WHERE manager_amount > 0 OR agent1_amount > 0 OR director_amount > 0
    ORDER BY id DESC LIMIT 10
''')

print("Rate vs Amount Analysis:")
print("=" * 100)
for row in cur.fetchall():
    order_id, name, mgr_rate, mgr_amt, a1_rate, a1_amt, dir_rate, dir_amt = row
    print(f"\nOrder {order_id} ({name}):")
    if mgr_amt and mgr_amt > 0:
        print(f"  Manager:  rate={mgr_rate}, amount={mgr_amt}")
        if mgr_rate and mgr_rate > 100:
            print(f"    ⚠️  ISSUE: Rate > 100% - should show 'Fix Amount'")
    if a1_amt and a1_amt > 0:
        print(f"  Agent1:   rate={a1_rate}, amount={a1_amt}")
        if a1_rate and a1_rate > 100:
            print(f"    ⚠️  ISSUE: Rate > 100% - should show 'Fix Amount'")
    if dir_amt and dir_amt > 0:
        print(f"  Director: rate={dir_rate}, amount={dir_amt}")
        if dir_rate and dir_rate > 100:
            print(f"    ⚠️  ISSUE: Rate > 100% - should show 'Fix Amount'")

conn.close()
