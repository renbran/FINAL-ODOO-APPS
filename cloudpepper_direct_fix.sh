#!/bin/bash
# CloudPepper Direct RPC Fix - Self-Service Script
# Run this if you have SSH/console access to CloudPepper

echo "🚀 CloudPepper Direct RPC Fix"
echo "=============================="

# Step 1: Apply database fixes (if you have psql access)
echo "1. Applying database fixes..."
if command -v psql &> /dev/null; then
    psql -d osustst -f autovacuum_fix.sql
    psql -d osustst -f datetime_fix.sql
    echo "✓ Database fixes applied"
else
    echo "⚠ No psql access - database fixes need manual application"
fi

# Step 2: Clear Odoo caches
echo "2. Clearing Odoo caches..."
if [ -d "/opt/odoo" ]; then
    find /opt/odoo -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
    find /opt/odoo -name "*.pyc" -delete 2>/dev/null
    echo "✓ Python cache cleared"
fi

# Step 3: Restart Odoo (if you have service access)
echo "3. Attempting Odoo restart..."
if command -v systemctl &> /dev/null; then
    sudo systemctl restart odoo
    echo "✓ Odoo service restarted"
elif command -v service &> /dev/null; then
    sudo service odoo restart
    echo "✓ Odoo service restarted"
else
    echo "⚠ No service access - manual restart required"
fi

echo ""
echo "✅ Direct fix completed!"
echo "Test your CloudPepper site now: https://osusbck.cloudpepper.site/"
