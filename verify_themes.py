import psycopg2
conn = psycopg2.connect(dbname='scholarixv2', user='postgres', host='localhost')
cur = conn.cursor()
cur.execute("SELECT name, state, latest_version FROM ir_module_module WHERE name IN ('sgc_tech_ai_theme', 'muk_web_theme') ORDER BY name")
print('Theme Module Status:')
print('=' * 60)
for row in cur.fetchall():
    print(f'{row[0]:25} {row[1]:12} {row[2]}')
conn.close()
