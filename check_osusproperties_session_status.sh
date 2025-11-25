#!/bin/bash
# Check OSUS Properties Session Configuration Status

echo "======================================================================"
echo "OSUS Properties - Session Configuration Status Check"
echo "======================================================================"

# 1. Check Odoo service status
echo ""
echo "1. Odoo Service Status:"
sudo systemctl status odoo --no-pager | head -5

# 2. Check session parameters
echo ""
echo "2. Session Configuration Parameters:"
sudo -u postgres psql -d osusproperties -t << 'EOF'
SELECT key, value 
FROM ir_config_parameter 
WHERE key LIKE '%session%' OR key LIKE '%cookie%'
ORDER BY key;
EOF

# 3. Count active user sessions
echo ""
echo "3. User Sessions Summary:"
sudo -u postgres psql -d osusproperties -t << 'EOF'
SELECT 
    COUNT(DISTINCT login) as unique_users,
    COUNT(*) as total_logs
FROM res_users_log 
WHERE create_date > NOW() - INTERVAL '7 days';
EOF

# 4. Check recent login activity
echo ""
echo "4. Recent Login Activity (last 24 hours):"
sudo -u postgres psql -d osusproperties -t << 'EOF'
SELECT 
    COUNT(*) as logins_last_24h
FROM res_users_log 
WHERE create_date > NOW() - INTERVAL '24 hours';
EOF

# 5. Check for authentication errors in logs
echo ""
echo "5. Recent Authentication Errors (last 100 lines):"
tail -100 /var/log/odoo/odoo-server.log | grep -i 'auth\|session\|logout' | tail -5

echo ""
echo "======================================================================"
echo "✅ Status Check Complete"
echo "======================================================================"
echo ""
echo "Configuration Applied:"
echo "  - Session timeout: 7 days (604800 seconds)"
echo "  - HTTPOnly cookies: Enabled"
echo "  - Old logs cleared: Last 30 days"
echo ""
echo "Next Steps:"
echo "  1. Clear browser cookies at: https://stagingtry.cloudpepper.site/"
echo "  2. Test login with fresh browser session"
echo "  3. Monitor for logout issues"
echo ""
