#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(dbname="scholarixv2")
cur = conn.cursor()

# Check views
cur.execute("SELECT id, key FROM ir_ui_view WHERE key ILIKE '%sales_offer%'")
print("=== Views ===")
for row in cur.fetchall():
    print(row)

# Check report actions
cur.execute("SELECT id, report_name, model FROM ir_act_report_xml WHERE report_name ILIKE '%sales_offer%'")
print("\n=== Report Actions ===")
for row in cur.fetchall():
    print(row)

conn.close()
