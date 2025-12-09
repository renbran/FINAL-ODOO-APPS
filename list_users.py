#!/usr/bin/env python3
import xmlrpc.client

url = "http://127.0.0.1:3000"
db = "osusproperties"

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
print("Server version:", common.version())

# Try various credentials
test_credentials = [
    ("admin", "admin"),
    ("admin", "OsUs@2025"),
    ("admin", "admin123"),
    ("admin", "odoo"),
    ("test", "test"),
    ("test", "OsUs@2025"),
]

for username, password in test_credentials:
    try:
        uid = common.authenticate(db, username, password, {})
        if uid:
            print(f"SUCCESS: {username} / {password} -> UID: {uid}")
            break
    except Exception as e:
        print(f"Error with {username}: {e}")
else:
    print("No valid credentials found")
