# CloudPepper Chart.js Emergency Fix Deployment

# Step 1: Backup current module
sudo cp -r /var/odoo/erposus/addons/oe_sale_dashboard_17 /var/odoo/erposus/addons/oe_sale_dashboard_17.backup.$(date +%Y%m%d_%H%M%S)

# Step 2: Upload emergency fix files
# Upload: oe_sale_dashboard_17/static/src/js/emergency_chartjs_fix.js
# Upload: oe_sale_dashboard_17/__manifest__.py

# Step 3: Set correct permissions
sudo chown -R odoo:odoo /var/odoo/erposus/addons/oe_sale_dashboard_17
sudo chmod -R 644 /var/odoo/erposus/addons/oe_sale_dashboard_17/static/src/js/*

# Step 4: Update module assets
sudo -u odoo odoo-bin -u oe_sale_dashboard_17 -d erposus --stop-after-init

# Step 5: Restart Odoo service
sudo systemctl restart odoo

# Step 6: Verify deployment
sudo systemctl status odoo
sudo tail -f /var/log/odoo/odoo.log | grep -i chart