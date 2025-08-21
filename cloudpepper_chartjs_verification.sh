#!/bin/bash
# CloudPepper Chart.js Emergency Fix Verification

echo "CloudPepper Chart.js Emergency Fix Verification"
echo "================================================="

# Check if emergency fix is loaded
echo "Checking emergency fix file..."
if [ -f "/var/odoo/erposus/addons/oe_sale_dashboard_17/static/src/js/emergency_chartjs_fix.js" ]; then
    echo "Emergency Chart.js fix file present"
    file_size=$(stat -c%s "/var/odoo/erposus/addons/oe_sale_dashboard_17/static/src/js/emergency_chartjs_fix.js")
    echo "File size: $file_size bytes"
else
    echo "Emergency Chart.js fix file missing"
fi

# Check Odoo service status
echo ""
echo "Checking Odoo service..."
if systemctl is-active --quiet odoo; then
    echo "Odoo service running"
else
    echo "Odoo service not running"
fi

# Check for Chart.js errors in logs
echo ""
echo "Checking for Chart.js errors in recent logs..."
recent_chartjs_errors=$(sudo tail -n 100 /var/log/odoo/odoo.log | grep -i "chart\.js\|chartjs" | grep -i "error\|fail")
if [ -z "$recent_chartjs_errors" ]; then
    echo "No recent Chart.js errors found"
else
    echo "Recent Chart.js related messages:"
    echo "$recent_chartjs_errors"
fi

# Check for emergency fix activation
echo ""
echo "Checking emergency fix activation..."
emergency_messages=$(sudo tail -n 50 /var/log/odoo/odoo.log | grep "CloudPepper Emergency")
if [ -n "$emergency_messages" ]; then
    echo "Emergency fix activation detected:"
    echo "$emergency_messages"
else
    echo "No emergency fix activation messages (may be normal if no errors occurred)"
fi

echo ""
echo "Verification complete!"
echo "Next: Test dashboard functionality in browser"
