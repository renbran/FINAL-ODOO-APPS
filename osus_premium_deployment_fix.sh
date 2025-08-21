#!/bin/bash

echo "=== OSUS PREMIUM MODULE DEPLOYMENT FIX ==="

# 1. Check current module status
echo "1. Checking current module status..."
cd /var/odoo/erposus

# 2. Verify addons paths
echo "2. Current addons paths:"
sudo -u odoo grep "addons_path" odoo.conf

# 3. Look for osus_premium in all addons directories
echo "3. Searching for osus_premium module..."
find /var/odoo/erposus -name "osus_premium" -type d 2>/dev/null

# 4. Check if module exists in extra-addons
echo "4. Checking extra-addons directory..."
ls -la extra-addons/odoo17_final*/osus_premium/ 2>/dev/null || echo "osus_premium not found in extra-addons"

# 5. If not found, let's check the git repository
echo "5. Checking git repository status..."
cd extra-addons/odoo17_final*/
git log --oneline -5 | grep -i osus || echo "No OSUS commits found in recent history"

# 6. Check if the module was committed
echo "6. Checking if osus_premium exists in repository..."
ls -la osus_premium/ 2>/dev/null || echo "osus_premium module not found in current git checkout"

# 7. If missing, we need to pull latest changes
echo "7. Pulling latest changes from repository..."
git fetch origin
git pull origin main

# 8. Verify module exists now
echo "8. Verifying module after pull..."
ls -la osus_premium/ 2>/dev/null || echo "osus_premium still not found - need manual deployment"

# 9. If still missing, we need to add module manually
if [ ! -d "osus_premium" ]; then
    echo "9. Module missing - need to add manually"
    echo "Please copy the osus_premium module to: $(pwd)/osus_premium/"
    echo "Then run: sudo systemctl restart odoo"
else
    echo "9. Module found - attempting installation..."
    cd /var/odoo/erposus
    sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d erposus --no-http --stop-after-init -i osus_premium
    echo "10. Restarting Odoo..."
    sudo systemctl restart odoo
    echo "11. Module should now be available at: http://your-domain/web?db=erposus"
fi
