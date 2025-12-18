import psycopg2
conn = psycopg2.connect(dbname='scholarixv2', user='postgres')
cur = conn.cursor()
cur.execute("""
    SELECT m1.name, m1.state 
    FROM ir_module_module_dependency d
    JOIN ir_module_module m1 ON d.module_id = m1.id
    WHERE d.name IN ('muk_web_theme', 'muk_web_chatter', 'muk_web_dialog', 'muk_web_appsbar', 'muk_web_colors')
    AND m1.state = 'installed'
""")
print('Modules depending on MuK components:')
print('=' * 60)
deps = cur.fetchall()
if deps:
    for row in deps:
        print(f'  {row[0]} ({row[1]})')
else:
    print('  No dependencies found - safe to uninstall')
conn.close()
