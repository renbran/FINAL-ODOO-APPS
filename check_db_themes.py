import psycopg2

conn = psycopg2.connect(dbname="scholarixv2", user="postgres")
cur = conn.cursor()

# Check for installed theme/web modules
cur.execute("""
    SELECT name, state, latest_version 
    FROM ir_module_module 
    WHERE state='installed' 
    AND (name LIKE '%theme%' OR name LIKE '%web_%' OR name LIKE '%css%' OR name LIKE '%style%' OR name LIKE '%sgc%')
    ORDER BY name
""")

print("="*80)
print("INSTALLED MODULES THAT MAY AFFECT CSS/THEMING:")
print("="*80)
for row in cur.fetchall():
    print(f"{row[0]:<45} {row[1]:<15} v{row[2]}")

# Check for CSS conflicts in ir_asset
cur.execute("""
    SELECT name, bundle, path 
    FROM ir_asset 
    WHERE bundle = 'web.assets_backend' 
    AND (path LIKE '%.scss' OR path LIKE '%.css')
    AND name LIKE '%theme%'
    LIMIT 50
""")

print("\n" + "="*80)
print("THEME ASSETS IN web.assets_backend:")
print("="*80)
for row in cur.fetchall():
    print(f"{row[0]:<30} | {row[2]}")

conn.close()
