
# Deployment Commands for scholarixv2 Database
# Execute these commands on the remote server

# Step 1: Navigate to Odoo directory
cd /var/odoo/scholarixv2

# Step 2: Backup the current module (optional but recommended)
sudo -u odoo cp -r addons/announcement_banner addons/announcement_banner.backup.$(date +%Y%m%d_%H%M%S)

# Step 3: Update the module in the database (METHOD 1 - Recommended)
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 -u announcement_banner --stop-after-init

# Alternative METHOD 2: Via Odoo shell
sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf -d scholarixv2 << 'EOFPYTHON'
# Update module via shell
env = self.env
module = env['ir.module.module'].search([('name', '=', 'announcement_banner')])
if module:
    module.button_immediate_upgrade()
    print("✅ Module 'announcement_banner' updated successfully")
else:
    print("❌ Module 'announcement_banner' not found")
env.cr.commit()
EOFPYTHON

# Step 4: Restart Odoo service (if needed)
sudo systemctl restart odoo

# Step 5: Clear browser cache and test
echo "✅ Deployment complete. Clear browser cache and test the announcement banner."
